#!/usr/bin/env python3
"""Inspect Xiaomi/Zepp/MiCreate watchface packages without modifying them.

The inspector understands ZIP-based .bin/.zpk packages, nested ZIP archives,
MiCreate .fprj/.info XML, JSON configuration files, PNG/TGA headers and
printable metadata strings. It reports evidence instead of claiming device
compatibility.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import struct
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

MAX_TEXT_BYTES = 1_000_000
MAX_BINARY_SCAN_BYTES = 4_000_000
MAX_NESTED_ARCHIVE_BYTES = 32_000_000
MAX_DEPTH = 3
PRINTABLE_RE = re.compile(rb"[\x20-\x7e]{4,}")
RESOLUTION_RE = re.compile(r"(?<!\d)(\d{2,4})\s*[xX×]\s*(\d{2,4})(?!\d)")
KEYWORD_RE = re.compile(
    r"(?i)(smart\s*band|mi\s*band|miband|amazfit|deviceSource|deviceType|"
    r"deviceVersion|deciceTypeName|designWidth|hyperos|zepp|micreate|easyface|"
    r"\bgts\b|\bnxp\b)"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect_image(data: bytes) -> dict[str, Any] | None:
    if (
        len(data) >= 24
        and data.startswith(b"\x89PNG\r\n\x1a\n")
        and data[12:16] == b"IHDR"
    ):
        width, height = struct.unpack(">II", data[16:24])
        return {"format": "png", "width": width, "height": height}

    if len(data) >= 18:
        image_type = data[2]
        width = int.from_bytes(data[12:14], "little")
        height = int.from_bytes(data[14:16], "little")
        pixel_depth = data[16]
        if (
            image_type in {1, 2, 3, 9, 10, 11}
            and width > 0
            and height > 0
            and pixel_depth in {8, 15, 16, 24, 32}
        ):
            return {
                "format": "tga",
                "width": width,
                "height": height,
                "pixelDepth": pixel_depth,
                "imageType": image_type,
            }
    return None


def decode_text(data: bytes) -> str | None:
    if not data:
        return ""
    if len(data) > MAX_TEXT_BYTES:
        return None
    for encoding in ("utf-8-sig", "utf-16", "gb18030", "latin-1"):
        try:
            text = data.decode(encoding)
        except UnicodeDecodeError:
            continue
        controls = sum(
            1 for char in text if ord(char) < 32 and char not in "\n\r\t"
        )
        if controls <= max(2, len(text) // 200):
            return text
    return None


def collect_text_evidence(
    text: str, source: str, evidence: dict[str, Any]
) -> None:
    evidence["resolutions"].update(
        f"{width}x{height}" for width, height in RESOLUTION_RE.findall(text)
    )

    for line in text.splitlines():
        stripped = line.strip()
        if stripped and KEYWORD_RE.search(stripped):
            evidence["keywordLines"].append(
                {"source": source, "text": stripped[:500]}
            )

    patterns = [
        r"DeviceType\s*=\s*[\"']?([^\"'\s<>]+)",
        r"DeviceTypeName\s*=\s*[\"']([^\"']+)",
        r"DeciceTypeName\s*=\s*[\"']([^\"']+)",
        r"deviceSource[\"']?\s*[:=]\s*[\"']?([A-Za-z0-9_-]+)",
    ]
    for pattern in patterns:
        for value in re.findall(pattern, text, flags=re.IGNORECASE):
            evidence["deviceIdentifiers"].add(str(value))


def collect_json_evidence(
    value: Any, source: str, evidence: dict[str, Any], path: str = ""
) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            lower = key.lower()
            if lower in {
                "devicesource",
                "devicetype",
                "devicetypename",
                "decicetypename",
                "deviceversion",
            }:
                evidence["deviceIdentifiers"].add(str(child))
            if lower in {"designwidth", "width", "height", "resolution"}:
                evidence["jsonGeometry"].append(
                    {"source": source, "path": child_path, "value": child}
                )
            collect_json_evidence(child, source, evidence, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            collect_json_evidence(child, source, evidence, f"{path}[{index}]")
    elif isinstance(value, str):
        collect_text_evidence(value, source, evidence)


def parse_structured_text(
    text: str, source: str, evidence: dict[str, Any]
) -> dict[str, Any] | None:
    stripped = text.lstrip()
    if stripped.startswith(("{", "[")):
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return None
        result: dict[str, Any] = {"kind": "json"}
        if isinstance(value, dict):
            selected: dict[str, Any] = {}
            for key in (
                "configVersion",
                "app",
                "platforms",
                "designWidth",
                "module",
                "deviceSource",
                "deviceType",
                "packageInfo",
                "bundleInfo",
            ):
                if key in value:
                    selected[key] = value[key]
            if selected:
                result["selected"] = selected
            collect_json_evidence(value, source, evidence)
        return result

    if stripped.startswith("<"):
        result = {"kind": "xml"}
        root = re.search(r"<([A-Za-z_][\w:.-]*)([^>]*)>", stripped)
        if root:
            result["root"] = root.group(1)
            attrs = dict(
                re.findall(
                    r"([A-Za-z_:][\w:.-]*)=[\"']([^\"']*)[\"']",
                    root.group(2),
                )
            )
            if attrs:
                result["rootAttributes"] = attrs
                for key in (
                    "DeviceType",
                    "DeviceVersion",
                    "DeviceTypeName",
                    "DeciceTypeName",
                ):
                    if key in attrs:
                        evidence["deviceIdentifiers"].add(attrs[key])
        return result
    return None


def printable_strings(data: bytes) -> list[str]:
    return [
        match.decode("ascii", errors="ignore")
        for match in PRINTABLE_RE.findall(data[:MAX_BINARY_SCAN_BYTES])
    ]


def package_classification(
    entry_names: set[str], structured: list[dict[str, Any]]
) -> list[str]:
    labels: list[str] = []
    lower_names = {name.lower() for name in entry_names}
    basenames = {PurePosixPath(name).name.lower() for name in entry_names}

    if "app.json" in basenames and (
        "app.bin" in basenames or "index.bin" in basenames
    ):
        labels.append("zip-based compiled watchface package")
    if any(name.endswith(".fprj") for name in lower_names):
        labels.append("MiCreate project")
    if any(name.endswith(".info") for name in lower_names):
        labels.append("MiCreate metadata")
    if any(name.endswith(".face") for name in lower_names):
        labels.append("MiCreate face output bundle")
    if any(name.endswith(".zpk") for name in lower_names):
        labels.append("Zepp OS package container")
    if any(
        item.get("parsed", {}).get("root") == "FaceProject"
        for item in structured
    ):
        labels.append("MiCreate FaceProject XML")
    if not labels:
        labels.append("generic ZIP/archive content")
    return sorted(set(labels))


def inspect_archive_bytes(
    data: bytes, source: str, depth: int, evidence: dict[str, Any]
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "source": source,
        "depth": depth,
        "container": "zip",
        "sha256": sha256_bytes(data),
        "size": len(data),
        "entries": [],
        "structuredFiles": [],
        "nestedArchives": [],
        "imageSummary": {},
    }
    image_counter: Counter[str] = Counter()
    image_dimensions: Counter[str] = Counter()
    entry_names: set[str] = set()

    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for info in archive.infolist():
            name = info.filename
            entry_names.add(name)
            entry = {
                "name": name,
                "size": info.file_size,
                "compressedSize": info.compress_size,
                "directory": info.is_dir(),
            }
            report["entries"].append(entry)
            if info.is_dir():
                continue
            try:
                payload = archive.read(info)
            except RuntimeError as exc:
                entry["readError"] = str(exc)
                continue

            image = detect_image(payload)
            if image:
                image_counter[image["format"]] += 1
                image_dimensions[f"{image['width']}x{image['height']}"] += 1
                continue

            suffix = PurePosixPath(name).suffix.lower()
            text = (
                decode_text(payload)
                if suffix
                in {".json", ".xml", ".info", ".fprj", ".txt", ".md", ".js"}
                else None
            )
            if text is not None:
                collect_text_evidence(text, f"{source}!/{name}", evidence)
                parsed = parse_structured_text(
                    text, f"{source}!/{name}", evidence
                )
                if parsed:
                    report["structuredFiles"].append(
                        {"name": name, "parsed": parsed}
                    )

            if (
                depth < MAX_DEPTH
                and len(payload) <= MAX_NESTED_ARCHIVE_BYTES
                and zipfile.is_zipfile(io.BytesIO(payload))
            ):
                report["nestedArchives"].append(
                    inspect_archive_bytes(
                        payload, f"{source}!/{name}", depth + 1, evidence
                    )
                )
            elif suffix in {".bin", ".face", ".dat"}:
                strings = printable_strings(payload)
                if strings:
                    collect_text_evidence(
                        "\n".join(strings), f"{source}!/{name}#strings", evidence
                    )

    report["imageSummary"] = {
        "formats": dict(image_counter),
        "dimensions": dict(image_dimensions.most_common(20)),
    }
    report["classifications"] = package_classification(
        entry_names, report["structuredFiles"]
    )
    return report


def inspect_path(path: Path) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "resolutions": set(),
        "deviceIdentifiers": set(),
        "keywordLines": [],
        "jsonGeometry": [],
    }
    report: dict[str, Any] = {
        "path": str(path),
        "name": path.name,
        "size": path.stat().st_size,
        "sha256": file_sha256(path),
    }
    data = path.read_bytes()

    if zipfile.is_zipfile(io.BytesIO(data)):
        report["package"] = inspect_archive_bytes(data, path.name, 0, evidence)
    else:
        report["container"] = "raw"
        image = detect_image(data)
        if image:
            report["image"] = image
        text = decode_text(data)
        if text is not None:
            collect_text_evidence(text, path.name, evidence)
            parsed = parse_structured_text(text, path.name, evidence)
            if parsed:
                report["structured"] = parsed
        strings = printable_strings(data)
        if strings:
            collect_text_evidence(
                "\n".join(strings), f"{path.name}#strings", evidence
            )

    report["evidence"] = {
        "resolutions": sorted(evidence["resolutions"]),
        "deviceIdentifiers": sorted(evidence["deviceIdentifiers"]),
        "jsonGeometry": evidence["jsonGeometry"][:100],
        "keywordLines": evidence["keywordLines"][:100],
    }
    return report


def markdown_summary(report: dict[str, Any]) -> str:
    lines = [
        f"# Watchface package inspection: {report['name']}",
        "",
        f"- Size: `{report['size']}` bytes",
        f"- SHA-256: `{report['sha256']}`",
    ]
    package = report.get("package")
    if package:
        lines.append(f"- Container: ZIP ({len(package['entries'])} entries)")
        lines.append(
            f"- Classification: {', '.join(package.get('classifications', []))}"
        )
        image_summary = package.get("imageSummary", {})
        if image_summary.get("formats"):
            lines.append(
                "- Images: `"
                + json.dumps(image_summary["formats"], ensure_ascii=False)
                + "`"
            )
        nested_count = len(package.get("nestedArchives", []))
        if nested_count:
            lines.append(f"- Nested archives: `{nested_count}`")
    else:
        lines.append(f"- Container: `{report.get('container', 'unknown')}`")

    evidence = report.get("evidence", {})
    lines.extend(["", "## Evidence"])
    lines.append(
        f"- Resolutions: `{', '.join(evidence.get('resolutions', [])) or 'none found'}`"
    )
    lines.append(
        "- Device identifiers: `"
        + (", ".join(evidence.get("deviceIdentifiers", [])) or "none found")
        + "`"
    )

    geometry = evidence.get("jsonGeometry", [])
    if geometry:
        lines.extend(["", "### JSON geometry"])
        for item in geometry[:20]:
            lines.append(
                f"- `{item['source']}` → `{item['path']}` = `{item['value']}`"
            )

    keyword_lines = evidence.get("keywordLines", [])
    if keyword_lines:
        lines.extend(["", "### Metadata lines"])
        for item in keyword_lines[:20]:
            lines.append(f"- `{item['source']}`: {item['text']}")

    lines.extend(
        [
            "",
            "> This report identifies metadata evidence only. It does not prove installation compatibility.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--json", dest="json_output", type=Path)
    parser.add_argument("--markdown", dest="markdown_output", type=Path)
    args = parser.parse_args()

    if not args.package.is_file():
        parser.error(f"Package does not exist: {args.package}")

    report = inspect_path(args.package.resolve())
    rendered_json = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered_json, encoding="utf-8")
    else:
        print(rendered_json, end="")

    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(
            markdown_summary(report), encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

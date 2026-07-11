#!/usr/bin/env python3
"""Validate Smart Band 10 Pro target profiles and P67 package evidence."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

VALID_STATUS = {
    "reference-build-chain",
    "verified-official-package",
    "verified-custom-build-target",
}
VALID_HARDWARE = {"none", "indirect", "reported", "official"}
VALID_BUILD_CHAIN = {"none", "reference", "tested"}
VALID_DEVICE_TARGET = {
    "unverified",
    "reference-only",
    "official-package-verified",
    "custom-build-verified",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"profile must be an object: {path}")
    return value


def require_int(value: dict, key: str, minimum: int = 0) -> int:
    result = value.get(key)
    if not isinstance(result, int) or isinstance(result, bool) or result < minimum:
        raise ValueError(f"{key} must be an integer >= {minimum}")
    return result


def require_enum(value: dict, key: str, choices: set[str]) -> str:
    result = value.get(key)
    if result not in choices:
        raise ValueError(f"{key} must be one of: {', '.join(sorted(choices))}")
    return result


def require_string(value: dict, key: str) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return result


def validate_platform(platform: object, profile_id: str) -> dict:
    if not isinstance(platform, dict):
        raise ValueError("verified package profiles require a platform object")
    required = {
        "deviceModel",
        "deviceType",
        "watchOS",
        "protocol",
        "resolutionCode",
        "packet",
        "region",
        "imageFormat",
        "imageCompression",
        "compressMethod",
    }
    missing = sorted(required - platform.keys())
    if missing:
        raise ValueError("platform is missing: " + ", ".join(missing))
    for key in required - {"imageCompression"}:
        require_string(platform, key)
    if not isinstance(platform.get("imageCompression"), bool):
        raise ValueError("platform.imageCompression must be a boolean")

    if profile_id == "p67-336x480":
        expected = {
            "deviceModel": "M2551B1",
            "deviceType": "P67",
            "watchOS": "vela",
            "protocol": "1.9.4",
            "resolutionCode": "XMHD03",
            "packet": "BIN",
            "region": "CN",
            "imageFormat": "indexed8",
            "imageCompression": True,
            "compressMethod": "RLEReversed",
        }
        mismatches = [
            f"{key}={platform.get(key)!r} (expected {expected_value!r})"
            for key, expected_value in expected.items()
            if platform.get(key) != expected_value
        ]
        if mismatches:
            raise ValueError("P67 platform mismatch: " + "; ".join(mismatches))
    return platform


def validate_artifact(artifact: object) -> dict:
    if not isinstance(artifact, dict):
        raise ValueError("verified package profiles require an artifact object")
    package_name = require_string(artifact, "packageName")
    require_string(artifact, "watchfaceVersion")
    package_hash = require_string(artifact, "packageSha256")
    resource_hash = require_string(artifact, "resourceBinSha256")
    magic = require_string(artifact, "resourceBinMagic")
    theme_count = require_int(artifact, "themeCount", 1)
    if not isinstance(artifact.get("editable"), bool):
        raise ValueError("artifact.editable must be a boolean")
    if not package_name.isdigit():
        raise ValueError("artifact.packageName must be numeric")
    if not SHA256_RE.fullmatch(package_hash):
        raise ValueError("artifact.packageSha256 must be a lowercase SHA-256")
    if not SHA256_RE.fullmatch(resource_hash):
        raise ValueError("artifact.resourceBinSha256 must be a lowercase SHA-256")
    if magic != "0x1234A55A":
        raise ValueError("artifact.resourceBinMagic must be 0x1234A55A")
    return {"packageName": package_name, "themeCount": theme_count}


def validate_profile(path: Path) -> dict:
    profile = load_json(path)
    if profile.get("schemaVersion") != 1:
        raise ValueError("schemaVersion must be 1")

    profile_id = require_string(profile, "id")
    if path.stem != profile_id:
        raise ValueError(f"filename must match id ({profile_id}.json)")

    width = require_int(profile, "width", 1)
    height = require_int(profile, "height", 1)
    if (width, height) != (336, 480):
        raise ValueError("only the verified 336x480 canvas is supported")

    panel_x = require_int(profile, "panelX", 1)
    panel_padding = require_int(profile, "panelPadding", 0)
    if panel_x >= width:
        raise ValueError("panelX must be inside the canvas")
    content_width = width - panel_x - panel_padding - 8
    if content_width < 80:
        raise ValueError(
            f"right panel content width is too small ({content_width}px; minimum 80px)"
        )

    status = require_enum(profile, "status", VALID_STATUS)
    evidence = profile.get("evidence")
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be an object")
    hardware = require_enum(evidence, "hardware", VALID_HARDWARE)
    build_chain = require_enum(evidence, "buildChain", VALID_BUILD_CHAIN)
    device_target = require_enum(evidence, "deviceTarget", VALID_DEVICE_TARGET)
    sources = evidence.get("sources")
    if not isinstance(sources, list) or not sources or not all(
        isinstance(item, str) and item.strip() for item in sources
    ):
        raise ValueError("evidence.sources must be a non-empty list of strings")

    platform = None
    artifact = None
    if status == "verified-official-package":
        if hardware != "official":
            raise ValueError("verified-official-package requires hardware=official")
        if device_target != "official-package-verified":
            raise ValueError(
                "verified-official-package requires deviceTarget=official-package-verified"
            )
        platform = validate_platform(profile.get("platform"), profile_id)
        artifact = validate_artifact(profile.get("artifact"))
    elif status == "verified-custom-build-target":
        if build_chain != "tested":
            raise ValueError("verified-custom-build-target requires buildChain=tested")
        if device_target != "custom-build-verified":
            raise ValueError(
                "verified-custom-build-target requires deviceTarget=custom-build-verified"
            )
        platform = validate_platform(profile.get("platform"), profile_id)
        artifact = validate_artifact(profile.get("artifact"))
    elif device_target not in {"unverified", "reference-only"}:
        raise ValueError("reference profiles cannot claim verified device targets")

    return {
        "id": profile_id,
        "canvas": f"{width}x{height}",
        "contentWidth": content_width,
        "status": status,
        "hardware": hardware,
        "buildChain": build_chain,
        "deviceTarget": device_target,
        "deviceType": None if platform is None else platform.get("deviceType"),
        "packageName": None if artifact is None else artifact.get("packageName"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profiles", type=Path)
    args = parser.parse_args()

    directory = args.profiles.resolve()
    if not directory.is_dir():
        print(f"ERROR: profile directory does not exist: {directory}", file=sys.stderr)
        return 2

    paths = sorted(
        path
        for path in directory.glob("*.json")
        if path.name != "profile.schema.json"
    )
    if not paths:
        print("ERROR: no target profiles found", file=sys.stderr)
        return 2

    results: list[dict] = []
    errors: list[str] = []
    ids: set[str] = set()
    for path in paths:
        try:
            result = validate_profile(path)
            if result["id"] in ids:
                raise ValueError(f"duplicate id: {result['id']}")
            ids.add(result["id"])
            results.append(result)
        except ValueError as exc:
            errors.append(f"{path.name}: {exc}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(results)} target profile(s)")
    for result in results:
        suffix = ""
        if result["deviceType"]:
            suffix += f", deviceType={result['deviceType']}"
        if result["packageName"]:
            suffix += f", package={result['packageName']}"
        print(
            "- {id}: {canvas}, panel={contentWidth}px, status={status}, "
            "hardware={hardware}, build={buildChain}, target={deviceTarget}{suffix}".format(
                suffix=suffix, **result
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

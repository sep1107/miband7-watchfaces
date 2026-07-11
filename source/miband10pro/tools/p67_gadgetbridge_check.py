#!/usr/bin/env python3
"""Check whether a P67 resource.bin matches Gadgetbridge import rules."""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

MAX_SIZE = 128 * 1024 * 1024
ID_OFFSET = 0x28
NAME_OFFSET = 0x68
PREVIEW_OFFSET = 0x20


def nul_text(data: bytes, offset: int, encoding: str = "utf-8") -> str | None:
    if not 0 <= offset < len(data):
        return None
    end = data.find(b"\0", offset)
    if end < 0:
        end = len(data)
    raw = data[offset:end]
    if not raw:
        return None
    try:
        return raw.decode(encoding)
    except UnicodeDecodeError:
        return None


def inspect(data: bytes) -> dict[str, object]:
    errors: list[str] = []
    if len(data) > MAX_SIZE:
        errors.append("file exceeds Gadgetbridge size limit")
    if len(data) <= NAME_OFFSET:
        errors.append("file is too short")
        return {"errors": errors}
    if data[:2] != b"\x5a\xa5":
        errors.append("watchface magic is not 5A A5")

    package_id = nul_text(data, ID_OFFSET, "ascii")
    if not package_id or not package_id.isdigit():
        errors.append("numeric package ID missing at 0x28")

    preview = struct.unpack_from("<I", data, PREVIEW_OFFSET)[0]
    if preview and preview + 12 > len(data):
        errors.append("preview header is outside the file")

    raw_name = data[NAME_OFFSET : NAME_OFFSET + 4]
    localized = raw_name == b"\xff\xff\xff\xff"
    name = None if localized else nul_text(data, NAME_OFFSET)
    if not localized and not name:
        errors.append("name missing at 0x68")

    return {
        "packageId": package_id,
        "name": name,
        "localizedName": localized,
        "previewOffset": preview,
        "size": len(data),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("resource_bin", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = inspect(args.resource_bin.read_bytes())
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.json:
        args.json.write_text(text + "\n", encoding="utf-8")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

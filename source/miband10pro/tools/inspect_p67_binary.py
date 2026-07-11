#!/usr/bin/env python3
"""Inspect Xiaomi P67/Vela resource.bin structure without extracting artwork."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any

MAGIC = 0x1234A55A
HEADER_SIZE = 168
THEME_CORE_SIZE = 88
RECORD_SIZE = 16
RECORD_TYPES = {
    0: "layout",
    1: "reserved_1",
    2: "image",
    3: "image_array",
    4: "sprite",
    5: "reserved_5",
    6: "translation",
    7: "data",
    8: "slot",
    9: "widget",
}


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def decode_version(value: int) -> str:
    return f"{(value >> 16) & 0xFFFF}.{(value >> 8) & 0xFF}.{value & 0xFF}"


def decode_text(raw: bytes) -> str | None:
    raw = raw.split(b"\0", 1)[0]
    if not raw or all(byte == 0xFF for byte in raw):
        return None
    return raw.decode("utf-8", errors="replace")


def parse_header(data: bytes) -> dict[str, Any]:
    if len(data) < HEADER_SIZE:
        raise ValueError("resource.bin is shorter than the 168-byte header")
    magic = u32(data, 0)
    if magic != MAGIC:
        raise ValueError(f"unexpected magic: 0x{magic:08X}")
    versions = [u32(data, 4 + index * 4) for index in range(5)]
    return {
        "magic": f"0x{magic:08X}",
        "versions": dict(
            zip(
                ["watchface", "editor", "generator", "binaryProtocol", "firmware"],
                map(decode_version, versions),
            )
        ),
        "colorGroupCount": data[24],
        "themeCount": data[28],
        "colorCount": data[29],
        "flags": f"0x{u16(data, 30):04X}",
        "previewImageAddress": u32(data, 32),
        "reservedWord": u32(data, 36),
        "packageId": decode_text(data[40:104]),
        "name": decode_text(data[104:168]),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def parse_record_tables(data: bytes, offset: int) -> list[dict[str, Any]]:
    tables = []
    for record_type in range(10):
        table_offset = offset + 8 + record_type * 8
        tables.append(
            {
                "recordType": record_type,
                "name": RECORD_TYPES[record_type],
                "count": u32(data, table_offset),
                "address": u32(data, table_offset + 4),
            }
        )
    return tables


def detect_theme_stride(data: bytes, theme_count: int) -> int:
    for stride in (176, 88):
        record_start = HEADER_SIZE + theme_count * stride
        if record_start > len(data):
            continue
        valid = True
        positive_addresses: list[int] = []
        for index in range(theme_count):
            offset = HEADER_SIZE + index * stride
            if offset + THEME_CORE_SIZE > len(data):
                valid = False
                break
            for table in parse_record_tables(data, offset):
                count = table["count"]
                address = table["address"]
                if count > 100_000:
                    valid = False
                    break
                if count:
                    if address < record_start or address + count * RECORD_SIZE > len(data):
                        valid = False
                        break
                    positive_addresses.append(address)
            if not valid:
                break
        if valid and positive_addresses and min(positive_addresses) == record_start:
            return stride
    raise ValueError("unable to identify the P67 theme-table stride")


def parse_theme(data: bytes, index: int, stride: int) -> dict[str, Any]:
    offset = HEADER_SIZE + index * stride
    theme: dict[str, Any] = {
        "index": index,
        "offset": offset,
        "backgroundUid": f"0x{u32(data, offset):08X}",
        "previewImageAddress": u32(data, offset + 4),
        "recordTables": parse_record_tables(data, offset),
    }
    extension_size = stride - THEME_CORE_SIZE
    if extension_size:
        extension_offset = offset + THEME_CORE_SIZE
        extension = data[extension_offset : extension_offset + extension_size]
        parsed: dict[str, Any] = {
            "size": extension_size,
            "rawSha256": hashlib.sha256(extension).hexdigest(),
        }
        if extension_size >= 88:
            parsed.update(
                {
                    "words": [u32(extension, index * 4) for index in range(4)],
                    "styleName": decode_text(extension[16:80]),
                    "reserved": extension[80:88].hex(),
                }
            )
        theme["extension"] = parsed
    return theme


def parse_payload_header(
    data: bytes, record_type: int, address: int, length: int
) -> dict[str, Any]:
    if length == 0:
        return {}
    if address + length > len(data):
        return {"error": "payload exceeds file"}
    if record_type == 0 and length >= 16:
        return {
            "resourceUid": f"0x{u32(data, address):08X}",
            "x": u16(data, address + 4),
            "y": u16(data, address + 6),
            "parameter": f"0x{u32(data, address + 8):08X}",
        }
    if record_type == 2 and length >= 12:
        flags = data[address + 1]
        return {
            "format": data[address],
            "flags": f"0x{flags:02X}",
            "compression": (flags >> 2) & 0x07,
            "width": u16(data, address + 4),
            "height": u16(data, address + 6),
            "encodedLength": u32(data, address + 8),
        }
    if record_type == 3 and length >= 12:
        return {
            "format": data[address],
            "imageCount": data[address + 1],
            "flags": f"0x{u16(data, address + 2):04X}",
            "width": u16(data, address + 4),
            "height": u16(data, address + 6),
            "encodedLength": u32(data, address + 8),
        }
    if record_type == 7 and length >= 2:
        return {"sourceId": u16(data, address)}
    if record_type == 8 and length >= 4:
        return {
            "widgetCount": data[address],
            "flags": f"0x{u16(data, address + 2):04X}",
        }
    if record_type == 9 and length >= 44:
        return {
            "name": decode_text(data[address : address + 32]),
            "backgroundUid": f"0x{u32(data, address + 32):08X}",
            "previewUid": f"0x{u32(data, address + 36):08X}",
            "recordCount": data[address + 40],
            "groupType": data[address + 41],
            "flags": f"0x{u16(data, address + 42):04X}",
        }
    return {}


def inspect_binary(data: bytes) -> dict[str, Any]:
    header = parse_header(data)
    theme_stride = detect_theme_stride(data, header["themeCount"])
    themes = [
        parse_theme(data, index, theme_stride)
        for index in range(header["themeCount"])
    ]
    record_area_start = HEADER_SIZE + header["themeCount"] * theme_stride
    records: list[dict[str, Any]] = []
    validation_errors: list[str] = []

    for theme in themes:
        for table in theme["recordTables"]:
            if not table["count"]:
                continue
            for record_index in range(table["count"]):
                offset = table["address"] + record_index * RECORD_SIZE
                uid, flags, data_address, data_length = struct.unpack_from(
                    "<IIII", data, offset
                )
                uid_type = (uid >> 24) & 0xFF
                record = {
                    "themeIndex": theme["index"],
                    "tableType": table["recordType"],
                    "recordIndex": record_index,
                    "offset": offset,
                    "uid": f"0x{uid:08X}",
                    "uidType": uid_type,
                    "uidIndex": uid & 0xFFFFFF,
                    "flags": f"0x{flags:08X}",
                    "dataAddress": data_address,
                    "dataLength": data_length,
                    "payload": parse_payload_header(
                        data, uid_type, data_address, data_length
                    ),
                }
                if uid_type != table["recordType"]:
                    validation_errors.append(
                        f"theme {theme['index']} table {table['recordType']} "
                        f"record {record_index}: uid type {uid_type}"
                    )
                if data_address + data_length > len(data):
                    validation_errors.append(
                        f"record at {offset}: payload "
                        f"[{data_address}, {data_address + data_length}) exceeds file"
                    )
                records.append(record)

    record_type_counts = Counter(
        RECORD_TYPES.get(record["uidType"], str(record["uidType"]))
        for record in records
    )
    raw_data_start = max(
        (record["offset"] + RECORD_SIZE for record in records),
        default=record_area_start,
    )
    return {
        "schemaVersion": 1,
        "header": header,
        "format": {
            "headerSize": HEADER_SIZE,
            "themeCoreSize": THEME_CORE_SIZE,
            "themeExtensionSize": theme_stride - THEME_CORE_SIZE,
            "themeSize": theme_stride,
            "recordSize": RECORD_SIZE,
            "recordAreaStart": record_area_start,
            "rawDataStart": raw_data_start,
        },
        "themes": themes,
        "recordTypeCounts": dict(sorted(record_type_counts.items())),
        "recordCount": len(records),
        "records": records,
        "validation": {"errors": validation_errors},
    }


def markdown(report: dict[str, Any]) -> str:
    header = report["header"]
    fmt = report["format"]
    lines = [
        "# P67 resource.bin report",
        "",
        f"- Package ID: `{header['packageId']}`",
        f"- Watchface version: `{header['versions']['watchface']}`",
        f"- Binary protocol: `{header['versions']['binaryProtocol']}`",
        f"- File size: `{header['size']}` bytes",
        f"- SHA-256: `{header['sha256']}`",
        f"- Header size: `{fmt['headerSize']}` bytes",
        f"- Theme size: `{fmt['themeSize']}` bytes",
        f"- Record size: `{fmt['recordSize']}` bytes",
        f"- Record area: `{fmt['recordAreaStart']}`",
        f"- Raw-data area: `{fmt['rawDataStart']}`",
        f"- Records: `{report['recordCount']}`",
        "",
        "## Themes",
        "",
    ]
    for theme in report["themes"]:
        style_name = (theme.get("extension") or {}).get("styleName")
        lines.append(
            f"- Theme {theme['index']}: style `{style_name}`, "
            f"preview `{theme['previewImageAddress']}`"
        )
    lines.extend(["", "## Record counts", ""])
    for name, count in report["recordTypeCounts"].items():
        lines.append(f"- `{name}`: {count}")
    lines.extend(
        [
            "",
            "## Validation",
            "",
            f"- Structural errors: `{len(report['validation']['errors'])}`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()
    try:
        report = inspect_binary(args.input.read_bytes())
    except (OSError, ValueError, struct.error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(markdown(report), encoding="utf-8")
    print(
        f"P67 resource.bin: package={report['header']['packageId']}, "
        f"themes={len(report['themes'])}, records={report['recordCount']}, "
        f"themeSize={report['format']['themeSize']}"
    )
    if report["validation"]["errors"]:
        for error in report["validation"]["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

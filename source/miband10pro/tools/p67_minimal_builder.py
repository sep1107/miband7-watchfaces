#!/usr/bin/env python3
"""Build a minimal one-theme P67 resource.bin with one full-screen image.

This is a structural probe, not yet an installable Mi Fitness package. It creates
all bytes from scratch: header, extended P67 theme table, RecordBase entries,
layout payload, preview image and indexed8/RLEReversed image payload.
"""
from __future__ import annotations

import argparse
import struct
from pathlib import Path

from p67_image_codec import pack_image_record

MAGIC = 0x1234A55A
HEADER_SIZE = 168
THEME_SIZE = 176
RECORD_SIZE = 16
CANVAS = (336, 480)
BLACK_COLOR_UID = 0x80000000


def encode_version(value: str) -> int:
    major, minor, patch = (int(part) for part in value.split("."))
    if not (0 <= major <= 0xFFFF and 0 <= minor <= 0xFF and 0 <= patch <= 0xFF):
        raise ValueError("version component out of range")
    return (major << 16) | (minor << 8) | patch


def fixed_text(value: str, size: int) -> bytes:
    encoded = value.encode("utf-8")
    if len(encoded) >= size:
        raise ValueError(f"text exceeds {size - 1} UTF-8 bytes")
    return encoded + b"\0" * (size - len(encoded))


def make_uid(record_type: int, index: int) -> int:
    if not 0 <= record_type <= 0xFF:
        raise ValueError("record_type must fit in one byte")
    if not 0 <= index <= 0xFFFFFF:
        raise ValueError("record index must fit in 24 bits")
    return (record_type << 24) | index


def demo_indexed8(width: int, height: int) -> tuple[bytes, bytes]:
    """Create a deterministic four-color probe without external dependencies."""

    palette = bytearray(256 * 4)
    colors = [
        (8, 10, 14, 255),
        (38, 220, 180, 255),
        (238, 244, 255, 255),
        (255, 122, 64, 255),
    ]
    for index, color in enumerate(colors):
        palette[index * 4 : index * 4 + 4] = bytes(color)

    indices = bytearray(width * height)
    for y in range(height):
        for x in range(width):
            band = (x // 42 + y // 60) % 2
            indices[y * width + x] = 1 if band else 0

    # A high-contrast center block makes orientation obvious in a future test.
    for y in range(205, 275):
        for x in range(36, 300):
            indices[y * width + x] = 2 if (x // 22) % 2 else 3

    return bytes(palette), bytes(indices)


def build_resource(
    package_id: str = "991107000001",
    name: str = "TIME FLIES PROBE",
    style_name: str = "Probe",
) -> bytes:
    width, height = CANVAS
    palette, indices = demo_indexed8(width, height)
    image = pack_image_record(width, height, palette, indices)

    record_start = HEADER_SIZE + THEME_SIZE
    layout_record_addr = record_start
    image_record_addr = record_start + RECORD_SIZE
    record_end = record_start + 2 * RECORD_SIZE

    layout_payload_addr = record_end
    preview_addr = layout_payload_addr + 16
    image_payload_addr = preview_addr + len(image)

    versions = [
        encode_version("1.0.0"),
        0,
        0,
        encode_version("0.9.3"),
        encode_version("1.0.0"),
    ]
    header = struct.pack(
        "<I5IB3xBBHII64s64s",
        MAGIC,
        *versions,
        0,
        1,
        0,
        0x0002,
        preview_addr,
        0,
        fixed_text(package_id, 64),
        fixed_text(name, 64),
    )

    tables: list[int] = []
    last_address = record_start
    for record_type in range(10):
        if record_type == 0:
            count, address = 1, layout_record_addr
            last_address = address
        elif record_type == 2:
            count, address = 1, image_record_addr
            last_address = address
        else:
            count, address = 0, last_address
        tables.extend((count, address))

    extension = struct.pack(
        "<IIII64s8s",
        0,
        record_end,
        0,
        record_end,
        fixed_text(style_name, 64),
        b"\0" * 8,
    )
    theme = (
        struct.pack("<II" + "II" * 10, BLACK_COLOR_UID, preview_addr, *tables)
        + extension
    )

    image_uid = make_uid(2, 0)
    records = (
        struct.pack("<IIII", make_uid(0, 0), 0, layout_payload_addr, 16)
        + struct.pack("<IIII", image_uid, 0, image_payload_addr, len(image))
    )
    layout = struct.pack("<IHHIHH", image_uid, 0, 0, 0, 0, 0)

    output = bytearray(header + theme + records + layout + image + image)
    output.extend(b"\0" * ((-len(output)) % 4))
    return bytes(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--package-id", default="991107000001")
    parser.add_argument("--name", default="TIME FLIES PROBE")
    parser.add_argument("--style-name", default="Probe")
    args = parser.parse_args()

    data = build_resource(args.package_id, args.name, args.style_name)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    print(f"Wrote {args.output} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Regression test for the from-scratch minimal P67 resource builder."""
from __future__ import annotations

import struct

from p67_image_codec import unpack_image_record
from p67_minimal_builder import HEADER_SIZE, MAGIC, THEME_SIZE, build_resource


def main() -> int:
    data = build_resource()

    assert len(data) % 4 == 0
    assert struct.unpack_from("<I", data, 0)[0] == MAGIC
    assert data[28] == 1

    preview_address = struct.unpack_from("<I", data, 32)[0]
    theme_preview_address = struct.unpack_from("<I", data, HEADER_SIZE + 4)[0]
    assert preview_address == theme_preview_address

    record_start = HEADER_SIZE + THEME_SIZE
    layout_count, layout_address = struct.unpack_from("<II", data, HEADER_SIZE + 8)
    image_count, image_address = struct.unpack_from(
        "<II", data, HEADER_SIZE + 8 + 2 * 8
    )
    assert (layout_count, layout_address) == (1, record_start)
    assert (image_count, image_address) == (1, record_start + 16)

    layout_uid, layout_flags, layout_data, layout_length = struct.unpack_from(
        "<IIII", data, layout_address
    )
    image_uid, image_flags, image_data, image_length = struct.unpack_from(
        "<IIII", data, image_address
    )
    assert layout_uid == 0
    assert layout_flags == 0
    assert layout_length == 16
    assert image_uid == 0x02000001
    assert image_flags == 0

    ref_uid, x, y, parameter, reserved1, reserved2 = struct.unpack_from(
        "<IHHIHH", data, layout_data
    )
    assert ref_uid == image_uid
    assert (x, y, parameter, reserved1, reserved2) == (0, 0, 0, 0, 0)

    preview = unpack_image_record(data[preview_address:image_data])
    image = unpack_image_record(data[image_data : image_data + image_length])
    assert preview["width"] == 336
    assert preview["height"] == 480
    assert image["width"] == 336
    assert image["height"] == 480
    assert preview["palette"] == image["palette"]
    assert preview["indices"] == image["indices"]
    assert len(image["indices"]) == 336 * 480

    print(f"P67 minimal resource builder test passed: {len(data)} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

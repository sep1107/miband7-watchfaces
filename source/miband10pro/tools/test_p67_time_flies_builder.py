#!/usr/bin/env python3
"""Regression tests for the dynamic TIME FLIES P67 watchface builder."""
from __future__ import annotations

import struct
import tempfile
import zipfile
from pathlib import Path

from p67_image_codec import unpack_image_array_record, unpack_image_record
from p67_time_flies_builder import (
    HEADER_SIZE,
    MAGIC,
    build_package,
    build_resource,
    zip_package,
)


def main() -> int:
    data, metadata = build_resource()
    assert len(data) % 4 == 0
    assert struct.unpack_from("<I", data, 0)[0] == MAGIC
    assert struct.unpack_from("<I", data, 0x20)[0] == metadata["previewOffset"]
    assert data[0x28 : 0x28 + 12] == b"991107100001"

    tables = [
        struct.unpack_from("<II", data, HEADER_SIZE + 8 + kind * 8)
        for kind in range(10)
    ]
    assert [count for count, _ in tables] == [8, 0, 3, 3, 0, 0, 0, 5, 0, 0]

    records: dict[int, list[tuple[int, int, int, int]]] = {}
    for kind, (count, address) in enumerate(tables):
        records[kind] = [
            struct.unpack_from("<IIII", data, address + index * 16)
            for index in range(count)
        ]
        for _, _, payload_address, payload_length in records[kind]:
            assert metadata["recordEnd"] <= payload_address
            assert payload_address + payload_length <= len(data)

    preview_end = records[2][0][2]
    preview = unpack_image_record(
        data[metadata["previewOffset"] : preview_end]
    )
    assert (preview["width"], preview["height"]) == (336, 480)

    for _, _, payload_address, payload_length in records[2]:
        unpack_image_record(
            data[payload_address : payload_address + payload_length]
        )

    expected_arrays = [(60, 96), (26, 40), (24, 36)]
    for record, dimensions in zip(records[3], expected_arrays):
        _, _, payload_address, payload_length = record
        decoded = unpack_image_array_record(
            data[payload_address : payload_address + payload_length]
        )
        assert len(decoded["images"]) == 10
        assert (decoded["width"], decoded["height"]) == dimensions

    source_ids = [
        struct.unpack_from("<H", data, record[2])[0]
        for record in records[7]
    ]
    assert source_ids == [0x1108, 0x1110, 0x1210, 0x1218, 0x2108]

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        package = root / "package"
        archive = root / "time-flies-p67.zip"
        report = build_package(package)
        zip_package(package, archive)
        assert (package / "resource.bin").read_bytes() == data
        assert report["sha256"] == metadata["sha256"]
        assert archive.is_file()
        with zipfile.ZipFile(archive) as zipped:
            names = set(zipped.namelist())
            assert {
                "resource.bin",
                "manifest.xml",
                "preview/preview.png",
                "resources/time_digits/0.png",
            } <= names

    print(
        "TIME FLIES dynamic P67 builder passed",
        len(data),
        metadata["sha256"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

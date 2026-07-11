#!/usr/bin/env python3
"""Regression tests for the Gadgetbridge-compatible P67 header checker."""
from __future__ import annotations

import struct
from pathlib import Path

from p67_gadgetbridge_check import inspect


def ordinary_probe() -> bytes:
    data = bytearray(256)
    data[:4] = struct.pack("<I", 0x1234A55A)
    struct.pack_into("<I", data, 0x20, 168)
    data[0x28 : 0x28 + 12] = b"991107000001"
    data[0x68 : 0x68 + 16] = b"TIME FLIES PROBE"
    return bytes(data)


def localized_probe() -> bytes:
    data = bytearray(ordinary_probe())
    table = struct.pack("<QI", 1, 10) + b"TIME FLIES"
    table_offset = len(data)
    data.extend(table)
    data[0x68:0xA8] = b"\0" * 64
    data[0x68:0x6C] = b"\xff\xff\xff\xff"
    struct.pack_into("<I", data, 0x74, table_offset)
    struct.pack_into("<I", data, 0x78, len(table))
    return bytes(data)


def assert_ios_probe_is_read_only() -> None:
    swift_path = (
        Path(__file__).resolve().parents[1]
        / "ios-probe"
        / "P67ReadOnlyProbe.swift"
    )
    swift = swift_path.read_text(encoding="utf-8")

    required = [
        "discoverServices",
        "discoverCharacteristics",
        "Xiaomi Smart Band 10 Pro",
        "0000FE95",
        "0000005E",
        "0000005F",
    ]
    for token in required:
        assert token in swift, f"missing iPhone probe token: {token}"

    forbidden = [
        ".writeValue(",
        ".setNotifyValue(",
        "sendEncryptedCommand",
        "watchfaceInstall",
        "DataUploadService",
        "setActive(",
        "deleteWatchface",
    ]
    for token in forbidden:
        assert token not in swift, f"iPhone probe is no longer read-only: {token}"


def main() -> int:
    ordinary = inspect(ordinary_probe())
    assert ordinary["errors"] == []
    assert ordinary["packageId"] == "991107000001"
    assert ordinary["name"] == "TIME FLIES PROBE"
    assert ordinary["localizedName"] is False

    localized = inspect(localized_probe())
    assert localized["errors"] == []
    assert localized["localizedName"] is True
    table = localized["localizedNameTable"]
    assert isinstance(table, dict)
    assert table["localeMask"] == "0x0000000000000001"
    assert table["localeCount"] == 1
    assert table["stringLengths"] == [10]

    broken = bytearray(ordinary_probe())
    broken[0x28:0x68] = b"x" + b"\0" * 63
    invalid = inspect(bytes(broken))
    assert "numeric package ID missing at 0x28" in invalid["errors"]

    broken_i18n = bytearray(localized_probe())
    struct.pack_into("<I", broken_i18n, 0x74, len(broken_i18n) + 16)
    invalid_i18n = inspect(bytes(broken_i18n))
    assert "localized name table is outside the file" in invalid_i18n["errors"]

    assert_ios_probe_is_read_only()
    print("P67 Gadgetbridge checker and iPhone read-only guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

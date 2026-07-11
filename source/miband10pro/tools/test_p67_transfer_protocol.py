#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import struct

from p67_transfer_protocol import (
    WATCHFACE_MAGIC,
    WATCHFACE_UPLOAD_TYPE,
    TransferFormatError,
    build_plan,
    build_upload_payload,
    inspect_upload_payload,
    inspect_watchface,
    reassemble_upload_chunks,
    split_upload_chunks,
)


def fake_watchface() -> bytes:
    data = bytearray(5000)
    struct.pack_into("<I", data, 0, WATCHFACE_MAGIC)
    data[0x28:0x28 + 13] = b"991107000001\0"
    data[0x68:0x68 + 17] = b"TIME FLIES PROBE\0"
    for index in range(168, len(data)):
        data[index] = (index * 37 + 11) & 0xFF
    return bytes(data)


def main() -> int:
    resource = fake_watchface()
    identity = inspect_watchface(resource)
    assert identity["packageId"] == "991107000001"
    assert identity["name"] == "TIME FLIES PROBE"
    assert identity["md5"] == hashlib.md5(resource).hexdigest()

    payload = build_upload_payload(resource)
    parsed = inspect_upload_payload(payload)
    assert parsed["uploadType"] == WATCHFACE_UPLOAD_TYPE
    assert parsed["declaredSize"] == len(resource)
    assert parsed["fileBytes"] == resource

    for chunk_size in (23, 64, 512, 2048):
        chunks = split_upload_chunks(payload, chunk_size)
        assert reassemble_upload_chunks(chunks) == payload
        total, first = struct.unpack_from("<HH", chunks[0], 0)
        assert total == len(chunks)
        assert first == 1
        assert all(len(chunk) <= chunk_size for chunk in chunks)

    plan = build_plan(resource, 64)
    assert plan["protocol"]["watchfaceCommandType"] == 4
    assert plan["protocol"]["watchfaceInstallSubtype"] == 4
    assert plan["protocol"]["dataUploadCommandType"] == 22
    assert plan["protocol"]["uploadType"] == 16
    assert reassemble_upload_chunks(plan["chunks"]) == plan["payload"]

    resumed = build_upload_payload(resource, resume_position=123)
    assert resumed[22:-4] == resource[123:]
    try:
        inspect_upload_payload(resumed)
    except TransferFormatError:
        pass
    else:
        raise AssertionError("resumed payload should not pass full-file inspection")

    print(
        f"P67 transfer protocol test passed: {len(payload)} bytes, "
        f"{len(plan['chunks'])} chunks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

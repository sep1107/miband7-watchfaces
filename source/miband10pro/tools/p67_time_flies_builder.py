from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import shutil
import struct
import zipfile
import zlib
from pathlib import Path

from p67_image_codec import pack_image_array_record, pack_image_record
from p67_time_flies_assets import Indexed, build_assets

MAGIC = 0x1234A55A
HEADER_SIZE = 168
THEME_SIZE = 176
RECORD_SIZE = 16
BLACK = 0x80000000
DEFAULT_PACKAGE_ID = "991107100001"


def fixed_text(value: str, size: int) -> bytes:
    raw = value.encode("utf-8")
    if len(raw) >= size:
        raise ValueError(f"text exceeds {size - 1} bytes")
    return raw + b"\0" * (size - len(raw))


def encode_version(value: str) -> int:
    major, minor, patch = map(int, value.split("."))
    return (major << 16) | (minor << 8) | patch


def uid(kind: int, index: int) -> int:
    return (kind << 24) | index


def image_bytes(image: Indexed) -> bytes:
    return pack_image_record(
        image.width, image.height, image.palette, image.indices
    )


def image_array_bytes(images: list[Indexed]) -> bytes:
    return pack_image_array_record(
        images[0].width,
        images[0].height,
        [(image.palette, image.indices) for image in images],
    )


def image_number(
    source: int, total_digits: int, flags: int, image_array_uid: int
) -> bytes:
    return struct.pack(
        "<HBBHHIbbhI",
        source,
        total_digits,
        flags,
        0,
        1000,
        image_array_uid,
        0,
        0,
        0,
        0,
    )


def layout_payload(resource_uid: int, x: int, y: int) -> bytes:
    return struct.pack("<IHHIHH", resource_uid, x, y, 0, 0, 0)


def build_resource(
    package_id: str = DEFAULT_PACKAGE_ID,
    name: str = "TIME FLIES",
    style: str = "TIME FLIES",
) -> tuple[bytes, dict[str, object]]:
    if not package_id.isdigit():
        raise ValueError("package ID must be numeric")

    artwork = build_assets()
    preview = image_bytes(artwork["preview"])
    direct_images = [
        image_bytes(artwork["background"]),
        image_bytes(artwork["colon"]),
        image_bytes(artwork["slash"]),
    ]
    image_arrays = [
        image_array_bytes(artwork["time_digits"]),
        image_array_bytes(artwork["date_digits"]),
        image_array_bytes(artwork["step_digits"]),
    ]

    # These payload layouts and source IDs are copied from the verified P67
    # M2551B1 package. The resource UIDs point at arrays generated above.
    data_payloads = [
        image_number(0x1108, 2, 0x15, uid(3, 0)),  # timeHour
        image_number(0x1110, 2, 0x15, uid(3, 0)),  # timeMinute
        image_number(0x1210, 2, 0x10, uid(3, 1)),  # dateMonth
        image_number(0x1218, 2, 0x11, uid(3, 1)),  # dateDay
        image_number(0x2108, 5, 0x11, uid(3, 2)),  # healthStepCount
    ]
    layouts = [
        (uid(2, 1), 0, 0),
        (uid(7, 0), 28, 84),
        (uid(2, 2), 151, 84),
        (uid(7, 1), 184, 84),
        (uid(7, 2), 92, 264),
        (uid(2, 3), 150, 264),
        (uid(7, 3), 176, 264),
        (uid(7, 4), 102, 399),
    ]
    counts = {
        0: len(layouts),
        2: len(direct_images),
        3: len(image_arrays),
        7: len(data_payloads),
    }

    record_start = HEADER_SIZE + THEME_SIZE
    table_addresses: dict[int, int] = {}
    cursor = record_start
    for kind in range(10):
        table_addresses[kind] = cursor
        cursor += counts.get(kind, 0) * RECORD_SIZE
    record_end = cursor

    payload_cursor = record_end
    payloads: list[bytes] = []
    records: dict[int, list[bytes]] = {kind: [] for kind in range(10)}

    def add_record(kind: int, record_uid: int, payload: bytes) -> None:
        nonlocal payload_cursor
        records[kind].append(
            struct.pack("<IIII", record_uid, 0, payload_cursor, len(payload))
        )
        payloads.append(payload)
        payload_cursor += len(payload)

    for index, (resource_uid, x, y) in enumerate(layouts):
        add_record(0, uid(0, index), layout_payload(resource_uid, x, y))

    # P67 reserves Image1 for an unregistered theme preview. The first visible
    # image is therefore Image2 / UID 0x02000001.
    preview_offset = payload_cursor
    payloads.append(preview)
    payload_cursor += len(preview)

    for index, payload in enumerate(direct_images, start=1):
        add_record(2, uid(2, index), payload)
    for index, payload in enumerate(image_arrays):
        add_record(3, uid(3, index), payload)
    for index, payload in enumerate(data_payloads):
        add_record(7, uid(7, index), payload)

    header = struct.pack(
        "<I5IB3xBBHII64s64s",
        MAGIC,
        encode_version("1.0.0"),
        0,
        0,
        encode_version("0.9.3"),
        encode_version("1.0.0"),
        0,
        1,
        0,
        0x0002,
        preview_offset,
        0,
        fixed_text(package_id, 64),
        fixed_text(name, 64),
    )

    tables: list[int] = []
    for kind in range(10):
        tables.extend((counts.get(kind, 0), table_addresses[kind]))
    theme = struct.pack(
        "<II" + "II" * 10, BLACK, preview_offset, *tables
    ) + struct.pack(
        "<IIII64s8s",
        0,
        record_end,
        0,
        record_end,
        fixed_text(style, 64),
        b"\0" * 8,
    )

    record_blob = b"".join(
        b"".join(records[kind]) for kind in range(10)
    )
    output = bytearray(header + theme + record_blob + b"".join(payloads))
    output.extend(b"\0" * ((-len(output)) % 4))

    metadata: dict[str, object] = {
        "packageId": package_id,
        "previewOffset": preview_offset,
        "recordEnd": record_end,
        "recordCounts": {str(kind): count for kind, count in counts.items()},
        "size": len(output),
        "sha256": hashlib.sha256(output).hexdigest(),
    }
    return bytes(output), metadata


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)
    )


def indexed_png(image: Indexed) -> bytes:
    rows = bytearray()
    for y in range(image.height):
        rows.append(0)
        row = image.indices[y * image.width : (y + 1) * image.width]
        for index in row:
            rows.extend(image.palette[index * 4 : index * 4 + 4])
    ihdr = struct.pack(">IIBBBBB", image.width, image.height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", zlib.compress(bytes(rows), 9))
        + png_chunk(b"IEND", b"")
    )


def capability_json() -> str:
    return json.dumps(
        [
            {"name": "protocol", "type": 1, "value": ["1.9.4"]},
            {"name": "resolution", "type": 2, "value": ["XMHD03"]},
            {"name": "region", "type": 2, "value": ["CN"]},
            {"name": "packet", "type": 2, "value": ["BIN"]},
            {"name": "image_compress", "type": 3, "value": ["01"]},
            {
                "name": "image_fmt",
                "type": 3,
                "value": ["00000000000000001"],
            },
        ],
        indent=2,
    ) + "\n"


def description_xml(package_id: str) -> str:
    digest = hashlib.md5(package_id.encode("ascii")).hexdigest()
    return f'''<?xml version="1.0" encoding="utf-8"?>
<watch>
    <shape>square</shape>
    <name>TIME FLIES</name>
    <deviceType>P67</deviceType>
    <version>1.0.0</version>
    <size>336x480</size>
    <author>sep1107</author>
    <pkgName>{package_id}</pkgName>
    <imageFormat>indexed8</imageFormat>
    <imageCompression>true</imageCompression>
    <editorVersion>1.0.0</editorVersion>
    <_recolorEnable>false</_recolorEnable>
    <temperatureUnitType>system</temperatureUnitType>
    <_id>{digest}</_id>
    <imageArrayRamMethod>whole</imageArrayRamMethod>
    <watchfaceType>normal</watchfaceType>
    <watchOS>vela</watchOS>
    <merchantId/>
    <introduce>TIME FLIES for Xiaomi Smart Band 10 Pro.</introduce>
</watch>
'''


def manifest_xml(package_id: str) -> str:
    time_images = "".join(
        f'<Image src="time_digits/{index}.png"/>' for index in range(10)
    )
    date_images = "".join(
        f'<Image src="date_digits/{index}.png"/>' for index in range(10)
    )
    step_images = "".join(
        f'<Image src="step_digits/{index}.png"/>' for index in range(10)
    )
    return f'''<?xml version="1.0" encoding="utf-8"?>
<Watchface name="TIME FLIES" width="336" height="480" id="{package_id}" SKU="false" compressMethod="RLEReversed" advanced="false" interactive="false" support_literal="false" editable="false">
    <Resources>
        <Image name="Image1" src="_preview/preview.png" compressMethod="RLEReversed" format="indexed8"/>
        <Image name="Image2" src="background.png" compressMethod="RLEReversed" format="indexed8"/>
        <Image name="Image3" src="colon.png" compressMethod="RLEReversed" format="indexed8"/>
        <Image name="Image4" src="slash.png" compressMethod="RLEReversed" format="indexed8"/>
        <ImageArray name="ImageArray1" compressMethod="RLEReversed" format="indexed8">{time_images}</ImageArray>
        <ImageArray name="ImageArray2" compressMethod="RLEReversed" format="indexed8">{date_images}</ImageArray>
        <ImageArray name="ImageArray3" compressMethod="RLEReversed" format="indexed8">{step_images}</ImageArray>
        <DataItemImageNumber name="Hour" source="timeHour" ref="@ImageArray1" leadingZero="true" totalDigits="2" parameter="1000" renderRule="alwaysShow" align="left"/>
        <DataItemImageNumber name="Minute" source="timeMinute" ref="@ImageArray1" leadingZero="true" totalDigits="2" parameter="1000" renderRule="alwaysShow" align="left"/>
        <DataItemImageNumber name="Month" source="dateMonth" ref="@ImageArray2" leadingZero="false" totalDigits="2" parameter="1000" renderRule="alwaysShow" align="right"/>
        <DataItemImageNumber name="Day" source="dateDay" ref="@ImageArray2" leadingZero="false" totalDigits="2" parameter="1000" renderRule="alwaysShow" align="left"/>
        <DataItemImageNumber name="Steps" source="healthStepCount" ref="@ImageArray3" leadingZero="false" totalDigits="5" parameter="1000" renderRule="alwaysShow" align="left"/>
    </Resources>
    <Theme type="normal" name="TIME FLIES" bgColor="#000000" isPhotoAlbumWatchface="false" preview="@Image1">
        <Layout ref="@Image2" x="0" y="0"/>
        <Layout ref="@Hour" x="28" y="84"/>
        <Layout ref="@Image3" x="151" y="84"/>
        <Layout ref="@Minute" x="184" y="84"/>
        <Layout ref="@Month" x="92" y="264"/>
        <Layout ref="@Image4" x="150" y="264"/>
        <Layout ref="@Day" x="176" y="264"/>
        <Layout ref="@Steps" x="102" y="399"/>
    </Theme>
</Watchface>
'''


def uidmap() -> str:
    return """Image2: 2000001
Image3: 2000002
Image4: 2000003
ImageArray1: 3000000
ImageArray2: 3000001
ImageArray3: 3000002
Hour: 7000000
Minute: 7000001
Month: 7000002
Day: 7000003
Steps: 7000004
"""


def build_package(
    directory: Path, package_id: str = DEFAULT_PACKAGE_ID
) -> dict[str, object]:
    if directory.exists():
        shutil.rmtree(directory)
    (directory / "preview").mkdir(parents=True)
    (directory / "resources" / "_preview").mkdir(parents=True)

    artwork = build_assets()
    resource, report = build_resource(package_id)
    (directory / "resource.bin").write_bytes(resource)
    (directory / "capability.json").write_text(
        capability_json(), encoding="utf-8"
    )
    (directory / "description.xml").write_text(
        description_xml(package_id), encoding="utf-8"
    )
    (directory / "manifest.xml").write_text(
        manifest_xml(package_id), encoding="utf-8"
    )
    (directory / "uidmap.map").write_text(uidmap(), encoding="utf-8")

    static_images = {
        "background.png": artwork["background"],
        "colon.png": artwork["colon"],
        "slash.png": artwork["slash"],
    }
    for filename, image in static_images.items():
        (directory / "resources" / filename).write_bytes(indexed_png(image))

    for group in ("time_digits", "date_digits", "step_digits"):
        target = directory / "resources" / group
        target.mkdir()
        for index, image in enumerate(artwork[group]):
            (target / f"{index}.png").write_bytes(indexed_png(image))

    preview_png = indexed_png(artwork["preview"])
    (directory / "resources" / "_preview" / "preview.png").write_bytes(
        preview_png
    )
    for filename in (
        "preview.png",
        "market-preview.png",
        "style_1_static.png",
        "aod-preview.png",
    ):
        (directory / "preview" / filename).write_bytes(preview_png)

    report["previewPngSize"] = len(preview_png)
    return report


def zip_package(directory: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(directory).as_posix())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--package-id", default=DEFAULT_PACKAGE_ID)
    parser.add_argument("--zip", type=Path)
    parser.add_argument("--resource-only", action="store_true")
    args = parser.parse_args()

    if args.resource_only:
        data, report = build_resource(args.package_id)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(data)
    else:
        report = build_package(args.output, args.package_id)
        if args.zip:
            zip_package(args.output, args.zip)
            report["zip"] = str(args.zip)

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

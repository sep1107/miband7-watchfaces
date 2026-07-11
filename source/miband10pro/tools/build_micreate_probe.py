#!/usr/bin/env python3
"""Generate a MiCreate XML probe for the Pro watchface format.

DeviceType 11 was observed in a Mi Band 8/9 Pro project tested by its author.
It is a format reference only and is not verified for Smart Band 10 Pro.
"""

from __future__ import annotations

import argparse
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

SOURCES = {
    "hour_tens": "1000911",
    "hour_ones": "911",
    "minute_tens": "1211",
    "minute_ones": "1111",
    "year": "812",
    "month": "1012",
    "day": "1812",
    "steps": "821",
    "heart": "822",
    "battery": "841",
    "weekday": "2012",
    "weather_icon": "3031",
    "weather_high": "1832",
    "weather_low": "2032",
}


def bitmap_list(prefix: str, count: int) -> str:
    return "|".join(f"{prefix}{index}.png" for index in range(count))


def indexed_list(prefix: str, count: int, step: int = 1) -> str:
    return "|".join(
        f"({index * step}):{prefix}{index}.png" for index in range(count)
    )


def add_static(screen: ET.Element, name: str, bitmap: str, x: int, y: int, width: int, height: int) -> None:
    ET.SubElement(screen, "Widget", {
        "Shape": "30", "Name": name, "Bitmap": bitmap,
        "X": str(x), "Y": str(y), "Width": str(width), "Height": str(height),
        "Alpha": "255", "Visible_Src": "0",
    })


def add_number(screen: ET.Element, name: str, bitmaps: str, x: int, y: int, source: str, digits: int, spacing: int = 0, blanking: int = 0) -> None:
    ET.SubElement(screen, "Widget", {
        "Shape": "32", "Name": name, "BitmapList": bitmaps,
        "X": str(x), "Y": str(y), "Width": "64", "Height": "97",
        "Alpha": "255", "Visible_Src": "0", "Digits": str(digits),
        "Alignment": "0", "Value_Src": source,
        "Spacing": str(spacing), "Blanking": str(blanking),
    })


def add_indexed(screen: ET.Element, name: str, bitmaps: str, x: int, y: int, source: str) -> None:
    ET.SubElement(screen, "Widget", {
        "Shape": "31", "Name": name, "BitmapList": bitmaps,
        "X": str(x), "Y": str(y), "Width": "48", "Height": "48",
        "Alpha": "255", "Alignment": "0", "DefaultIndex": "0",
        "Value_Src": "0", "Spacing": "0", "Blanking": "0",
        "Visible_Src": "0", "Index_Src": source,
    })


def copy_assets(source: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    files: list[tuple[Path, str]] = [(source / "bg/bg.png", "background.png")]
    for index in range(10):
        files.extend([
            (source / f"time/{index}.png", f"time_{index}.png"),
            (source / f"date/{index}.png", f"date_{index}.png"),
            (source / f"battery/{index}.png", f"battery_{index}.png"),
        ])
    for index in range(1, 8):
        files.append((source / f"week/{index}.png", f"week_{index - 1}.png"))
    for index in range(29):
        files.append((source / f"weather/{index}.png", f"weather_{index}.png"))
    files.append((source / "weather/negative.png", "minus.png"))

    missing = [str(path) for path, _ in files if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing source assets:\n" + "\n".join(missing))
    for path, name in files:
        shutil.copy2(path, output / name)


def build(device_type: int, project_id: int, title: str) -> ET.ElementTree:
    root = ET.Element("FaceProject", {"DeviceType": str(device_type), "Id": str(project_id)})
    root.append(ET.Comment("DeviceType 11 is an 8/9 Pro reference, not verified for Smart Band 10 Pro."))
    screen = ET.SubElement(root, "Screen", {"Title": title, "Bitmap": "example.png"})
    add_static(screen, "background", "background.png", 0, 0, 188, 480)

    time_digits = bitmap_list("time_", 10)
    date_digits = bitmap_list("date_", 10)
    signed_digits = date_digits + "|minus.png"

    add_number(screen, "hour_tens", time_digits, 28, 150, SOURCES["hour_tens"], 1)
    add_number(screen, "hour_ones", time_digits, 96, 150, SOURCES["hour_ones"], 1)
    add_number(screen, "minute_tens", time_digits, 28, 254, SOURCES["minute_tens"], 1)
    add_number(screen, "minute_ones", time_digits, 96, 254, SOURCES["minute_ones"], 1)

    add_number(screen, "year", date_digits, 210, 60, SOURCES["year"], 4, 1)
    add_number(screen, "month", date_digits, 276, 60, SOURCES["month"], 2, 1)
    add_number(screen, "day", date_digits, 306, 60, SOURCES["day"], 2, 1)
    add_indexed(screen, "weekday", indexed_list("week_", 7), 210, 92, SOURCES["weekday"])

    add_indexed(screen, "weather_icon", indexed_list("weather_", 29), 210, 138, SOURCES["weather_icon"])
    add_number(screen, "weather_low", signed_digits, 264, 145, SOURCES["weather_low"], 3, blanking=1)
    add_number(screen, "weather_high", signed_digits, 300, 145, SOURCES["weather_high"], 3, blanking=1)
    add_number(screen, "steps", date_digits, 210, 225, SOURCES["steps"], 6, 1, 1)
    add_number(screen, "heart", date_digits, 210, 290, SOURCES["heart"], 3, blanking=1)
    add_indexed(screen, "battery_bar", indexed_list("battery_", 10, 10), 210, 365, SOURCES["battery"])
    add_number(screen, "battery", date_digits, 268, 365, SOURCES["battery"], 3, 1, 1)
    return ET.ElementTree(root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_assets", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--device-type", type=int, default=11)
    parser.add_argument("--project-id", type=int, default=166210081)
    parser.add_argument("--title", default="TIME FLIES Pro Format Probe")
    parser.add_argument("--accept-reference-device-type", action="store_true")
    args = parser.parse_args()

    if args.device_type == 11 and not args.accept_reference_device_type:
        parser.error("DeviceType 11 is only an 8/9 Pro reference; acknowledge it explicitly")

    images = args.output_dir / "images"
    copy_assets(args.source_assets, images)
    preview = args.source_assets.parent.parent / "preview.png"
    if preview.is_file():
        shutil.copy2(preview, images / "example.png")

    tree = build(args.device_type, args.project_id, args.title)
    ET.indent(tree, space="\t")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / "TimeFlies_ProProbe.fprj"
    tree.write(output, encoding="utf-8", xml_declaration=True)
    ET.parse(output)
    print(f"Generated {output}")
    print(f"Copied {len(list(images.glob('*.png')))} probe images")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

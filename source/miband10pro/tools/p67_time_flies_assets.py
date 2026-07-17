from __future__ import annotations

from dataclasses import dataclass

CANVAS = (336, 480)
RGBA = tuple[int, int, int, int]

BG: RGBA = (7, 10, 16, 255)
PANEL: RGBA = (18, 24, 34, 255)
GRID: RGBA = (36, 45, 60, 255)
WHITE: RGBA = (244, 247, 251, 255)
MUTED: RGBA = (145, 157, 178, 255)
ACCENT: RGBA = (72, 222, 188, 255)
ORANGE: RGBA = (255, 135, 76, 255)


@dataclass(frozen=True)
class Indexed:
    width: int
    height: int
    palette: bytes
    indices: bytes


class Canvas:
    def __init__(self, width: int, height: int, colors: list[RGBA], fill: int = 0):
        self.width = width
        self.height = height
        self.colors = list(colors)
        self.pixels = bytearray([fill]) * (width * height)

    def rect(self, x0: int, y0: int, x1: int, y1: int, color: int) -> None:
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.width, x1), min(self.height, y1)
        if x0 >= x1 or y0 >= y1:
            return
        row = bytes([color]) * (x1 - x0)
        for y in range(y0, y1):
            start = y * self.width + x0
            self.pixels[start : start + len(row)] = row

    def rounded(self, x0: int, y0: int, x1: int, y1: int, radius: int, color: int) -> None:
        for y in range(y0, y1):
            edge = min(y - y0, y1 - 1 - y)
            inset = max(0, radius - edge) if edge < radius else 0
            if inset:
                inset = max(0, inset // 2)
            self.rect(x0 + inset, y, x1 - inset, y + 1, color)

    def line(self, x0: int, y0: int, x1: int, y1: int, color: int, thick: int = 1) -> None:
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        error = dx + dy
        while True:
            self.rect(
                x0 - thick // 2,
                y0 - thick // 2,
                x0 + (thick + 1) // 2,
                y0 + (thick + 1) // 2,
                color,
            )
            if x0 == x1 and y0 == y1:
                break
            twice = 2 * error
            if twice >= dy:
                error += dy
                x0 += sx
            if twice <= dx:
                error += dx
                y0 += sy

    def paste_mask(self, image: Indexed, x: int, y: int, color: int) -> None:
        for row in range(image.height):
            for column in range(image.width):
                if image.indices[row * image.width + column]:
                    px, py = x + column, y + row
                    if 0 <= px < self.width and 0 <= py < self.height:
                        self.pixels[py * self.width + px] = color

    def indexed(self) -> Indexed:
        palette = bytearray()
        for color in self.colors:
            palette.extend(color)
        if len(palette) > 1024:
            raise ValueError("indexed8 palette has more than 256 colors")
        palette.extend(b"\0" * (1024 - len(palette)))
        return Indexed(self.width, self.height, bytes(palette), bytes(self.pixels))


FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "
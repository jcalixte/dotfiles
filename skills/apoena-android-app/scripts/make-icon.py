#!/usr/bin/env python3
"""Draw the launcher icon of an App: a grid mark on a brand colour, both derived from the applicationId.

Usage: make-icon.py --id dev.apoena.umoena --res app/src/main/res

Writes res/mipmap-<density>/ic_launcher.png. Plain PNGs, no adaptive icon: fdroidserver
cannot rasterise an adaptive XML icon, so the Store would list the App without one.
"""
import argparse
import colorsys
import hashlib
import struct
import zlib
from pathlib import Path

DENSITIES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
SAMPLES = 4  # supersampling per axis, for smooth edges
GRID = 4  # the mark is a GRID x GRID field of rounded squares


def brand_color(digest):
    """A hue from the digest, darkened until white on it clears WCAG AA (4.5:1)."""
    hue = digest[0] / 256
    for lightness in (0.46, 0.42, 0.38, 0.34, 0.30, 0.26):
        rgb = colorsys.hls_to_rgb(hue, lightness, 0.58)
        channels = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
        luminance = 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]
        if 1.05 / (luminance + 0.05) >= 4.5:
            break
    return tuple(round(c * 255) for c in rgb)


def mark_cells(digest):
    """A left-right symmetric pattern, so the mark reads as a designed shape, not noise."""
    bits = int.from_bytes(digest[1:9], "big")
    cells = set()
    for y in range(GRID):
        for x in range((GRID + 1) // 2):
            if bits >> (y * GRID + x) & 1:
                cells.add((x, y))
                cells.add((GRID - 1 - x, y))
    return cells or {(x, y) for x in range(GRID) for y in range(GRID) if (x + y) % 2 == 0}


def rounded_square_covers(px, py, left, top, side, radius):
    dx = max(left - px, px - (left + side), 0)
    dy = max(top - py, py - (top + side), 0)
    inset = min(px - left, left + side - px, py - top, top + side - py)
    if inset < 0:
        return False
    cx = min(max(px, left + radius), left + side - radius)
    cy = min(max(py, top + radius), top + side - radius)
    return (px - cx) ** 2 + (py - cy) ** 2 <= radius**2 and dx == 0 and dy == 0


def render(size, color, cells):
    cell = size * 0.19
    gap = size * 0.04
    span = GRID * cell + (GRID - 1) * gap
    origin = (size - span) / 2
    squares = [
        (origin + gx * (cell + gap), origin + gy * (cell + gap), cell, cell * 0.28)
        for gx, gy in cells
    ]
    rows = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            on_icon = on_mark = 0
            for sy in range(SAMPLES):
                py = y + (sy + 0.5) / SAMPLES
                for sx in range(SAMPLES):
                    px = x + (sx + 0.5) / SAMPLES
                    if not rounded_square_covers(px, py, 0, 0, size, size * 0.22):
                        continue
                    on_icon += 1
                    if any(rounded_square_covers(px, py, *sq) for sq in squares):
                        on_mark += 1
            total = SAMPLES**2
            white = on_mark / total
            row += bytes(round(c + (255 - c) * white) for c in color)
            row += bytes([round(255 * on_icon / total)])
        rows.append(bytes(row))
    return rows


def write_png(path, rows):
    raw = b"".join(b"\x00" + row for row in rows)
    size = len(rows)

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def main():
    parser = argparse.ArgumentParser(description="Draw the launcher icon of an App.")
    parser.add_argument("--id", required=True, help="applicationId, e.g. dev.apoena.umoena")
    parser.add_argument("--res", required=True, type=Path, help="app/src/main/res")
    args = parser.parse_args()

    digest = hashlib.sha256(args.id.encode()).digest()
    color, cells = brand_color(digest), mark_cells(digest)
    for density, size in DENSITIES.items():
        out = args.res / f"mipmap-{density}"
        out.mkdir(parents=True, exist_ok=True)
        write_png(out / "ic_launcher.png", render(size, color, cells))
        print(f"{out / 'ic_launcher.png'} ({size}x{size})")


if __name__ == "__main__":
    main()

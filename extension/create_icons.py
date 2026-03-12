"""
Generate VoxStory extension icons as solid-color PNGs using only stdlib.
Run: python create_icons.py
"""

import os
import struct
import zlib


def _make_chunk(chunk_type: bytes, data: bytes) -> bytes:
    body = chunk_type + data
    crc = zlib.crc32(body) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + body + struct.pack(">I", crc)


def create_solid_png(path: str, size: int, rgb: tuple) -> None:
    """Write a minimal, valid solid-color PNG file."""
    r, g, b = rgb

    # IHDR: width, height, bit_depth=8, color_type=2 (RGB), comp=0, filter=0, interlace=0
    ihdr_data = struct.pack(">II5B", size, size, 8, 2, 0, 0, 0)

    # Raw image data: one filter byte (0) per row, then RGB pixels
    raw = b""
    for _ in range(size):
        raw += b"\x00" + bytes([r, g, b] * size)
    idat_data = zlib.compress(raw, 9)

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(_make_chunk(b"IHDR", ihdr_data))
        f.write(_make_chunk(b"IDAT", idat_data))
        f.write(_make_chunk(b"IEND", b""))


if __name__ == "__main__":
    os.makedirs("icons", exist_ok=True)
    # Jira primary blue — #0052CC
    color = (0, 82, 204)
    for size in [16, 32, 48, 128]:
        out = f"icons/icon{size}.png"
        create_solid_png(out, size, color)
        print(f"Created {out}")
    print("Done.")

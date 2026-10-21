"""极简 PNG 写入工具（RGBA 8bit），只用标准库。"""

import os
import struct
import zlib


def write_png(path, width, height, canvas):
    """canvas[y][x] = (r, g, b, a)"""
    raw = b"".join(
        b"\x00" + bytes(channel for px in row for channel in px) for row in canvas
    )

    def chunk(tag, data):
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)

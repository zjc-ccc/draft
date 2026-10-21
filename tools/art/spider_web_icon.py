"""生成 assets/props/spider-web/preview/spider-web_icon_32.png

32x32 物品栏图标：简化蛛网，8 条放射丝 + 3 圈略带下垂的环丝。
图标上不做螺旋，圈数少了才看得清。
"""

import math
import os

from png_util import write_png

W = H = 32
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "props", "spider-web", "preview", "spider-web_icon_32.png")

CX = CY = 15.5
SPOKES = 8
START = -math.pi / 2
HUB = 3.0
RINGS = (7.4, 13.2)
OUTER = 13.8

SILK = (214, 228, 238, 230)
SILK_BRIGHT = (240, 248, 252, 245)

canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        canvas[y][x] = color


def line(x0, y0, x1, y1, color):
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 3) + 1
    for i in range(steps + 1):
        u = i / steps
        put(int(round(x0 + (x1 - x0) * u)), int(round(y0 + (y1 - y0) * u)), color)


def polar(r, ang):
    return CX + r * math.cos(ang), CY + r * math.sin(ang)


# 放射丝
for i in range(SPOKES):
    ang = START + 2 * math.pi * i / SPOKES
    x0, y0 = polar(HUB, ang)
    x1, y1 = polar(OUTER, ang)
    line(x0, y0, x1, y1, SILK)

# 环丝
for radius in RINGS:
    for i in range(SPOKES):
        a0 = START + 2 * math.pi * i / SPOKES
        a1 = START + 2 * math.pi * (i + 1) / SPOKES
        steps = 8
        for t in range(steps + 1):
            u = t / steps
            ang = a0 + (a1 - a0) * u
            r = radius * (1.0 - 0.03 * math.sin(math.pi * u))
            x, y = polar(r, ang)
            put(int(round(x)), int(round(y)), SILK)

# 网心
for i in range(SPOKES):
    a0 = START + 2 * math.pi * i / SPOKES
    a1 = START + 2 * math.pi * (i + 1) / SPOKES
    for t in range(7):
        u = t / 6
        x, y = polar(HUB, a0 + (a1 - a0) * u)
        put(int(round(x)), int(round(y)), SILK_BRIGHT)

write_png(OUT, W, H, canvas)
print("wrote", OUT)

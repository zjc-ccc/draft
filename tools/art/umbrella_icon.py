"""生成 assets/props/umbrella/preview/umbrella_icon_32.png

32x32 物品栏图标：打开状态的雨伞。
32px 下画笔有限，去掉伞骨细线，只保留伞面明暗分片、伞沿弧和手柄。
"""

import math
import os

from png_util import write_png

W = H = 32
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "props", "umbrella", "preview", "umbrella_icon_32.png")

CX = 15.5
TOP = 4
RIM = 14.5
HALF = 14.0
SHAFT_BOTTOM = 25

TEAL = [
    (24, 68, 78, 255),
    (28, 96, 106, 255),
    (46, 138, 138, 255),
    (86, 184, 176, 255),
    (140, 224, 206, 255),
]
PANELS = (1.06, 1.04, 0.98, 0.91, 0.85)

OUTLINE = (10, 26, 32, 255)
METAL = (186, 198, 200, 255)
METAL_DARK = (112, 126, 130, 255)
WOOD = (120, 78, 46, 255)
WOOD_LIGHT = (160, 112, 70, 255)

canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        canvas[y][x] = color


def get(x, y):
    if 0 <= x < W and 0 <= y < H:
        return canvas[y][x]
    return (0, 0, 0, 0)


def shade(color, factor):
    return (
        max(0, min(255, int(color[0] * factor))),
        max(0, min(255, int(color[1] * factor))),
        max(0, min(255, int(color[2] * factor))),
        color[3],
    )


def half_width(y):
    s = (y - TOP) / (RIM - TOP)
    s = max(0.0, min(1.0, s))
    return HALF * math.sin(math.pi / 2 * s) ** 0.62


def rim_at(x):
    p = max(-1.0, min(1.0, (x - CX) / HALF))
    droop = 1.0 * abs(p) ** 2
    phase = (p + 1.0) / 2.0 * len(PANELS)
    scallop = 0.5 - 0.5 * math.cos(2 * math.pi * phase)
    return RIM + droop + 0.9 * scallop


def ramp(s):
    s = max(0.0, min(1.0, s)) * (len(TEAL) - 1)
    i = int(s)
    f = s - i
    if i >= len(TEAL) - 1:
        return TEAL[-1]
    a, b = TEAL[i], TEAL[i + 1]
    return (
        int(a[0] + (b[0] - a[0]) * f),
        int(a[1] + (b[1] - a[1]) * f),
        int(a[2] + (b[2] - a[2]) * f),
        255,
    )


# 伞杆
for y in range(TOP, SHAFT_BOTTOM):
    put(15, y, METAL)
    put(16, y, METAL_DARK)

# 伞面
for y in range(TOP, H):
    hw = half_width(y)
    if hw < 0.4:
        continue
    s = max(0.0, min(1.0, (y - TOP) / (RIM - TOP)))
    for x in range(int(round(CX - hw)), int(round(CX + hw)) + 1):
        if y > rim_at(x):
            continue
        p = (x - CX) / max(hw, 0.001)
        idx = max(0, min(len(PANELS) - 1, int((p + 1.0) / 2.0 * len(PANELS))))
        put(x, y, shade(ramp(s), PANELS[idx]))

# 伞尖：短尖 + 金属球
put(16, 0, METAL)
for x in (15, 16):
    put(x, 1, METAL)
    put(x, 2, METAL_DARK if x == 16 else METAL)
for x in range(14, 18):
    put(x, 3, METAL if x < 17 else METAL_DARK)

# 手柄：木质 J 形弯钩
hook_cx, hook_cy = 18.5, SHAFT_BOTTOM + 0.5
for radius in (2.6, 3.1, 3.6, 4.1):
    for deg in range(-2, 182, 3):
        rad = math.radians(deg)
        x = int(round(hook_cx + radius * math.cos(rad)))
        y = int(round(hook_cy + radius * math.sin(rad)))
        put(x, y, WOOD_LIGHT if y <= hook_cy + 1.6 else WOOD)

for y in range(SHAFT_BOTTOM - 2, int(hook_cy) + 1):
    put(15, y, WOOD_LIGHT)
    put(16, y, WOOD)

# 描边
for y in range(H):
    for x in range(W):
        if canvas[y][x][3] == 0:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if get(x + dx, y + dy)[3] == 0:
                canvas[y][x] = OUTLINE
                break

write_png(OUT, W, H, canvas)
print("wrote", OUT)

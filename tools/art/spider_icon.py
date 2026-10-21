"""生成 assets/characters/spider/preview/spider_icon_32.png

32x32 物品栏图标：静态站姿的蜘蛛，身体比动画帧略大，腿收得更紧。
"""

import math
import os

from png_util import write_png

W = H = 32
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "characters", "spider", "preview", "spider_icon_32.png")

CX = 16.0
HEAD_Y = 11.0
ABDO_Y = 21.0
HEAD_RX, HEAD_RY = 6.5, 5.5
ABDO_RX, ABDO_RY = 7.5, 8.0

BODY = (78, 60, 102, 255)
BODY_HI = (112, 90, 142, 255)
BODY_DARK = (54, 40, 72, 255)
PATTERN = (138, 114, 170, 255)
LEG = (120, 98, 150, 255)
OUTLINE = (20, 14, 28, 255)

EYE_RIM = (12, 22, 40, 255)
EYE_DEEP = (44, 146, 212, 255)
EYE = (104, 216, 255, 255)
EYE_HI = (236, 252, 255, 255)

EYE_PATTERN = (
    ".RRR.",
    "RDDDR",
    "RDBDR",
    "RDDDR",
    ".RRR.",
)

LEGS_LEFT = (
    ((11.5, 11.5), (7.5, 8.5), (3.5, 6.5)),
    ((10.5, 14.5), (5.8, 13.0), (1.5, 11.5)),
    ((10.5, 18.0), (5.8, 19.5), (1.5, 21.0)),
    ((11.5, 21.0), (7.5, 24.0), (3.5, 26.0)),
)

canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
body = [[False] * W for _ in range(H)]


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        canvas[y][x] = color


def line(x0, y0, x1, y1, color, b0=1, b1=1):
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    for i in range(steps + 1):
        u = i / steps
        x = int(round(x0 + (x1 - x0) * u))
        y = int(round(y0 + (y1 - y0) * u))
        b = max(1, int(round(b0 + (b1 - b0) * u)))
        for bx in range(b):
            for by in range(b):
                put(x + bx, y + by, color)


# 腿
for side, sign in ((0, -1.0), (1, 1.0)):
    for attach, knee, foot in LEGS_LEFT:
        def mirror(p):
            return (CX + sign * (p[0] - CX), p[1])

        ax, ay = mirror(attach)
        kx, ky = mirror(knee)
        fx, fy = mirror(foot)
        line(ax, ay, kx, ky, LEG, b0=2, b1=2)
        line(kx, ky, fx, fy, LEG, b0=2, b1=1)

# 身体遮罩
for y in range(H):
    for x in range(W):
        dxh = (x - CX) / HEAD_RX
        dyh = (y - HEAD_Y) / HEAD_RY
        dxa = (x - CX) / ABDO_RX
        dya = (y - ABDO_Y) / ABDO_RY
        if dxh * dxh + dyh * dyh <= 1.0 or dxa * dxa + dya * dya <= 1.0:
            body[y][x] = True

top = HEAD_Y - HEAD_RY
bottom = ABDO_Y + ABDO_RY
for y in range(H):
    for x in range(W):
        if not body[y][x]:
            continue
        t = (y - top) / (bottom - top)
        if t < 0.2:
            color = BODY_HI
        elif t < 0.58:
            color = BODY
        else:
            color = BODY_DARK
        put(x, y, color)

# 腹部人字形花纹
for dx in (-2, -1, 0, 1, 2):
    px = int(round(CX + dx))
    py = int(round(ABDO_Y - 2 + abs(dx) * 0.6))
    if 0 <= px < W and 0 <= py < H and body[py][px]:
        put(px, py, PATTERN)

# 身体描边
for y in range(H):
    for x in range(W):
        if body[y][x] or canvas[y][x][3] != 0:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and body[ny][nx]:
                canvas[y][x] = OUTLINE
                break

# 眼睛
colors = {"R": EYE_RIM, "D": EYE_DEEP, "B": EYE}
for ex in (CX - 3.4, CX + 3.4):
    ox = int(round(ex)) - 2
    oy = int(round(HEAD_Y - 0.6)) - 2
    for row, pattern in enumerate(EYE_PATTERN):
        for col, ch in enumerate(pattern):
            if ch in colors:
                put(ox + col, oy + row, colors[ch])
    put(ox + 1, oy + 1, EYE_HI)

write_png(OUT, W, H, canvas)
print("wrote", OUT)

"""生成 assets/characters/cockroach/preview/cockroach_icon_32.png

32x32 物品栏图标：简化俯视蟑螂。
头朝下，两根触角伸到画布下沿以外；翅缝、前胸背板亮边保留，腿只留轮廓。
"""

import math
import os

from png_util import write_png

W = H = 32
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "characters", "cockroach", "preview", "cockroach_icon_32.png")

INK = (26, 18, 10, 255)

WING_EDGE = (34, 22, 12, 255)
WING_DARK = (48, 30, 16, 255)
WING_MID = (72, 47, 26, 255)
WING = (96, 66, 38, 255)
WING_HI = (128, 92, 54, 255)

PRO_DARK = (44, 29, 17, 255)
PRO = (78, 52, 31, 255)
PRO_HI = (106, 74, 44, 255)
PRO_RIM = (156, 122, 78, 255)

HEAD_DARK = (46, 30, 18, 255)
HEAD = (72, 49, 30, 255)
EYE = (28, 22, 18, 255)

LEG = (86, 61, 38, 255)
ANT = (104, 72, 44, 255)

CX = 16.0

BODY = (
    (4, 0.6), (6, 1.6), (8, 2.8), (10, 3.6), (12, 4.2), (15, 4.6),
    (17, 4.4), (18, 4.2), (19, 5.0), (21, 5.4), (23, 4.6), (24, 3.2),
)
HEAD_ROWS = ((24, 2.8), (25, 2.9), (26, 2.4), (27, 1.2))

LEGS = (
    (22.0, 2.30, -0.45, 3.0, 4.0),   # 前
    (19.0, 2.78, 0.30, 3.0, 4.2),    # 中
    (14.0, 3.85, 0.46, 3.6, 4.6),    # 后
)

canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
solid = [[False] * W for _ in range(H)]
hard = [[False] * W for _ in range(H)]


def put(x, y, color):
    x = int(round(x))
    y = int(round(y))
    if 0 <= x < W and 0 <= y < H:
        canvas[y][x] = color
        solid[y][x] = True


def put_hard(x, y, color):
    x = int(round(x))
    y = int(round(y))
    if 0 <= x < W and 0 <= y < H:
        canvas[y][x] = color
        solid[y][x] = True
        hard[y][x] = True


def line(x0, y0, x1, y1, color):
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    for i in range(steps + 1):
        t = i / float(steps)
        put(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, color)


def interp(table, y):
    if y <= table[0][0]:
        return table[0][1]
    if y >= table[-1][0]:
        return table[-1][1]
    for i in range(len(table) - 1):
        y0, v0 = table[i]
        y1, v1 = table[i + 1]
        if y0 <= y <= y1:
            t = (y - y0) / float(y1 - y0)
            return v0 + (v1 - v0) * t
    return table[-1][1]


def body_hw(y):
    return interp(BODY, y)


def head_hw(y):
    return interp(HEAD_ROWS, y)


def draw_leg(idx, side):
    cox_y, ang, turn, femur, tibia = LEGS[idx]
    a = ang if side < 0 else math.pi - ang
    cox_x = CX + side * (body_hw(cox_y) - 0.8)
    kx = cox_x + math.cos(a) * femur
    ky = cox_y + math.sin(a) * femur
    b = a + (turn if side < 0 else -turn)
    fx = kx + math.cos(b) * tibia
    fy = ky + math.sin(b) * tibia
    line(cox_x, cox_y, kx, ky, LEG)
    put(kx, ky, LEG)
    line(kx, ky, fx, fy, LEG)


def draw_wings():
    for y in range(4, 19):
        hw = body_hw(y) - 0.3
        left = int(round(CX - hw))
        right = int(round(CX + hw))
        for x in range(left, right + 1):
            if x in (15, 16):
                c = WING_EDGE
            elif x in (14, 17):
                c = WING_HI
            elif x in (13, 18):
                c = WING
            else:
                c = WING_MID if abs(x - CX) < hw - 1.2 else WING_DARK
            put_hard(x, y, c)


def draw_pronotum():
    for y in range(18, 25):
        hw = body_hw(y)
        for x in range(int(round(CX - hw)), int(round(CX + hw)) + 1):
            ad = abs(x - CX) / max(1.0, hw)
            if y <= 19:
                c = PRO_DARK if ad > 0.5 else PRO
            elif ad > 0.82:
                c = PRO_DARK
            elif ad > 0.55:
                c = PRO
            elif ad < 0.3:
                c = PRO_HI
            else:
                c = PRO
            put_hard(x, y, c)
    for x in range(int(round(CX - body_hw(22.5))), int(round(CX + body_hw(22.5))) + 1):
        put_hard(x, 22, PRO_RIM if abs(x - CX) < 2.5 else PRO_HI)


def draw_head():
    for y in range(24, 28):
        hw = head_hw(y)
        for x in range(int(round(CX - hw)), int(round(CX + hw)) + 1):
            c = HEAD if abs(x - CX) < hw * 0.5 else HEAD_DARK
            put_hard(x, y, c)
    for s in (-1, 1):
        put_hard(CX + s * 2.2, 25, EYE)
        put_hard(CX + s * 2.2, 26, EYE)


def draw_antenna(side):
    x0, y0 = CX + side * 1.2, 26.5
    x1, y1 = CX + side * 4.5, 29.0
    x2, y2 = CX + side * 9.5, 35.0
    n = 18
    for i in range(n + 1):
        u = i / float(n)
        x = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * x1 + u * u * x2
        y = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * y1 + u * u * y2
        put(x, y, ANT)


def draw_outline():
    for y in range(H):
        for x in range(W):
            if solid[y][x]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and hard[ny][nx]:
                    canvas[y][x] = INK
                    solid[y][x] = True
                    break


for idx, side in ((2, -1), (2, 1), (1, -1), (1, 1), (0, -1), (0, 1)):
    draw_leg(idx, side)

draw_wings()
draw_pronotum()
draw_head()
draw_antenna(-1)
draw_antenna(1)
draw_outline()

write_png(OUT, W, H, canvas)
print("wrote", OUT)

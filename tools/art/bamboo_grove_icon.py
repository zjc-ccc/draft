"""生成 assets/props/bamboo-grove/preview/bamboo-grove_icon_32.png

32x32 物品栏图标：简化的一小片竹林。
三根青竹从土堆里钻出来，底部挤在一起、上面各自散开，每根顶端几片竹叶。
"""

import math
import os

from png_util import write_png

W = H = 32
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "props", "bamboo-grove", "preview", "bamboo-grove_icon_32.png")

INK = (24, 30, 18, 255)

BAMBOO_HI = (176, 206, 116, 255)
BAMBOO = (128, 166, 78, 255)
BAMBOO_MID = (98, 136, 58, 255)
BAMBOO_DARK = (68, 98, 42, 255)
NODE_RING = (204, 216, 150, 255)

LEAF_HI = (154, 194, 94, 255)
LEAF = (110, 154, 68, 255)
LEAF_DARK = (66, 100, 44, 255)

SOIL = (86, 66, 48, 255)
SOIL_HI = (112, 90, 66, 255)
SOIL_DARK = (56, 42, 30, 255)

canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
solid = [[False] * W for _ in range(H)]


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        canvas[y][x] = color


def leaf(x0, y0, ang, length, col, hi):
    """细长竹叶：中段 2px，上半边提亮。"""
    length = max(3, int(round(length)))
    ux = math.cos(ang)
    uy = math.sin(ang)
    x1 = x0 + ux * length
    y1 = y0 + uy * length
    for py in range(int(math.floor(min(y0, y1))) - 2, int(math.ceil(max(y0, y1))) + 3):
        for px in range(int(math.floor(min(x0, x1))) - 2, int(math.ceil(max(x0, x1))) + 3):
            if not (0 <= px < W and 0 <= py < H):
                continue
            vx = px + 0.5 - x0
            vy = py + 0.5 - y0
            t = (vx * ux + vy * uy) / length
            if t < 0.0 or t > 1.0:
                continue
            off = vx * (-uy) + vy * ux
            hw = 0.85 * math.sin(math.pi * t) ** 0.75
            if abs(off) > hw:
                continue
            put(px, py, LEAF_DARK if t > 0.86 else (hi if (off * ux < 0) else col))
            solid[py][px] = True


def culm(bx, tx, by, ty, curve, w):
    """一根竹竿：底部直、越高越往外弯，3px 宽，隔几像素一道竹节。"""
    nodes = [ty + 4 + i * 5 for i in range(9)]
    nodes = [n for n in nodes if n < by - 1]
    for y in range(ty, by + 1):
        t = (by - y) / float(by - ty)
        cx = bx + (tx - bx) * (t ** curve)
        ww = max(1, w - int(round(t * (w - 1) * 0.5)))
        left = int(round(cx - ww / 2.0))
        near = any(abs(y - n) < 1 for n in nodes)
        for i in range(ww):
            x = left + i
            if not (0 <= x < W):
                continue
            if near:
                c = NODE_RING if (y % 2 == 0) else BAMBOO_DARK
            elif i == 0:
                c = BAMBOO_HI
            elif i == ww - 1:
                c = BAMBOO_DARK
            else:
                c = BAMBOO
            put(x, y, c)
            solid[y][x] = True
    return int(round(tx)), ty


# 土堆
for y in range(27, H):
    for x in range(3, 29):
        dx = (x + 0.5 - 16.0) / 12.5
        dy = (y + 0.5 - 31.5) / 4.6
        if dx * dx + dy * dy > 1.0:
            continue
        c = SOIL_HI if y < 28 else (SOIL if y < 30 else SOIL_DARK)
        put(x, y, c)
        solid[y][x] = True

# 三根竹竿（左、中、右）
culm(13, 7, 29, 9, 2.4, 3)
culm(20, 25, 29, 11, 2.4, 3)
culm(16, 16, 29, 6, 2.0, 3)

# 叶：每根顶端朝外散几片
for ax, ay, s in ((7, 9, -1), (25, 11, 1), (16, 6, 1)):
    for ang, ln in ((0.30, 8), (0.80, 7), (-0.30, 7)):
        a = ang if s > 0 else math.pi - ang
        leaf(ax, ay, a, ln, LEAF, LEAF_HI)
    leaf(ax, ay, -1.35 if s > 0 else math.pi + 1.35, 6, LEAF, LEAF_HI)

# 外描边
for y in range(H):
    for x in range(W):
        if solid[y][x]:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and solid[ny][nx]:
                canvas[y][x] = INK
                break

write_png(OUT, W, H, canvas)
print("wrote", OUT)

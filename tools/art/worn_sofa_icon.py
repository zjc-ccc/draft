"""生成 assets/props/worn-sofa/preview/worn-sofa_icon_32.png

32x32 物品栏图标：简化侧视沙发。保留靠背（右）、坐塾、扶手（左）、
两个乱堆的靠枕，以及几块暗黄污渍。
"""

import math
import os

from png_util import write_png

W = H = 32
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "props", "worn-sofa", "preview", "worn-sofa_icon_32.png")

BROWN = (80, 57, 41, 255)
BROWN_MID = (96, 70, 51, 255)
BROWN_HI = (116, 87, 64, 255)
BROWN_DARK = (56, 40, 28, 255)
BROWN_SHADE = (44, 31, 21, 255)
OUTLINE = (30, 21, 15, 255)

PILLOW_A = (100, 74, 54, 255)
PILLOW_A_HI = (126, 96, 72, 255)
PILLOW_B = (72, 51, 36, 255)
PILLOW_B_HI = (102, 74, 54, 255)

STAIN = (118, 98, 53, 255)
DUST = (172, 162, 140, 255)
WOOD = (70, 46, 30, 255)
WOOD_HI = (96, 68, 44, 255)

canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
solid = [[False] * W for _ in range(H)]


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        canvas[y][x] = color


def rrect(x0, y0, x1, y1, radii, color):
    rtl, rtr, rbr, rbl = radii
    pts = []
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            ok = True
            if x < x0 + rtl and y < y0 + rtl:
                ok = (x - (x0 + rtl)) ** 2 + (y - (y0 + rtl)) ** 2 <= rtl * rtl
            elif x > x1 - rtr and y < y0 + rtr:
                ok = (x - (x1 - rtr)) ** 2 + (y - (y0 + rtr)) ** 2 <= rtr * rtr
            elif x > x1 - rbr and y > y1 - rbr:
                ok = (x - (x1 - rbr)) ** 2 + (y - (y1 - rbr)) ** 2 <= rbr * rbr
            elif x < x0 + rbl and y > y1 - rbl:
                ok = (x - (x0 + rbl)) ** 2 + (y - (y1 - rbl)) ** 2 <= rbl * rbl
            if ok:
                put(x, y, color)
                solid[y][x] = True
                pts.append((x, y))
    return pts


def pillow(cx, cy, hw, hh, r, angle, base, hi, dark):
    ca = math.cos(angle)
    sa = math.sin(angle)
    pts = []
    members = set()
    for y in range(int(cy - hh - hw - 1), int(cy + hh + hw + 2)):
        for x in range(int(cx - hw - hh - 1), int(cx + hw + hh + 2)):
            lx = (x - cx) * ca + (y - cy) * sa
            ly = -(x - cx) * sa + (y - cy) * ca
            if abs(lx) <= hw and abs(ly) <= hh:
                qx = abs(lx) - (hw - r)
                qy = abs(ly) - (hh - r)
                if qx <= 0 or qy <= 0 or qx * qx + qy * qy <= r * r:
                    put(x, y, base)
                    solid[y][x] = True
                    pts.append((x, y))
                    members.add((x, y))
    for x, y in pts:
        lx = (x - cx) * ca + (y - cy) * sa
        ly = -(x - cx) * sa + (y - cy) * ca
        if ly < -hh * 0.25:
            canvas[y][x] = hi
        elif ly > hh * 0.4:
            canvas[y][x] = dark
    for x, y in pts:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in members:
                canvas[y][x] = BROWN_SHADE
                break


# 靠背（右）
pts = rrect(18, 4, 29, 21, (6, 3, 1, 1), BROWN)
for x, y in pts:
    if y <= 5:
        canvas[y][x] = BROWN_HI
for y in range(7, 21):
    put(18, y, BROWN_DARK)
    put(19, y, BROWN_DARK)

# 坐塾（中间），顶面拱一点
pts = rrect(5, 11, 23, 20, (3, 2, 1, 1), BROWN)
for x in range(7, 22):
    lift = int(round(math.sin(math.pi * (x - 7) / 15.0) * 1.8))
    for k in range(lift):
        put(x, 10 - k, BROWN_HI)
        solid[10 - k][x] = True
for x, y in pts:
    if y == 11:
        canvas[y][x] = BROWN_HI

# 木框 + 腿
rrect(5, 20, 27, 22, (1, 1, 1, 1), WOOD)
for x in range(6, 27):
    if canvas[20][x][3] != 0:
        put(x, 20, WOOD_HI)
for x in range(6, 27):
    if canvas[22][x][3] != 0:
        put(x, 22, BROWN_SHADE)
for lx in (7, 24):
    for y in range(23, 26):
        for x in range(lx, lx + 2):
            put(x, y, WOOD)
            solid[y][x] = True
    put(lx, 23, WOOD_HI)

# 两个靠枕，乱堆在左边
pillow(10, 8, 5.5, 4.2, 2.0, math.radians(-16), PILLOW_A, PILLOW_A_HI, BROWN_DARK)
pillow(15, 12, 5.0, 3.2, 1.8, math.radians(19), PILLOW_B, PILLOW_B_HI, BROWN_SHADE)

# 扶手（左，盖在前面）
pts = rrect(1, 8, 8, 21, (4, 4, 1, 1), BROWN)
for x, y in pts:
    if y <= 9:
        canvas[y][x] = BROWN_HI
for y in range(10, 21):
    put(8, y, BROWN_SHADE)

# 污渍
for cx, cy, rx, ry in ((14, 17, 3.2, 1.6), (24, 9, 2.4, 1.8), (4, 12, 2.2, 1.2)):
    for y in range(int(cy - ry - 1), int(cy + ry + 2)):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            if not (0 <= x < W and 0 <= y < H) or not solid[y][x]:
                continue
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 1.0:
                put(x, y, STAIN)

# 灰尘
put(21, 4, DUST)
put(7, 8, DUST)
put(2, 9, DUST)
put(19, 18, DUST)

# 外描边
for y in range(H):
    for x in range(W):
        if solid[y][x] or canvas[y][x][3] != 0:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and solid[ny][nx]:
                canvas[y][x] = OUTLINE
                break

write_png(OUT, W, H, canvas)
print("wrote", OUT)

"""生成 assets/props/worn-sofa/preview/worn-sofa_icon_32.png

32x32 物品栏图标：正面平视的简化版破旧双人沙发。
构图上把明暗拉开：靠背整片压暗、座垫亮面、两侧扶手居中，靠背明显高出扶手；
两个靠枕堆在左边，再点两块暗黄污渍和一点积灰。
"""

import math
import os

from png_util import write_png

W = H = 32
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "props", "worn-sofa", "preview", "worn-sofa_icon_32.png")

INK = (24, 17, 12, 255)
BACK = (64, 46, 33, 255)
BACK_TOP = (98, 72, 53, 255)
SEAT = (108, 79, 58, 255)
SEAT_TOP = (140, 108, 82, 255)
SEAT_MID = (124, 94, 70, 255)
SEAT_BOT = (70, 50, 36, 255)
ARM = (112, 84, 61, 255)
ARM_TOP = (138, 106, 80, 255)
ARM_SIDE = (56, 40, 29, 255)
RIM = (62, 45, 33, 255)

PILLOW_A = (154, 122, 95, 255)
PILLOW_A_HI = (174, 144, 116, 255)
PILLOW_A_DARK = (126, 98, 76, 255)
PILLOW_B = (112, 85, 65, 255)
PILLOW_B_HI = (132, 104, 81, 255)
PILLOW_B_DARK = (90, 68, 52, 255)

STAIN = (120, 102, 64, 255)
DUST = (184, 174, 152, 255)
WOOD = (76, 51, 35, 255)
WOOD_HI = (104, 74, 50, 255)
WOOD_DARK = (48, 32, 22, 255)

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

    def inside(x, y):
        lx = (x - cx) * ca + (y - cy) * sa
        ly = -(x - cx) * sa + (y - cy) * ca
        if abs(lx) > hw or abs(ly) > hh:
            return False
        qx = abs(lx) - (hw - r)
        qy = abs(ly) - (hh - r)
        return qx <= 0 or qy <= 0 or qx * qx + qy * qy <= r * r

    pts = []
    for y in range(int(cy - hh - hw - 1), int(cy + hh + hw + 2)):
        for x in range(int(cx - hw - hh - 1), int(cx + hw + hh + 2)):
            if inside(x, y):
                put(x, y, base)
                solid[y][x] = True
                pts.append((x, y))

    # 上亮下暗，只有一条，别加描边（32 像素加不起）
    for x, y in pts:
        ly = -(x - cx) * sa + (y - cy) * ca
        if ly <= -hh + 1.0:
            canvas[y][x] = hi
        elif ly >= hh - 0.9:
            canvas[y][x] = dark


# 腿
for lx in (6, 23):
    for y in range(23, 28):
        put(lx, y, WOOD)
        put(lx + 1, y, WOOD)
        solid[y][lx] = solid[y][lx + 1] = True
    put(lx, 23, WOOD_HI)
    put(lx + 1, 27, WOOD_DARK)

# 木框
pts = rrect(3, 21, 28, 23, (1, 1, 1, 1), WOOD)
for x, y in pts:
    if y == 21:
        canvas[y][x] = WOOD_HI
    elif y == 23:
        canvas[y][x] = WOOD_DARK

# 靠背：一整片横跨沙发，压暗
pts = rrect(4, 4, 27, 17, (3, 3, 0, 0), BACK)
for x, y in pts:
    if y <= 5:
        canvas[y][x] = BACK_TOP

# 座垫
pts = rrect(1, 15, 30, 21, (1, 1, 2, 2), SEAT)
for x, y in pts:
    if y == 15:
        canvas[y][x] = SEAT_TOP
    elif y == 16:
        canvas[y][x] = SEAT_MID
    elif y >= 20:
        canvas[y][x] = SEAT_BOT

# 两个靠枕：斜靠在靠背的暗面上，堆在左边
pillow(9, 9.5, 4.0, 2.4, 1.4, math.radians(-10), PILLOW_A, PILLOW_A_HI, PILLOW_A_DARK)
pillow(13, 12, 3.4, 1.9, 1.1, math.radians(14), PILLOW_B, PILLOW_B_HI, PILLOW_B_DARK)

# 两侧扶手，盖在最前面
for x0, x1, mirrored in ((1, 6, False), (25, 30, True)):
    pts = rrect(x0, 9, x1, 21, (3, 3, 1, 1), ARM)
    for x, y in pts:
        if y <= 10:
            canvas[y][x] = ARM_TOP
        elif y >= 20:
            canvas[y][x] = ARM_SIDE
    inner = x1 if not mirrored else x0
    for y in range(11, 21):
        if solid[y][inner]:
            put(inner, y, ARM_SIDE)

# 污渍
for px, py in ((21, 8), (22, 8), (21, 9), (22, 9), (22, 12), (23, 12), (22, 13), (23, 13),
               (17, 18), (18, 18), (17, 19), (22, 20), (23, 20)):
    if solid[py][px]:
        put(px, py, STAIN)

# 积灰
for x, y in ((8, 4), (16, 4), (24, 4), (2, 9), (29, 9), (6, 15), (25, 15)):
    put(x, y, DUST)

# 外描边
for y in range(H):
    for x in range(W):
        if solid[y][x] or canvas[y][x][3] != 0:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and solid[ny][nx]:
                canvas[y][x] = INK
                break

write_png(OUT, W, H, canvas)
print("wrote", OUT)

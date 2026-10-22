"""生成 assets/props/pendant-lamp/preview/pendant-lamp_icon_32.png

32x32 物品栏图标：简化版复古吊灯（亮着的状态）。
吸顶盘 + 一小段电线 + 黄铜锥形灯罩 + 灯口下一颗亮着的灯泡。
"""

import math
import os

from png_util import write_png

W = H = 32
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "props", "pendant-lamp", "preview", "pendant-lamp_icon_32.png")

INK = (26, 19, 14, 255)
BRASS_HI = (226, 186, 118, 255)
BRASS = (180, 138, 76, 255)
BRASS_MID = (148, 108, 56, 255)
BRASS_DARK = (106, 74, 40, 255)
BRASS_SHADE = (70, 47, 27, 255)
PATINA = (94, 100, 66, 255)
CORD = (44, 32, 25, 255)
DUST = (176, 168, 148, 255)

BULB_WHITE = (255, 248, 220, 255)
BULB_WARM = (252, 214, 132, 255)
BULB_AMBER = (236, 172, 88, 255)
BULB_EDGE = (198, 134, 64, 255)

canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
solid = [[False] * W for _ in range(H)]
soft = set()

RAMP = (BRASS_SHADE, BRASS_DARK, BRASS_MID, BRASS, BRASS_HI)

CANOPY_TOP, CANOPY_BOTTOM = 1, 5
CORD_TOP, CORD_BOTTOM = 5, 12
SOCKET_TOP, SOCKET_BOTTOM = 11, 15
SHADE_TOP, SHADE_BOTTOM = 15, 25
CX = 16.0
BULB_CY, BULB_R = 26.0, 2.8


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        canvas[y][x] = color


def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return (
        int(round(c1[0] + (c2[0] - c1[0]) * t)),
        int(round(c1[1] + (c2[1] - c1[1]) * t)),
        int(round(c1[2] + (c2[2] - c1[2]) * t)),
        255,
    )


def ramp_color(b):
    v = max(0.0, min(1.0, b)) * (len(RAMP) - 1)
    return RAMP[min(int(round(v)), len(RAMP) - 1)]


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


def shade_half(y):
    t = (y - SHADE_TOP) / float(SHADE_BOTTOM - SHADE_TOP)
    return 3.0 + 6.0 * (t ** 1.25)


# 吸顶盘
pts = rrect(11, CANOPY_TOP, 20, CANOPY_BOTTOM, (1, 1, 1, 1), BRASS)
for x, y in pts:
    if y == CANOPY_TOP:
        canvas[y][x] = BRASS_HI
    elif y >= CANOPY_BOTTOM:
        canvas[y][x] = BRASS_DARK
put(12, CANOPY_TOP + 1, DUST)

# 电线
for y in range(CORD_TOP, CORD_BOTTOM + 1):
    put(15, y, CORD)
    solid[y][15] = True
    soft.add((15, y))

# 灯头
pts = rrect(13, SOCKET_TOP, 18, SOCKET_BOTTOM, (1, 1, 1, 1), BRASS_MID)
for x, y in pts:
    if x <= 13:
        canvas[y][x] = BRASS
    elif x >= 18:
        canvas[y][x] = BRASS_DARK

# 灯泡（先画，灯罩会盖住上沿）
for y in range(int(BULB_CY - BULB_R) - 1, int(BULB_CY + BULB_R) + 2):
    for x in range(int(CX - BULB_R) - 1, int(CX + BULB_R) + 2):
        dx = x + 0.5 - CX
        dy = y + 0.5 - BULB_CY
        d = math.hypot(dx, dy)
        if d > BULB_R:
            continue
        if d <= 1.2:
            c = BULB_WHITE
        elif d <= 2.2:
            c = BULB_WARM
        else:
            c = BULB_EDGE
        put(x, y, c)
        solid[y][x] = True
put(int(CX) - 1, int(BULB_CY) - 1, BULB_WHITE)

# 灯罩
for y in range(SHADE_TOP, SHADE_BOTTOM + 1):
    half = shade_half(y)
    for x in range(int(round(CX - half)), int(round(CX + half)) + 1):
        u = (x + 0.5 - CX) / half
        b = 0.55 - 0.35 * u + 0.22 * math.exp(-(((u + 0.45) / 0.30) ** 2))
        put(x, y, ramp_color(b))
        solid[y][x] = True

# 上沿 + 底沿卷边
for x in range(int(round(CX - shade_half(SHADE_TOP))), int(round(CX + shade_half(SHADE_TOP))) + 1):
    put(x, SHADE_TOP, BRASS_MID)
for y in (SHADE_BOTTOM - 1, SHADE_BOTTOM):
    half = shade_half(SHADE_BOTTOM)
    for x in range(int(round(CX - half)), int(round(CX + half)) + 1):
        if not solid[y][x]:
            continue
        put(x, y, BRASS_HI if y == SHADE_BOTTOM - 1 else BRASS_SHADE)
        # 灯口内壁被灯泡照暖
        if abs(x + 0.5 - CX) < half - 1.5:
            put(x, y, mix(canvas[y][x], BULB_WARM, 0.5))

# 氧化斑
for px, py in ((21, 20), (22, 20), (11, 22), (20, 17)):
    if solid[py][px]:
        put(px, py, mix(canvas[py][px], PATINA, 0.7))

# 外描边
for y in range(H):
    for x in range(W):
        if solid[y][x]:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and solid[ny][nx] and (nx, ny) not in soft:
                canvas[y][x] = INK
                break

write_png(OUT, W, H, canvas)
print("wrote", OUT)

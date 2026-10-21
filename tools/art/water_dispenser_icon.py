"""生成 assets/props/water-dispenser/preview/water-dispenser_icon_32.png

32x32 物品栏图标：简化饮水机。水桶占上半部分，水位约 60%，
机身只保留顶板、红蓝两个出水口和接水盘。
"""

import os

from png_util import write_png

W = H = 32
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "props", "water-dispenser", "preview", "water-dispenser_icon_32.png")

MACHINE = (222, 227, 234, 255)
MACHINE_HI = (246, 249, 252, 255)
MACHINE_DARK = (186, 194, 206, 255)
MACHINE_EDGE = (92, 100, 116, 255)
NICHE = (166, 176, 190, 255)
NICHE_EDGE = (118, 126, 142, 255)
TRAY = (104, 113, 128, 255)
SPOUT = (140, 150, 166, 255)

HOT = (210, 76, 68, 255)
HOT_HI = (240, 128, 114, 255)
COLD = (72, 132, 214, 255)
COLD_HI = (132, 184, 240, 255)

GLASS_EDGE = (140, 174, 200, 255)
GLASS_AIR = (208, 230, 244, 255)
WATER_TOP = (162, 222, 250, 255)
WATER = (78, 168, 226, 255)
WATER_DEEP = (52, 132, 198, 255)

canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
machine = [[False] * W for _ in range(H)]


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        canvas[y][x] = color


def rect(x0, y0, x1, y1, color, mark=False):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(x, y, color)
            if mark and 0 <= x < W and 0 <= y < H:
                machine[y][x] = True


# ---- 水桶：先画，机身会盖住瓶颈下半段 ----
rect(9, 1, 22, 8, GLASS_AIR)
rect(10, 9, 21, 10, GLASS_AIR)
rect(13, 11, 18, 14, GLASS_AIR)

# 水（约 60%）
rect(10, 5, 21, 10, WATER)
rect(10, 5, 21, 5, WATER_TOP)
rect(18, 6, 21, 10, WATER_DEEP)
rect(14, 11, 17, 12, WATER_DEEP)

# 水桶描边
for x in range(9, 23):
    put(x, 0, GLASS_EDGE)
for y in range(1, 9):
    put(8, y, GLASS_EDGE)
    put(23, y, GLASS_EDGE)
put(9, 9, GLASS_EDGE)
put(8, 9, GLASS_EDGE)
put(22, 10, GLASS_EDGE)
put(21, 10, GLASS_EDGE)
put(12, 11, GLASS_EDGE)
put(19, 11, GLASS_EDGE)
put(13, 12, GLASS_EDGE)
put(18, 12, GLASS_EDGE)
put(12, 13, GLASS_EDGE)
put(19, 13, GLASS_EDGE)

# 玻璃高光
rect(11, 2, 11, 7, (255, 255, 255, 255))

# ---- 机身 ----
rect(4, 12, 27, 13, MACHINE_DARK, mark=True)
rect(5, 14, 26, 28, MACHINE, mark=True)
rect(5, 14, 26, 14, MACHINE_HI)
rect(5, 15, 5, 26, MACHINE_HI)
rect(26, 15, 26, 26, MACHINE_DARK)
rect(5, 26, 26, 28, MACHINE_DARK)
rect(7, 29, 24, 30, MACHINE_DARK, mark=True)
put(22, 16, (104, 202, 126, 255))

# 红蓝出水口（直接装在白色面板上，比挖凹槽更清楚）
rect(9, 18, 12, 20, HOT)
rect(9, 18, 12, 18, HOT_HI)
rect(10, 21, 10, 22, SPOUT)
rect(19, 18, 22, 20, COLD)
rect(19, 18, 22, 18, COLD_HI)
rect(20, 21, 20, 22, SPOUT)

# 接水盘
rect(8, 24, 23, 25, TRAY)
rect(8, 24, 23, 24, NICHE_EDGE)

# 机身外描边
for y in range(H):
    for x in range(W):
        if machine[y][x] or canvas[y][x][3] != 0:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and machine[ny][nx]:
                canvas[y][x] = MACHINE_EDGE
                break

write_png(OUT, W, H, canvas)
print("wrote", OUT)

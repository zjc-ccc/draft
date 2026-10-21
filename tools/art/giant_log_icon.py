"""生成 assets/props/giant-log/preview/giant-log_icon_32.png

32x32 物品栏图标：只保留轮廓、体积和切面年轮，去掉细碎树皮纹理。
"""

import math
import os

from png_util import write_png

W = H = 32
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "props", "giant-log", "preview", "giant-log_icon_32.png")

OUTLINE = (44, 28, 14, 255)
BARK_1 = (176, 130, 82, 255)
BARK_3 = (130, 90, 52, 255)
BARK_4 = (108, 72, 40, 255)
BARK_5 = (86, 55, 30, 255)
BARK_7 = (52, 32, 16, 255)
BARK_LINE = (48, 29, 14, 255)

FACE = (240, 216, 168, 255)
FACE_MID = (224, 196, 144, 255)
FACE_SHADE = (204, 172, 120, 255)
RING = (188, 146, 90, 255)
RING_DARK = (152, 112, 66, 255)
RIM = (74, 46, 24, 255)

TOP, BOTTOM = 9, 23
CY = 16.0
BODY_L, BODY_R = 5, 24
RX_R, RY_R = 5.5, 7.0

canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        canvas[y][x] = color


def get(x, y):
    if 0 <= x < W and 0 <= y < H:
        return canvas[y][x]
    return (0, 0, 0, 0)


def inside_face(x, y):
    return ((x - BODY_R) / RX_R) ** 2 + ((y - CY) / RY_R) ** 2 <= 1.02


def bark_color(y):
    if y <= TOP:
        return BARK_1
    if y <= 13:
        return BARK_3
    if y <= 17:
        return BARK_4
    if y <= 20:
        return BARK_5
    return BARK_7


def draw_body():
    for x in range(BODY_L, BODY_R + 1):
        for y in range(TOP, BOTTOM + 1):
            put(x, y, bark_color(y))
    # 左端 1px 倒角，避免直角太硬
    for x, y in ((BODY_L, TOP), (BODY_L, TOP + 1), (BODY_L, BOTTOM - 1), (BODY_L, BOTTOM)):
        put(x, y, (0, 0, 0, 0))


def draw_bark():
    # 两道褶皱，够读就行
    for y0 in (13, 19):
        for x in range(BODY_L + 1, BODY_R):
            y = y0 + round(0.6 * math.sin(x * 0.55 + y0))
            if get(x, y)[3] == 0:
                continue
            put(x, y, BARK_LINE)


def draw_face():
    for x in range(BODY_R - int(RX_R) - 1, W):
        for y in range(TOP - 1, BOTTOM + 2):
            if not inside_face(x, y):
                continue

            nx = (x - BODY_R) / RX_R
            ny = (y - CY) / RY_R
            r = math.hypot(nx, ny)

            if r > 0.80:
                put(x, y, RIM)
                continue

            color = FACE
            if ny > 0.35:
                color = FACE_SHADE
            elif ny > -0.1:
                color = FACE_MID
            phase = r * 2.2
            if phase - math.floor(phase) < 0.36:
                color = RING
            put(x, y, color)

    put(BODY_R, 16, RING_DARK)


def draw_outline():
    for y in range(H):
        for x in range(W):
            if canvas[y][x][3] == 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if get(x + dx, y + dy)[3] == 0:
                    canvas[y][x] = OUTLINE
                    break


draw_body()
draw_bark()
draw_face()
draw_outline()
write_png(OUT, W, H, canvas)
print("wrote", OUT)

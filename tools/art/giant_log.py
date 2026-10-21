"""生成 assets/props/giant-log/export/giant-log.png

64x64 像素原木：侧视横放，外圈褶皱树皮，右端切面有年轮。
只用标准库（zlib + struct）写 PNG，不依赖 Pillow。

用法: python tools/art/giant_log.py
"""
import math
import os

from png_util import write_png

W = H = 64
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "props", "giant-log", "export", "giant-log.png")

# --- 调色板 ---------------------------------------------------------------
OUTLINE = (44, 28, 14, 255)

BARK_1 = (176, 130, 82, 255)   # 顶部受光
BARK_2 = (154, 110, 66, 255)
BARK_3 = (130, 90, 52, 255)
BARK_4 = (108, 72, 40, 255)
BARK_5 = (86, 55, 30, 255)
BARK_6 = (66, 41, 21, 255)
BARK_7 = (52, 32, 16, 255)     # 底部暗部
BARK_LINE = (48, 29, 14, 255)  # 褶皱线

FACE = (240, 216, 168, 255)
FACE_MID = (224, 196, 144, 255)
FACE_SHADE = (204, 172, 120, 255)
RING = (188, 146, 90, 255)
RING_DARK = (166, 126, 76, 255)
RIM = (74, 46, 24, 255)
RIM_LIGHT = (112, 76, 44, 255)

# --- 几何 ---------------------------------------------------------------
TOP, BOTTOM = 20, 43                 # 侧面上下沿
CY = 31.5
BODY_L, BODY_R = 6, 52
RX_L, RY_L = 5.0, 12.0               # 左端圆角
RX_R, RY_R = 8.0, 11.5               # 右端切面

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


def inside_body(x, y):
    if x < BODY_L:
        return ((x - BODY_L) / RX_L) ** 2 + ((y - CY) / RY_L) ** 2 <= 1.0
    if x > BODY_R:
        return False
    return TOP <= y <= BOTTOM


def inside_face(x, y):
    return ((x - BODY_R) / RX_R) ** 2 + ((y - CY) / RY_R) ** 2 <= 1.0


def bark_color(y):
    if y <= 20:
        return BARK_1
    if y <= 22:
        return BARK_2
    if y <= 27:
        return BARK_3
    if y <= 32:
        return BARK_4
    if y <= 37:
        return BARK_5
    if y <= 41:
        return BARK_6
    return BARK_7


# --- 绘制 ---------------------------------------------------------------

def draw_body():
    for x in range(BODY_L - int(RX_L), BODY_R + 1):
        for y in range(TOP - 2, BOTTOM + 1):
            if inside_body(x, y):
                color = bark_color(y)
                if x < BODY_L:
                    color = shade(color, 0.9)
                put(x, y, color)


def draw_bark():
    # 横向褶皱：波浪线，断点模拟树皮裂开
    for y0 in (24, 29, 34, 39):
        for x in range(BODY_L, BODY_R):
            y = y0 + round(1.0 * math.sin(x * 0.30 + y0 * 1.9))
            if get(x, y)[3] == 0:
                continue
            if (x * 13 + y0 * 7) % 23 < 3:
                continue
            put(x, y, BARK_LINE)

    # 上部褶皱的受光边，只在亮面加短段
    for y0 in (24, 29):
        for x in range(BODY_L + 2, BODY_R - 4):
            y = y0 + round(1.0 * math.sin(x * 0.30 + y0 * 1.9)) - 1
            if get(x, y)[3] == 0:
                continue
            if (x * 5 + y0) % 9 < 4:
                put(x, y, BARK_1)
            else:
                put(x, y, BARK_2)

    # 短的纵向裂纹
    for x0, y_from, y_to in ((12, 23, 29), (27, 33, 41), (42, 24, 31)):
        for y in range(y_from, y_to):
            x = x0 + round(0.6 * math.sin(y * 0.5 + x0))
            if get(x, y)[3] == 0:
                continue
            put(x, y, BARK_LINE)

    # 树疤
    for rx, ry, color in ((4.6, 2.6, shade(BARK_4, 0.9)), (2.4, 1.4, BARK_LINE)):
        for dx in range(-6, 7):
            for dy in range(-4, 5):
                if (dx / rx) ** 2 + (dy / ry) ** 2 <= 1.0:
                    if get(26 + dx, 30 + dy)[3] != 0:
                        put(26 + dx, 30 + dy, color)


def draw_face():
    for x in range(BODY_R - int(RX_R) - 1, 63):
        for y in range(TOP - 2, BOTTOM + 2):
            if not inside_face(x, y):
                continue

            nx = (x - BODY_R) / RX_R
            ny = (y - CY) / RY_R
            r = math.hypot(nx, ny)
            theta = math.atan2(ny, nx)

            # 树皮断口（外圈）
            if r > 0.84:
                color = RIM_LIGHT if ny < -0.15 else RIM
                put(x, y, color)
                continue

            wobble = 0.015 * math.sin(2.0 * theta + 1.1) + 0.010 * math.sin(5.0 * theta)
            rr = r + wobble

            color = FACE
            if rr > 0.62 and ny > 0.1:
                color = FACE_SHADE
            elif rr > 0.5:
                color = FACE_MID

            # 年轮：三圈
            phase = rr * 3.6
            if phase - math.floor(phase) < 0.30:
                color = RING
            if abs(rr - 0.78) < 0.04:
                color = RING_DARK

            # 靠身体一侧稍微压暗，做出断面的厚度
            if nx < -0.3 and rr > 0.70:
                color = RING_DARK
            elif nx < -0.55:
                color = shade(color, 0.9)
            put(x, y, color)

    # 髓心
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        put(BODY_R - 1 + dx, 32 + dy, RING_DARK)

    # 从髓心裂向边的裂纹
    for i in range(4, 30):
        rr = i / 30.0
        x = int(round(BODY_R - 0.5 + math.cos(2.6) * rr * RX_R))
        y = int(round(CY + math.sin(2.6) * rr * RY_R))
        if get(x, y)[3] != 0 and i % 6 != 0:
            put(x, y, RING_DARK)


def draw_highlights():
    for x in range(BODY_L, BODY_R):
        if get(x, TOP)[3] != 0:
            put(x, TOP, BARK_1)
        if get(x, TOP + 1)[3] != 0:
            put(x, TOP + 1, BARK_2)
    for x in range(14, 38):
        if get(x, TOP + 2)[3] != 0:
            put(x, TOP + 2, BARK_1)


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
draw_highlights()
draw_outline()
write_png(OUT, W, H, canvas)
print("wrote", OUT)

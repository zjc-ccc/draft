"""生成 assets/props/worn-sofa/export/worn-sofa_idle_00..07.png

96x56 破旧双人沙发，侧视（坐塾在左、靠背在右、近处一个扶手）：
- 深棕布面，暗黄色污渍，边角和缝隙积灰
- 两个靠枕乱堆在左边，一个斜靠扶手、一个歪在坐塾上
- 8 帧循环：空气里几粒灰尘慢慢飘

用法: python tools/art/worn_sofa.py
"""

import math
import os
import random

from png_util import write_png

W, H = 96, 56
FRAMES = 8
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "assets", "props", "worn-sofa", "export")

BROWN = (80, 57, 41, 255)
BROWN_MID = (96, 70, 51, 255)
BROWN_HI = (114, 85, 62, 255)
BROWN_DARK = (56, 40, 28, 255)
BROWN_SHADE = (44, 31, 21, 255)
SEAM = (47, 33, 23, 255)
OUTLINE = (30, 21, 15, 255)

PILLOW_A = (98, 72, 52, 255)
PILLOW_A_HI = (124, 94, 70, 255)
PILLOW_B = (72, 51, 36, 255)
PILLOW_B_HI = (102, 74, 54, 255)

STAIN_CORE = (126, 105, 55, 255)
STAIN_MID = (110, 92, 50, 255)
STAIN_EDGE = (94, 79, 47, 255)

DUST = (176, 166, 144, 255)
DUST_DIM = (140, 130, 110, 255)

WOOD = (72, 48, 32, 255)
WOOD_HI = (98, 70, 46, 255)
WOOD_DARK = (46, 30, 21, 255)

canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
solid = [[False] * W for _ in range(H)]

rng = random.Random(23)


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        canvas[y][x] = color


def rrect(x0, y0, x1, y1, radii, color, mark=True):
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
                if mark:
                    solid[y][x] = True
                pts.append((x, y))
    return pts


def band(pts, y0, y1, top=0, bottom=0, top_color=None, bottom_color=None):
    for x, y in pts:
        if top_color is not None and y <= y0 + top - 1:
            canvas[y][x] = top_color
        elif bottom_color is not None and y >= y1 - bottom + 1:
            canvas[y][x] = bottom_color


def rotated_pillow(cx, cy, hw, hh, r, angle, base, hi, dark):
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
                if (qx <= 0 or qy <= 0 or qx * qx + qy * qy <= r * r):
                    put(x, y, base)
                    solid[y][x] = True
                    pts.append((x, y))
                    members.add((x, y))

    # 上亮下暗，做出枕头鼓起来的感觉
    for x, y in pts:
        lx = (x - cx) * ca + (y - cy) * sa
        ly = -(x - cx) * sa + (y - cy) * ca
        if ly < -hh * 0.28:
            canvas[y][x] = hi
        elif ly > hh * 0.42:
            canvas[y][x] = dark

    # 内缝线
    for x, y in pts:
        lx = (x - cx) * ca + (y - cy) * sa
        ly = -(x - cx) * sa + (y - cy) * ca
        if abs(lx) <= hw - 2.0 and abs(ly) <= hh - 2.0:
            qx = abs(lx) - (hw - 2.0 - r * 0.6)
            qy = abs(ly) - (hh - 2.0 - r * 0.6)
            if abs(lx) > hw - 3.2 or abs(ly) > hh - 3.2:
                canvas[y][x] = SEAM
            elif qx > 0 and qy > 0 and qx * qx + qy * qy > (r * 0.6) ** 2:
                canvas[y][x] = SEAM

    # 中间的扣子
    put(int(round(cx)), int(round(cy)), SEAM)
    put(int(round(cx)) - 1, int(round(cy)), dark)
    put(int(round(cx)), int(round(cy)) - 1, hi)

    # 内侧描边（用深棕，不用纯黑，边缘更柔和）
    for x, y in pts:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in members:
                canvas[y][x] = BROWN_SHADE
                break
    return pts


def draw_leg(x):
    for y in range(44, 53):
        t = (y - 44) / 8.0
        half = 3.8 - t * 1.1
        left = int(round(x - half))
        right = int(round(x + half))
        for x2 in range(left, right + 1):
            put(x2, y, WOOD)
            solid[y][x2] = True
        put(left, y, WOOD_HI)
        put(right, y, WOOD_DARK)
        if right > left:
            put(right - 1, y, WOOD)


def wrinkle_h(x, y, n):
    for i in range(n):
        if 0 <= x + i < W and solid[y][x + i]:
            put(x + i, y, SEAM)
            if solid[y - 1][x + i]:
                put(x + i, y - 1, BROWN_MID)


def wrinkle_v(x, y, n):
    for i in range(n):
        if 0 <= y + i < H and solid[y + i][x]:
            put(x, y + i, SEAM)
            if solid[y + i][x + 1]:
                put(x + 1, y + i, BROWN_MID)


def draw_stain(cx, cy, rx, ry):
    for y in range(int(cy - ry - 3), int(cy + ry + 4)):
        for x in range(int(cx - rx - 3), int(cx + rx + 4)):
            if not (0 <= x < W and 0 <= y < H) or not solid[y][x]:
                continue
            u = (x - cx) / rx
            v = (y - cy) / ry
            d = u * u + v * v
            ang = math.atan2(v, u)
            wob = 1.0 + 0.20 * math.sin(3 * ang + 1.7) + 0.13 * math.sin(5 * ang + 0.4)
            if d <= 0.50 * wob:
                put(x, y, STAIN_CORE)
            elif d <= 0.95 * wob:
                put(x, y, STAIN_MID if (x * 3 + y * 5) % 5 < 3 else STAIN_EDGE)
            elif d <= 1.45 * wob and (x * 3 + y * 5) % 7 < 2:
                put(x, y, STAIN_EDGE)


def draw_dust_specks():
    spots = []
    # 靠背顶
    for x in range(70, 89, 9):
        spots.append((x, 9))
    # 扶手顶
    for x in range(8, 21, 6):
        spots.append((x, 17))
    # 坐塾前沿
    for x in range(28, 62, 11):
        spots.append((x, 25))
    # 靠枕顶
    spots.append((30, 11))
    # 靠背和坐塾之间的缝
    for x in range(65, 68):
        spots.append((x, 27))
        spots.append((x, 33))
    for x, y in spots:
        put(x, y, DUST if (x + y) % 3 else DUST_DIM)
        if (x * 2 + y) % 3 == 0:
            put(x, y + 1, DUST_DIM)
    # 少量零散灰点，只落在地上表面
    for _ in range(8):
        x = rng.randrange(10, 88)
        y = rng.randrange(9, 42)
        if solid[y][x] and not solid[y - 1][x]:
            put(x, y, DUST_DIM)


MOTES = (
    (18.0, 10.0, 2.2, 0.00),
    (36.0, 4.0, 2.4, 0.32),
    (48.0, 9.0, 2.0, 0.62),
    (64.0, 3.5, 2.2, 0.15),
    (80.0, 4.5, 2.4, 0.78),
)


def draw_motes(frame):
    t = frame / FRAMES
    for mx, my, amp, phase in MOTES:
        a = (t + phase) % 1.0
        x = mx + math.sin(a * math.tau) * amp
        y = my + math.cos(a * math.tau) * amp * 1.2
        bright = math.sin(a * math.tau + 1.1)
        color = DUST if bright > 0 else DUST_DIM
        put(int(round(x)), int(round(y)), color)
        if bright > 0.6:
            put(int(round(x)) + 1, int(round(y)), DUST_DIM)


def build(frame):
    global canvas, solid
    canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
    solid = [[False] * W for _ in range(H)]

    # 腿
    draw_leg(18)
    draw_leg(78)

    # 木框
    pts = rrect(12, 39, 88, 44, (2, 2, 2, 2), WOOD)
    band(pts, 39, 44, top=1, bottom=2, top_color=WOOD_HI, bottom_color=WOOD_DARK)
    for x in range(16, 88):
        if canvas[42][x][3] != 0 and (x * 5) % 13 == 0:
            put(x, 42, WOOD_DARK)

    # 靠背：左上角大圆角，做出后倾的斜肩
    pts = rrect(66, 8, 90, 41, (15, 7, 3, 3), BROWN)
    band(pts, 8, 41, top=2, bottom=3, top_color=BROWN_HI, bottom_color=BROWN_DARK)
    # 靠背顶部的滚边
    for x in range(72, 89):
        if canvas[10][x][3] != 0:
            put(x, 10, BROWN_MID)
    for y in range(14, 41):
        put(66, y, BROWN_DARK)
        put(67, y, BROWN_DARK)
        put(68, y, SEAM)
        put(69, y, BROWN_DARK)
    for y in range(9, 41):
        put(90, y, BROWN_SHADE)
        put(89, y, BROWN_DARK)

    # 坐塾
    pts = rrect(20, 24, 69, 39, (5, 4, 3, 3), BROWN)
    band(pts, 24, 39, top=2, bottom=2, top_color=BROWN_HI, bottom_color=BROWN_DARK)
    # 中间鼓起来一点，别像床板
    for x in range(23, 67):
        lift = int(round(math.sin(math.pi * (x - 23) / 43.0) * 4.0))
        for k in range(lift):
            y = 23 - k
            if 0 <= y < H:
                put(x, y, BROWN_HI if k >= lift - 2 else BROWN_MID)
                solid[y][x] = True
    for x in range(24, 68):
        if canvas[35][x][3] != 0:
            put(x, 35, SEAM)
        if canvas[36][x][3] != 0:
            put(x, 36, BROWN_MID)
    # 坐塾和靠背之间的暗缝
    for y in range(24, 40):
        for x in range(64, 68):
            if canvas[y][x][3] != 0:
                put(x, y, BROWN_SHADE)

    # 两个靠枕：一个立着斜靠扶手，一个歪在坐塾上，乱堆在左边
    rotated_pillow(30, 18, 9.5, 7.5, 3.5, math.radians(-16), PILLOW_A, PILLOW_A_HI, BROWN_DARK)
    rotated_pillow(43, 25, 9, 5.5, 3.0, math.radians(19), PILLOW_B, PILLOW_B_HI, BROWN_SHADE)

    # 扶手盖在最前面
    pts = rrect(4, 16, 22, 41, (8, 8, 3, 3), BROWN)
    band(pts, 16, 41, top=3, bottom=2, top_color=BROWN_HI, bottom_color=BROWN_DARK)
    for x in range(6, 22):
        if canvas[23][x][3] != 0:
            put(x, 23, SEAM)
    for y in range(17, 41):
        put(21, y, SEAM)
        put(22, y, BROWN_SHADE)

    # 布料褶皱
    wrinkle_h(27, 31, 5)
    wrinkle_h(52, 30, 4)
    wrinkle_h(60, 33, 4)
    wrinkle_h(30, 37, 4)
    wrinkle_v(74, 22, 4)
    wrinkle_v(80, 27, 3)
    wrinkle_v(85, 19, 3)
    wrinkle_h(9, 28, 5)
    wrinkle_h(13, 35, 4)

    # 污渍
    draw_stain(31, 32, 5, 2)
    draw_stain(76, 16, 4, 3)
    draw_stain(81, 31, 5, 3)
    draw_stain(13, 21, 4, 2)
    draw_stain(35, 16, 3, 2)
    draw_stain(57, 31, 5, 3)
    draw_stain(47, 24, 3, 2)

    # 灰尘
    draw_dust_specks()

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

    draw_motes(frame)
    return canvas


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for frame in range(FRAMES):
        canvas = build(frame)
        path = os.path.join(OUT_DIR, f"worn-sofa_idle_{frame:02d}.png")
        write_png(path, W, H, canvas)
    print("wrote", FRAMES, "frames to", OUT_DIR)


if __name__ == "__main__":
    main()

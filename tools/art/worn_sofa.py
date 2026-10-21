"""生成 assets/props/worn-sofa/export/worn-sofa_idle_00..07.png

96x56 破旧双人沙发，正面平视（能看到横跨整张沙发的靠背）：
- 靠背一整片横跨沙发，分成左右两块，明显高出座垫
- 座垫两块并排，中间一道缝；两只扶手在两侧，盖在靠背和座垫前面
- 深棕布面，暗黄色污渍，边角和缝隙积灰
- 两个靠枕斜靠在靠背上，都堆在左边
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
BACK_FACE = (62, 44, 31, 255)
SHADOW = (36, 25, 17, 255)
SEAM = (47, 33, 23, 255)
OUTLINE = (30, 21, 15, 255)

PILLOW_A = (112, 84, 62, 255)
PILLOW_A_HI = (138, 106, 80, 255)
PILLOW_B = (92, 68, 48, 255)
PILLOW_B_HI = (118, 90, 66, 255)

STAIN_CORE = (104, 90, 56, 255)
STAIN_MID = (94, 81, 53, 255)
STAIN_EDGE = (86, 74, 50, 255)

DUST = (176, 166, 144, 255)
DUST_DIM = (140, 130, 110, 255)

WOOD = (72, 48, 32, 255)
WOOD_HI = (98, 70, 46, 255)
WOOD_DARK = (46, 30, 21, 255)

BACK_TOP, BACK_BOTTOM = 6, 29
SEAT_TOP, SEAT_BOTTOM = 22, 38
RAIL_TOP, RAIL_BOTTOM = 38, 44
SEAM_X = 48

canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
solid = [[False] * W for _ in range(H)]

rng = random.Random(23)


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


def rotated_pillow(cx, cy, hw, hh, r, angle, base, hi, dark):
    ca = math.cos(angle)
    sa = math.sin(angle)

    def inside(x, y, hw2, hh2, r2):
        lx = (x - cx) * ca + (y - cy) * sa
        ly = -(x - cx) * sa + (y - cy) * ca
        if abs(lx) > hw2 or abs(ly) > hh2:
            return False
        qx = abs(lx) - (hw2 - r2)
        qy = abs(ly) - (hh2 - r2)
        return qx <= 0 or qy <= 0 or qx * qx + qy * qy <= r2 * r2

    pts = []
    members = set()
    for y in range(int(cy - hh - hw - 1), int(cy + hh + hw + 2)):
        for x in range(int(cx - hw - hh - 1), int(cx + hw + hh + 2)):
            if inside(x, y, hw, hh, r):
                put(x, y, base)
                solid[y][x] = True
                pts.append((x, y))
                members.add((x, y))

    # 上亮下暗，做出枕头鼓起来的感觉
    for x, y in pts:
        ly = -(x - cx) * sa + (y - cy) * ca
        if ly <= -hh + 2.4:
            canvas[y][x] = hi
        elif ly >= hh - 1.8:
            canvas[y][x] = dark
        else:
            canvas[y][x] = base

    # 内缝线：沿内缩一圈的连续虚线，做出枕头包边
    ihw, ihh, ir = hw - 2.2, hh - 2.2, max(0.6, r - 0.8)
    for x, y in pts:
        if not inside(x, y, ihw, ihh, ir):
            continue
        edge = False
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if not inside(x + dx, y + dy, ihw, ihh, ir):
                edge = True
                break
        if edge:
            canvas[y][x] = SEAM

    # 内侧描边（深棕，不用纯黑）
    for x, y in pts:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in members:
                canvas[y][x] = BROWN_SHADE
                break
    return pts


def draw_leg(x):
    for y in range(45, 52):
        t = (y - 45) / 6.0
        half = 3.6 - t * 1.0
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


def wrinkle_v(x, y, n):
    for i in range(n):
        if 0 <= y + i < H and solid[y + i][x]:
            put(x, y + i, SEAM)


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


def draw_back():
    """靠背：横跨整张沙发的一整片。"""
    pts = rrect(10, BACK_TOP, 86, BACK_BOTTOM, (5, 5, 0, 0), BACK_FACE)
    # 顶部滚边
    for x, y in pts:
        if y == BACK_TOP:
            canvas[y][x] = BROWN_HI
        elif y == BACK_TOP + 1:
            canvas[y][x] = BROWN_HI
        elif y == BACK_TOP + 2:
            canvas[y][x] = BROWN_MID
        elif y == BACK_TOP + 3:
            canvas[y][x] = BROWN_MID
        elif y == BACK_TOP + 4:
            canvas[y][x] = SEAM
    # 左右两块靠垫的分界
    for y in range(BACK_TOP + 6, BACK_BOTTOM + 1):
        if solid[y][SEAM_X]:
            put(SEAM_X, y, SEAM)
        if solid[y][SEAM_X + 1]:
            put(SEAM_X + 1, y, BROWN_MID)
    # 座垫挡在靠背前面，靠背底部留遮挡阴影
    for y in range(SEAT_TOP - 3, SEAT_TOP):
        for x in range(10, 87):
            if solid[y][x]:
                put(x, y, SHADOW if y == SEAT_TOP - 1 else BROWN_SHADE)


def draw_seat():
    """座垫：左右两块。"""
    pts = rrect(6, SEAT_TOP, 90, SEAT_BOTTOM, (2, 2, 3, 3), BROWN)
    for x, y in pts:
        if y == SEAT_TOP:
            canvas[y][x] = BROWN_HI
        elif y == SEAT_TOP + 1:
            canvas[y][x] = BROWN_HI
        elif y == SEAT_TOP + 2:
            canvas[y][x] = BROWN_MID
        elif y == SEAT_TOP + 3:
            canvas[y][x] = SEAM
        elif y >= SEAT_BOTTOM - 1:
            canvas[y][x] = BROWN_DARK
    # 两块座垫之间的缝
    for y in range(SEAT_TOP + 4, SEAT_BOTTOM):
        if solid[y][SEAM_X]:
            put(SEAM_X, y, SEAM)
        if solid[y][SEAM_X + 1]:
            put(SEAM_X + 1, y, BROWN_MID)


def draw_rail():
    pts = rrect(10, RAIL_TOP, 86, RAIL_BOTTOM, (2, 2, 2, 2), WOOD)
    for x, y in pts:
        if y == RAIL_TOP:
            canvas[y][x] = WOOD_HI
        elif y >= RAIL_BOTTOM - 1:
            canvas[y][x] = WOOD_DARK
    for x in range(14, 86):
        if canvas[42][x][3] != 0 and (x * 5) % 13 == 0:
            put(x, 42, WOOD_DARK)


def draw_arm(x0, x1, mirrored):
    pts = rrect(x0, 13, x1, 42, (6, 6, 2, 2), BROWN)
    for x, y in pts:
        if y <= 14:
            canvas[y][x] = BROWN_HI
        elif y == 15:
            canvas[y][x] = BROWN_HI
        elif y == 16:
            canvas[y][x] = BROWN_MID
        elif y == 20:
            canvas[y][x] = SEAM
        elif y >= 41:
            canvas[y][x] = BROWN_DARK
    # 扶手内侧（朝座垫那面）压一道暗边
    inner = x1 if not mirrored else x0
    for y in range(17, 42):
        if solid[y][inner]:
            put(inner, y, SEAM)
        nb = inner - 1 if not mirrored else inner + 1
        if solid[y][nb]:
            put(nb, y, BROWN_MID)
    outer = x0 if not mirrored else x1
    for y in range(18, 42):
        if solid[y][outer]:
            put(outer, y, BROWN_MID if not mirrored else BROWN_SHADE)


def draw_dust_specks():
    spots = []
    # 靠背顶
    for x in range(16, 84, 8):
        spots.append((x, BACK_TOP))
    # 两侧扶手顶
    for x in (5, 10, 85, 90):
        spots.append((x, 13))
    # 座垫前沿
    for x in range(20, 82, 12):
        spots.append((x, SEAT_TOP))
    # 靠背和座垫之间的缝
    for x in range(24, 80, 22):
        spots.append((x, SEAT_TOP - 1))
    for x, y in spots:
        put(x, y, DUST if (x + y) % 3 else DUST_DIM)
        if (x * 2 + y) % 3 == 0:
            put(x, y + 1, DUST_DIM)
    # 少量零散灰点，只落在上表面
    for _ in range(8):
        x = rng.randrange(6, 91)
        y = rng.randrange(8, 40)
        if solid[y][x] and not solid[y - 1][x]:
            put(x, y, DUST_DIM)


MOTES = (
    (10.0, 3.0, 1.6, 0.00),
    (26.0, 2.0, 1.4, 0.32),
    (44.0, 3.5, 1.6, 0.62),
    (62.0, 2.0, 1.4, 0.15),
    (78.0, 3.5, 1.6, 0.78),
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

    # 腿 → 木框 → 靠背 → 座垫
    draw_leg(15)
    draw_leg(81)
    draw_rail()
    draw_back()
    draw_seat()

    # 两个靠枕：斜靠在靠背上，都堆在左边
    rotated_pillow(27, 16, 9.5, 7.5, 3.5, math.radians(-14), PILLOW_A, PILLOW_A_HI, BROWN_DARK)
    rotated_pillow(39, 24, 8.5, 5.5, 3.0, math.radians(18), PILLOW_B, PILLOW_B_HI, BROWN_SHADE)

    # 两只扶手盖在最前面
    draw_arm(2, 14, False)
    draw_arm(82, 94, True)

    # 布料褶皱
    wrinkle_h(30, 33, 5)
    wrinkle_h(58, 31, 5)
    wrinkle_v(70, 24, 4)
    wrinkle_v(34, 15, 4)
    wrinkle_h(6, 27, 4)
    wrinkle_h(87, 28, 4)

    # 污渍
    draw_stain(26, 14, 3, 2)
    draw_stain(64, 12, 4, 2)
    draw_stain(74, 20, 3, 2)
    draw_stain(22, 31, 4, 2)
    draw_stain(64, 31, 4, 2)
    draw_stain(72, 35, 3, 1)
    draw_stain(8, 22, 2, 2)
    draw_stain(88, 30, 2, 2)

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

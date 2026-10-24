"""生成 assets/characters/cockroach/export/cockroach_walk_00..07.png

64x64 蟑螂，俯视（贴地虫眼：镜头压在蟑螂背上往下看）。
头朝画面下方，两根长触角一直伸到画布下沿以外，所以看着像从画面下方探进来。

8 帧 @ 8fps：三角步态（六条腿两组交替）+ 触角轻摆，身体不动。

用法: python tools/art/cockroach.py
"""

import math
import os

from png_util import write_png

W, H = 64, 64
FRAMES = 8
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "assets", "characters", "cockroach", "export")

INK = (26, 18, 10, 255)

WING_EDGE = (34, 22, 12, 255)
WING_DARK = (48, 30, 16, 255)
WING_MID = (72, 47, 26, 255)
WING = (94, 64, 36, 255)
WING_HI = (124, 88, 50, 255)
WING_SHEEN = (166, 128, 82, 255)

PRO_DARK = (44, 29, 17, 255)
PRO = (74, 49, 29, 255)
PRO_HI = (102, 71, 42, 255)
PRO_RIM = (158, 124, 80, 255)

HEAD_DARK = (46, 30, 18, 255)
HEAD = (76, 52, 32, 255)
EYE = (30, 24, 20, 255)
EYE_HI = (100, 90, 74, 255)

LEG = (80, 57, 35, 255)
LEG_HI = (128, 98, 62, 255)
ANT = (94, 64, 38, 255)
ANT_HI = (142, 106, 68, 255)

CX = 32.0

# 身体轮廓：y -> 半宽（上 = 尾尖，下 = 颈部）
BODY = (
    (8, 0.9), (10, 1.8), (12, 3.2), (15, 5.0), (18, 6.6), (22, 7.8), (26, 8.3),
    (30, 8.1), (34, 7.4), (36, 7.0), (37, 6.7),
    (38, 8.0), (40, 9.0), (42, 9.2), (44, 8.8), (46, 7.2), (47, 5.4),
)
HEAD_ROWS = ((47, 4.6), (48, 4.8), (49, 4.6), (50, 4.2), (51, 3.6), (52, 2.6), (53, 1.4))

# 腿：根部 y、大腿角（左）、膝盖转角（左）、大腿长、小腿长
LEGS = (
    (43.0, 2.15, -0.40, 6.0, 8.0),   # 前
    (38.0, 2.92, 0.16, 7.0, 8.5),    # 中
    (28.0, 3.85, 0.46, 8.0, 10.0),   # 后
)
# 三角步态：左前 / 右中 / 左后 同相，另外三条反相
LEG_PHASE = {(0, -1): 0.0, (0, 1): math.pi,
             (1, -1): math.pi, (1, 1): 0.0,
             (2, -1): 0.0, (2, 1): math.pi}

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


def line(x0, y0, x1, y1, color, thick=1):
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    for i in range(steps + 1):
        t = i / float(steps)
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        put(x, y, color)
        if thick >= 2:
            put(x, y + 1, color)


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


def draw_leg(idx, side, swing):
    """一条腿：根部藏在身体下，膝盖折一下，胫节带两根小刺，末端一小节跗节。"""
    cox_y, ang, turn, femur, tibia = LEGS[idx]
    a = ang + swing if side < 0 else (math.pi - ang) + swing
    cox_x = CX + side * (body_hw(cox_y) - 1.5)

    kx = cox_x + math.cos(a) * femur
    ky = cox_y + math.sin(a) * femur

    b = a + (turn if side < 0 else -turn)
    fx = kx + math.cos(b) * tibia
    fy = ky + math.sin(b) * tibia

    # 大腿：2px，上缘提亮，末端一个关节疙瘩
    line(cox_x, cox_y, kx, ky, LEG, 2)
    for t in (0.25, 0.5, 0.75):
        put(cox_x + (kx - cox_x) * t, cox_y + (ky - cox_y) * t - 0.9, LEG_HI)
    # 关节：2x2 一小块，腿才不会在膝盖处断开
    put(kx, ky, LEG_HI)
    put(kx, ky + 1, LEG)
    put(kx + 0.6, ky, LEG)
    put(kx + 0.6, ky + 1, LEG)

    # 胫节：也是 2px，末端再收一截 1px
    line(kx, ky, kx + (fx - kx) * 0.62, ky + (fy - ky) * 0.62, LEG, 2)
    line(kx + (fx - kx) * 0.62, ky + (fy - ky) * 0.62, fx, fy, LEG, 1)

    # 胫节小刺
    px, py = -math.sin(b), math.cos(b)
    for t in (0.45, 0.72):
        sx = kx + (fx - kx) * t
        sy = ky + (fy - ky) * t
        line(sx, sy, sx + px * 2.0, sy + py * 2.0, LEG, 1)

    c = b + 0.5 * (1 if side > 0 else -1)
    put(fx, fy, LEG_HI)
    put(fx + math.cos(c) * 2.0, fy + math.sin(c) * 2.0, LEG)


def draw_cerci():
    for s in (-1, 1):
        line(CX + s * 1.4, 11.0, CX + s * 3.2, 7.6, LEG)
        put(CX + s * 3.2, 7.0, LEG_HI)


def antenna_points(side, frame):
    """触角：二次贝塞尔，末端直接跑出画布下沿。"""
    t = math.tau * frame / FRAMES
    sway = math.sin(t + 0.6 + (0.0 if side < 0 else 1.2)) * 1.8
    x0, y0 = CX + side * 2.2, 53.0
    x1, y1 = CX + side * (16.0 + sway * 0.4), 60.0
    x2, y2 = CX + side * (32.0 + sway), 71.0
    pts = []
    n = 34
    for i in range(n + 1):
        u = i / float(n)
        x = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * x1 + u * u * x2
        y = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * y1 + u * u * y2
        pts.append((x, y))
    return pts


def draw_antenna(side, frame):
    pts = antenna_points(side, frame)
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        u = i / float(n - 1)
        put(x, y, ANT)
        # 根部两像素宽一点，往尖端收成 1px
        if u < 0.34:
            put(x + side * 1.0, y, ANT)
            if i % 4 == 0:
                put(x, y - 1, ANT_HI)
        elif i % 7 == 3:
            put(x - side * 1.0, y, ANT)


def draw_wings():
    for y in range(8, 38):
        hw = body_hw(y) - 0.5
        left = int(round(CX - hw))
        right = int(round(CX + hw))
        for x in range(left, right + 1):
            if x == 32:
                c = WING_EDGE
            else:
                if x < 32:
                    q = (31 - x) / max(1.0, (31 - left))
                else:
                    q = (x - 33) / max(1.0, (right - 33))
                if q < 0.05:
                    c = WING_HI
                elif q < 0.30:
                    c = WING
                elif q < 0.62:
                    c = WING_MID
                elif q < 0.86:
                    c = WING_DARK
                else:
                    c = WING_EDGE
            put_hard(x, y, c)

    # 翅尖（尾端）压暗
    for y in (8, 9, 10):
        for x in range(int(CX - body_hw(y)), int(CX + body_hw(y)) + 1):
            put_hard(x, y, WING_DARK)

    # 反光斑：贴内缘、偏前，不整齐的两小块
    for (px, py) in ((29, 19), (30, 20), (30, 21), (29, 21), (30, 22),
                     (34, 18), (35, 19), (35, 20)):
        put_hard(px, py, WING_SHEEN)


def draw_pronotum():
    """前胸背板：盖住翅膀根部的一块近椭圆盾片，前缘一道亮边。"""
    for y in range(37, 49):
        hw = body_hw(y)
        left = int(round(CX - hw))
        right = int(round(CX + hw))
        for x in range(left, right + 1):
            ad = abs(x - CX) / max(1.0, hw)
            if y <= 39:
                c = PRO_DARK if ad > 0.55 else PRO
            elif ad > 0.86:
                c = PRO_DARK
            elif ad > 0.62:
                c = PRO
            elif ad < 0.24:
                c = PRO_HI
            else:
                c = PRO
            put_hard(x, y, c)

    # 前缘（靠近头）一道亮边，盾片才有厚度
    for x in range(int(CX - body_hw(45) + 1), int(CX + body_hw(45)) + 1):
        put_hard(x, 45, PRO_RIM if abs(x - CX) < 3.5 else PRO_HI)

    # 两片暗斑：破一下中间那块平色
    for s, y0, y1 in ((-1, 40, 44), (1, 41, 45)):
        for y in range(y0, y1):
            put_hard(CX + s * 3.2, y, PRO_DARK)


def draw_head():
    for y in range(47, 54):
        hw = head_hw(y)
        for x in range(int(CX - hw), int(CX + hw) + 1):
            d = (x - CX) / max(1.0, hw)
            c = HEAD if abs(d) < 0.5 else HEAD_DARK
            put_hard(x, y, c)

    # 复眼：前侧方两颗小暗块
    for s in (-1, 1):
        ex = CX + s * 3.6
        for dy in (50, 51):
            put_hard(ex, dy, EYE)
            put_hard(ex + s, dy, EYE)
        put_hard(ex + s * 0.5, 50, EYE_HI)

    # 唇基 + 下颚须
    for x in (31, 32):
        put_hard(x, 52, HEAD)
        put(x, 54, ANT)


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


def build(frame):
    global canvas, solid, hard
    canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
    solid = [[False] * W for _ in range(H)]
    hard = [[False] * W for _ in range(H)]

    t = math.tau * frame / FRAMES

    # 后腿在下、前腿在上
    for idx, side in ((2, -1), (2, 1), (1, -1), (1, 1), (0, -1), (0, 1)):
        swing = 0.14 * math.sin(t + LEG_PHASE[(idx, side)])
        draw_leg(idx, side, swing)

    draw_cerci()
    draw_wings()
    draw_pronotum()
    draw_head()
    draw_antenna(-1, frame)
    draw_antenna(1, frame)
    draw_outline()
    return canvas


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for frame in range(FRAMES):
        write_png(os.path.join(OUT_DIR, f"cockroach_walk_{frame:02d}.png"), W, H, build(frame))
    print("wrote", FRAMES, "frames to", OUT_DIR)


if __name__ == "__main__":
    main()

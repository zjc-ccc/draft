"""生成 assets/characters/spider/export/spider_<方向>_00..11.png

32x32 蜘蛛，俯视，先按「朝上」绘制，再旋转 90/180/270 度得到四个方向。
12 帧交替四足步态：L1/L3/R2/R4 与 L2/L4/R1/R3 两组交替。
两只大蓝眼睛始终在头部前端。

用法: python tools/art/spider.py
"""

import math
import os

from png_util import write_png

W = H = 32
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "assets", "characters", "spider", "export")

FRAMES = 12
CX = 16.0
HEAD_Y = 12.0
ABDO_Y = 22.2
HEAD_RX, HEAD_RY = 5.8, 4.6
ABDO_RX, ABDO_RY = 7.0, 7.4

BODY = (78, 60, 102, 255)
BODY_HI = (112, 90, 142, 255)
BODY_DARK = (54, 40, 72, 255)
PATTERN = (138, 114, 170, 255)
LEG = (120, 98, 150, 255)
LEG_HI = (170, 148, 198, 255)
OUTLINE = (20, 14, 28, 255)

EYE_RIM = (12, 22, 40, 255)
EYE_DEEP = (44, 146, 212, 255)
EYE = (104, 216, 255, 255)
EYE_HI = (236, 252, 255, 255)

# 每条腿：挂点、膝盖、脚尖（朝上时的坐标，左半侧）
# 膝盖比挂点和脚尖更靠内/外，形成明显的折角
LEGS_LEFT = (
    ((11.4, 10.0), (8.4, 7.4), (4.8, 4.4)),
    ((10.6, 12.4), (6.4, 11.2), (1.8, 12.6)),
    ((10.6, 15.0), (6.4, 16.4), (1.8, 15.6)),
    ((11.4, 17.0), (8.0, 20.6), (4.4, 24.2)),
)

# 交替步态：True = 第一组，False = 第二组
GAIT = (
    (True, False, True, False),    # 左 1-4
    (False, True, False, True),    # 右 1-4
)

# 5x5 眼睛图案：R 深框、D 深蓝、B 亮蓝
EYE_PATTERN = (
    ".RRR.",
    "RDDDR",
    "RDBDR",
    "RDDDR",
    ".RRR.",
)


def blank():
    return [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]


def draw_spider(phase):
    canvas = blank()
    body = [[False] * W for _ in range(H)]

    def put(x, y, color):
        if 0 <= x < W and 0 <= y < H:
            canvas[y][x] = color

    def line(x0, y0, x1, y1, color, b0=1, b1=1):
        steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for i in range(steps + 1):
            u = i / steps
            x = int(round(x0 + (x1 - x0) * u))
            y = int(round(y0 + (y1 - y0) * u))
            b = max(1, int(round(b0 + (b1 - b0) * u)))
            for bx in range(b):
                for by in range(b):
                    put(x + bx, y + by, color)

    # 身体轻微上下浮动
    bob = round(0.5 * math.sin(phase * 2))

    # --- 腿（先画，身体盖住根部） ---
    for side, sign in ((0, -1.0), (1, 1.0)):
        for i, (attach, knee, foot) in enumerate(LEGS_LEFT):
            group_phase = phase + (0.0 if GAIT[side][i] else math.pi)
            swing = math.sin(group_phase)
            lift = max(0.0, math.cos(group_phase))

            def mirror(p):
                return (CX + sign * (p[0] - CX), p[1])

            ax, ay = mirror(attach)
            kx, ky = mirror(knee)
            fx, fy = mirror(foot)

            # 迈步沿行进方向摆动（朝上 = y 减小），抬腿时往回收一点
            fy += swing * 2.2
            ky += swing * 1.1
            fx += lift * 1.3 * sign * -1.0
            kx += lift * 0.7 * sign * -1.0

            ay += bob
            ky += bob
            fy += bob

            line(ax, ay, kx, ky, LEG, b0=2, b1=2)
            line(kx, ky, fx, fy, LEG, b0=2, b1=1)
            put(int(round(kx)), int(round(ky)), LEG_HI)

    # --- 身体：头胸部 + 腹部合成一个整体，统一打光，避免接缝 ---
    for y in range(H):
        for x in range(W):
            dxh = (x - CX) / HEAD_RX
            dyh = (y - (HEAD_Y + bob)) / HEAD_RY
            dxa = (x - CX) / ABDO_RX
            dya = (y - (ABDO_Y + bob)) / ABDO_RY
            if dxh * dxh + dyh * dyh <= 1.0 or dxa * dxa + dya * dya <= 1.0:
                body[y][x] = True

    top = HEAD_Y + bob - HEAD_RY
    bottom = ABDO_Y + bob + ABDO_RY
    for y in range(H):
        for x in range(W):
            if not body[y][x]:
                continue
            t = (y - top) / (bottom - top)
            if t < 0.2:
                color = BODY_HI
            elif t < 0.58:
                color = BODY
            else:
                color = BODY_DARK
            put(x, y, color)

    # 腹部花纹：一道浅浅的人字形
    for dx in (-2, -1, 0, 1, 2):
        px = int(round(CX + dx))
        py = int(round(ABDO_Y + bob - 2 + abs(dx) * 0.6))
        if 0 <= px < W and 0 <= py < H and body[py][px]:
            put(px, py, PATTERN)

    # --- 身体描边（只描身体外缘，不破坏腿） ---
    for y in range(H):
        for x in range(W):
            if body[y][x] or canvas[y][x][3] != 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and body[ny][nx]:
                    canvas[y][x] = OUTLINE
                    break

    # --- 两只大蓝眼睛 ---
    colors = {"R": EYE_RIM, "D": EYE_DEEP, "B": EYE}
    for ex in (CX - 3.0, CX + 3.0):
        ox = int(round(ex)) - 2
        oy = int(round(HEAD_Y + bob - 0.4)) - 2
        for row, pattern in enumerate(EYE_PATTERN):
            for col, ch in enumerate(pattern):
                if ch in colors:
                    put(ox + col, oy + row, colors[ch])
        put(ox + 1, oy + 1, EYE_HI)

    return canvas


def rotate_cw(canvas):
    return [[canvas[H - 1 - x][y] for x in range(W)] for y in range(H)]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    directions = ("up", "right", "down", "left")
    for i in range(FRAMES):
        base = draw_spider(2 * math.pi * i / FRAMES)
        for turns, name in enumerate(directions):
            canvas = base
            for _ in range(turns):
                canvas = rotate_cw(canvas)
            path = os.path.join(OUT_DIR, f"spider_{name}_{i:02d}.png")
            write_png(path, W, H, canvas)
    print("wrote", len(directions) * FRAMES, "frames to", OUT_DIR)


if __name__ == "__main__":
    main()

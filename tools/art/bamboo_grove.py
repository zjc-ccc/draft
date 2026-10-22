"""生成 assets/props/bamboo-grove/export/bamboo-grove_sway_00..07.png

96x160 一小片竹林：6 根成熟的青竹，底部在土堆里挤在一起、笔直往上，
越高越各自朝外散开，每根顶上都有竹叶。土堆上有草和落叶。

8 帧 @ 6fps：竹梢随风轻摆，土堆和竹根不动，循环无缝。

用法: python tools/art/bamboo_grove.py
"""

import math
import os

from png_util import write_png

W, H = 96, 160
FRAMES = 8
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "assets", "props", "bamboo-grove", "export")

INK = (24, 30, 18, 255)

BAMBOO_HI = (170, 200, 110, 255)
BAMBOO = (126, 162, 76, 255)
BAMBOO_MID = (96, 132, 56, 255)
BAMBOO_DARK = (68, 98, 42, 255)
BAMBOO_EDGE = (44, 66, 30, 255)
NODE_RING = (198, 210, 142, 255)

LEAF_HI = (150, 190, 90, 255)
LEAF = (110, 152, 68, 255)
LEAF_DARK = (72, 108, 46, 255)
LEAF_EDGE = (50, 80, 36, 255)

LEAF_DRY = (156, 148, 76, 255)
LEAF_DRY_DARK = (118, 108, 58, 255)

SOIL = (86, 66, 48, 255)
SOIL_HI = (110, 88, 64, 255)
SOIL_DARK = (58, 44, 32, 255)
GRASS = (100, 134, 62, 255)

# bx, by   竹根（会被土堆盖住）
# tx, ty   竹梢
# w        竹竿粗细
# curve    越大底部越直、越高越往外弯
# phase    摇摆相位
# tone     明度系数（靠后的竹子压暗一点）
STALKS = (
    (41, 154, 15, 34, 3, 2.6, 1.10, 0.74),
    (44, 153, 23, 22, 4, 2.4, 0.40, 0.84),
    (62, 154, 77, 38, 4, 2.5, 4.00, 0.84),
    (59, 153, 66, 18, 5, 2.2, 3.10, 0.94),
    (47, 152, 32, 14, 6, 2.2, 0.00, 1.00),
    (53, 152, 50, 8, 5, 2.0, 2.00, 1.00),
)

DRAW_ORDER = (0, 1, 2, 3, 4, 5)

SWAY_AMP = 1.6

MOUND_CX, MOUND_CY = 52.0, 160.0
MOUND_RX, MOUND_RY = 26.0, 13.0

canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
solid = [[False] * W for _ in range(H)]
hard = [[False] * W for _ in range(H)]


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        canvas[y][x] = color


def tone(color, f):
    return (
        max(0, min(255, int(round(color[0] * f)))),
        max(0, min(255, int(round(color[1] * f)))),
        max(0, min(255, int(round(color[2] * f)))),
        255,
    )


def sway(t, frame, phase):
    """t=0 在竹根（不动），t=1 在竹梢（摆得最多）。"""
    a = math.tau * frame / FRAMES
    return SWAY_AMP * (t ** 2) * math.sin(a + phase + t * 1.2)


def stalk_center(bx, tx, t, curve, frame, phase):
    x = bx + (tx - bx) * (t ** curve)
    return x + sway(t, frame, phase)


def ww_at(t, w):
    return max(2, w - int(round(t * (w - 2) * 0.45)))


def draw_stalk(bx, by, tx, ty, w, curve, phase, f, frame):
    """一根竹子：一段段往上画，越往上越细，隔一段一个竹节。"""
    hi = tone(BAMBOO_HI, f)
    base = tone(BAMBOO, f)
    mid = tone(BAMBOO_MID, f)
    dark = tone(BAMBOO_DARK, f)
    edge = tone(BAMBOO_EDGE, f)
    ring = tone(NODE_RING, f)

    node_ts = [0.07 + i * 0.105 for i in range(9) if 0.07 + i * 0.105 < 0.97]

    for y in range(ty, by + 1):
        t = (by - y) / float(by - ty)
        t = max(0.0, min(1.0, t))
        cx = stalk_center(bx, tx, t, curve, frame, phase)
        ww = ww_at(t, w)
        if t > 0.90:
            ww = max(1, ww - 2)

        near_node = any(abs(t - nt) < 0.012 for nt in node_ts)
        if near_node:
            ww = max(2, ww - 1)

        left = int(round(cx - ww / 2.0))
        for i in range(ww):
            x = left + i
            if not (0 <= x < W):
                continue
            if i == 0:
                c = hi
            elif i == ww - 1:
                c = dark if ww > 3 else mid
            elif i == ww - 2 and ww >= 4:
                c = mid
            else:
                c = base
            if near_node:
                c = ring if (y + 1) % 2 == 0 else edge
            put(x, y, c)
            solid[y][x] = True
            hard[y][x] = True


def draw_stalk_leaves(bx, by, tx, ty, w, curve, phase, f, frame):
    """每根三丛侧叶 + 梢头一丛，竹竿尖不会光秃秃。"""
    outward = 1 if tx >= bx else -1
    clumps = ((0.58, -outward, 3, 14),
              (0.69, outward, 3, 15),
              (0.80, -outward, 3, 15),
              (0.90, outward, 3, 14))
    t_off = ((phase * 7) % 1.0 - 0.5) * 0.05
    for t_anchor, side, count, length in clumps:
        t_use = max(0.2, min(0.98, t_anchor + t_off))
        ax = stalk_center(bx, tx, t_use, curve, frame, phase)
        ay = by + (ty - by) * t_use
        ax += side * (ww_at(t_use, w) / 2.0)
        draw_leaf_clump(ax, ay, side, count, length, f)

    ax = stalk_center(bx, tx, 1.0, curve, frame, phase)
    draw_leaf_clump(ax, ty + 2, outward, 4, 13, f, tip=True)


def draw_leaf_clump(x, y, side, count, length, f, tip=False):
    """一丛竹叶：短枝朝外斜下，叶子沿枝一片片垂下来，近乎平行。"""
    s = 1 if side > 0 else -1
    if tip:
        stem_ang = 0.15 if s > 0 else math.pi - 0.15
        leaf_ang = 0.70 if s > 0 else math.pi - 0.70
    else:
        stem_ang = 0.40 if s > 0 else math.pi - 0.40
        leaf_ang = 0.95 if s > 0 else math.pi - 0.95

    col = tone(LEAF, f)
    hi = tone(LEAF_HI, f)
    dark = tone(LEAF_DARK, f)

    for i in range(count):
        j = i - (count - 1) / 2.0
        sx = x + math.cos(stem_ang) * (i * 4.0)
        sy = y + math.sin(stem_ang) * (i * 4.0) + 1
        ang = leaf_ang + j * 0.15 * s
        ln = length - abs(j) * 2.6
        leaf(sx, sy, ang, ln, col, hi, dark)


def _stamp_leaf(x0, y0, ang, length, pad, pick):
    """按梭形范围铺像素；pick(t, off, hw, ux) 返回颜色。"""
    ux = math.cos(ang)
    uy = math.sin(ang)
    x1 = x0 + ux * length
    y1 = y0 + uy * length
    x_lo = int(math.floor(min(x0, x1))) - 3
    x_hi = int(math.ceil(max(x0, x1))) + 3
    y_lo = int(math.floor(min(y0, y1))) - 3
    y_hi = int(math.ceil(max(y0, y1))) + 3

    for py in range(y_lo, y_hi + 1):
        for px in range(x_lo, x_hi + 1):
            if not (0 <= px < W and 0 <= py < H):
                continue
            vx = px + 0.5 - x0
            vy = py + 0.5 - y0
            t = (vx * ux + vy * uy) / length
            if t < 0.0 or t > 1.0:
                continue
            off = vx * (-uy) + vy * ux
            hw = 1.02 * math.sin(math.pi * t) ** 0.75 + pad
            if abs(off) > hw:
                continue
            put(px, py, pick(t, off, hw, ux))
            solid[py][px] = True


def leaf(x0, y0, ang, length, col, hi, dark):
    """一片竹叶：细长的梭形，上半边提亮、下缘压一道暗边、叶尖再暗一点。"""
    length = max(3, int(round(length)))

    def pick(t, off, hw, ux):
        if abs(ux) < 0.25:
            upper = off < 0
        else:
            upper = off * ux < 0
        if t > 0.88:
            return dark
        return hi if upper else col

    _stamp_leaf(x0, y0, ang, length, 0.0, pick)


def draw_mound():
    for y in range(int(MOUND_CY - MOUND_RY), H):
        for x in range(int(MOUND_CX - MOUND_RX), int(MOUND_CX + MOUND_RX) + 1):
            dx = (x + 0.5 - MOUND_CX) / MOUND_RX
            dy = (y + 0.5 - MOUND_CY) / MOUND_RY
            if dx * dx + dy * dy > 1.0:
                continue
            if y < 148:
                c = SOIL_HI
            elif y < 152:
                c = SOIL
            else:
                c = SOIL_DARK
            if (x * 7 + y * 3) % 11 == 0 and y < 152:
                c = SOIL_DARK
            put(x, y, c)
            solid[y][x] = True
            hard[y][x] = True

    # 草
    for gx, gh in ((33, 4), (37, 6), (44, 3), (57, 5), (63, 4), (69, 6), (73, 3)):
        base_y = 146
        while base_y < H - 1 and not solid[base_y][gx]:
            base_y += 1
        for i in range(gh):
            bx2 = gx + (0 if i < gh // 2 + 1 else 1)
            py = base_y - i - 1
            if 0 <= py < H and 0 <= bx2 < W:
                put(bx2, py, GRASS)
                solid[py][bx2] = True
        if 0 <= base_y - gh < H:
            put(gx, base_y - gh, tone(LEAF_HI, 0.9))

    # 落叶
    for lx, ly, ang, ln, dry in ((38, 152, 0.15, 4, True), (46, 155, -0.2, 3, False),
                                 (58, 153, 0.1, 4, True), (64, 156, 0.25, 3, True),
                                 (50, 150, -0.1, 3, False), (70, 151, 0.2, 3, True)):
        for i in range(ln):
            px = int(round(lx + math.cos(ang) * i))
            py = int(round(ly + math.sin(ang) * i))
            if 0 <= px < W and 0 <= py < H and solid[py][px]:
                put(px, py, LEAF_DRY if dry else LEAF_DARK)
                if i == 1:
                    put(px, py - 1, LEAF_DRY_DARK if dry else tone(LEAF, 0.9))


def draw_outline():
    """竹竿/土堆描黑边，竹叶只描一圈暗绿，免得叶子被黑边吃掉。"""
    for y in range(H):
        for x in range(W):
            if solid[y][x]:
                continue
            touch_hard = False
            touch_leaf = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < W and 0 <= ny < H):
                    continue
                if hard[ny][nx]:
                    touch_hard = True
                    break
                if solid[ny][nx]:
                    touch_leaf = True
            if touch_hard:
                canvas[y][x] = INK
            elif touch_leaf:
                canvas[y][x] = LEAF_EDGE


def build(frame):
    global canvas, solid, hard
    canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
    solid = [[False] * W for _ in range(H)]
    hard = [[False] * W for _ in range(H)]

    for idx in DRAW_ORDER:
        bx, by, tx, ty, w, curve, phase, f = STALKS[idx]
        draw_stalk(bx, by, tx, ty, w, curve, phase, f, frame)
        draw_stalk_leaves(bx, by, tx, ty, w, curve, phase, f, frame)

    draw_mound()
    draw_outline()
    return canvas


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for frame in range(FRAMES):
        write_png(os.path.join(OUT_DIR, f"bamboo-grove_sway_{frame:02d}.png"), W, H, build(frame))
    print("wrote", FRAMES, "frames to", OUT_DIR)


if __name__ == "__main__":
    main()

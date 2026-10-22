"""生成 assets/props/pendant-lamp/export/ 下的：

- pendant-lamp_off_00.png     关灯，1 帧
- pendant-lamp_on_00..07.png  开灯，8 帧（灯泡亮度轻微呼吸）
- pendant-lamp_glow_00.png    96x96 叠加用暖光晕（引擎里 Additive 叠在灯泡位置）

64x128 复古吊灯：顶部吸顶盘 + 长长的一根电线 + 黄铜锥形灯罩，
灯罩下面露出一颗灯泡。灯罩有氧化斑和划痕，灯口内壁有点积灰。

用法: python tools/art/pendant_lamp.py
"""

import math
import os

from png_util import write_png

W, H = 64, 128
ON_FRAMES = 8
GLOW_SIZE = 96

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "assets", "props", "pendant-lamp", "export")

INK = (26, 19, 14, 255)

BRASS_HI = (226, 186, 118, 255)
BRASS = (180, 138, 76, 255)
BRASS_MID = (148, 108, 56, 255)
BRASS_DARK = (106, 74, 40, 255)
BRASS_SHADE = (70, 47, 27, 255)

PATINA = (94, 100, 66, 255)
PATINA_DARK = (72, 76, 50, 255)

CORD = (44, 32, 25, 255)
CORD_HI = (62, 46, 35, 255)

GLASS = (162, 152, 130, 255)
GLASS_HI = (208, 200, 178, 255)
GLASS_DARK = (116, 108, 90, 255)
FILAMENT_OFF = (96, 88, 72, 255)

BULB_WHITE = (255, 248, 220, 255)
BULB_WARM = (252, 214, 132, 255)
BULB_AMBER = (236, 172, 88, 255)
BULB_EDGE = (198, 134, 64, 255)

DUST = (176, 168, 148, 255)

CANOPY_TOP, CANOPY_BOTTOM = 2, 9
CORD_TOP, CORD_BOTTOM = 9, 72
SOCKET_TOP, SOCKET_BOTTOM = 70, 86
SHADE_TOP, SHADE_BOTTOM = 84, 112
BULB_CX, BULB_CY, BULB_R = 32.0, 118.0, 5.2

# 8 帧的亮度：整体很稳，只有一处轻轻一沉，像老灯泡
LEVELS = (1.00, 0.96, 0.92, 0.95, 0.99, 1.00, 0.90, 0.95)

canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
solid = [[False] * W for _ in range(H)]
soft = set()

rng_state = 7


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


BRASS_RAMP = (BRASS_SHADE, BRASS_DARK, BRASS_MID, BRASS, BRASS_HI)

BAYER = (
    (0, 8, 2, 10),
    (12, 4, 14, 6),
    (3, 11, 1, 9),
    (15, 7, 13, 5),
)


def ramp_color(b, x, y):
    """把 0~1 的亮度映射到 5 级黄铜色阶（不用抖动，硬边更像黄铜）。"""
    v = max(0.0, min(1.0, b)) * (len(BRASS_RAMP) - 1)
    i = int(round(v))
    return BRASS_RAMP[min(i, len(BRASS_RAMP) - 1)]


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
    return 6.5 + 12.0 * (t ** 1.3)


def draw_canopy():
    pts = rrect(25, CANOPY_TOP, 38, CANOPY_BOTTOM, (2, 2, 1, 1), BRASS)
    for x, y in pts:
        if y <= CANOPY_TOP + 1:
            canvas[y][x] = BRASS_HI
        elif y == CANOPY_BOTTOM:
            canvas[y][x] = BRASS_DARK
        elif y == CANOPY_BOTTOM - 1:
            canvas[y][x] = BRASS_MID
    # 吸顶盘下面的小接头
    for y in range(CANOPY_BOTTOM + 1, CANOPY_BOTTOM + 4):
        for x in (30, 31, 32, 33):
            put(x, y, BRASS_DARK if x >= 32 else BRASS_MID)
            solid[y][x] = True
            soft.add((x, y))
    put(31, CANOPY_BOTTOM + 2, BRASS_HI)


def draw_cord():
    for y in range(CORD_TOP, CORD_BOTTOM + 1):
        put(32, y, CORD)
        solid[y][32] = True
        soft.add((32, y))
    # 每隔一段一根细绞纹
    for y in range(CORD_TOP + 4, CORD_BOTTOM, 11):
        put(32, y, CORD_HI)


def draw_socket():
    pts = rrect(28, SOCKET_TOP, 36, SOCKET_BOTTOM, (2, 2, 1, 1), BRASS_MID)
    for x, y in pts:
        if x <= 29:
            canvas[y][x] = BRASS
        elif x >= 35:
            canvas[y][x] = BRASS_DARK
        if y == SOCKET_TOP:
            canvas[y][x] = BRASS_HI
    # 灯罩上沿的卡圈
    for y in (SOCKET_BOTTOM - 3, SOCKET_BOTTOM - 2):
        for x in range(26, 39):
            put(x, y, BRASS_DARK if y == SOCKET_BOTTOM - 2 else BRASS)
            solid[y][x] = True


def draw_bulb(level):
    """灯泡：level 为 None 表示关灯，否则是 0~1 的亮度。"""
    # 灯头（黄铜，大部分被灯罩挡住）
    rrect(29, 106, 35, 114, (1, 1, 1, 1), BRASS_DARK)

    on = level is not None
    for y in range(int(BULB_CY - BULB_R) - 1, int(BULB_CY + BULB_R) + 2):
        for x in range(int(BULB_CX - BULB_R) - 1, int(BULB_CX + BULB_R) + 2):
            dx = x + 0.5 - BULB_CX
            dy = y + 0.5 - BULB_CY
            d = math.hypot(dx, dy)
            if d > BULB_R:
                continue

            if on:
                k = level
                if d <= 2.6:
                    base = mix(BULB_AMBER, BULB_WHITE, k)
                elif d <= 4.2:
                    base = mix(BULB_AMBER, BULB_WARM, (d - 2.6) / 1.6 * 0.7 + k * 0.3)
                else:
                    base = mix(BULB_EDGE, BULB_AMBER, max(0.0, 1.0 - (d - 4.2) / 1.2) * k)
            else:
                base = GLASS
                if d > BULB_R - 1.0:
                    base = GLASS_DARK
                elif dy < -1.0 and dx < -0.5:
                    base = GLASS_HI
                elif dy > 2.0:
                    base = GLASS_DARK

            put(x, y, base)
            solid[y][x] = True

    # 左上高光
    if on:
        put(int(BULB_CX) - 2, int(BULB_CY) - 3, BULB_WHITE)
        put(int(BULB_CX) - 3, int(BULB_CY) - 2, BULB_WHITE)
    else:
        put(int(BULB_CX) - 2, int(BULB_CY) - 3, GLASS_HI)
        put(int(BULB_CX) - 3, int(BULB_CY) - 2, GLASS_HI)

    # 灯丝：一小段折线
    fil = BULB_WHITE if on else FILAMENT_OFF
    for x, y in ((31, 116), (32, 117), (33, 118), (32, 119), (31, 120)):
        if solid[y][x]:
            put(x, y, fil)
    if on:
        put(32, 118, BULB_WHITE)
        put(31, 118, mix(BULB_WHITE, BULB_WARM, 0.4))


def draw_shade(level):
    """黄铜锥形灯罩：左亮右暗，平滑过渡 + 抖动，底沿一道卷边。"""
    on = level is not None
    for y in range(SHADE_TOP, SHADE_BOTTOM + 1):
        half = shade_half(y)
        for x in range(int(round(BULB_CX - half)), int(round(BULB_CX + half)) + 1):
            u = (x + 0.5 - BULB_CX) / half
            b = 0.55 - 0.35 * u
            b += 0.22 * math.exp(-(((u + 0.45) / 0.30) ** 2))
            put(x, y, ramp_color(b, x, y))
            solid[y][x] = True

    # 上沿
    for x in range(int(round(BULB_CX - shade_half(SHADE_TOP))), int(round(BULB_CX + shade_half(SHADE_TOP))) + 1):
        put(x, SHADE_TOP, BRASS_MID)
        put(x, SHADE_TOP + 1, BRASS)
    # 中段一道接缝
    seam_y = SHADE_TOP + 12
    for x in range(int(round(BULB_CX - shade_half(seam_y))), int(round(BULB_CX + shade_half(seam_y))) + 1):
        if solid[seam_y][x]:
            put(x, seam_y, BRASS_DARK)
            if solid[seam_y + 1][x]:
                put(x, seam_y + 1, BRASS_HI if (x + seam_y) % 5 else BRASS)

    # 底沿卷边
    for y in (SHADE_BOTTOM - 2, SHADE_BOTTOM - 1, SHADE_BOTTOM):
        half = shade_half(SHADE_BOTTOM)
        for x in range(int(round(BULB_CX - half)), int(round(BULB_CX + half)) + 1):
            if not solid[y][x]:
                continue
            if y == SHADE_BOTTOM - 2:
                put(x, y, BRASS_HI)
            elif y == SHADE_BOTTOM - 1:
                put(x, y, BRASS)
            else:
                put(x, y, BRASS_SHADE)
            # 灯亮时内壁被照暖
            if on and y >= SHADE_BOTTOM - 2 and abs(x + 0.5 - BULB_CX) < half - 2:
                put(x, y, mix(canvas[y][x], BULB_WARM, 0.45 * level))

    # 氧化斑（跟底色混一下，别像贴上去的色块）
    for cx, cy, r in ((43, 96, 2.0), (45, 103, 1.5), (23, 101, 1.3), (37, 90, 1.1)):
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                if not (0 <= x < W and 0 <= y < H) or not solid[y][x]:
                    continue
                if math.hypot(x - cx, y - cy) <= r and (x + y) % 3:
                    put(x, y, mix(canvas[y][x], PATINA if (x * 2 + y) % 3 else PATINA_DARK, 0.72))

    # 划痕
    for x, y in ((27, 93), (28, 93), (29, 94), (38, 107), (39, 107), (40, 108)):
        if solid[y][x]:
            put(x, y, BRASS_HI if (x + y) % 2 else BRASS_MID)


def draw_dust_and_outline():
    # 灯罩底沿和卷边上的灰
    for x in range(20, 45, 5):
        y = SHADE_BOTTOM - 2
        if solid[y][x]:
            put(x, y, DUST)
    # 吸顶盘上的灰
    for x in (27, 33, 36):
        if solid[CANOPY_TOP + 1][x]:
            put(x, CANOPY_TOP + 1, DUST)

    for y in range(H):
        for x in range(W):
            if solid[y][x]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and solid[ny][nx] and (nx, ny) not in soft:
                    canvas[y][x] = INK
                    break


def build(level):
    global canvas, solid, soft
    canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
    solid = [[False] * W for _ in range(H)]
    soft = set()

    draw_canopy()
    draw_cord()
    draw_socket()
    draw_bulb(level)
    draw_shade(level)
    draw_dust_and_outline()
    return canvas


def build_glow():
    """96x96 的暖光晕：中心最亮，往外平滑衰减（光效层不做抖动，叠上去才干净）。"""
    size = GLOW_SIZE
    c = (size - 1) / 2.0
    radius = size / 2.0 - 1.0
    glow = [[(0, 0, 0, 0) for _ in range(size)] for _ in range(size)]
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - c, y - c)
            if d > radius:
                continue
            f = max(0.0, 1.0 - d / radius) ** 2.2
            a = int(round(176 * f))
            if a <= 0:
                continue
            rgb = mix(BULB_WHITE, (255, 176, 92, 255), (d / radius) ** 0.8)
            glow[y][x] = (rgb[0], rgb[1], rgb[2], a)
    return glow


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    write_png(os.path.join(OUT_DIR, "pendant-lamp_off_00.png"), W, H, build(None))
    for i, level in enumerate(LEVELS):
        write_png(os.path.join(OUT_DIR, f"pendant-lamp_on_{i:02d}.png"), W, H, build(level))
    write_png(os.path.join(OUT_DIR, "pendant-lamp_glow_00.png"), GLOW_SIZE, GLOW_SIZE, build_glow())

    print("wrote 1 off + %d on + 1 glow to %s" % (ON_FRAMES, OUT_DIR))


if __name__ == "__main__":
    main()

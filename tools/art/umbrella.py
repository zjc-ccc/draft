"""生成 assets/props/umbrella/export/umbrella_open_00..07.png

48x64 像素雨伞，侧视直立：伞尖在上、伞柄在下。
8 帧描述从收起到完全打开的过程（t = 0 → 1）。

用法: python tools/art/umbrella.py
"""

import math
import os

from png_util import write_png

W, H = 48, 64
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "assets", "props", "umbrella", "export")

FRAMES = 8
CX = 23.5
TOP = 6
SHAFT_BOTTOM = 56

# 伞面：伞顶深、伞沿浅
TEAL = [
    (20, 56, 66, 255),
    (20, 72, 84, 255),
    (30, 106, 114, 255),
    (44, 144, 142, 255),
    (74, 184, 176, 255),
    (124, 216, 200, 255),
    (166, 240, 220, 255),
]

# 每片伞面的受光：左亮右暗
PANELS = (1.08, 1.06, 0.99, 0.91, 0.84)
RIB = (18, 58, 68, 255)

OUTLINE = (10, 26, 32, 255)
METAL = (186, 198, 200, 255)
METAL_DARK = (112, 126, 130, 255)
WOOD = (112, 74, 44, 255)
WOOD_LIGHT = (158, 112, 70, 255)


def shade(color, factor):
    return (
        max(0, min(255, int(color[0] * factor))),
        max(0, min(255, int(color[1] * factor))),
        max(0, min(255, int(color[2] * factor))),
        color[3],
    )


def render(t):
    canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]

    def put(x, y, color):
        if 0 <= x < W and 0 <= y < H:
            canvas[y][x] = color

    def get(x, y):
        if 0 <= x < W and 0 <= y < H:
            return canvas[y][x]
        return (0, 0, 0, 0)

    # --- 形状参数：随 t 从收起插值到打开 ---
    half = 5.0 + 15.0 * t
    rim_y = 28.0 - 7.0 * math.sqrt(t)
    power = 0.98 - 0.33 * math.sqrt(t)
    amp = 1.8 * t ** 0.35
    taper = 0.55 * (1.0 - math.sqrt(t))      # 收起时伞沿向伞杆收拢

    span = rim_y - TOP

    def half_width(y):
        s = (y - TOP) / span
        s = max(0.0, min(1.0, s))
        w = half * math.sin(math.pi / 2 * s) ** power
        # 收拢状态在伞沿处收细，避免变成喇叭
        w *= 1.0 - taper * s ** 3
        return w

    def rim_at(x):
        p = max(-1.0, min(1.0, (x - CX) / max(half, 0.001)))
        # 伞沿向两侧下垂，避免底部变成一条直线
        droop = 1.6 * t * abs(p) ** 2
        # 布面在两根伞骨之间下垂，形成扇贝边
        phase = (p + 1.0) / 2.0 * len(PANELS)
        scallop = 0.5 - 0.5 * math.cos(2 * math.pi * phase)
        return rim_y + droop + amp * scallop

    def ramp(s):
        s = max(0.0, min(1.0, s)) * (len(TEAL) - 1)
        i = int(s)
        f = s - i
        if i >= len(TEAL) - 1:
            return TEAL[-1]
        a, b = TEAL[i], TEAL[i + 1]
        return (
            int(a[0] + (b[0] - a[0]) * f),
            int(a[1] + (b[1] - a[1]) * f),
            int(a[2] + (b[2] - a[2]) * f),
            255,
        )

    # --- 伞杆（先画，伞面会盖住收起状态下的杆） ---
    for y in range(TOP, SHAFT_BOTTOM):
        put(23, y, METAL)
        put(24, y, METAL_DARK)

    # --- 伞面 ---
    for y in range(TOP, int(math.ceil(rim_y + amp + 2)) + 1):
        hw = half_width(y)
        if hw < 0.4:
            continue
        s = max(0.0, min(1.0, (y - TOP) / span))
        for x in range(int(round(CX - hw)), int(round(CX + hw)) + 1):
            if y > rim_at(x):
                continue
            color = ramp(s)
            if t > 0.02:
                p = (x - CX) / max(hw, 0.001)
                idx = max(0, min(len(PANELS) - 1, int((p + 1.0) / 2.0 * len(PANELS))))
                color = shade(color, PANELS[idx])
            put(x, y, color)

    # --- 伞骨：伞片交界处 ---
    if t > 0.2:
        for k in range(1, len(PANELS)):
            p = -1.0 + 2.0 * k / len(PANELS)
            for y in range(TOP + 2, int(rim_y) + 1):
                hw = half_width(y)
                if hw < 1.5:
                    continue
                x = int(round(CX + p * hw))
                if get(x, y)[3] != 0 and y <= rim_at(x):
                    put(x, y, RIB)

    # --- 收拢状态的折痕和束带 ---
    if t < 0.5:
        for off in (-0.58, -0.18, 0.22, 0.62):
            for y in range(TOP + 2, int(rim_y)):
                hw = half_width(y)
                x = int(round(CX + off * hw))
                if get(x, y)[3] != 0:
                    put(x, y, shade(get(x, y), 0.74))
        strap_y = int(TOP + span * 0.74)
        for x in range(int(CX - half_width(strap_y)) - 1, int(CX + half_width(strap_y)) + 2):
            if get(x, strap_y)[3] != 0:
                put(x, strap_y, (26, 66, 74, 255))

    # --- 伞骨末端的下巢 ---
    runner_y = int(round(rim_at(CX))) + 1
    for x in range(22, 26):
        put(x, runner_y, METAL if x < 25 else METAL_DARK)
        put(x, runner_y + 1, METAL_DARK)

    # --- 伞尖（上）：短尖 + 金属球 ---
    put(24, 2, METAL)
    for x in (23, 24):
        put(x, 3, METAL)
        put(x, 4, METAL_DARK if x == 24 else METAL)
    for x in range(22, 26):
        put(x, 5, METAL if x < 25 else METAL_DARK)

    # --- 伞柄：木质 J 形弯钩 ---
    hook_cx, hook_cy = 27.0, SHAFT_BOTTOM + 1.0
    for radius in (2.8, 3.4, 4.0, 4.6):
        for deg in range(-2, 182, 3):
            rad = math.radians(deg)
            x = int(round(hook_cx + radius * math.cos(rad)))
            y = int(round(hook_cy + radius * math.sin(rad)))
            put(x, y, WOOD_LIGHT if y <= hook_cy + 1.8 else WOOD)

    for y in range(SHAFT_BOTTOM - 1, int(hook_cy) + 1):
        put(23, y, WOOD)
        put(24, y, WOOD)

    # --- 描边 ---
    for y in range(H):
        for x in range(W):
            if canvas[y][x][3] == 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if get(x + dx, y + dy)[3] == 0:
                    canvas[y][x] = OUTLINE
                    break

    return canvas


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for i in range(FRAMES):
        t = i / (FRAMES - 1)
        path = os.path.join(OUT_DIR, f"umbrella_open_{i:02d}.png")
        write_png(path, W, H, render(t))
        print("wrote", path)


if __name__ == "__main__":
    main()

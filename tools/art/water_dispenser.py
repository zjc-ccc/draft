"""生成 assets/props/water-dispenser/export/water-dispenser_<档位>_00..07.png

48x80 饮水机，正面平视：
- 顶部倒插的桶装水，玻璃瓶身 + 蓝色水，水位分 5 档（100/75/50/25/0）
- 白色机身，红色热水口、蓝色冷水口，下方接水盘
- 每档 8 帧：桶里气泡上升，冷水口飘一缕冷气

画法：先画水桶（瓶颈伸到机身里），再画机身把瓶颈下半段盖住，
这样瓶颈看起来是插进卡座里的。

用法: python tools/art/water_dispenser.py
"""

import math
import os

from png_util import write_png

W, H = 48, 80
FRAMES = 8
CX = 23.5
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "assets", "props", "water-dispenser", "export")

LEVELS = (("level-100", 1.0), ("level-75", 0.75), ("level-50", 0.5), ("level-25", 0.25), ("level-0", 0.0))

# 玻璃
GLASS_FILL = (198, 228, 246, 72)
GLASS_EDGE = (146, 178, 202, 245)
GLASS_RIM = (216, 238, 250, 240)
GLASS_WET_EDGE = (136, 186, 220, 245)
GLASS_WET_RIM = (188, 224, 246, 245)
GLASS_SHINE = (255, 255, 255, 105)

# 水
WATER_HI = (104, 190, 236, 232)
WATER_TOP = (158, 220, 250, 238)
WATER = (80, 170, 228, 232)
WATER_DEEP = (54, 136, 202, 232)
BUBBLE = (230, 248, 255, 240)

# 机身
MACHINE = (222, 227, 234, 255)
MACHINE_HI = (244, 247, 251, 255)
MACHINE_DARK = (186, 194, 206, 255)
MACHINE_EDGE = (92, 100, 116, 255)
PLATE = (206, 212, 222, 255)
PLATE_EDGE = (168, 176, 190, 255)
NICHE = (170, 180, 194, 255)
NICHE_EDGE = (124, 132, 148, 255)
NICHE_SHADE = (148, 158, 174, 255)
TRAY = (128, 138, 154, 255)
TRAY_DARK = (104, 113, 128, 255)
TRAY_LIP = (158, 168, 184, 255)
VENT = (176, 184, 198, 255)
SPOUT = (146, 156, 172, 255)
LED = (104, 202, 126, 255)
COLLAR = (150, 158, 172, 255)
COLLAR_DARK = (116, 124, 140, 255)

HOT = (210, 76, 68, 255)
HOT_HI = (240, 128, 114, 255)
COLD = (72, 132, 214, 255)
COLD_HI = (132, 184, 240, 255)

MIST_A = (206, 236, 250, 175)
MIST_B = (202, 232, 248, 115)
MIST_C = (198, 230, 246, 60)

canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
machine_mask = [[False] * W for _ in range(H)]
interior = [[False] * W for _ in range(H)]


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        canvas[y][x] = color


def rect(x0, y0, x1, y1, color, mark=True):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(x, y, color)
            if mark and 0 <= x < W and 0 <= y < H:
                machine_mask[y][x] = True


def border(x0, y0, x1, y1, color):
    for x in range(x0, x1 + 1):
        put(x, y0, color)
        put(x, y1, color)
    for y in range(y0, y1 + 1):
        put(x0, y, color)
        put(x1, y, color)


def bottle_half_width(y):
    """瓶身半宽：上圆角 → 直筒 → 圆弧收肩 → 细瓶颈。"""
    if y < 2 or y > 31:
        return 0.0
    if y == 2:
        return 8.5
    if y == 3:
        return 9.6
    if y <= 19:
        return 10.5
    if y <= 26:
        t = (y - 19) / 7.0
        return 10.5 - 8.0 * (t ** 2.2)
    return 2.5


def row_span(y):
    hw = int(round(bottle_half_width(y)))
    if hw <= 0:
        return None
    return (int(round(CX - hw)), int(round(CX + hw)) - 1)


def wall_thickness(y):
    return 2 if y <= 24 else 1


def surface_y(fill):
    return 28.0 - fill * 25.5


BUBBLES = (
    (-6, 1, 0.00),
    (-3, 2, 0.35),
    (0, 1, 0.62),
    (3, 2, 0.14),
    (6, 1, 0.80),
    (-4, 1, 0.50),
)


def draw_bottle(fill, frame):
    top = surface_y(fill)
    surface = int(math.ceil(top)) if fill > 0.0 else 32

    # 玻璃底色：整只瓶子铺一层淡蓝，空瓶也能看出轮廓
    for y in range(2, 32):
        span = row_span(y)
        if span is None:
            continue
        for x in range(span[0], span[1] + 1):
            interior[y][x] = True
            put(x, y, GLASS_FILL)

    # 水：从瓶颈往上灌，水面是一条水平线
    if fill > 0.0:
        for y in range(max(3, surface), 32):
            span = row_span(y)
            if span is None:
                continue
            width = span[1] - span[0] + 1
            for x in range(span[0], span[1] + 1):
                if not interior[y][x]:
                    continue
                t = (x - span[0]) / max(1, width - 1)
                if y == surface:
                    color = WATER_TOP
                elif y >= 27:
                    color = WATER_DEEP
                elif t > 0.78:
                    color = WATER_DEEP
                elif t < 0.15:
                    color = WATER_HI
                else:
                    color = WATER
                put(x, y, color)

        # 气泡
        depth = 28.0 - top
        if depth > 3.0:
            for dx, size, phase in BUBBLES:
                u = (frame / FRAMES + phase) % 1.0
                by = 28.0 - u * depth
                bx = int(round(CX + dx))
                iy = int(round(by))
                if 3 <= iy <= 26 and interior[iy][bx]:
                    put(bx, iy, BUBBLE)
                    if size == 2 and interior[iy][bx + 1]:
                        put(bx + 1, iy, BUBBLE)

    # 玻璃壁：外层深一点，内层亮一点；收肩处只留 1px
    for y in range(2, 32):
        span = row_span(y)
        if span is None:
            continue
        wet = fill > 0.0 and y >= surface
        edge = GLASS_WET_EDGE if wet else GLASS_EDGE
        rim = GLASS_WET_RIM if wet else GLASS_RIM
        wall = wall_thickness(y)
        for k in range(wall):
            outer = k == wall - 1
            put(span[0] - 1 - k, y, edge if outer else rim)
            put(span[1] + 1 + k, y, edge if outer else rim)

    # 瓶口顶边
    top_span = row_span(2)
    for x in range(top_span[0] - 2, top_span[1] + 3):
        put(x, 0, GLASS_EDGE)
        put(x, 1, GLASS_RIM)

    # 竖向高光
    for y in range(5, 21):
        put(16, y, GLASS_SHINE)


def draw_machine():
    # 顶板 / 机身 / 底座
    rect(2, 29, 45, 31, MACHINE_DARK)
    rect(3, 30, 44, 30, MACHINE)
    rect(4, 32, 43, 72, MACHINE)
    rect(4, 32, 43, 32, MACHINE_DARK)
    rect(4, 33, 43, 34, MACHINE_HI)
    rect(4, 35, 5, 70, MACHINE_HI)
    rect(42, 34, 43, 70, MACHINE_DARK)
    rect(4, 70, 43, 72, MACHINE_DARK)
    rect(6, 73, 41, 76, MACHINE_DARK)
    rect(7, 74, 40, 76, (152, 160, 174, 255))

    # 桶口卡座：瓶颈两侧压一道暗边，看起来像插在顶板里
    rect(17, 30, 19, 30, COLLAR_DARK, mark=False)
    rect(27, 30, 29, 30, COLLAR_DARK, mark=False)

    # 铭牌 + 指示灯
    rect(16, 35, 31, 39, PLATE)
    border(16, 35, 31, 39, PLATE_EDGE)
    rect(22, 36, 25, 38, COLD)
    put(37, 33, LED)

    # 出水口凹槽
    rect(9, 43, 38, 59, NICHE, mark=False)
    border(9, 43, 38, 59, NICHE_EDGE)
    rect(10, 44, 37, 45, NICHE_SHADE, mark=False)

    # 热水口（左，红）
    rect(12, 44, 19, 44, HOT_HI, mark=False)
    rect(13, 45, 18, 48, HOT)
    rect(13, 45, 18, 45, HOT_HI, mark=False)
    rect(15, 49, 15, 51, SPOUT, mark=False)
    put(15, 52, SPOUT)
    put(14, 52, SPOUT)

    # 冷水口（右，蓝）
    rect(28, 44, 35, 44, COLD_HI, mark=False)
    rect(29, 45, 34, 48, COLD)
    rect(29, 45, 34, 45, COLD_HI, mark=False)
    rect(32, 49, 32, 51, SPOUT, mark=False)
    put(32, 52, SPOUT)
    put(33, 52, SPOUT)

    # 接水盘
    rect(11, 53, 36, 58, TRAY, mark=False)
    rect(11, 53, 36, 53, TRAY_DARK, mark=False)
    for x in range(13, 36, 3):
        rect(x, 54, x, 57, TRAY_DARK, mark=False)
    rect(11, 58, 36, 58, TRAY_LIP, mark=False)

    # 侧面散热格栅
    for y in range(63, 70, 2):
        rect(33, y, 40, y, VENT, mark=False)

    # 机身外描边
    for y in range(H):
        for x in range(W):
            if machine_mask[y][x] or canvas[y][x][3] != 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and machine_mask[ny][nx]:
                    canvas[y][x] = MACHINE_EDGE
                    break


def draw_mist(frame):
    for w in range(3):
        t = (frame / FRAMES + w * 0.33) % 1.0
        y = 52.0 + t * 6.0
        sway = math.sin((t + w * 0.3) * math.tau) * 1.5
        x = 31.0 + sway - t * 1.5
        shade = MIST_A if t < 0.3 else (MIST_B if t < 0.65 else MIST_C)
        cx = int(round(x))
        cy = int(round(y))
        put(cx, cy, shade)
        put(cx + 1, cy, shade)
        put(cx, cy + 1, shade)


def build(fill, frame):
    global canvas, machine_mask, interior
    canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
    machine_mask = [[False] * W for _ in range(H)]
    interior = [[False] * W for _ in range(H)]

    draw_bottle(fill, frame)
    draw_machine()
    draw_mist(frame)
    return canvas


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, fill in LEVELS:
        for frame in range(FRAMES):
            canvas = build(fill, frame)
            path = os.path.join(OUT_DIR, f"water-dispenser_{name}_{frame:02d}.png")
            write_png(path, W, H, canvas)
    print("wrote", len(LEVELS) * FRAMES, "frames to", OUT_DIR)


if __name__ == "__main__":
    main()

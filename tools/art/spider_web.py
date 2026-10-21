"""生成 assets/props/spider-web/export/spider-web.png

96x96 蛛网：14 条放射丝 + 一条从网心向外绕 7 圈的对数螺旋捕捉丝。
角度、半径都带固定种子的随机抖动，避免画成规整的雷达图。
"""

import math
import os
import random

from png_util import write_png

W = H = 96
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "props", "spider-web", "export", "spider-web.png")

CX = CY = 47.5
SPOKES = 12
START = -math.pi / 2
HUB = 5.5
R0 = 11.0
R1 = 42.5
TURNS = 4.5

SILK_BRIGHT = (240, 248, 252, 240)
SILK_SPIRAL = (206, 222, 234, 200)
SILK_SOFT = (186, 202, 216, 165)

rng = random.Random(11)

canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        canvas[y][x] = color


def line(x0, y0, x1, y1, color):
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    for i in range(steps + 1):
        u = i / steps
        put(int(round(x0 + (x1 - x0) * u)), int(round(y0 + (y1 - y0) * u)), color)


def polar(r, ang):
    return CX + r * math.cos(ang), CY + r * math.sin(ang)


# --- 放射丝：角度和长度各自略微分岔 ---
spoke_angles = []
for i in range(SPOKES):
    base = START + 2 * math.pi * i / SPOKES
    spoke_angles.append(base + math.radians(rng.uniform(-2.2, 2.2)))

# 先画螺旋，再画放射丝，让放射丝压在螺旋上面
# 捕捉丝：一根从网心绕到外圈的多边形螺旋，每经过一根放射丝就往外跳一格
segments = int(TURNS * SPOKES)
for s in range(segments):
    i = s % SPOKES
    j = (i + 1) % SPOKES
    a0 = spoke_angles[i]
    a1 = spoke_angles[j]
    if a1 < a0:
        a1 += 2 * math.pi

    r0 = R0 * (R1 / R0) ** (s / segments)
    r1 = R0 * (R1 / R0) ** ((s + 1) / segments)

    # 丝线在两根放射丝之间下垂
    sag = 0.025 + 0.01 * math.sin(s * 1.7)
    arc = (r0 + r1) * 0.5 * (a1 - a0)
    steps = max(6, int(arc * 1.6))
    for t in range(steps + 1):
        u = t / steps
        ang = a0 + (a1 - a0) * u
        r = (r0 + (r1 - r0) * u) * (1.0 - sag * math.sin(math.pi * u))
        x, y = polar(r, ang)
        put(int(round(x)), int(round(y)), SILK_SPIRAL)

# 放射丝
for i in range(SPOKES):
    ang = spoke_angles[i]
    outer = R1 + rng.uniform(-2.5, 1.0)
    x0, y0 = polar(HUB * 0.7, ang)
    x1, y1 = polar(outer, ang)
    line(x0, y0, x1, y1, SILK_BRIGHT)

# 网心小圈
for i in range(SPOKES):
    a0 = spoke_angles[i]
    a1 = spoke_angles[(i + 1) % SPOKES]
    if a1 < a0:
        a1 += 2 * math.pi
    for t in range(11):
        u = t / 10
        x, y = polar(HUB, a0 + (a1 - a0) * u)
        put(int(round(x)), int(round(y)), SILK_BRIGHT)

# 锚丝：外圈拉到四角，表示网挂在空间里
for deg in (-137, -43, 43, 137):
    ang = math.radians(deg) + math.radians(rng.uniform(-3, 3))
    x0, y0 = polar(R1 * 0.96, ang)
    x1, y1 = polar(66.0, ang)
    line(x0, y0, x1, y1, SILK_SOFT)

# 两根垂下来的断丝
for ang_deg, drop in ((-158, 11), (26, 9)):
    ang = math.radians(ang_deg)
    x0, y0 = polar(R1 * 0.86, ang)
    line(x0, y0, x0 + math.cos(ang) * 2.5, y0 + drop, SILK_SOFT)

write_png(OUT, W, H, canvas)
print("wrote", OUT)

# -*- coding: utf-8 -*-
"""行道树 / 树池 / 长椅 / 垃圾桶 / 饮水台 / 公告栏 / 校训牌 / 自行车棚 / 指示牌 / 路灯"""

import math
import random

import bpy

from campus_core import (TOP_Z, toon_mat, emit_mat, box, cyl, sphere, rect, quad,
                         torus, tube, strip, text_mesh, stage_group, link)

random.seed(21)

M_TRUNK = toon_mat("Trunk", "#7b5b42")
M_TRUNK_D = toon_mat("TrunkDark", "#6a4c37")
M_LEAF = toon_mat("Leaf", "#5a9450")
M_LEAF_D = toon_mat("LeafDark", "#487f42")
M_LEAF_L = toon_mat("LeafLight", "#75ad5c")
M_SOIL = toon_mat("Soil", "#6b5440")
M_CONC = toon_mat("Concrete", "#cfc8b8")
M_STEEL = toon_mat("Steel", "#a8b1bb")
M_STEEL_D = toon_mat("SteelDark", "#6f7883")
M_WOOD = toon_mat("Wood", "#b07a4d")
M_WOOD_D = toon_mat("WoodDark", "#8d5f3c")
M_BIN = toon_mat("BinGreen", "#4d7f63")
M_DARK = toon_mat("Dark", "#2b3138")
M_WHITE = toon_mat("PaperWhite", "#f4f1e6")
M_STONE = toon_mat("Stone", "#d8d0be")
M_STONE_D = toon_mat("StoneDark", "#a89f8c")
M_LAMP = emit_mat("LampGlow", "#ffe2b0", 2.6)
M_SCREEN = emit_mat("ScreenBlue", "#8fd0e8", 1.2)


# ================================================================
#  行道树
# ================================================================
def tree(name, x, y, s=1.2, seed=0, col=None):
    rnd = random.Random(seed)
    obs = []
    # 树池
    pit = 0.46
    for i, (dx, dy, w, d) in enumerate([(0, pit / 2, pit, 0.05), (0, -pit / 2, pit, 0.05),
                                        (pit / 2, 0, 0.05, pit), (-pit / 2, 0, 0.05, pit)]):
        obs.append(box("%s_Pit%d" % (name, i), (w, d, 0.05), (x + dx, y + dy, TOP_Z + 0.025),
                       M_CONC, col=col))
    obs.append(rect("%s_Soil" % name, x, y, pit - 0.12, pit - 0.12, TOP_Z + 0.008, M_SOIL, col=col))
    # 树干
    obs.append(cyl("%s_Trunk" % name, 0.052 * s, 0.040 * s, 0.62 * s, (x, y, TOP_Z + 0.31 * s),
                   M_TRUNK, seg=8, col=col))
    # 分叉
    for i in range(2):
        a = rnd.random() * 3.14
        obs.append(cyl("%s_Branch%d" % (name, i), 0.022 * s, 0.012 * s, 0.26 * s,
                       (x + math.cos(a) * 0.08 * s, y + math.sin(a) * 0.08 * s, TOP_Z + 0.68 * s),
                       M_TRUNK_D, seg=6, rz=a, rx=math.radians(18), col=col))
    # 树冠
    clumps = [(0.0, 0.0, 0.90, 0.30), (0.15, 0.10, 1.02, 0.24), (-0.16, 0.10, 0.98, 0.22),
              (0.02, -0.18, 1.00, 0.23), (-0.05, 0.02, 1.14, 0.21)]
    for i, (dx, dy, dz, r) in enumerate(clumps):
        mat = M_LEAF if i % 3 == 0 else (M_LEAF_D if i % 3 == 1 else M_LEAF_L)
        obs.append(sphere("%s_Crown%d" % (name, i), r * s,
                          (x + dx * s, y + dy * s, TOP_Z + dz * s), mat, seg=12, col=col))
    return obs


def build_trees(col):
    obs = []
    specs = [(-4.95, -3.90, 1.34), (-3.15, -3.90, 1.16), (1.55, -3.90, 1.38),
             (3.45, -3.90, 1.20), (5.10, -3.85, 1.10),
             (5.35, -2.55, 1.16), (5.30, 3.90, 1.22),
             (-4.55, 5.06, 1.32), (-1.85, 5.06, 1.16), (0.95, 5.06, 1.36),
             (3.30, 5.08, 1.18), (-5.30, 5.12, 1.20)]
    for i, (x, y, s) in enumerate(specs):
        obs += tree("Tree%d" % i, x, y, s, seed=i * 13 + 5, col=col)
    # 灌木
    bushes = [(2.55, -3.55, 0.9), (-2.35, 4.05, 0.85), (4.55, 4.10, 0.95), (5.45, 0.65, 0.8)]
    for i, (x, y, s) in enumerate(bushes):
        for k in range(3):
            a = k * 2.1 + i
            obs.append(sphere("Bush%d_%d" % (i, k), 0.11 * s,
                              (x + math.cos(a) * 0.07, y + math.sin(a) * 0.07, TOP_Z + 0.10 * s),
                              M_LEAF_D if k % 2 else M_LEAF, seg=10, col=col))
    stage_group(obs, 104, 0.28, 12, 'pop')
    return obs


# ================================================================
#  长椅 / 垃圾桶 / 饮水台
# ================================================================
def bench(name, x, y, rz=0.0, col=None):
    obs = []
    obs.append(box("%s_Seat" % name, (0.66, 0.24, 0.045), (x, y, TOP_Z + 0.17), M_WOOD, rz=rz, col=col))
    bx = -math.sin(rz) * 0.105
    by = -math.cos(rz) * 0.105
    for i in range(3):
        obs.append(box("%s_Slat%d" % (name, i), (0.66, 0.05, 0.035),
                       (x + bx, y + by, TOP_Z + 0.25 + i * 0.06), M_WOOD, rz=rz, col=col))
    for s in (-1, 1):
        lx = x + math.cos(rz) * 0.26 * s
        ly = y + math.sin(rz) * 0.26 * s
        obs.append(box("%s_Leg%d" % (name, s), (0.05, 0.20, 0.17), (lx, ly, TOP_Z + 0.085),
                       M_STEEL_D, rz=rz, col=col))
    return obs


def bin_(name, x, y, col=None):
    obs = []
    obs.append(cyl("%s_Body" % name, 0.085, 0.075, 0.26, (x, y, TOP_Z + 0.13), M_BIN, seg=12, col=col))
    obs.append(cyl("%s_Lid" % name, 0.092, 0.092, 0.035, (x, y, TOP_Z + 0.275), M_STEEL_D, seg=12, col=col))
    obs.append(cyl("%s_Hole" % name, 0.045, 0.045, 0.012, (x, y, TOP_Z + 0.296), M_DARK, seg=10, col=col))
    return obs


def build_street_furniture(col):
    obs = []
    obs += bench("BenchA", 2.25, 4.25, rz=math.radians(6), col=col)
    obs += bench("BenchB", -0.95, 4.25, rz=math.radians(-4), col=col)
    obs += bin_("BinA", 3.95, 4.35, col=col)
    obs += bin_("BinB", -0.20, -3.52, col=col)
    # 饮水台
    x, y = 0.55, 4.42
    obs.append(box("DrinkBase", (0.34, 0.30, 0.42), (x, y, TOP_Z + 0.21), M_CONC, col=col))
    obs.append(box("DrinkTop", (0.40, 0.34, 0.05), (x, y, TOP_Z + 0.445), M_STONE, col=col))
    obs.append(cyl("DrinkBowl", 0.085, 0.06, 0.035, (x + 0.10, y + 0.10, TOP_Z + 0.487), M_STEEL, seg=12, col=col))
    obs.append(cyl("DrinkTap", 0.014, 0.012, 0.10, (x + 0.02, y + 0.10, TOP_Z + 0.52), M_STEEL_D, seg=8, col=col))
    stage_group(obs, 118, 1.2, 12, 'pop')
    return obs


# ================================================================
#  公告栏 / 校训牌 / 指示牌
# ================================================================
def build_signs(col):
    obs = []
    # 公告栏（面向镜头方向）
    x, y = 5.00, -2.70
    rz = math.radians(-45)
    obs.append(box("BoardFrame", (0.96, 0.06, 0.62), (x, y, TOP_Z + 0.72), M_WOOD_D, rz=rz, col=col))
    obs.append(box("BoardFace", (0.88, 0.04, 0.52), (x + 0.03, y + 0.03, TOP_Z + 0.72), M_WHITE, rz=rz, col=col))
    obs.append(box("BoardRoof", (1.06, 0.20, 0.05), (x + 0.02, y + 0.02, TOP_Z + 1.06), M_WOOD, rz=rz, col=col))
    for s in (-1, 1):
        obs.append(cyl("BoardPost%d" % s, 0.035, 0.035, 1.0, (x - 0.36 * s, y + 0.36 * s, TOP_Z + 0.35),
                       M_WOOD_D, seg=8, col=col))
    # 海报
    posters = [(-0.24, 0.14, "#e9c46a"), (0.02, 0.10, "#8ecae6"), (0.26, 0.12, "#ef8a72")]
    for i, (dx, dz, hx) in enumerate(posters):
        px = x + dx * math.cos(rz) - dz * 0  # 沿板面横向
        py = y + dx * math.sin(rz)
        obs.append(box("Poster%d" % i, (0.18, 0.012, 0.22), (px + 0.05, py + 0.05, TOP_Z + 0.70 + dz - 0.10),
                       toon_mat("Poster%d" % i, hx), rz=rz, col=col))
    t = text_mesh("BoardText", "社团招新", 0.085, (x + 0.055, y + 0.045, TOP_Z + 0.99),
                  (math.radians(90), 0, math.radians(135)), toon_mat("InkBlue", "#3c5a78"), col=col)
    if t:
        obs.append(t)

    # 校训石
    x, y = 2.45, 5.16
    rz = math.radians(-45)
    obs.append(box("MottoStone", (0.92, 0.24, 0.50), (x, y, TOP_Z + 0.25), M_STONE, rz=rz, col=col))
    obs.append(box("MottoBase", (1.04, 0.34, 0.08), (x, y, TOP_Z + 0.04), M_STONE_D, rz=rz, col=col))
    t2 = text_mesh("MottoText", "明德笃学", 0.15, (x + 0.02, y + 0.02, TOP_Z + 0.31),
                   (math.radians(90), 0, math.radians(135)), toon_mat("InkRed", "#a63a2f"), col=col)
    if t2:
        obs.append(t2)

    # 校园指示牌
    x, y = 3.60, -2.78
    obs.append(cyl("SignPole", 0.028, 0.028, 0.92, (x, y, TOP_Z + 0.46), M_STEEL_D, seg=8, col=col))
    for i, (dz, w) in enumerate(((0.82, 0.40), (0.62, 0.34))):
        obs.append(box("SignBoard%d" % i, (w, 0.035, 0.13), (x + w / 2 - 0.04, y, TOP_Z + dz),
                       toon_mat("SignBlue", "#3f6f9e"), col=col))
        obs.append(box("SignArrow%d" % i, (0.09, 0.035, 0.09), (x + w - 0.03, y, TOP_Z + dz),
                       toon_mat("SignBlue", "#3f6f9e"), rz=math.radians(45), col=col))
    t3 = text_mesh("SignText", "操场", 0.062, (x + 0.16, y + 0.02, TOP_Z + 0.82),
                   (math.radians(90), 0, math.radians(180)), M_WHITE, col=col)
    if t3:
        obs.append(t3)
    stage_group(obs, 122, 1.2, 12, 'pop')
    return obs


# ================================================================
#  自行车棚 + 自行车
# ================================================================
def bike(name, x, y, col, rz=0.0):
    obs = []
    z = TOP_Z
    for s in (-1, 1):
        obs.append(torus("%s_Wheel%d" % (name, s), 0.088, 0.008,
                         (x, y + s * 0.11, z + 0.095), M_DARK,
                         seg_major=16, seg_minor=5, rot=(0, math.radians(90), 0), col=col))
    obs.append(tube("%s_Frame" % name,
                    [(x, y - 0.08, z + 0.095), (x, y + 0.02, z + 0.22), (x, y + 0.09, z + 0.10),
                     (x, y + 0.02, z + 0.09), (x, y - 0.08, z + 0.095)],
                    0.012, toon_mat("BikeFrame", "#3c6f8f"), col=col))
    obs.append(cyl("%s_Seat" % name, 0.035, 0.028, 0.05, (x, y + 0.01, z + 0.26),
                   M_DARK, seg=8, col=col))
    obs.append(cyl("%s_Bar" % name, 0.008, 0.008, 0.20, (x, y - 0.10, z + 0.24),
                   M_STEEL, seg=6, ry=math.radians(90), col=col))
    return obs


def build_bike_shed(col):
    obs = []
    x, y = -4.68, 3.70
    for i, (dx, dy) in enumerate([(-0.86, -0.44), (0.86, -0.44), (-0.86, 0.44), (0.86, 0.44)]):
        obs.append(cyl("ShedPost%d" % i, 0.028, 0.024, 0.78, (x + dx, y + dy, TOP_Z + 0.39),
                       M_STEEL_D, seg=8, col=col))
    roof = box("ShedRoof", (1.96, 1.16, 0.05), (x, y, TOP_Z + 0.80), toon_mat("ShedRoof", "#7fa8a0"),
               col=col)
    roof.rotation_euler[1] = math.radians(5.0)
    obs.append(roof)
    obs.append(box("ShedBeam", (1.98, 0.06, 0.07), (x, y - 0.46, TOP_Z + 0.72), M_STEEL_D, col=col))
    obs.append(box("ShedBeam2", (1.98, 0.06, 0.07), (x, y + 0.46, TOP_Z + 0.76), M_STEEL_D, col=col))
    for i in range(3):
        obs += bike("Bike%d" % i, x - 0.58 + i * 0.58, y + 0.02, col)
    stage_group(obs, 116, 0.9, 12, 'pop')
    return obs


# ================================================================
#  路灯
# ================================================================
def lamp(name, x, y, rz=0.0, col=None):
    obs = []
    obs.append(cyl("%s_Base" % name, 0.07, 0.06, 0.07, (x, y, TOP_Z + 0.035), M_STEEL_D, seg=10, col=col))
    obs.append(cyl("%s_Pole" % name, 0.028, 0.022, 1.02, (x, y, TOP_Z + 0.55), M_STEEL, seg=8, col=col))
    cx, sy = math.cos(rz), math.sin(rz)
    obs.append(box("%s_Arm" % name, (0.26, 0.055, 0.05),
                   (x + cx * 0.16, y + sy * 0.16, TOP_Z + 1.32), M_STEEL, rz=rz, col=col))
    obs.append(box("%s_Head" % name, (0.22, 0.14, 0.06),
                   (x + cx * 0.31, y + sy * 0.31, TOP_Z + 1.24), M_LAMP, rz=rz, col=col))
    return obs


def build_lamps(col):
    obs = []
    specs = [(-3.90, -4.10, math.radians(90)), (1.40, -4.10, math.radians(90)),
             (4.90, 2.90, math.radians(-90)), (-0.90, 4.90, math.radians(-90))]
    for i, (x, y, rz) in enumerate(specs):
        obs += lamp("Lamp%d" % i, x, y, rz, col=col)
    stage_group(obs, 112, 1.0, 12, 'pop')
    return obs

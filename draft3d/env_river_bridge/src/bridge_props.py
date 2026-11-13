# -*- coding: utf-8 -*-
"""
黄昏滨河跨河桥 · 绿化与街具
行道树 / 绿篱 / 花坛 / 路灯 / 长椅 / 垃圾桶 / 路牌 / 滨河系船柱
"""

import math

from bridge_core import (TOP_Z, HALF, PROM_Y0, PROM_Y1, ROAD_Y0, ROAD_Y1,
                         SIDE_Y0, SIDE_Y1, BELT_Y0, BELT_Y1,
                         box, cyl, sphere, rect, slab, tube, poly,
                         toon_mat, emit_mat, text_mesh, stage, stage_group)

BELT_TOP = TOP_Z + 0.10
SIDE_TOP = TOP_Z + 0.07
PROM_TOP = TOP_Z + 0.05

HEDGE = "M_Hedge"
HEDGE_DARK = "M_HedgeDark"
LEAF_A = "M_LeafA"
LEAF_B = "M_LeafB"
TRUNK = "M_Trunk"
FLOWER_R = "M_FlowerRed"
FLOWER_Y = "M_FlowerYellow"
FLOWER_P = "M_FlowerPink"
LAMP_POST = "M_LampPost"
LAMP_GLOW = "M_LampGlow"
WOOD = "M_BenchWood"
IRON = "M_Iron"
SIGN_BLUE = "M_SignBlue"
SIGN_WHITE = "M_SignWhite"


def mats():
    toon_mat(HEDGE, "#4a7f3c")
    toon_mat(HEDGE_DARK, "#3d6b32")
    toon_mat(LEAF_A, "#5b9147")
    toon_mat(LEAF_B, "#6fa653")
    toon_mat(TRUNK, "#6d4b35")
    toon_mat(FLOWER_R, "#e0574f")
    toon_mat(FLOWER_Y, "#f2c64d")
    toon_mat(FLOWER_P, "#e98aa8")
    toon_mat(LAMP_POST, "#3a3d42")
    toon_mat(WOOD, "#9a6a45")
    toon_mat(IRON, "#4a4f55")
    toon_mat(SIGN_BLUE, "#2f5f9e")
    toon_mat(SIGN_WHITE, "#f4efe0")
    emit_mat(LAMP_GLOW, "#ffd79b", 1.0)


# ---------------------------------------------------------------- 行道树
TREE_X = (-5.30, -3.85, -2.40, -0.95, 0.95, 2.40, 3.85, 5.30)


def tree(name, x, y, scale, col, tone=0):
    obs = []
    z0 = BELT_TOP
    h = 0.62 * scale
    obs.append(cyl(name + "_Trunk", 0.048 * scale, 0.038 * scale, h,
                   (x, y, z0 + h / 2), toon_mat(TRUNK, "#6d4b35"), seg=10, col=col))
    leaf = LEAF_A if tone % 2 == 0 else LEAF_B
    color = "#5b9147" if tone % 2 == 0 else "#6fa653"
    m = toon_mat(leaf, color)
    obs.append(sphere(name + "_L0", 0.235 * scale, (x, y, z0 + h + 0.10 * scale), m, seg=12, col=col))
    obs.append(sphere(name + "_L1", 0.165 * scale, (x - 0.15 * scale, y + 0.05 * scale,
                                                    z0 + h + 0.26 * scale), m, seg=10, col=col))
    obs.append(sphere(name + "_L2", 0.145 * scale, (x + 0.14 * scale, y - 0.06 * scale,
                                                    z0 + h + 0.22 * scale), m, seg=10, col=col))
    return obs


def build_trees(col):
    mats()
    obs = []
    for sy in (1, -1):
        for i, x in enumerate(TREE_X):
            jitter = 0.06 if (i + (sy > 0)) % 2 else -0.04
            obs += tree("Tree%s%02d" % ("N" if sy > 0 else "S", i),
                        x + jitter, sy * 5.70, 1.0 if i % 3 else 1.12, col, i)
    stage_group(obs, 88, 0.35, 12, 'pop')


# ---------------------------------------------------------------- 绿篱 / 花坛
def build_hedges(col):
    obs = []
    for sy in (1, -1):
        tag = "N" if sy > 0 else "S"
        y = sy * 5.55
        x = -HALF + 0.30
        i = 0
        while x < HALF - 0.40:
            if 0.62 <= abs(x) <= 1.35 and i % 2 == 0:
                x += 0.36
                continue
            ln = 0.62
            obs.append(box("Hedge_%s%02d" % (tag, i), (ln, 0.34, 0.26),
                           (x + ln / 2, y, BELT_TOP + 0.13),
                           toon_mat(HEDGE, "#4a7f3c"), col=col))
            obs.append(box("HedgeTop_%s%02d" % (tag, i), (ln - 0.06, 0.28, 0.06),
                           (x + ln / 2, y, BELT_TOP + 0.28),
                           toon_mat(HEDGE_DARK, "#3d6b32"), col=col))
            x += ln + 0.34
            i += 1
    stage_group(obs, 84, 0.30, 12, 'pop')


def build_flowers(col):
    mats()
    obs = []
    clusters = [(-5.05, 5.82), (-3.20, 5.86), (-1.60, 5.84), (0.10, 5.86),
                (1.90, 5.84), (3.40, 5.86), (5.05, 5.82)]
    fmats = [toon_mat(FLOWER_R, "#e0574f"), toon_mat(FLOWER_Y, "#f2c64d"),
             toon_mat(FLOWER_P, "#e98aa8")]
    for sy in (1, -1):
        for i, (x, yb) in enumerate(clusters):
            y = sy * yb
            obs.append(rect("Flower_Soil%s%d" % ("N" if sy > 0 else "S", i), x, y,
                            0.46, 0.30, BELT_TOP + 0.012,
                            toon_mat(HEDGE_DARK, "#3d6b32"), col=col))
            for k in range(5):
                ang = 2 * math.pi * k / 5 + i
                fx = x + 0.15 * math.cos(ang)
                fy = y + 0.09 * math.sin(ang)
                obs.append(sphere("Flower_%s%d_%d" % ("N" if sy > 0 else "S", i, k), 0.043,
                                  (fx, fy, BELT_TOP + 0.05),
                                  fmats[(i + k) % 3], seg=8, col=col))
    stage_group(obs, 92, 0.25, 10, 'pop')


# ---------------------------------------------------------------- 路灯
def build_lamps(col):
    obs = []
    spots = [(-3.90, 4.86), (3.90, 4.86), (-3.90, -4.86), (3.90, -4.86),
             (-0.40, 5.10), (-0.40, -5.10)]
    for i, (x, y) in enumerate(spots):
        sy = 1 if y > 0 else -1
        obs.append(cyl("Lamp_Post%d" % i, 0.045, 0.038, 1.02,
                       (x, y, SIDE_TOP + 0.51), toon_mat(LAMP_POST, "#3a3d42"), seg=10, col=col))
        obs.append(cyl("Lamp_Base%d" % i, 0.075, 0.062, 0.09,
                       (x, y, SIDE_TOP + 0.045), toon_mat(LAMP_POST, "#3a3d42"), seg=10, col=col))
        # 灯头（朝马路一侧挑出）
        arm_y = y - sy * 0.20
        obs.append(tube("Lamp_Arm%d" % i, [(x, y, SIDE_TOP + 1.02), (x, arm_y, SIDE_TOP + 1.06)],
                        0.026, toon_mat(LAMP_POST, "#3a3d42"), col=col, res=3))
        obs.append(box("Lamp_Head%d" % i, (0.16, 0.16, 0.07),
                       (x, arm_y, SIDE_TOP + 1.03), toon_mat(LAMP_POST, "#3a3d42"), col=col))
        obs.append(box("Lamp_Glass%d" % i, (0.13, 0.13, 0.035),
                       (x, arm_y, SIDE_TOP + 0.985), emit_mat(LAMP_GLOW, "#ffd79b", 1.0), col=col))
    stage_group(obs, 96, 0.45, 12, 'rise')


# ---------------------------------------------------------------- 长椅 / 垃圾桶
def bench(name, x, y, col, face=1):
    obs = []
    z = PROM_TOP
    obs.append(box(name + "_Seat", (0.66, 0.24, 0.045), (x, y, z + 0.20),
                   toon_mat(WOOD, "#9a6a45"), col=col))
    obs.append(box(name + "_Back", (0.66, 0.045, 0.20), (x, y + face * 0.10, z + 0.33),
                   toon_mat(WOOD, "#9a6a45"), col=col))
    for sx in (-1, 1):
        obs.append(box(name + "_Leg%d" % sx, (0.05, 0.20, 0.20),
                       (x + sx * 0.26, y, z + 0.10), toon_mat(IRON, "#4a4f55"), col=col))
    return obs


def build_furniture(col):
    obs = []
    for sy in (1, -1):
        for i, x in enumerate((-4.40, -2.60, 2.60, 4.40)):
            obs += bench("Bench%s%d" % ("N" if sy > 0 else "S", i), x,
                         sy * 1.72, col, face=-sy)
    # 垃圾桶
    for sy in (1, -1):
        for i, x in enumerate((-3.55, 3.55)):
            obs.append(cyl("Bin%s%d" % ("N" if sy > 0 else "S", i), 0.075, 0.085, 0.24,
                           (x, sy * 1.74, PROM_TOP + 0.12),
                           toon_mat(IRON, "#4a4f55"), seg=12, col=col))
    stage_group(obs, 100, 0.7, 12, 'pop')


# ---------------------------------------------------------------- 路牌 / 系船柱
def build_signs(col):
    obs = []
    labels = [("滨河路", 4.95, 4.52), ("望江桥", -4.95, 4.52),
              ("滨河路", 4.95, -4.52), ("望江桥", -4.95, -4.52)]
    for i, (body, x, y) in enumerate(labels):
        sy = 1 if y > 0 else -1
        obs.append(cyl("Sign_Post%d" % i, 0.024, 0.024, 0.72,
                       (x, y, SIDE_TOP + 0.36), toon_mat(LAMP_POST, "#3a3d42"), seg=10, col=col))
        obs.append(box("Sign_Board%d" % i, (0.52, 0.035, 0.20),
                       (x, y, SIDE_TOP + 0.63), toon_mat(SIGN_BLUE, "#2f5f9e"), col=col))
        t = text_mesh("Sign_Text%d" % i, body, 0.105, (x, y - sy * 0.022, SIDE_TOP + 0.628),
                      (math.radians(90), 0, 0 if sy > 0 else math.pi),
                      toon_mat(SIGN_WHITE, "#f4efe0"), col=col)
        if t:
            obs.append(t)
    stage_group(obs, 104, 0.8, 12, 'pop')


def build_mooring(col):
    obs = []
    for sy in (1, -1):
        x = -HALF + 0.55
        while x < HALF - 0.4:
            if abs(x) > 1.25:
                obs.append(cyl("Mooring%s%s" % ("N" if sy > 0 else "S", int(x * 10)),
                               0.035, 0.028, 0.30, (x, sy * 1.50, PROM_TOP + 0.15),
                               toon_mat(IRON, "#4a4f55"), seg=10, col=col))
            x += 1.15
    stage_group(obs, 106, 0.35, 10, 'pop')

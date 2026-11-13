# -*- coding: utf-8 -*-
"""天台建筑体：底座、屋顶、女儿墙、楼梯间、水箱、外机、晾衣绳、广告牌"""

import math
from mathutils import Vector
from ramen_core import (ROOF_Z, toon_mat, emit_mat, box, cyl, sphere, plane, quad,
                        torus, tube, text_mesh, stage_group, srgb, link, BASE)

M_CONCRETE = toon_mat("Concrete", "#3f4656")
M_CONCRETE_D = toon_mat("ConcreteDark", "#2f3543")
M_COPING = toon_mat("Coping", "#59627a")
M_METAL = toon_mat("Metal", "#7d8798")
M_METAL_D = toon_mat("MetalDark", "#2a3240")
M_RUST = toon_mat("Rust", "#7d5a48")
M_WOOD = toon_mat("Wood", "#6a4a35")
M_WOOD_D = toon_mat("WoodDark", "#453026")
M_DARK = toon_mat("DarkPanel", "#141a26")
M_WHITE = toon_mat("ClothWhite", "#cfd2d8")
M_BLUE = toon_mat("ClothBlue", "#5d7c9c")
M_PINK = toon_mat("ClothPink", "#b07a86")
M_PLANT = toon_mat("Plant", "#3f6b4a")
M_PLANT_D = toon_mat("PlantDark", "#2c4d36")
M_POT = toon_mat("Pot", "#8a5b45")
M_CARD = toon_mat("Cardboard", "#a67b44")
M_TANK = toon_mat("TankMetal", "#7f8ba0")
M_STAIN = toon_mat("Stain", "#3a4150")

NEON_PINK = emit_mat("NeonPinkMat", "#ff4f9a", 2.6)
NEON_CYAN = emit_mat("NeonCyanMat", "#4fd8ff", 2.4)
NEON_WARM = emit_mat("NeonWarmMat", "#ffc36a", 2.2)


def neon_text(name, body, size, loc, col, mat=NEON_PINK, extrude=0.015):
    ob = text_mesh(name, body, size, loc, (math.pi / 2, 0, math.pi), mat, col, extrude)
    if ob is None:
        # 无日文字体时的占位灯条
        obs = []
        for i in range(3):
            obs.append(box("%s_bar%d" % (name, i), (size * 2.2, 0.03, size * 0.16),
                           (loc[0], loc[1], loc[2] + (i - 1) * size * 0.42), mat, col=col))
        return obs
    return [ob]


# ================================================================
#  底座 + 屋顶
# ================================================================
def build_base(col):
    obs = []
    m_plinth = toon_mat("Plinth", "#12161f")
    m_trim = toon_mat("PlinthTrim", "#212a3a")
    m_rim = emit_mat("PlinthRim", "#3c6ea6", 1.4)

    obs.append(box("Plinth", (10.4, 10.4, 0.76), (0, 0, -0.38), m_plinth, col=col))
    obs.append(box("PlinthTrim", (10.7, 10.7, 0.1), (0, 0, -0.77), m_trim, col=col))
    for name, dims, loc in (
            ("RimF", (10.0, 0.02, 0.045), (0, 5.21, -0.06)),
            ("RimB", (10.0, 0.02, 0.045), (0, -5.21, -0.06)),
            ("RimR", (0.02, 10.0, 0.045), (5.21, 0, -0.06)),
            ("RimL", (0.02, 10.0, 0.045), (-5.21, 0, -0.06))):
        obs.append(box(name, dims, loc, m_rim, col=col))

    # 屋顶楼板
    obs.append(box("RoofSlab", (10.0, 10.0, ROOF_Z), (0, 0, ROOF_Z / 2),
                   M_CONCRETE, col=col))
    # 水泥分格缝
    for i in range(-4, 5):
        obs.append(box("SeamX%d" % i, (0.022, 9.9, 0.006), (i, 0, ROOF_Z + 0.003),
                       M_STAIN, col=col))
        obs.append(box("SeamY%d" % i, (9.9, 0.022, 0.006), (0, i, ROOF_Z + 0.003),
                       M_STAIN, col=col))

    # 女儿墙
    for name, dims, loc in (
            ("ParapetF", (10.0, 0.22, 0.95), (0, 4.89, ROOF_Z + 0.475)),
            ("ParapetB", (10.0, 0.22, 0.95), (0, -4.89, ROOF_Z + 0.475)),
            ("ParapetR", (0.22, 10.0, 0.95), (4.89, 0, ROOF_Z + 0.475)),
            ("ParapetL", (0.22, 10.0, 0.95), (-4.89, 0, ROOF_Z + 0.475))):
        obs.append(box(name, dims, loc, M_CONCRETE, col=col))
    for name, dims, loc in (
            ("CopF", (10.24, 0.3, 0.07), (0, 4.89, ROOF_Z + 0.985)),
            ("CopB", (10.24, 0.3, 0.07), (0, -4.89, ROOF_Z + 0.985)),
            ("CopR", (0.3, 10.24, 0.07), (4.89, 0, ROOF_Z + 0.985)),
            ("CopL", (0.3, 10.24, 0.07), (-4.89, 0, ROOF_Z + 0.985))):
        obs.append(box(name, dims, loc, M_COPING, col=col))

    # 女儿墙内侧的赛博灯带（青）
    obs.append(box("EdgeNeonF", (8.2, 0.024, 0.035), (0, 4.76, ROOF_Z + 0.60), NEON_CYAN, col=col))
    obs.append(box("EdgeNeonR", (0.024, 8.2, 0.035), (4.76, 0, ROOF_Z + 0.60), NEON_CYAN, col=col))
    obs.append(box("EdgeNeonB", (8.2, 0.024, 0.035), (0, -4.76, ROOF_Z + 0.60), NEON_CYAN, col=col))

    # 外侧落水管（正面可见）
    obs.append(cyl("DownPipe", 0.068, 0.068, 2.1, (3.1, 5.27, 0.15), M_METAL_D, seg=10, col=col))
    obs.append(cyl("DownPipeElbow", 0.075, 0.075, 0.34, (3.1, 5.12, 1.22),
                   M_METAL_D, seg=10, rx=math.pi / 2, col=col))
    for i in range(3):
        obs.append(box("PipeClamp%d" % i, (0.16, 0.05, 0.05),
                       (3.1, 5.23, -0.3 + i * 0.62), M_METAL_D, col=col))
    # 右侧外墙线管
    obs.append(cyl("SidePipe", 0.05, 0.05, 1.4, (5.27, 2.4, 0.55), M_METAL_D, seg=8, col=col))

    stage_group(obs, 1, 1.2, 16, 'rise')
    return obs


# ================================================================
#  楼梯间出入口
# ================================================================
def build_stairwell(col):
    cx, cy = -3.15, -3.05
    obs = []
    obs.append(box("StairBody", (2.5, 2.2, 2.35), (cx, cy, ROOF_Z + 1.175),
                   M_CONCRETE_D, col=col))
    obs.append(box("StairRoof", (2.72, 2.42, 0.14), (cx, cy, ROOF_Z + 2.42),
                   M_COPING, col=col))
    obs.append(box("StairBand", (2.54, 2.24, 0.1), (cx, cy, ROOF_Z + 1.55),
                   M_CONCRETE, col=col))

    fy = cy + 1.1
    obs.append(box("DoorFrame", (0.98, 0.1, 1.78), (cx, fy + 0.02, ROOF_Z + 0.91),
                   M_METAL_D, col=col))
    obs.append(box("Door", (0.84, 0.08, 1.64), (cx, fy + 0.07, ROOF_Z + 0.83),
                   M_METAL, col=col))
    obs.append(box("DoorGlow", (0.7, 0.02, 0.03), (cx, fy + 0.115, ROOF_Z + 0.06),
                   NEON_WARM, col=col))
    obs.append(box("DoorHandle", (0.05, 0.06, 0.2), (cx + 0.3, fy + 0.13, ROOF_Z + 0.85),
                   M_METAL_D, col=col))
    obs.append(box("DoorCanopy", (1.25, 0.6, 0.06), (cx, fy + 0.3, ROOF_Z + 2.02),
                   M_METAL_D, col=col))
    obs.append(box("DoorLamp", (0.22, 0.14, 0.1), (cx, fy + 0.12, ROOF_Z + 1.92),
                   NEON_WARM, col=col))

    # 配电箱
    obs.append(box("ElecBox", (0.46, 0.14, 0.62), (cx + 1.02, fy + 0.06, ROOF_Z + 1.42),
                   M_METAL_D, col=col))
    obs.append(box("ElecLabel", (0.3, 0.02, 0.16), (cx + 1.02, fy + 0.14, ROOF_Z + 1.55),
                   M_WHITE, col=col))
    for i in range(3):
        obs.append(box("ElecMeter%d" % i, (0.28, 0.03, 0.05),
                       (cx + 1.02, fy + 0.145, ROOF_Z + 1.30 - i * 0.11),
                       toon_mat("Meter", "#89c9a4"), col=col))

    # 排气管
    obs.append(cyl("VentPipe", 0.085, 0.085, 0.9, (cx - 1.0, cy - 0.8, ROOF_Z + 2.9),
                   M_METAL, seg=10, col=col))
    obs.append(cyl("VentCap", 0.13, 0.09, 0.1, (cx - 1.0, cy - 0.8, ROOF_Z + 3.38),
                   M_METAL_D, seg=10, col=col))

    # 楼梯间外墙招牌：営業中
    obs.append(box("SignBox", (1.0, 0.1, 0.42), (cx - 0.62, fy + 0.06, ROOF_Z + 2.12),
                   M_DARK, col=col))
    obs.extend(neon_text("StairSign", "営業中", 0.2, (cx - 0.62, fy + 0.13, ROOF_Z + 2.12),
                         col, NEON_PINK))

    # 天线
    base = (cx - 0.42, cy - 0.62)
    obs.append(cyl("AntennaMast", 0.028, 0.022, 2.4, (base[0], base[1], ROOF_Z + 2.68 + 1.2),
                   M_METAL_D, seg=8, col=col))
    for i, (z, w) in enumerate(((2.55, 0.9), (2.95, 0.7), (3.3, 0.5))):
        obs.append(box("AntennaBar%d" % i, (w, 0.03, 0.03),
                       (base[0], base[1], ROOF_Z + z), M_METAL_D, col=col))
    obs.append(box("AntennaBox", (0.2, 0.12, 0.3), (base[0] + 0.25, base[1], ROOF_Z + 2.75),
                   M_METAL_D, col=col))

    # 右侧面（朝相机）：小窗 + 外机 + 立管
    wx = cx + 1.26
    obs.append(box("StairWindowFrame", (0.06, 0.86, 0.62), (wx, cy + 0.5, ROOF_Z + 1.65),
                   M_METAL_D, col=col))
    obs.append(box("StairWindow", (0.03, 0.74, 0.5), (wx + 0.03, cy + 0.5, ROOF_Z + 1.65),
                   emit_mat("WindowWarm", "#ffb96e", 1.4), col=col))
    for i in range(2):
        obs.append(box("StairWinBar%d" % i, (0.04, 0.04, 0.52),
                       (wx + 0.04, cy + 0.5 + (i - 0.5) * 0.26, ROOF_Z + 1.65),
                       M_METAL_D, col=col))
    obs.append(box("StairAC", (0.26, 0.72, 0.5), (wx + 0.1, cy - 0.72, ROOF_Z + 0.42),
                   M_METAL, col=col))
    obs.append(torus("StairACRing", 0.19, 0.025, (wx + 0.24, cy - 0.72, ROOF_Z + 0.42),
                     M_METAL_D, seg_major=16, seg_minor=5,
                     rot=(0, math.pi / 2, 0), col=col))
    obs.append(cyl("StairPipe", 0.045, 0.045, 1.9, (wx + 0.05, cy + 1.0, ROOF_Z + 0.95),
                   M_METAL_D, seg=8, col=col))
    obs.append(box("StairPoster", (0.02, 0.34, 0.46), (wx + 0.02, cy - 0.18, ROOF_Z + 1.5),
                   emit_mat("PosterGlow", "#6fd8ff", 0.9), col=col))

    stage_group(obs, 40, 1.4, 16, 'rise')
    return obs


# ================================================================
#  水箱
# ================================================================
def build_water_tank(col):
    cx, cy = 3.35, -3.15
    obs = []
    for i, (dx, dy) in enumerate(((-0.55, -0.55), (0.55, -0.55), (-0.55, 0.55), (0.55, 0.55))):
        obs.append(cyl("TankLeg%d" % i, 0.065, 0.065, 0.92,
                       (cx + dx, cy + dy, ROOF_Z + 0.46), M_METAL_D, seg=8, col=col))
    obs.append(box("TankFrame", (1.2, 1.2, 0.08), (cx, cy, ROOF_Z + 0.86), M_METAL_D, col=col))
    obs.append(cyl("TankBody", 0.92, 0.92, 1.42, (cx, cy, ROOF_Z + 1.62), M_TANK, seg=24, col=col))
    obs.append(cyl("TankTop", 0.92, 0.34, 0.2, (cx, cy, ROOF_Z + 2.43), M_TANK, seg=24, col=col))
    for i, z in enumerate((0.95, 1.55, 2.15)):
        obs.append(torus("TankBand%d" % i, 0.925, 0.022, (cx, cy, ROOF_Z + z),
                         M_METAL_D, seg_major=24, seg_minor=6, col=col))

    # 侧面爬梯
    lx = cx - 0.98
    for i, dy in enumerate((-0.22, 0.22)):
        obs.append(box("LadderRail%d" % i, (0.04, 0.04, 1.5),
                       (lx, cy + dy, ROOF_Z + 1.6), M_METAL_D, col=col))
    for i in range(6):
        obs.append(box("LadderRung%d" % i, (0.04, 0.48, 0.03),
                       (lx, cy, ROOF_Z + 1.0 + i * 0.24), M_METAL_D, col=col))

    # 进出水管
    obs.append(cyl("TankPipe", 0.055, 0.055, 0.8, (cx + 0.95, cy + 0.4, ROOF_Z + 0.55),
                   M_METAL_D, seg=8, col=col))
    obs.append(tube("TankPipeBend", [(cx + 0.95, cy + 0.4, ROOF_Z + 0.95),
                                     (cx + 0.95, cy + 0.9, ROOF_Z + 0.95),
                                     (cx + 0.95, cy + 0.9, ROOF_Z + 0.1)],
                    0.05, M_METAL_D, col=col))

    # 水箱编号
    obs.append(box("TankPlate", (0.5, 0.02, 0.24), (cx, cy + 0.93, ROOF_Z + 1.72),
                   M_WHITE, col=col))

    stage_group(obs, 58, 1.2, 16, 'rise')
    return obs


# ================================================================
#  空调外机 / 晾衣绳
# ================================================================
def build_ac(col):
    obs = []
    for i, (x, y) in enumerate(((4.35, -0.75), (4.35, -1.75))):
        obs.append(box("ACBody%d" % i, (0.58, 0.92, 0.66), (x, y, ROOF_Z + 0.33),
                       M_METAL, col=col))
        obs.append(box("ACFront%d" % i, (0.05, 0.84, 0.58), (x - 0.3, y, ROOF_Z + 0.33),
                       M_METAL_D, col=col))
        obs.append(torus("ACRing%d" % i, 0.24, 0.028, (x - 0.325, y, ROOF_Z + 0.34),
                         M_METAL_D, seg_major=18, seg_minor=6,
                         rot=(0, math.pi / 2, 0), col=col))
        for j in range(3):
            a = j * math.pi / 3 + i * 0.4
            ob = box("ACBlade%d_%d" % (i, j), (0.014, 0.4, 0.07),
                     (x - 0.33, y, ROOF_Z + 0.34), M_METAL_D, col=col)
            ob.rotation_euler[0] = a
            obs.append(ob)
        obs.append(tube("ACDrain%d" % i, [(x - 0.1, y - 0.42, ROOF_Z + 0.06),
                                          (x - 0.1, y - 0.75, ROOF_Z + 0.02)],
                        0.018, M_METAL_D, col=col))
    stage_group(obs, 96, 1.2, 14, 'pop')
    return obs


def build_clothesline(col):
    obs = []
    ly = 1.95
    for i, x in enumerate((-4.35, -2.75)):
        obs.append(cyl("LinePole%d" % i, 0.035, 0.028, 2.15, (x, ly, ROOF_Z + 1.075),
                       M_METAL, seg=8, col=col))
        obs.append(box("LineBase%d" % i, (0.22, 0.22, 0.05), (x, ly, ROOF_Z + 0.02),
                       M_METAL_D, col=col))
    obs.append(tube("ClothesLine", [(-4.35, ly, ROOF_Z + 2.12),
                                    (-2.75, ly, ROOF_Z + 2.05)], 0.012,
                    M_METAL_D, col=col))
    cloths = [(-3.98, 0.54, 0.76, M_WHITE, 0.06),
              (-3.42, 0.6, 0.6, M_BLUE, -0.09),
              (-2.92, 0.48, 0.84, M_PINK, 0.04)]
    for i, (x, w, h, mat, rz) in enumerate(cloths):
        ob = box("Cloth%d" % i, (w, 0.03, h), (x, ly + 0.02, ROOF_Z + 2.05 - h / 2), mat,
                 rz=rz, col=col)
        obs.append(ob)
        obs.append(box("Clip%d" % i, (0.04, 0.06, 0.08),
                       (x - w * 0.28, ly + 0.02, ROOF_Z + 2.06), M_METAL_D, col=col))
    stage_group(obs, 100, 1.4, 14, 'pop')
    return obs


# ================================================================
#  霓虹广告牌
# ================================================================
def build_billboard(col):
    obs = []
    cx, cy = 0.0, -4.42
    for i, x in enumerate((-1.05, 1.05)):
        obs.append(cyl("BBPost%d" % i, 0.055, 0.05, 2.4, (x, cy, ROOF_Z + 1.35 + 1.2),
                       M_METAL_D, seg=8, col=col))
    obs.append(box("BBoard", (2.9, 0.14, 1.5), (cx, cy, ROOF_Z + 3.1), M_DARK, col=col))
    # 边框霓虹
    obs.append(box("BBTop", (2.9, 0.05, 0.05), (cx, cy + 0.11, ROOF_Z + 3.83), NEON_PINK, col=col))
    obs.append(box("BBBot", (2.9, 0.05, 0.05), (cx, cy + 0.11, ROOF_Z + 2.37), NEON_PINK, col=col))
    obs.append(box("BBLeft", (0.05, 0.05, 1.5), (cx - 1.43, cy + 0.11, ROOF_Z + 3.1), NEON_PINK, col=col))
    obs.append(box("BBRight", (0.05, 0.05, 1.5), (cx + 1.43, cy + 0.11, ROOF_Z + 3.1), NEON_PINK, col=col))
    obs.extend(neon_text("BBText", "ラーメン", 0.66, (cx, cy + 0.15, ROOF_Z + 3.28),
                         col, NEON_PINK))
    obs.extend(neon_text("BBSub", "深夜営業", 0.2, (cx - 0.18, cy + 0.15, ROOF_Z + 2.67),
                         col, NEON_CYAN))
    obs.append(box("BBLine", (1.6, 0.03, 0.03), (cx, cy + 0.15, ROOF_Z + 2.52),
                   NEON_CYAN, col=col))
    # 顶部射灯架
    obs.append(box("BBLampBar", (2.6, 0.06, 0.06), (cx, cy + 0.05, ROOF_Z + 3.95), M_METAL_D, col=col))
    for i, x in enumerate((-0.9, 0.0, 0.9)):
        obs.append(cyl("BBLamp%d" % i, 0.09, 0.06, 0.18, (x, cy + 0.18, ROOF_Z + 3.9),
                       M_METAL_D, seg=10, rx=math.radians(50), col=col))
        obs.append(cyl("BBBulb%d" % i, 0.06, 0.06, 0.02, (x, cy + 0.26, ROOF_Z + 3.8),
                       NEON_WARM, seg=10, rx=math.radians(50), col=col))
    stage_group(obs, 70, 1.6, 16, 'rise')
    return obs

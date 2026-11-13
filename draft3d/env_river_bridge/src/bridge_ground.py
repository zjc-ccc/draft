# -*- coding: utf-8 -*-
"""
黄昏滨河跨河桥 · 地面层
底座台基 / 河道水面 / 石砌护岸 / 柏油马路与标线 / 人行道 / 绿化带地面
"""

import math

from bridge_core import (HALF, TOP_Z, BED_Z, WATER_Z, RIVER_HALF,
                         PROM_Y0, PROM_Y1, ROAD_Y0, ROAD_Y1,
                         SIDE_Y0, SIDE_Y1, BELT_Y0, BELT_Y1,
                         box, cyl, sphere, rect, slab, toon_mat, emit_mat,
                         stage, stage_group)

ASPHALT = "M_Asphalt"
LINE = "M_RoadLine"
CURB = "M_Curb"
SIDEWALK = "M_Sidewalk"
SIDEWALK_LINE = "M_SidewalkJoint"
BELT_GRASS = "M_BeltGrass"
STONE = "M_StoneWall"
STONE_DARK = "M_StoneDark"
COPING = "M_Coping"
WATER = "M_Water"
WATER_FOAM = "M_WaterFoam"
BASE_BODY = "M_BaseBody"
PLINTH = "M_Plinth"
BED = "M_RiverBed"


def mats():
    toon_mat(ASPHALT, "#43484f")
    toon_mat(LINE, "#f3ead4")
    toon_mat(CURB, "#cec6b4")
    toon_mat(SIDEWALK, "#d6cebc")
    toon_mat(SIDEWALK_LINE, "#b3a996")
    toon_mat(BELT_GRASS, "#6da44d")
    toon_mat(STONE, "#a9a08c")
    toon_mat(STONE_DARK, "#8b8371")
    toon_mat(COPING, "#ded5c0")
    toon_mat(WATER, "#3d89a8")
    toon_mat(WATER_FOAM, "#8ecfdd")
    toon_mat(BASE_BODY, "#c2b79e")
    toon_mat(PLINTH, "#2c2833")
    toon_mat(BED, "#5f6455")


# ---------------------------------------------------------------- 底座
def build_base(col):
    mats()
    obs = []
    obs.append(slab("Base_Plinth", -HALF - 0.16, HALF + 0.16, -HALF - 0.16, HALF + 0.16,
                    -0.54, -0.30, toon_mat(PLINTH, "#2c2833"), col=col))
    obs.append(slab("Base_PlinthRim", -HALF - 0.05, HALF + 0.05, -HALF - 0.05, HALF + 0.05,
                    -0.30, -0.26, toon_mat(STONE_DARK, "#8b8371"), col=col))
    # 河道两侧台基（中间留出河道）
    obs.append(slab("Base_LandN", -HALF, HALF, RIVER_HALF, HALF, -0.30, TOP_Z,
                    toon_mat(BASE_BODY, "#c2b79e"), col=col))
    obs.append(slab("Base_LandS", -HALF, HALF, -HALF, -RIVER_HALF, -0.30, TOP_Z,
                    toon_mat(BASE_BODY, "#c2b79e"), col=col))
    # 河道两端封口（断面）
    for sx in (-1, 1):
        obs.append(slab("Base_RiverEnd%d" % sx, sx * HALF - 0.10 * sx, HALF * sx,
                        -RIVER_HALF, RIVER_HALF, -0.30, TOP_Z,
                        toon_mat(STONE_DARK, "#8b8371"), col=col))
    stage_group(obs, 1, 2.0, 14, 'rise')


# ---------------------------------------------------------------- 河道
def build_river(col):
    obs = []
    obs.append(slab("River_Bed", -HALF, HALF, -RIVER_HALF, RIVER_HALF, BED_Z, BED_Z + 0.04,
                    toon_mat(BED, "#5f6455"), col=col))
    # 水面
    obs.append(rect("River_Water", 0.0, 0.0, HALF * 2 - 0.06, RIVER_HALF * 2 - 0.04,
                    WATER_Z, toon_mat(WATER, "#3d89a8"), col=col))
    # 波纹亮带
    ripples = []
    for i, (yy, ln, w) in enumerate([(0.86, 3.4, 0.05), (0.62, 1.9, 0.035),
                                     (-0.34, 4.2, 0.05), (-0.74, 2.4, 0.035),
                                     (0.18, 1.5, 0.03), (-1.06, 1.8, 0.03)]):
        ripples.append(rect("River_Ripple%d" % i, -2.2 + i * 0.72, yy, ln, w,
                            WATER_Z + 0.004, toon_mat(WATER_FOAM, "#8ecfdd"), col=col))
    stage_group(obs, 6, 3.0, 14, 'rise')
    stage_group(ripples, 9, 1.2, 12, 'pop')


def build_banks(col):
    obs = []
    wall_h = TOP_Z - BED_Z
    for sy in (1, -1):
        y0 = sy * RIVER_HALF
        obs.append(slab("Bank_Wall%s" % ("N" if sy > 0 else "S"),
                        -HALF, HALF, y0 - 0.05, y0 + 0.05, BED_Z, TOP_Z,
                        toon_mat(STONE, "#a9a08c"), col=col))
        # 压顶
        obs.append(slab("Bank_Coping%s" % ("N" if sy > 0 else "S"),
                        -HALF, HALF, y0 - 0.09, y0 + 0.11, TOP_Z - 0.02, TOP_Z + 0.05,
                        toon_mat(COPING, "#ded5c0"), col=col))
        # 砌缝两道
        for k, zz in enumerate((BED_Z + 0.20, BED_Z + 0.40)):
            obs.append(slab("Bank_Joint%s%d" % ("N" if sy > 0 else "S", k),
                            -HALF + 0.05, HALF - 0.05, y0 - 0.07, y0 - 0.045, zz, zz + 0.018,
                            toon_mat(STONE_DARK, "#8b8371"), col=col))
        # 水线（贴水面的一条深色带）
        obs.append(slab("Bank_Waterline%s" % ("N" if sy > 0 else "S"),
                        -HALF + 0.02, HALF - 0.02, y0 - 0.062, y0 - 0.052,
                        WATER_Z - 0.01, WATER_Z + 0.035,
                        toon_mat("M_Waterline", "#2b6b84"), col=col))
    stage_group(obs, 12, 1.6, 13, 'rise')


# ---------------------------------------------------------------- 马路
def build_roads(col):
    mats()
    obs = []
    for sy in (1, -1):
        ya, yb = sorted((sy * ROAD_Y0, sy * ROAD_Y1))
        obs.append(rect("Road_Surface%s" % ("N" if sy > 0 else "S"), 0.0, sy * (ROAD_Y0 + ROAD_Y1) / 2,
                        HALF * 2, ROAD_Y1 - ROAD_Y0, TOP_Z + 0.004,
                        toon_mat(ASPHALT, "#43484f"), col=col))
        # 路缘石
        obs.append(slab("Road_CurbIn%s" % ("N" if sy > 0 else "S"), -HALF, HALF,
                        sy * ROAD_Y0 - 0.05, sy * ROAD_Y0 + 0.03, TOP_Z, TOP_Z + 0.075,
                        toon_mat(CURB, "#cec6b4"), col=col))
        obs.append(slab("Road_CurbOut%s" % ("N" if sy > 0 else "S"), -HALF, HALF,
                        sy * ROAD_Y1 - 0.03, sy * ROAD_Y1 + 0.05, TOP_Z, TOP_Z + 0.075,
                        toon_mat(CURB, "#cec6b4"), col=col))
    stage_group(obs, 20, 2.0, 14, 'rise')


def build_markings(col):
    obs = []
    for sy in (1, -1):
        cy = sy * (ROAD_Y0 + ROAD_Y1) / 2
        # 中央虚线
        x = -HALF + 0.35
        i = 0
        while x < HALF - 0.3:
            obs.append(rect("Road_Dash%s%02d" % ("N" if sy > 0 else "S", i),
                            x, cy, 0.42, 0.055, TOP_Z + 0.010,
                            toon_mat(LINE, "#f3ead4"), col=col))
            x += 0.86
            i += 1
        # 两侧实线
        for k, yy in enumerate((sy * (ROAD_Y0 + 0.34), sy * (ROAD_Y1 - 0.34))):
            obs.append(rect("Road_Edge%s%d" % ("N" if sy > 0 else "S", k),
                            0.0, yy, HALF * 2 - 0.2, 0.045, TOP_Z + 0.010,
                            toon_mat(LINE, "#f3ead4"), col=col))
        # 斑马线（桥侧人行道前）
        for m in range(7):
            obs.append(rect("Road_Zebra%s%d" % ("N" if sy > 0 else "S", m),
                            4.62, sy * (ROAD_Y0 + 0.20 + m * 0.30), 0.62, 0.16,
                            TOP_Z + 0.011, toon_mat(LINE, "#f3ead4"), col=col))
    stage_group(obs, 26, 0.55, 10, 'pop')


# ---------------------------------------------------------------- 人行道 / 绿化带
def build_walkways(col):
    obs = []
    for sy in (1, -1):
        ya, yb = sorted((sy * SIDE_Y0, sy * SIDE_Y1))
        obs.append(slab("Walk_Sidewalk%s" % ("N" if sy > 0 else "S"),
                        -HALF, HALF, ya, yb, TOP_Z, TOP_Z + 0.07,
                        toon_mat(SIDEWALK, "#d6cebc"), col=col))
        # 铺装缝
        x = -HALF + 0.42
        i = 0
        while x < HALF - 0.2:
            obs.append(rect("Walk_Joint%s%02d" % ("N" if sy > 0 else "S", i),
                            x, sy * (SIDE_Y0 + SIDE_Y1) / 2, 0.022, SIDE_Y1 - SIDE_Y0 - 0.06,
                            TOP_Z + 0.074, toon_mat(SIDEWALK_LINE, "#b3a996"), col=col))
            x += 0.5
            i += 1
        # 滨河步道
        ya2, yb2 = sorted((sy * PROM_Y0, sy * PROM_Y1))
        obs.append(slab("Walk_Promenade%s" % ("N" if sy > 0 else "S"),
                        -HALF, HALF, ya2, yb2, TOP_Z, TOP_Z + 0.05,
                        toon_mat(STONE, "#a9a08c"), col=col))
        # 绿化带草面
        ya3, yb3 = sorted((sy * BELT_Y0, sy * BELT_Y1))
        obs.append(slab("Walk_Belt%s" % ("N" if sy > 0 else "S"),
                        -HALF, HALF, ya3, yb3, TOP_Z, TOP_Z + 0.10,
                        toon_mat(BELT_GRASS, "#6da44d"), col=col))
        # 绿化带外侧石缘
        obs.append(slab("Walk_BeltCurb%s" % ("N" if sy > 0 else "S"), -HALF, HALF,
                        sy * BELT_Y0 - 0.045, sy * BELT_Y0 + 0.045, TOP_Z, TOP_Z + 0.14,
                        toon_mat(COPING, "#ded5c0"), col=col))
    stage_group(obs, 32, 1.4, 14, 'rise')


# ---------------------------------------------------------------- 碎石 / 河边细节
def build_river_detail(col):
    obs = []
    # 水面靠岸的浅色水线
    for sy in (1, -1):
        obs.append(rect("River_Shore%s" % ("N" if sy > 0 else "S"), 0.0,
                        sy * (RIVER_HALF - 0.10), HALF * 2 - 0.1, 0.07,
                        WATER_Z + 0.005, toon_mat(WATER_FOAM, "#8ecfdd"), col=col))
    # 河床零星石块
    rocks = []
    for i, (x, y, r) in enumerate([(-4.3, 0.9, 0.12), (-2.6, -1.0, 0.10), (1.4, 1.05, 0.09),
                                   (3.2, -0.95, 0.11), (0.4, 1.15, 0.08), (-1.2, -1.15, 0.07)]):
        rocks.append(sphere("River_Rock%d" % i, r, (x, y, WATER_Z - 0.02),
                            toon_mat(STONE_DARK, "#8b8371"), seg=8, col=col))
    stage_group(obs, 16, 1.2, 12, 'rise')
    stage_group(rocks, 17, 1.0, 12, 'pop')

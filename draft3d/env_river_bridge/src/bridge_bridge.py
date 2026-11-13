# -*- coding: utf-8 -*-
"""
黄昏滨河跨河桥 · 桥体层
石砌桥台 / 钢拱吊杆 / 木板桥面 / 白色栏杆 / 两端平台与楼梯 / 桥灯牌匾
"""

import math

from bridge_core import (TOP_Z, DECK_Z, DECK_BOT, DECK_HALF, DECK_END, BED_Z,
                         PROM_Y0, ROAD_Y0, SIDE_Y0, SIDE_Y1,
                         box, cyl, sphere, rect, slab, tube, poly, prism,
                         toon_mat, emit_mat, text_mesh, stage, stage_group,
                         arch_pts)

STONE = "M_BridgeStone"
STONE_TRIM = "M_BridgeStoneTrim"
PLANK_A = "M_PlankA"
PLANK_B = "M_PlankB"
BEAM = "M_BridgeBeam"
STEEL = "M_SteelRed"
HANGER = "M_Hanger"
RAIL = "M_RailWhite"
STAIR = "M_StairStone"
CONCRETE = "M_Column"
LAMP = "M_BridgeLamp"
PLAQUE = "M_Plaque"
PLAQUE_TXT = "M_PlaqueText"

STAIR_TOP = TOP_Z + 0.07          # 人行道顶面
STAIR_X0 = DECK_HALF              # 楼梯起点 X
STAIR_STEPS = 9
STAIR_TREAD = 0.25
STAIR_RUN = STAIR_STEPS * STAIR_TREAD
STAIR_Y0, STAIR_Y1 = SIDE_Y0 - 0.02, SIDE_Y1 + 0.02
LAND_Y0, LAND_Y1 = DECK_END - 0.06, SIDE_Y1 + 0.02


def mats():
    toon_mat(STONE, "#b4a88f")
    toon_mat(STONE_TRIM, "#cfc4a9")
    toon_mat(PLANK_A, "#b07a52")
    toon_mat(PLANK_B, "#a06e49")
    toon_mat(BEAM, "#8f8574")
    toon_mat(STEEL, "#cf5138")
    toon_mat(HANGER, "#e9e2d2")
    toon_mat(RAIL, "#f0e9da")
    toon_mat(STAIR, "#c8bda4")
    toon_mat(CONCRETE, "#d8d1c0")
    toon_mat(PLAQUE, "#eae2ce")
    toon_mat(PLAQUE_TXT, "#22303f")
    emit_mat(LAMP, "#ffd79b", 1.0)


# ---------------------------------------------------------------- 桥台 / 支柱
def build_abutments(col):
    obs = []
    for sy in (1, -1):
        tag = "N" if sy > 0 else "S"
        y0, y1 = sorted((sy * 1.24, sy * 1.96))
        obs.append(box("Abutment_%s" % tag, (2.06, y1 - y0, DECK_BOT + 0.04 - BED_Z),
                       (0.0, (y0 + y1) / 2, (BED_Z + DECK_BOT + 0.04) / 2),
                       toon_mat(STONE, "#b4a88f"), col=col))
        # 台帽压顶
        obs.append(box("Abutment_Cap%s" % tag, (2.16, y1 - y0 + 0.10, 0.07),
                       (0.0, (y0 + y1) / 2, DECK_BOT + 0.045),
                       toon_mat(STONE_TRIM, "#cfc4a9"), col=col))
        # 拱脚垫石
        for sx in (-1, 1):
            obs.append(box("Abutment_Pad%s%d" % (tag, sx), (0.16, 0.20, 0.12),
                           (sx * 0.72, sy * 1.30, TOP_Z + 0.06),
                           toon_mat(STONE_TRIM, "#cfc4a9"), col=col))
        # 端部立柱（撑桥面跨马路）
        for sx in (-1, 1):
            obs.append(cyl("Column_%s%d" % (tag, sx), 0.105, 0.105, DECK_BOT - TOP_Z,
                           (sx * 0.62, sy * (ROAD_Y0 + 0.34), (TOP_Z + DECK_BOT) / 2),
                           toon_mat(CONCRETE, "#d8d1c0"), seg=14, col=col))
            obs.append(cyl("ColumnCap_%s%d" % (tag, sx), 0.16, 0.13, 0.07,
                           (sx * 0.62, sy * (ROAD_Y0 + 0.34), DECK_BOT - 0.02),
                           toon_mat(CONCRETE, "#d8d1c0"), seg=14, col=col))
            obs.append(box("ColumnBase_%s%d" % (tag, sx), (0.32, 0.32, 0.08),
                           (sx * 0.62, sy * (ROAD_Y0 + 0.34), TOP_Z + 0.04),
                           toon_mat(STONE_TRIM, "#cfc4a9"), col=col))
    stage_group(obs, 38, 1.2, 14, 'rise')


# ---------------------------------------------------------------- 钢拱
def build_arch(col):
    obs = []
    z_spring, z_peak = TOP_Z + 0.06, DECK_BOT - 0.10
    pts = arch_pts(-1.50, 1.50, z_spring, z_peak, n=16)
    for sx in (-1, 1):
        rib = tube("Arch_Rib%d" % sx, [(sx * 0.72, y, z) for y, z in pts],
                   0.058, toon_mat(STEEL, "#cf5138"), col=col, res=6, bevel_res=2)
        stage(rib, 46, 12, 'pop')
        obs.append(rib)
    # 横向剪刀撑
    for i, k in enumerate((0.0, 0.45, -0.45)):
        y = k * 1.5
        t = y / 1.5
        z = z_spring + (z_peak - z_spring) * (1.0 - t * t) - 0.09
        obs.append(box("Arch_Brace%d" % i, (1.44, 0.06, 0.05), (0.0, y, z),
                       toon_mat(STEEL, "#cf5138"), col=col))
    # 吊杆
    for i in range(13):
        y = -1.32 + i * 0.22
        t = y / 1.5
        z = z_spring + (z_peak - z_spring) * (1.0 - t * t)
        for sx in (-1, 1):
            obs.append(tube("Hanger_%d%d" % (i, sx),
                            [(sx * 0.72, y, z), (sx * 0.72, y, DECK_BOT)],
                            0.014, toon_mat(HANGER, "#e9e2d2"), col=col, res=3))
    stage_group(obs, 49, 0.5, 10, 'pop')


# ---------------------------------------------------------------- 桥面
def build_deck(col):
    mats()
    obs = []
    # 桥面底板
    obs.append(box("Deck_Slab", (DECK_HALF * 2, DECK_END * 2, DECK_Z - 0.07 - DECK_BOT),
                   (0.0, 0.0, (DECK_BOT + DECK_Z - 0.07) / 2),
                   toon_mat(BEAM, "#8f8574"), col=col))
    # 桥面板（顺桥向长条）
    n = 6
    pw = DECK_HALF * 2 / n
    for i in range(n):
        x = -DECK_HALF + pw * (i + 0.5)
        m = toon_mat(PLANK_A if i % 2 == 0 else PLANK_B,
                     "#b07a52" if i % 2 == 0 else "#a06e49")
        obs.append(box("Deck_Plank%d" % i, (pw - 0.012, DECK_END * 2 - 0.02, 0.07),
                       (x, 0.0, DECK_Z - 0.035), m, col=col))
    # 两侧边梁
    for sx in (-1, 1):
        obs.append(box("Deck_EdgeBeam%d" % sx, (0.09, DECK_END * 2, 0.22),
                       (sx * (DECK_HALF + 0.005), 0.0, DECK_Z - 0.09),
                       toon_mat(STEEL, "#cf5138"), col=col))
    # 端横梁
    for sy in (1, -1):
        obs.append(box("Deck_EndBeam%d" % sy, (DECK_HALF * 2 + 0.1, 0.10, 0.20),
                       (0.0, sy * (DECK_END - 0.04), DECK_Z - 0.09),
                       toon_mat(STEEL, "#cf5138"), col=col))
    stage_group(obs, 54, 0.8, 12, 'rise')


def build_deck_railing(col):
    obs = []
    rail_z = DECK_Z + 0.63
    for sx in (-1, 1):
        x = sx * (DECK_HALF - 0.05)
        # 立柱
        y = -DECK_END + 0.12
        i = 0
        while y <= DECK_END - 0.10:
            obs.append(box("Rail_Post%d_%02d" % (sx, i), (0.05, 0.05, 0.63),
                           (x, y, DECK_Z + 0.315), toon_mat(RAIL, "#f0e9da"), col=col))
            y += 0.42
            i += 1
        # 上下横杆
        obs.append(tube("Rail_Top%d" % sx, [(x, -DECK_END, rail_z), (x, DECK_END, rail_z)],
                        0.030, toon_mat(RAIL, "#f0e9da"), col=col, res=4))
        obs.append(tube("Rail_Mid%d" % sx, [(x, -DECK_END, DECK_Z + 0.36), (x, DECK_END, DECK_Z + 0.36)],
                        0.018, toon_mat(RAIL, "#f0e9da"), col=col, res=4))
    stage_group(obs, 60, 0.35, 10, 'rise')


# ---------------------------------------------------------------- 平台与楼梯
def build_landing(col, sy):
    tag = "N" if sy > 0 else "S"
    obs = []
    y0, y1 = sorted((sy * LAND_Y0, sy * LAND_Y1))
    obs.append(box("Landing_Slab%s" % tag, (DECK_HALF * 2, y1 - y0, 0.10),
                   (0.0, (y0 + y1) / 2, DECK_Z - 0.05),
                   toon_mat(BEAM, "#8f8574"), col=col))
    # 平台铺板
    obs.append(box("Landing_Deck%s" % tag, (DECK_HALF * 2 - 0.02, y1 - y0 - 0.02, 0.03),
                   (0.0, (y0 + y1) / 2, DECK_Z + 0.015),
                   toon_mat(PLANK_A, "#b07a52"), col=col))
    # 平台支柱
    for sx in (-1, 1):
        obs.append(cyl("Landing_Col%s%d" % (tag, sx), 0.10, 0.10, DECK_Z - 0.10 - TOP_Z,
                       (sx * 0.55, sy * (SIDE_Y1 - 0.22), (TOP_Z + DECK_Z - 0.10) / 2),
                       toon_mat(CONCRETE, "#d8d1c0"), seg=14, col=col))
    stage_group(obs, 64, 1.2, 12, 'rise')
    return obs


def build_stair(col, sy):
    tag = "N" if sy > 0 else "S"
    sx = 1 if sy > 0 else -1          # 南北两侧楼梯分列左右，构图平衡
    obs = []
    y0, y1 = sorted((sy * STAIR_Y0, sy * STAIR_Y1))
    rise = (DECK_Z - STAIR_TOP) / STAIR_STEPS
    # 每级踏面各自落地，侧面呈清晰阶梯
    for i in range(STAIR_STEPS):
        xa = sx * (STAIR_X0 + STAIR_TREAD * i)
        xb = sx * (STAIR_X0 + STAIR_TREAD * (i + 1))
        z = DECK_Z - rise * (i + 1)
        obs.append(box("Stair_%s_%02d" % (tag, i),
                       (STAIR_TREAD, y1 - y0, z - TOP_Z),
                       ((xa + xb) / 2, (y0 + y1) / 2, (TOP_Z + z) / 2),
                       toon_mat(STAIR, "#c8bda4"), col=col))
    # 梯段外沿矮墙
    obs.append(slab("Stair_Wall%s" % tag,
                    min(sx * STAIR_X0, sx * (STAIR_X0 + STAIR_RUN)),
                    max(sx * STAIR_X0, sx * (STAIR_X0 + STAIR_RUN)),
                    sy * (STAIR_Y1 - 0.02), sy * STAIR_Y1 + 0.02,
                    TOP_Z, STAIR_TOP + 0.06,
                    toon_mat(STONE_TRIM, "#cfc4a9"), col=col))
    stage_group(obs, 68, 0.7, 12, 'rise')
    return obs


def build_stair_railing(col, sy):
    tag = "N" if sy > 0 else "S"
    sx = 1 if sy > 0 else -1
    obs = []
    y = sy * (STAIR_Y1 - 0.05)
    z_hi = DECK_Z + 0.63
    z_lo = STAIR_TOP + 0.63
    # 斜扶手
    obs.append(tube("StairRail_Top%s" % tag,
                    [(sx * STAIR_X0, y, z_hi), (sx * (STAIR_X0 + STAIR_RUN), y, z_lo)],
                    0.030, toon_mat(RAIL, "#f0e9da"), col=col, res=4))
    # 栏杆立柱随踏步下降
    n = 6
    for i in range(n + 1):
        k = i / n
        x = sx * (STAIR_X0 + STAIR_RUN * k)
        z = z_hi + (z_lo - z_hi) * k
        obs.append(box("StairRail_Post%s%02d" % (tag, i), (0.045, 0.045, 0.63),
                       (x, y, z - 0.315), toon_mat(RAIL, "#f0e9da"), col=col))
    # 平台外沿栏杆
    land_y = sy * (LAND_Y1 - 0.03)
    for i, x in enumerate((sx * 0.78, 0.0, -sx * 0.72)):
        obs.append(box("LandingRail_Post%s%d" % (tag, i), (0.045, 0.045, 0.63),
                       (x, land_y, DECK_Z + 0.315), toon_mat(RAIL, "#f0e9da"), col=col))
    obs.append(tube("LandingRail_Top%s" % tag,
                    [(-0.80, land_y, DECK_Z + 0.63), (0.80, land_y, DECK_Z + 0.63)],
                    0.030, toon_mat(RAIL, "#f0e9da"), col=col, res=4))
    stage_group(obs, 72, 0.45, 10, 'pop')


# ---------------------------------------------------------------- 桥灯 / 牌匾
def build_bridge_detail(col):
    obs = []
    for sy in (1, -1):
        for sx in (-1, 1):
            x, y = sx * (DECK_HALF - 0.09), sy * (SIDE_Y0 + 0.12)
            obs.append(cyl("BridgeLamp_Post%d%d" % (sy, sx), 0.032, 0.030, 0.52,
                           (x, y, DECK_Z + 0.26), toon_mat(RAIL, "#f0e9da"), seg=10, col=col))
            obs.append(sphere("BridgeLamp_Head%d%d" % (sy, sx), 0.075,
                              (x, y, DECK_Z + 0.56), emit_mat(LAMP, "#ffd79b", 1.0),
                              seg=10, col=col))
    stage_group(obs, 76, 0.6, 12, 'pop')

    # 桥名牌（挂在桥面端梁立面，正对桥下马路）
    plaque = []
    for sy in (1, -1):
        tag = "N" if sy > 0 else "S"
        y = sy * (DECK_END + 0.075)
        plaque.append(box("Plaque_%s" % tag, (0.80, 0.03, 0.20),
                          (0.0, y, DECK_Z - 0.12),
                          toon_mat(PLAQUE, "#eae2ce"), col=col))
        rot = (math.radians(90), 0, 0 if sy > 0 else math.pi)
        t = text_mesh("Plaque_Text%s" % tag, "望江桥", 0.115,
                      (0.0, y + sy * 0.019, DECK_Z - 0.125), rot,
                      toon_mat(PLAQUE_TXT, "#22303f"), col=col)
        if t:
            plaque.append(t)
    stage_group(plaque, 80, 1.0, 10, 'pop')
    return obs


# ---------------------------------------------------------------- 汇总
def build_bridge(col):
    mats()
    build_abutments(col)
    build_arch(col)
    build_deck(col)
    build_deck_railing(col)
    for sy in (1, -1):
        build_landing(col, sy)
        build_stair(col, sy)
        build_stair_railing(col, sy)
    build_bridge_detail(col)

# -*- coding: utf-8 -*-
"""主视觉：屋台拉面摊（台车、雨棚、暖帘、灯笼、灯箱、操作台、桌凳）"""

import math
from ramen_core import (ROOF_Z, toon_mat, emit_mat, box, cyl, sphere, plane,
                        torus, tube, text_mesh, stage_group)

M_WOOD = toon_mat("StallWood", "#5a3928")
M_WOOD2 = toon_mat("StallWood2", "#7a5136")
M_WOOD_L = toon_mat("StallWoodLight", "#96683f")
M_RED = toon_mat("StallRed", "#bf3a30", emit=0.18)
M_RED_D = toon_mat("StallRedDark", "#8e2a24")
M_CLOTH = toon_mat("NorenCloth", "#2b4270", emit=0.12)
M_CLOTH_D = toon_mat("NorenClothDark", "#203258", emit=0.12)
M_STEEL = toon_mat("Steel", "#c3cad5")
M_STEEL_D = toon_mat("SteelDark", "#7e8794")
M_BAMBOO = toon_mat("Bamboo", "#b78d55")
M_BAMBOO_D = toon_mat("BambooDark", "#8d6a3c")
M_BOWL = toon_mat("Bowl", "#ece6d6")
M_BOWL_R = toon_mat("BowlRim", "#b83a34")
M_SOUP = emit_mat("Soup", "#dda45a", 1.0)
M_DARK = toon_mat("DarkPanel", "#12161f")
M_METAL_D = toon_mat("StallMetalDark", "#2a3240")
M_METAL = toon_mat("StallMetal", "#7d8798")
M_PAPER_R = emit_mat("PaperRed", "#ff5d3a", 1.9)
M_PAPER_W = emit_mat("PaperWarm", "#ffcf94", 1.7)
M_WHITE = toon_mat("White", "#e9e4d6")
M_SIGN = emit_mat("SignFace", "#ffe2b4", 1.5)
M_NEON_P = emit_mat("StallNeonPink", "#ff4f9a", 2.6)
M_NEON_C = emit_mat("StallNeonCyan", "#4fd8ff", 2.3)
M_MENU = toon_mat("MenuPaper", "#d9d1bd")
M_PLASTIC = toon_mat("StoolRed", "#c23f36", emit=0.05)
M_FOOD = toon_mat("Food", "#c98c4d")

CX, CY = 0.0, 0.45
COUNT = ROOF_Z + 1.08          # 台面高度
ROOFTOP = COUNT + 1.62         # 车顶高度


# ================================================================
#  台车主体
# ================================================================
def build_stall(col):
    obs = []
    W, D = 3.5, 1.8
    # 柜体
    obs.append(box("CartBody", (W, D, 1.0), (CX, CY, ROOF_Z + 0.5), M_WOOD, col=col))
    obs.append(box("CartInset", (W - 0.18, D - 0.12, 0.74), (CX, CY, ROOF_Z + 0.56), M_WOOD2, col=col))
    # 前脸竖条
    for i in range(11):
        x = -1.55 + i * 0.31
        obs.append(box("SlatF%d" % i, (0.035, 0.03, 0.82), (x, CY + D / 2 + 0.005, ROOF_Z + 0.52),
                       M_WOOD_L, col=col))
    for i in range(9):
        x = 1.78
        obs.append(box("SlatR%d" % i, (0.03, 0.035, 0.82), (x, -0.32 + i * 0.19, ROOF_Z + 0.52),
                       M_WOOD_L, col=col))
    # 侧墙菜单纸
    for i in range(2):
        obs.append(box("SideMenu%d" % i, (0.022, 0.24, 0.38),
                       (1.812, -0.34 + i * 0.26, ROOF_Z + 0.68), M_MENU, col=col))
        obs.append(box("SideMenuInk%d" % i, (0.012, 0.16, 0.03),
                       (1.826, -0.34 + i * 0.26, ROOF_Z + 0.79), M_RED_D, col=col))

    # 前脸红底白字招牌
    obs.append(box("CartBanner", (2.0, 0.022, 0.36), (CX, 1.383, ROOF_Z + 0.52), M_RED, col=col))
    obs.append(box("CartBannerEdge", (2.04, 0.012, 0.03), (CX, 1.394, ROOF_Z + 0.68), M_RED_D, col=col))
    bt = text_mesh("CartText", "らーめん", 0.19, (CX, 1.399, ROOF_Z + 0.52),
                   (math.pi / 2, 0, math.pi), M_WHITE, col, 0.0)
    if bt:
        obs.append(bt)

    # 轮子
    for i, x in enumerate((-1.62, 1.62)):
        obs.append(cyl("Wheel%d" % i, 0.3, 0.3, 0.11, (x, CY + 0.52, ROOF_Z + 0.2),
                       M_METAL_D, seg=18, ry=math.pi / 2, col=col))
        obs.append(cyl("WheelHub%d" % i, 0.1, 0.1, 0.13, (x, CY + 0.52, ROOF_Z + 0.2),
                       M_STEEL_D, seg=12, ry=math.pi / 2, col=col))
        obs.append(box("AxleMount%d" % i, (0.1, 0.18, 0.5), (x, CY + 0.5, ROOF_Z + 0.25),
                       M_WOOD2, col=col))

    # 台面
    obs.append(box("CounterTop", (3.8, 2.0, 0.08), (CX, CY, COUNT - 0.04), M_WOOD_L, col=col))
    obs.append(box("CounterEdge", (3.86, 2.06, 0.05), (CX, CY, COUNT - 0.095), M_WOOD2, col=col))

    # 侧板（右侧只做后半段，保证视线能看进操作台）
    obs.append(box("SideL", (0.09, 1.9, 1.62), (-1.76, CY, COUNT + 0.85), M_WOOD2, col=col))
    obs.append(box("SideR", (0.09, 0.72, 1.62), (1.76, -0.18, COUNT + 0.85), M_WOOD2, col=col))
    obs.append(box("BackWall", (3.6, 0.09, 1.62), (CX, -0.48, COUNT + 0.85), M_WOOD, col=col))

    # 立柱
    for i, (x, y) in enumerate(((-1.72, 1.34), (1.72, 1.34), (-1.72, -0.42), (1.72, -0.42))):
        obs.append(box("Post%d" % i, (0.07, 0.07, ROOFTOP - COUNT), (x, y, (COUNT + ROOFTOP) / 2),
                       M_WOOD2, col=col))

    # 车顶
    obs.append(box("StallRoof", (4.1, 2.3, 0.1), (CX, 0.4, ROOFTOP + 0.05), M_WOOD, col=col))
    obs.append(box("RoofTrimF", (4.14, 0.08, 0.12), (CX, 1.52, ROOFTOP - 0.02), M_WOOD2, col=col))
    obs.append(box("RoofTrimB", (4.14, 0.08, 0.12), (CX, -0.72, ROOFTOP - 0.02), M_WOOD2, col=col))
    for i in range(7):
        x = -1.8 + i * 0.6
        obs.append(box("RoofBatten%d" % i, (0.05, 2.24, 0.035), (x, 0.4, ROOFTOP + 0.11), M_WOOD2, col=col))
    # 顶部红色塑料雨棚
    awn = box("Awning", (4.15, 1.2, 0.05), (CX, 2.05, 2.86), M_RED, col=col)
    awn.rotation_euler[0] = math.radians(-20)
    obs.append(awn)
    obs.append(box("AwningEdge", (4.16, 0.07, 0.09), (CX, 2.62, 2.66), M_RED_D, col=col))
    for i, x in enumerate((-1.95, 1.95)):
        obs.append(cyl("AwningPole%d" % i, 0.032, 0.032, 2.3, (x, 2.52, ROOF_Z + 1.15),
                       M_METAL_D, seg=8, col=col))
        obs.append(box("AwningFoot%d" % i, (0.16, 0.16, 0.04), (x, 2.52, ROOF_Z + 0.02),
                       M_METAL_D, col=col))
        obs.append(tube("AwningStay%d" % i, [(x, 2.52, 2.58), (x, 1.62, ROOFTOP + 0.02)],
                        0.026, M_METAL_D, col=col))

    # 暖帘（5 片）
    for i in range(5):
        x = -1.36 + i * 0.68
        mat = M_CLOTH if i % 2 == 0 else M_CLOTH_D
        obs.append(box("Noren%d" % i, (0.65, 0.025, 0.5), (x, 2.46, 2.42), mat, col=col))
    obs.append(box("NorenRod", (3.62, 0.05, 0.05), (CX, 2.46, 2.69), M_WOOD2, col=col))
    for i in range(5):
        if i == 2:
            continue
        obs.append(cyl("NorenDot%d" % i, 0.115, 0.115, 0.012, (-1.36 + i * 0.68, 2.482, 2.47),
                       M_WHITE, seg=16, rx=math.pi / 2, col=col))
    tx = text_mesh("NorenText", "らーめん", 0.23, (0.0, 2.488, 2.36),
                   (math.pi / 2, 0, math.pi), M_WHITE, col, 0.0)
    if tx:
        obs.append(tx)
    else:
        obs.append(cyl("NorenMark", 0.11, 0.11, 0.012, (0.0, 2.482, 2.38),
                       M_WHITE, seg=16, rx=math.pi / 2, col=col))

    tail = build_interior(col)
    obs.extend(tail)
    body = obs[:len(obs) - len(tail)] if tail else obs
    stage_group(body, 26, 1.1, 16, 'rise')
    return obs


# ================================================================
#  操作台内部
# ================================================================
def build_interior(col):
    o = []
    # 后墙层架
    o.append(box("ShelfA", (3.3, 0.3, 0.055), (CX, -0.3, COUNT + 0.52), M_WOOD_L, col=col))
    o.append(box("ShelfB", (3.3, 0.28, 0.05), (CX, -0.31, COUNT + 1.02), M_WOOD_L, col=col))
    for i in range(2):
        o.append(box("ShelfBracketA%d" % i, (0.05, 0.26, 0.4), (-1.4 + i * 2.8, -0.35, COUNT + 0.32),
                     M_WOOD2, col=col))
    # 瓶罐
    bottle_cols = ["#b9402f", "#d8b25e", "#3f6b4a", "#e0d6bf", "#8b4a2f", "#4a6c8c"]
    for i in range(11):
        x = -1.42 + i * 0.27
        h = 0.18 + (i % 3) * 0.05
        o.append(cyl("Bottle%d" % i, 0.05, 0.045, h, (x, -0.28, COUNT + 0.58 + h / 2),
                     toon_mat("Bottle%d" % (i % 6), bottle_cols[i % 6]), seg=8, col=col))
        if i % 3 == 0:
            o.append(cyl("BottleCap%d" % i, 0.025, 0.025, 0.03,
                         (x, -0.28, COUNT + 0.59 + h), M_STEEL_D, seg=8, col=col))
    # 上层碗
    for i in range(4):
        x = -1.3 + i * 0.32
        o.append(cyl("ShelfBowl%d" % i, 0.11, 0.085, 0.09, (x, -0.3, COUNT + 1.1),
                     M_BOWL, seg=14, col=col))
    for i in range(4):
        x = 0.1 + i * 0.1
        o.append(cyl("CanStack%d" % i, 0.055, 0.055, 0.11, (1.25 - (i % 2) * 0.12, -0.3,
                     COUNT + 1.1 + (i // 2) * 0.11), M_RED_D, seg=10, col=col))

    # 大汤锅
    o.append(cyl("BigPot", 0.29, 0.27, 0.42, (-0.95, 0.28, COUNT + 0.21), M_STEEL, seg=18, col=col))
    o.append(cyl("BigPotSoup", 0.25, 0.25, 0.02, (-0.95, 0.28, COUNT + 0.40), M_SOUP, seg=18, col=col))
    o.append(torus("BigPotRim", 0.29, 0.018, (-0.95, 0.28, COUNT + 0.42), M_STEEL_D,
                   seg_major=18, seg_minor=6, col=col))
    o.append(box("PotHandleL", (0.1, 0.05, 0.03), (-1.27, 0.28, COUNT + 0.38), M_STEEL_D, col=col))
    o.append(box("PotHandleR", (0.1, 0.05, 0.03), (-0.63, 0.28, COUNT + 0.38), M_STEEL_D, col=col))

    # 小锅
    o.append(cyl("SubPot", 0.19, 0.18, 0.3, (-0.28, 0.56, COUNT + 0.15), M_STEEL_D, seg=16, col=col))
    o.append(cyl("SubPotSoup", 0.16, 0.16, 0.02, (-0.28, 0.56, COUNT + 0.30), M_SOUP, seg=16, col=col))

    # 蒸笼
    for i in range(3):
        o.append(cyl("Steamer%d" % i, 0.27, 0.27, 0.11, (0.42, 0.3, COUNT + 0.055 + i * 0.115),
                     M_BAMBOO, seg=18, col=col))
        o.append(cyl("SteamerRim%d" % i, 0.285, 0.285, 0.025, (0.42, 0.3, COUNT + 0.11 + i * 0.115),
                     M_BAMBOO_D, seg=18, col=col))
    o.append(cyl("SteamerLid", 0.29, 0.08, 0.1, (0.42, 0.3, COUNT + 0.4), M_BAMBOO, seg=18, col=col))
    o.append(cyl("SteamerKnob", 0.04, 0.04, 0.04, (0.42, 0.3, COUNT + 0.47), M_BAMBOO_D, seg=8, col=col))

    # 碗、砧板、刀、调料
    for i in range(3):
        o.append(cyl("Bowl%d" % i, 0.1, 0.075, 0.07, (1.0, 0.52, COUNT + 0.035 + i * 0.06),
                     M_BOWL, seg=14, col=col))
        o.append(torus("BowlRim%d" % i, 0.1, 0.012, (1.0, 0.52, COUNT + 0.07 + i * 0.06),
                       M_BOWL_R, seg_major=14, seg_minor=5, col=col))
    o.append(box("Board", (0.44, 0.3, 0.035), (1.28, 0.02, COUNT + 0.02), M_WOOD_L, col=col))
    o.append(box("Knife", (0.26, 0.05, 0.012), (1.26, 0.06, COUNT + 0.045), M_STEEL, rz=0.3, col=col))
    for i in range(2):
        o.append(cyl("Sauce%d" % i, 0.045, 0.04, 0.18, (1.4 - i * 0.14, 0.38, COUNT + 0.09),
                     M_DARK if i == 0 else M_RED_D, seg=8, col=col))
    o.append(box("ChopBox", (0.14, 0.09, 0.12), (-1.38, 0.58, COUNT + 0.06), M_WOOD2, col=col))

    # 长柄勺、夹子挂杆
    o.append(tube("Rail", [(-0.55, -0.42, COUNT + 1.42), (1.5, -0.42, COUNT + 1.42)],
                  0.012, M_STEEL_D, col=col))
    for i, x in enumerate((0.0, 0.28, 0.56)):
        o.append(box("Hook%d" % i, (0.02, 0.02, 0.12), (x, -0.42, COUNT + 1.36), M_STEEL_D, col=col))
        o.append(cyl("Ladle%d" % (i % 2), 0.07, 0.06, 0.03, (x, -0.42, COUNT + 1.24),
                     M_STEEL, seg=10, col=col))
        o.append(box("LadleHandle%d" % i, (0.02, 0.02, 0.2), (x, -0.42, COUNT + 1.33), M_STEEL, col=col))

    # 菜单纸条
    for i in range(4):
        o.append(box("MenuStrip%d" % i, (0.2, 0.012, 0.34), (-0.5 + i * 0.36, -0.425, COUNT + 1.02),
                     M_MENU, col=col))
        o.append(box("MenuInk%d" % i, (0.13, 0.006, 0.03), (-0.5 + i * 0.36, -0.432, COUNT + 1.1),
                     M_RED_D, col=col))
    # 后墙小挂钟
    o.append(cyl("Clock", 0.12, 0.12, 0.04, (1.35, -0.43, COUNT + 1.0), M_WHITE, seg=16,
                 rx=math.pi / 2, col=col))
    o.append(cyl("ClockFace", 0.1, 0.1, 0.045, (1.35, -0.44, COUNT + 1.0), M_DARK, seg=16,
                 rx=math.pi / 2, col=col))

    # 顶部灯带 + 吊灯
    o.append(box("InnerStrip", (3.2, 0.05, 0.04), (CX, -0.2, ROOFTOP - 0.1), emit_mat("StripWarm", "#ffd9a4", 2.2), col=col))
    for i, x in enumerate((-1.0, 0.65)):
        o.append(tube("LampCord%d" % i, [(x, 0.25, ROOFTOP - 0.1), (x, 0.25, 2.78)], 0.008,
                      M_METAL_D, col=col))
        o.append(cyl("Shade%d" % i, 0.16, 0.09, 0.14, (x, 0.25, 2.72), M_RED_D, seg=14, col=col))
        o.append(cyl("Bulb%d" % i, 0.05, 0.05, 0.04, (x, 0.25, 2.63), emit_mat("BulbWarm", "#ffca86", 3.0),
                     seg=10, col=col))

    # 热气
    for i in range(5):
        x = -0.95 + (i % 2) * 0.55 + (i // 2) * 0.18
        r = 0.1 + 0.03 * (i % 3)
        o.append(sphere("Steam%d" % i, r, (x, 0.3 + (i % 2) * 0.12, 1.95 + i * 0.11),
                        emit_mat("SteamMat", "#ffd9b4", 0.35), seg=8, col=col))

    stage_group(o, 34, 1.0, 14, 'pop')
    return o


# ================================================================
#  灯笼串 / 灯箱 / 招牌
# ================================================================
def build_lanterns(col):
    obs = []
    pts = [(-2.02, 2.5, 2.62), (-1.4, 2.53, 2.56), (-0.45, 2.55, 2.52),
           (0.5, 2.55, 2.52), (1.45, 2.53, 2.56), (2.0, 2.5, 2.62)]
    obs.append(tube("LanternWire", pts, 0.012, M_METAL_D, col=col))
    xs = [-1.62, -0.92, 0.92, 1.62]
    for i, x in enumerate(xs):
        z = 2.31
        mat = M_PAPER_R if i % 2 == 0 else M_PAPER_W
        obs.append(cyl("Lantern%d" % i, 0.135, 0.135, 0.3, (x, 2.55, z), mat, seg=14, col=col))
        obs.append(cyl("LanternCapT%d" % i, 0.07, 0.07, 0.04, (x, 2.55, z + 0.17), M_DARK, seg=10, col=col))
        obs.append(cyl("LanternCapB%d" % i, 0.07, 0.07, 0.04, (x, 2.55, z - 0.17), M_DARK, seg=10, col=col))
        obs.append(tube("LanternCord%d" % i, [(x, 2.55, z + 0.19), (x, 2.55, z + 0.27)],
                        0.008, M_METAL_D, col=col))
        obs.append(torus("LanternRing%d" % i, 0.135, 0.008, (x, 2.55, z), M_DARK,
                         seg_major=14, seg_minor=4, rot=(math.pi / 2, 0, 0), col=col))
    stage_group(obs, 62, 1.4, 14, 'pop')
    return obs


def build_signs(col):
    obs = []
    # 立式灯箱
    lx, ly = 2.42, 1.62
    obs.append(box("LightBox", (0.6, 0.26, 1.5), (lx, ly, ROOF_Z + 0.75), M_DARK, col=col))
    obs.append(box("LightBoxFace", (0.5, 0.02, 1.34), (lx, ly + 0.14, ROOF_Z + 0.76), M_SIGN, col=col))
    obs.append(box("LightBoxTop", (0.66, 0.32, 0.06), (lx, ly, ROOF_Z + 1.52), M_RED_D, col=col))
    obs.append(box("LightBoxBase", (0.66, 0.34, 0.06), (lx, ly, ROOF_Z + 0.03), M_RED_D, col=col))
    tx = text_mesh("BoxText", "ら\nー\nめ\nん", 0.19, (lx, ly + 0.152, ROOF_Z + 0.78),
                   (math.pi / 2, 0, math.pi), M_RED_D, col, 0.0)
    if tx:
        obs.append(tx)
    else:
        for i in range(4):
            obs.append(box("BoxBar%d" % i, (0.16, 0.01, 0.1), (lx, ly + 0.155, ROOF_Z + 0.45 + i * 0.22),
                           M_RED_D, col=col))

    # 车顶小霓虹 24H
    obs.append(box("NeonBack", (0.56, 0.05, 0.26), (1.86, 1.2, ROOFTOP + 0.28), M_DARK, col=col))
    nt = text_mesh("Neon24", "24H", 0.19, (1.86, 1.235, ROOFTOP + 0.28),
                   (math.pi / 2, 0, math.pi), M_NEON_C, col, 0.006)
    if nt:
        obs.append(nt)
    else:
        obs.append(box("Neon24Bar", (0.4, 0.02, 0.06), (1.86, 1.235, ROOFTOP + 0.28), M_NEON_C, col=col))

    # 侧挂小招牌
    obs.append(box("SideSign", (0.06, 0.7, 0.42), (1.9, -0.05, COUNT + 1.05), M_DARK, col=col))
    obs.append(box("SideSignEdge", (0.02, 0.7, 0.04), (1.94, -0.05, COUNT + 1.24), M_NEON_P, col=col))
    obs.append(tube("SideSignHang", [(1.88, -0.4, COUNT + 1.3), (1.88, 0.3, COUNT + 1.3)],
                    0.02, M_METAL_D, col=col))

    # 左侧幟旗
    obs.append(cyl("NoboriPole", 0.028, 0.028, 2.5, (-2.42, 2.05, ROOF_Z + 1.25), M_METAL, seg=8, col=col))
    obs.append(box("NoboriFlag", (0.44, 0.02, 1.28), (-2.19, 2.05, ROOF_Z + 1.78), M_RED, col=col))
    obs.append(box("NoboriBar", (0.5, 0.035, 0.035), (-2.2, 2.05, ROOF_Z + 2.4), M_METAL_D, col=col))
    nt2 = text_mesh("NoboriText", "ラ\nー\nメ\nン", 0.17, (-2.185, 2.065, ROOF_Z + 1.8),
                    (math.pi / 2, 0, math.pi), M_WHITE, col, 0.0)
    if nt2:
        obs.append(nt2)

    stage_group(obs, 72, 1.6, 16, 'pop')
    return obs


# ================================================================
#  折叠桌与塑料凳
# ================================================================
def build_seating(col):
    obs = []
    # 折叠桌
    tx, ty = -0.15, 3.22
    obs.append(box("TableTop", (1.32, 0.8, 0.06), (tx, ty, ROOF_Z + 0.68), M_WOOD_L, col=col))
    obs.append(box("TableEdge", (1.36, 0.84, 0.03), (tx, ty, ROOF_Z + 0.645), M_WOOD2, col=col))
    for sx in (-1, 1):
        for sy in (-1, 1):
            leg = box("TableLeg%d%d" % (sx, sy), (0.04, 0.04, 0.7),
                      (tx + sx * 0.55, ty + sy * 0.3, ROOF_Z + 0.33), M_METAL, col=col)
            leg.rotation_euler[0] = sy * math.radians(7)
            leg.rotation_euler[1] = -sx * math.radians(6)
            obs.append(leg)
    # 桌面餐具
    for i, dx in enumerate((-0.28, 0.26)):
        obs.append(cyl("TblBowl%d" % i, 0.11, 0.08, 0.08, (tx + dx, ty + 0.05, ROOF_Z + 0.75),
                       M_BOWL, seg=14, col=col))
        obs.append(cyl("TblSoup%d" % i, 0.09, 0.09, 0.015, (tx + dx, ty + 0.05, ROOF_Z + 0.785),
                       M_SOUP, seg=14, col=col))
        obs.append(box("Chop%d" % i, (0.22, 0.014, 0.012), (tx + dx + 0.02, ty - 0.17, ROOF_Z + 0.715),
                       M_WOOD2, rz=0.2 - i * 0.4, col=col))
    obs.append(cyl("TblBottle", 0.055, 0.05, 0.24, (tx + 0.5, ty - 0.1, ROOF_Z + 0.83),
                   toon_mat("BeerBottle", "#8a5a2a"), seg=10, col=col))
    obs.append(box("TblMenu", (0.22, 0.3, 0.012), (tx - 0.05, ty + 0.3, ROOF_Z + 0.72),
                   M_MENU, rz=0.2, col=col))

    # 塑料凳
    stools = [(-1.18, 3.08, 0.35), (1.02, 3.3, -0.4), (1.62, 2.55, 0.9)]
    for i, (x, y, rz) in enumerate(stools):
        obs.append(cyl("StoolSeat%d" % i, 0.2, 0.18, 0.07, (x, y, ROOF_Z + 0.5), M_PLASTIC,
                       seg=14, rz=rz, col=col))
        for j in range(4):
            a = rz + j * math.pi / 2 + math.pi / 4
            lx = math.cos(a) * 0.13
            ly = math.sin(a) * 0.13
            leg = box("StoolLeg%d_%d" % (i, j), (0.04, 0.04, 0.5),
                      (x + lx, y + ly, ROOF_Z + 0.25), M_PLASTIC, col=col)
            leg.rotation_euler[0] = -ly * 0.7
            leg.rotation_euler[1] = lx * 0.7
            obs.append(leg)
        obs.append(torus("StoolRing%d" % i, 0.16, 0.014, (x, y, ROOF_Z + 0.18), M_PLASTIC,
                         seg_major=14, seg_minor=5, col=col))

    # 靠台面的高脚凳
    obs.append(cyl("BarStoolSeat", 0.18, 0.18, 0.06, (0.85, 2.05, ROOF_Z + 0.62), M_PLASTIC,
                   seg=14, col=col))
    obs.append(cyl("BarStoolPost", 0.035, 0.035, 0.6, (0.85, 2.05, ROOF_Z + 0.31), M_METAL_D, seg=8, col=col))
    obs.append(cyl("BarStoolBase", 0.19, 0.19, 0.04, (0.85, 2.05, ROOF_Z + 0.02), M_METAL_D, seg=14, col=col))

    stage_group(obs, 118, 1.2, 14, 'pop')
    return obs

# -*- coding: utf-8 -*-
"""
黄昏滨河跨河桥 · 外卖店与收货点
S 侧（Blender -Y）人行道上的外卖门面：主体 / 灯箱招牌 / 遮阳棚 / 橱窗 /
取餐窗口 / 外卖架 / 取餐光圈 / 菜单立牌 / 送餐电动车
N 侧人行道的收货点：光圈 / 立牌 / 待取包裹
"""

import math

from bridge_core import (TOP_Z,
                         SHOP_X0, SHOP_X1, SHOP_BACK_Y, SHOP_FRONT_Y,
                         SHOP_H, SHOP_TOP, SHOP_PICK_X, SHOP_PICK_Y,
                         DROP_X, DROP_Y,
                         box, cyl, tube,
                         toon_mat, emit_mat, text_mesh, stage_group,
                         add_light)

SIDE_TOP = TOP_Z + 0.07
CX = (SHOP_X0 + SHOP_X1) / 2.0
CY = (SHOP_BACK_Y + SHOP_FRONT_Y) / 2.0
W = SHOP_X1 - SHOP_X0
D = SHOP_FRONT_Y - SHOP_BACK_Y
FRONT = SHOP_FRONT_Y

WALL = "M_ShopWall"
WALL_DARK = "M_ShopWallDark"
ROOF = "M_ShopRoof"
TRIM = "M_ShopTrim"
RED = "M_ShopRed"
CREAM = "M_ShopCream"
SIGN = "M_ShopSign"
SIGN_TXT = "M_ShopSignText"
GLASS = "M_ShopGlass"
DARK = "M_ShopDark"
COUNTER = "M_ShopCounter"
METAL = "M_ShopMetal"
BAG = "M_ShopBag"
BAG_BAND = "M_ShopBagBand"
SCOOT = "M_ScooterBody"
SCOOT_BOX = "M_ScooterBox"
DROP_RING = "M_DropRing"
DROP_DISC = "M_DropDisc"
GLOW = "M_ShopGlow"
CARTON = "M_Carton"
CARTON_TAPE = "M_CartonTape"


def mats():
    toon_mat(WALL, "#e6d2b4")
    toon_mat(WALL_DARK, "#b9a184")
    toon_mat(ROOF, "#7c5a45")
    toon_mat(TRIM, "#f4ecdc")
    toon_mat(RED, "#c9483c")
    toon_mat(CREAM, "#f6ead0")
    toon_mat(SIGN_TXT, "#b3352b")
    toon_mat(DARK, "#2f2822")
    toon_mat(COUNTER, "#9b6a44")
    toon_mat(METAL, "#565c64")
    toon_mat(BAG, "#e7c383")
    toon_mat(BAG_BAND, "#cf6a4a")
    toon_mat(SCOOT, "#4c7ea8")
    toon_mat(SCOOT_BOX, "#f2c14e")
    toon_mat(DROP_DISC, "#bfe6dc")
    toon_mat(CARTON, "#c8a06a")
    toon_mat(CARTON_TAPE, "#e8dcc0")
    emit_mat(SIGN, "#fdf3d8", 0.85)
    emit_mat(GLASS, "#ffcb8c", 0.55)
    emit_mat(GLOW, "#ffd08f", 0.90)
    emit_mat(DROP_RING, "#79d7c0", 0.90)


def ring(name, cx, cy, r, z, mat, col, tr=0.012, seg=28):
    pts = [(cx + r * math.cos(2.0 * math.pi * i / seg),
            cy + r * math.sin(2.0 * math.pi * i / seg), z) for i in range(seg)]
    return tube(name, pts, tr, mat, col=col, res=3, close=True)


# ---------------------------------------------------------------- 外卖门面
def build_shop_front(col):
    obs = []
    # 主体 / 勒脚 / 檐口
    obs.append(box("Shop_Body", (W, D, SHOP_H), (CX, CY, TOP_Z + SHOP_H / 2),
                   toon_mat(WALL, "#e6d2b4"), col=col))
    obs.append(box("Shop_Plinth", (W + 0.06, D + 0.05, 0.14), (CX, CY, TOP_Z + 0.07),
                   toon_mat(WALL_DARK, "#b9a184"), col=col))
    obs.append(box("Shop_Roof", (W + 0.14, D + 0.14, 0.10), (CX, CY, SHOP_TOP + 0.05),
                   toon_mat(ROOF, "#7c5a45"), col=col))
    obs.append(box("Shop_RoofTrim", (W + 0.18, D + 0.18, 0.03), (CX, CY, SHOP_TOP + 0.015),
                   toon_mat(TRIM, "#f4ecdc"), col=col))

    # 灯箱招牌（外框 + 发光面板 + 文字）
    obs.append(box("Shop_SignFrame", (W - 0.26, 0.04, 0.34), (CX, FRONT + 0.030, 1.12),
                   toon_mat(ROOF, "#7c5a45"), col=col))
    obs.append(box("Shop_Sign", (W - 0.34, 0.07, 0.28), (CX, FRONT + 0.035, 1.12),
                   emit_mat(SIGN, "#fdf3d8", 0.85), col=col))
    t = text_mesh("Shop_SignText", "麦香外卖", 0.20, (CX, FRONT + 0.078, 1.12),
                  (math.radians(90), 0.0, math.pi),
                  toon_mat(SIGN_TXT, "#b3352b"), col=col)
    if t:
        obs.append(t)

    # 橱窗
    obs.append(box("Shop_WindowFrame", (1.66, 0.06, 0.52), (CX - 0.55, FRONT + 0.010, 0.70),
                   toon_mat(TRIM, "#f4ecdc"), col=col))
    obs.append(box("Shop_Window", (1.54, 0.03, 0.42), (CX - 0.55, FRONT + 0.045, 0.70),
                   emit_mat(GLASS, "#ffcb8c", 0.55), col=col))
    obs.append(box("Shop_WindowMullion", (0.04, 0.04, 0.42), (CX - 0.55, FRONT + 0.055, 0.70),
                   toon_mat(TRIM, "#f4ecdc"), col=col))

    # 遮阳棚（红白条纹，向前下倾）
    n = 6
    sw = (W - 0.18) / n
    for i in range(n):
        m = toon_mat(RED if i % 2 == 0 else CREAM,
                     "#c9483c" if i % 2 == 0 else "#f6ead0")
        board = box("Shop_Awning%d" % i, (sw, 0.32, 0.03),
                    (SHOP_X0 + 0.09 + sw * (i + 0.5), FRONT + 0.17, 0.960), m, col=col)
        board.rotation_euler[0] = math.radians(-12)
        obs.append(board)
    obs.append(box("Shop_AwningValance", (W - 0.18, 0.025, 0.085),
                   (CX, FRONT + 0.325, 0.875),
                   toon_mat(CREAM, "#f6ead0"), col=col))
    vt = text_mesh("Shop_AwningText", "取餐窗口", 0.062, (CX, FRONT + 0.340, 0.874),
                   (math.radians(90), 0.0, math.pi),
                   toon_mat(RED, "#c9483c"), col=col)
    if vt:
        obs.append(vt)

    stage_group(obs, 112, 0.8, 16, 'rise')


# ---------------------------------------------------------------- 取餐口 / 外卖架
def build_pickup(col):
    obs = []
    wx = SHOP_PICK_X
    # 取餐窗口
    obs.append(box("Shop_HatchBack", (0.86, 0.05, 0.42), (wx, FRONT + 0.015, 0.70),
                   toon_mat(DARK, "#2f2822"), col=col))
    obs.append(box("Shop_HatchGlass", (0.74, 0.02, 0.32), (wx, FRONT + 0.045, 0.70),
                   emit_mat(GLASS, "#ffcb8c", 0.55), col=col))
    obs.append(box("Shop_HatchCounter", (0.94, 0.18, 0.045), (wx, FRONT + 0.09, 0.50),
                   toon_mat(COUNTER, "#9b6a44"), col=col))
    for sx in (-1, 1):
        obs.append(box("Shop_HatchJamb%d" % sx, (0.045, 0.05, 0.46),
                       (wx + sx * 0.45, FRONT + 0.020, 0.70),
                       toon_mat(TRIM, "#f4ecdc"), col=col))

    # 外卖架（店面西端，板上放三份外卖）
    rx, ry = -7.02, -4.82
    for sx in (-1, 1):
        for sy in (-1, 1):
            obs.append(box("Shop_RackLeg%d%d" % (sx, sy), (0.035, 0.035, 0.40),
                           (rx + sx * 0.30, ry + sy * 0.11, SIDE_TOP + 0.20),
                           toon_mat(METAL, "#565c64"), col=col))
    for k, zz in enumerate((0.44, 0.62, 0.80)):
        obs.append(box("Shop_RackShelf%d" % k, (0.64, 0.26, 0.025),
                       (rx, ry, zz), toon_mat(METAL, "#565c64"), col=col))
    for i, sx in enumerate((-0.21, 0.0, 0.21)):
        obs.append(box("Shop_Bag%d" % i, (0.15, 0.11, 0.17),
                       (rx + sx, ry, 0.715), toon_mat(BAG, "#e7c383"), col=col))
        obs.append(box("Shop_BagBand%d" % i, (0.158, 0.118, 0.028),
                       (rx + sx, ry, 0.755), toon_mat(BAG_BAND, "#cf6a4a"), col=col))

    # 取餐光圈（地面标识，玩法里按坐标判定）
    obs.append(cyl("Shop_PickDisc", 0.21, 0.21, 0.010,
                   (SHOP_PICK_X, SHOP_PICK_Y, SIDE_TOP + 0.006),
                   toon_mat(TRIM, "#f4ecdc"), seg=24, col=col))
    obs.append(ring("Shop_PickRing", SHOP_PICK_X, SHOP_PICK_Y, 0.235,
                    SIDE_TOP + 0.014, emit_mat(GLOW, "#ffd08f", 0.90), col))

    # 菜单立牌
    obs.append(box("Shop_MenuBoard", (0.30, 0.028, 0.28), (-4.26, -4.72, SIDE_TOP + 0.24),
                   toon_mat(CREAM, "#f6ead0"), col=col))
    for sx in (-1, 1):
        obs.append(box("Shop_MenuLeg%d" % sx, (0.022, 0.022, 0.12),
                       (-4.26 + sx * 0.11, -4.72, SIDE_TOP + 0.06),
                       toon_mat(METAL, "#565c64"), col=col))
    mt = text_mesh("Shop_MenuText", "取餐", 0.085, (-4.26, -4.704, SIDE_TOP + 0.25),
                   (math.radians(90), 0.0, math.pi),
                   toon_mat(RED, "#c9483c"), col=col)
    if mt:
        obs.append(mt)

    # 屋顶空调外机
    obs.append(box("Shop_AC", (0.30, 0.22, 0.16), (-6.98, -5.66, SHOP_TOP + 0.13),
                   toon_mat(METAL, "#565c64"), col=col))

    stage_group(obs, 122, 0.5, 12, 'pop')


# ---------------------------------------------------------------- 送餐电动车
def build_scooter(col):
    obs = []
    x, y = -6.55, -4.12
    z = TOP_Z
    for i, wx in enumerate((-0.28, 0.28)):
        obs.append(cyl("Scoot_Wheel%d" % i, 0.085, 0.085, 0.05,
                       (x + wx, y, z + 0.085), toon_mat(DARK, "#2f2822"),
                       seg=16, rx=math.radians(90), col=col))
    obs.append(box("Scoot_Deck", (0.52, 0.15, 0.035), (x, y, z + 0.13),
                   toon_mat(METAL, "#565c64"), col=col))
    obs.append(box("Scoot_Body", (0.34, 0.13, 0.13), (x - 0.10, y, z + 0.23),
                   toon_mat(SCOOT, "#4c7ea8"), col=col))
    obs.append(box("Scoot_Seat", (0.20, 0.11, 0.045), (x + 0.16, y, z + 0.33),
                   toon_mat(DARK, "#2f2822"), col=col))
    column = box("Scoot_Column", (0.04, 0.04, 0.30), (x - 0.30, y, z + 0.30),
                 toon_mat(METAL, "#565c64"), col=col)
    column.rotation_euler[1] = math.radians(14)
    obs.append(column)
    obs.append(box("Scoot_Bar", (0.04, 0.30, 0.035), (x - 0.335, y, z + 0.44),
                   toon_mat(METAL, "#565c64"), col=col))
    obs.append(box("Scoot_Box", (0.20, 0.22, 0.24), (x + 0.32, y, z + 0.54),
                   toon_mat(SCOOT_BOX, "#f2c14e"), col=col))
    obs.append(box("Scoot_BoxBand", (0.205, 0.225, 0.035), (x + 0.32, y, z + 0.58),
                   toon_mat(RED, "#c9483c"), col=col))
    stage_group(obs, 128, 0.6, 12, 'pop')


# ---------------------------------------------------------------- 收货点
def build_drop(col):
    obs = []
    obs.append(cyl("Drop_Disc", 0.24, 0.24, 0.010, (DROP_X, DROP_Y, SIDE_TOP + 0.006),
                   toon_mat(DROP_DISC, "#bfe6dc"), seg=24, col=col))
    obs.append(ring("Drop_Ring", DROP_X, DROP_Y, 0.255, SIDE_TOP + 0.014,
                    emit_mat(DROP_RING, "#79d7c0", 0.90), col))

    # 收货立牌
    bx, by = DROP_X - 0.48, DROP_Y - 0.02
    obs.append(box("Drop_Board", (0.32, 0.028, 0.28), (bx, by, SIDE_TOP + 0.24),
                   toon_mat(CREAM, "#f6ead0"), col=col))
    for sx in (-1, 1):
        obs.append(box("Drop_BoardLeg%d" % sx, (0.022, 0.022, 0.12),
                       (bx + sx * 0.12, by, SIDE_TOP + 0.06),
                       toon_mat(METAL, "#565c64"), col=col))
    t = text_mesh("Drop_BoardText", "收货点", 0.080, (bx, by - 0.016, SIDE_TOP + 0.25),
                  (math.radians(90), 0.0, 0.0),
                  toon_mat(SIGN_TXT, "#b3352b"), col=col)
    if t:
        obs.append(t)

    # 待取包裹
    parcels = [(0.42, 0.06, 0.10, 0.22, 0.20), (0.44, -0.20, 0.09, 0.18, 0.16),
               (0.44, 0.06, 0.29, 0.16, 0.15)]
    for i, (dx, dy, dz, pw, pd) in enumerate(parcels):
        obs.append(box("Drop_Parcel%d" % i, (pw, pd, 0.18),
                       (DROP_X + dx, DROP_Y + dy, SIDE_TOP + dz),
                       toon_mat(CARTON, "#c8a06a"), col=col))
        obs.append(box("Drop_ParcelTape%d" % i, (0.045, pd + 0.004, 0.185),
                       (DROP_X + dx, DROP_Y + dy, SIDE_TOP + dz),
                       toon_mat(CARTON_TAPE, "#e8dcc0"), col=col))
    stage_group(obs, 132, 0.5, 12, 'pop')


# ---------------------------------------------------------------- 汇总
def build_shop(col):
    mats()
    build_shop_front(col)
    build_pickup(col)
    build_scooter(col)
    build_drop(col)
    add_light("ShopGlow", 'POINT', (SHOP_PICK_X, -4.60, 1.18), 26, "#ffb96a", size=0.28)

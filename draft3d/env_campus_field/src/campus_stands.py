# -*- coding: utf-8 -*-
"""阶梯看台 / 座椅 / 顶棚 / 栏杆 / 主席台 / 计分牌 / 场地投光灯"""

import math

from campus_core import (TOP_Z, toon_mat, emit_mat, box, cyl, sphere, rect, quad,
                         tube, text_mesh, stage_group)

M_STAND = toon_mat("StandConc", "#ded7c7")
M_STAND_D = toon_mat("StandConcD", "#c6bfae")
M_SEAT = toon_mat("SeatBlue", "#3f6fae")
M_SEAT_L = toon_mat("SeatLight", "#a7c8de")
M_STEEL = toon_mat("Steel", "#a8b1bb")
M_STEEL_D = toon_mat("SteelDark", "#7c858f")
M_ROOF = toon_mat("Roof", "#e3ddce")
M_ROOF_D = toon_mat("RoofDark", "#c8c2b2")
M_PANEL = toon_mat("Panel", "#2c3239")
M_WALL = toon_mat("Wall", "#d9d1c1")
M_LED = emit_mat("LEDAmber", "#ffb45c", 2.2)
M_LAMP = emit_mat("FloodLamp", "#fff0cf", 3.0)

FRONT_X = -2.72
ROW_TREAD = 0.50
ROW_RISE = 0.22
ROWS = 5
STAND_Y0, STAND_Y1 = -1.85, 3.05
STAND_CY = (STAND_Y0 + STAND_Y1) / 2
STAND_LEN = STAND_Y1 - STAND_Y0


def _row_x(i):
    return FRONT_X - ROW_TREAD * (i + 0.5)


def _row_top(i):
    return TOP_Z + ROW_RISE * (i + 1)


def build_stand(col):
    obs = []
    for i in range(ROWS):
        h = ROW_RISE * (i + 1)
        obs.append(box("StandRow%d" % i, (ROW_TREAD, STAND_LEN, h),
                       (_row_x(i), STAND_CY, TOP_Z + h / 2), M_STAND, col=col))
        # 踏面收边
        obs.append(box("StandEdge%d" % i, (0.03, STAND_LEN, 0.035),
                       (FRONT_X - ROW_TREAD * i - 0.015, STAND_CY, _row_top(i) + 0.017),
                       M_STAND_D, col=col))
    # 后墙
    obs.append(box("StandBackWall", (0.14, STAND_LEN, 1.62),
                   (FRONT_X - ROW_TREAD * ROWS - 0.02, STAND_CY, TOP_Z + 0.81), M_WALL, col=col))
    # 两侧封边
    for s, y in ((-1, STAND_Y0 - 0.05), (1, STAND_Y1 + 0.05)):
        for i in range(ROWS):
            obs.append(box("StandSide%d_%d" % (s, i), (ROW_TREAD, 0.10, ROW_RISE * (i + 1)),
                           (_row_x(i), y, TOP_Z + ROW_RISE * (i + 1) / 2), M_STAND_D, col=col))
    stage_group(obs, 54, 0.7, 12, 'pop')
    return obs


def build_seats(col):
    obs = []
    n = 14
    span = STAND_LEN - 0.5
    for i in range(ROWS):
        top = _row_top(i)
        rx = _row_x(i)
        for k in range(n):
            y = STAND_Y0 + 0.25 + span * k / (n - 1)
            if i == ROWS - 1 and -0.28 < y < 1.58:
                continue
            mat = M_SEAT if (i + k) % 2 else M_SEAT_L
            obs.append(box("Seat%d_%d" % (i, k), (0.19, 0.20, 0.05),
                           (rx + 0.05, y, top + 0.03), mat, col=col))
            obs.append(box("SeatBack%d_%d" % (i, k), (0.05, 0.20, 0.13),
                           (rx - 0.07, y, top + 0.095), mat, col=col))
    stage_group(obs, 62, 0.35, 10, 'pop')
    return obs


def build_railing(col):
    obs = []
    # 前缘栏杆
    for k in range(9):
        y = STAND_Y0 - 0.02 + (STAND_LEN + 0.04) * k / 8
        obs.append(cyl("RailPost%d" % k, 0.018, 0.018, 0.62, (FRONT_X + 0.06, y, TOP_Z + 0.31),
                       M_STEEL, seg=8, col=col))
    for i, h in enumerate((0.60, 0.34)):
        obs.append(cyl("RailBar%d" % i, 0.014, 0.014, STAND_LEN + 0.04,
                       (FRONT_X + 0.06, STAND_CY, TOP_Z + h), M_STEEL,
                       seg=8, rx=math.radians(90), col=col))
    # 后墙顶栏杆
    bx = FRONT_X - ROW_TREAD * ROWS - 0.02
    for k in range(5):
        y = STAND_Y0 + 0.1 + (STAND_LEN - 0.2) * k / 4
        obs.append(cyl("RailTopPost%d" % k, 0.015, 0.015, 0.24, (bx, y, TOP_Z + 1.74),
                       M_STEEL_D, seg=8, col=col))
    obs.append(cyl("RailTopBar", 0.014, 0.014, STAND_LEN - 0.2,
                   (bx, STAND_CY, TOP_Z + 1.85), M_STEEL_D, seg=8, rx=math.radians(90), col=col))
    stage_group(obs, 70, 0.8, 12, 'pop')
    return obs


def build_canopy(col):
    obs = []
    bx = FRONT_X - ROW_TREAD * ROWS - 0.02
    # 顶棚（向后略微抬升）
    roof = box("Roof", (2.96, STAND_LEN + 0.44, 0.08), (-3.95, STAND_CY, TOP_Z + 1.50), M_ROOF, col=col)
    roof.rotation_euler[1] = math.radians(6.2)
    obs.append(roof)
    roof2 = box("RoofUnder", (2.86, STAND_LEN + 0.36, 0.03), (-3.95, STAND_CY, TOP_Z + 1.455), M_ROOF_D, col=col)
    roof2.rotation_euler[1] = math.radians(6.2)
    obs.append(roof2)
    # 屋面檩条
    for k in range(9):
        y = STAND_Y0 - 0.18 + (STAND_LEN + 0.36) * k / 8
        rib = box("RoofRib%d" % k, (2.90, 0.045, 0.035), (-3.95, y, TOP_Z + 1.555), M_ROOF_D, col=col)
        rib.rotation_euler[1] = math.radians(6.2)
        obs.append(rib)
    # 前檐板
    obs.append(box("Fascia", (0.06, STAND_LEN + 0.44, 0.17), (-2.48, STAND_CY, TOP_Z + 1.27),
                   toon_mat("FasciaBlue", "#9db7c8"), col=col))
    # 后支撑柱
    for k in range(4):
        y = STAND_Y0 + 0.35 + (STAND_LEN - 0.7) * k / 3
        obs.append(cyl("PostBack%d" % k, 0.038, 0.038, 0.72, (bx + 0.04, y, TOP_Z + 1.24),
                       M_STEEL_D, seg=10, col=col))
    # 前立柱（两端）
    for s in (-1, 1):
        y = STAND_CY + s * (STAND_LEN / 2 + 0.12)
        obs.append(cyl("PostFront%d" % s, 0.042, 0.042, 1.42, (-2.55, y, TOP_Z + 0.71),
                       M_STEEL_D, seg=10, col=col))
    stage_group(obs, 66, 1.6, 14, 'rise')
    return obs


def build_scoreboard(col):
    obs = []
    obs.append(box("ScorePanel", (0.05, 1.36, 0.40), (-2.40, -1.30, TOP_Z + 1.27), M_PANEL, col=col))
    obs.append(box("ScorePanelRim", (0.03, 1.42, 0.46), (-2.43, -1.30, TOP_Z + 1.27), M_STEEL_D, col=col))
    t = text_mesh("ScoreText", "3 : 2", 0.19, (-2.36, -1.30, TOP_Z + 1.27),
                  (math.radians(90), 0, math.radians(90)), M_LED, col=col)
    if t:
        obs.append(t)
    # 主席台铭牌
    t2 = text_mesh("PodiumSign", "主席台", 0.17, (-2.42, 0.62, TOP_Z + 1.27),
                   (math.radians(90), 0, math.radians(90)), toon_mat("SignWhite", "#f7f3e8"), col=col)
    if t2:
        obs.append(t2)
    # 校训横幅
    t3 = text_mesh("MottoStand", "阳光体育", 0.19, (-2.42, 1.95, TOP_Z + 1.27),
                   (math.radians(90), 0, math.radians(90)), toon_mat("SignRed", "#d1483a"), col=col)
    if t3:
        obs.append(t3)
    stage_group(obs, 74, 1.6, 12, 'pop')
    return obs


def build_podium(col):
    obs = []
    bx = _row_x(ROWS - 1)
    top = _row_top(ROWS - 1)
    obs.append(box("PodiumDeck", (0.50, 1.60, 0.05), (bx, 0.65, top + 0.025), M_ROOF_D, col=col))
    for i in range(3):
        y = 0.10 + i * 0.55
        obs.append(box("PodiumDesk%d" % i, (0.30, 0.42, 0.10), (bx + 0.02, y, top + 0.13), M_ROOF, col=col))
        obs.append(box("PodiumChair%d" % i, (0.22, 0.20, 0.06), (bx - 0.16, y, top + 0.09), M_SEAT, col=col))
        obs.append(box("PodiumChairB%d" % i, (0.05, 0.20, 0.20), (bx - 0.26, y, top + 0.18), M_SEAT, col=col))
    stage_group(obs, 78, 1.0, 12, 'pop')
    return obs


def build_floodlights(col):
    obs = []
    for i, y in enumerate((STAND_Y0 - 0.25, STAND_Y1 + 0.25)):
        x = -5.52
        obs.append(cyl("FloodPole%d" % i, 0.05, 0.035, 2.55, (x, y, TOP_Z + 1.28), M_STEEL_D, seg=10, col=col))
        obs.append(box("FloodBar%d" % i, (0.10, 0.62, 0.06), (x - 0.02, y, TOP_Z + 2.58), M_STEEL_D, col=col))
        for k in range(3):
            obs.append(box("FloodHead%d_%d" % (i, k), (0.16, 0.14, 0.09),
                           (x + 0.10, y - 0.22 + k * 0.22, TOP_Z + 2.56), M_LAMP, col=col))
    stage_group(obs, 82, 1.2, 14, 'rise')
    return obs

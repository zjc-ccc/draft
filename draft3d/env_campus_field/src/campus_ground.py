# -*- coding: utf-8 -*-
"""底座 / 道路 / 塑胶跑道 / 足球场 / 跳远沙坑 / 落叶"""

import math
import random

import bpy

from campus_core import (TOP_Z, HALF, TRACK_CX, TRACK_CY, R_OUT, R_IN, S_HALF,
                         LANE_W, TRACK_W,
                         toon_mat, box, cyl, sphere, plane, rect, quad, torus, tube,
                         strip, ring_strip, stadium_fill, flat_ring, arc_ring,
                         rect_outline, text_mesh, stage_group, link)

random.seed(7)

M_GRASS = toon_mat("Grass", "#86b268")
M_GRASS_D = toon_mat("GrassDark", "#79a55d")
M_SLAB = toon_mat("Slab", "#e4dece")
M_SLAB_D = toon_mat("SlabDark", "#8f8a7e")
M_TRACK = toon_mat("TrackRed", "#c9573f")
M_TRACK_D = toon_mat("TrackRedDark", "#ad473a")
M_WHITE = toon_mat("LineWhite", "#f5f2e7")
M_TURF = toon_mat("Turf", "#57a05a")
M_TURF_D = toon_mat("TurfDark", "#488d4c")
M_SAND = toon_mat("Sand", "#ddc78f")
M_ASPHALT = toon_mat("Asphalt", "#6d7278")
M_WALK = toon_mat("Walkway", "#d6cebd")
M_CONCRETE = toon_mat("Concrete", "#cfc8b8")
M_METAL = toon_mat("Steel", "#aab3bd")
M_NET = toon_mat("NetWhite", "#eef2f4")
M_LEAF_A = toon_mat("LeafOrange", "#d98a45")
M_LEAF_B = toon_mat("LeafYellow", "#e0b757")


def tri(name, verts, mat, col):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], [(0, 1, 2)])
    me.update()
    ob = bpy.data.objects.new(name, me)
    link(ob, col)
    if mat:
        me.materials.append(mat)
    return ob


# ================================================================
#  底座
# ================================================================
def build_base(col):
    obs = []
    obs.append(box("BaseSlab", (HALF * 2, HALF * 2, 0.46), (0, 0, TOP_Z - 0.23), M_SLAB, col=col))
    obs.append(box("BasePlinth", (HALF * 2 + 0.5, HALF * 2 + 0.5, 0.14), (0, 0, -0.10), M_SLAB_D, col=col))
    obs.append(box("BaseLip", (HALF * 2 + 0.16, HALF * 2 + 0.16, 0.05), (0, 0, -0.035), M_SLAB, col=col))
    obs.append(plane("GrassTop", HALF * 2 - 0.02, HALF * 2 - 0.02, (0, 0, TOP_Z + 0.002), M_GRASS, col=col))
    # 草坪深浅块，打破单调
    patches = [(-3.6, 4.6, 3.0, 1.8, 0.0), (4.2, 4.4, 2.4, 2.0, 0.1),
               (-4.4, -3.4, 2.6, 2.2, -0.12), (3.2, -2.9, 3.0, 2.0, 0.06)]
    for i, (x, y, w, d, rz) in enumerate(patches):
        obs.append(rect("GrassPatch%d" % i, x, y, w, d, TOP_Z + 0.003, M_GRASS_D, rz=rz, col=col))
    stage_group([obs[0], obs[1], obs[2]], 1, 2, 10, 'rise')
    stage_group([obs[3], obs[4], obs[5], obs[6], obs[7]], 10, 2, 12, 'pop')
    return obs


# ================================================================
#  道路 / 人行道
# ================================================================
def build_road(col):
    obs = []
    y_road = -5.42
    obs.append(rect("Road", 0, y_road, HALF * 2 - 0.02, 1.16, TOP_Z + 0.004, M_ASPHALT, col=col))
    obs.append(rect("RoadEdgeA", 0, y_road + 0.49, HALF * 2 - 0.02, 0.06, TOP_Z + 0.008, M_WHITE, col=col))
    obs.append(rect("RoadEdgeB", 0, y_road - 0.49, HALF * 2 - 0.02, 0.06, TOP_Z + 0.008, M_WHITE, col=col))
    # 中央虚线
    for i in range(9):
        x = -5.0 + i * 1.22
        obs.append(rect("RoadDash%d" % i, x, y_road, 0.56, 0.055, TOP_Z + 0.009, M_WHITE, col=col))
    # 人行道
    obs.append(rect("Walk", 0, -4.53, HALF * 2 - 0.02, 0.62, TOP_Z + 0.005, M_WALK, col=col))
    for i in range(11):
        x = -5.5 + i * 1.1
        obs.append(rect("WalkJoint%d" % i, x, -4.53, 0.018, 0.6, TOP_Z + 0.007, M_CONCRETE, col=col))
    # 路缘石
    obs.append(box("Curb", (HALF * 2 - 0.02, 0.09, 0.07), (0, -4.2, TOP_Z + 0.02), M_CONCRETE, col=col))
    # 临场地一侧的步道（串起自行车棚 / 长椅 / 饮水台 / 篮球场）
    wy = 4.55
    obs.append(rect("WalkNorth", 0.9, wy, 8.6, 0.56, TOP_Z + 0.005, M_WALK, col=col))
    for i in range(10):
        obs.append(rect("WalkNorthJoint%d" % i, -3.3 + i * 0.95, wy, 0.018, 0.54,
                        TOP_Z + 0.007, M_CONCRETE, col=col))
    stage_group(obs[:3], 12, 2, 12, 'pop')
    stage_group(obs[3:], 16, 0.6, 10, 'pop')
    return obs


# ================================================================
#  塑胶跑道
# ================================================================
def build_track(col):
    obs = []
    z_apron = TOP_Z + 0.006
    z_track = TOP_Z + 0.012
    z_line = TOP_Z + 0.018

    obs.append(ring_strip("Apron", TRACK_CX, TRACK_CY, R_OUT + 0.17, S_HALF, 0.17,
                          z_apron, M_CONCRETE, arcs=40, sides=8, col=col))
    obs.append(ring_strip("TrackRed", TRACK_CX, TRACK_CY, R_OUT, S_HALF, TRACK_W,
                          z_track, M_TRACK, arcs=44, sides=10, col=col))
    # 内外压边（深红）
    obs.append(ring_strip("TrackEdgeOut", TRACK_CX, TRACK_CY, R_OUT, S_HALF, 0.035,
                          z_line, M_TRACK_D, arcs=44, sides=10, col=col))
    obs.append(flat_ring("TrackEdgeIn", TRACK_CX, TRACK_CY, R_IN + 0.05, R_IN, z_line,
                         M_WHITE, seg=44, col=col))

    # 分道线
    for k in range(1, 8):
        obs.append(ring_strip("Lane%d" % k, TRACK_CX, TRACK_CY, R_OUT - k * LANE_W, S_HALF,
                              0.017, z_line, M_WHITE, arcs=44, sides=10, col=col))

    # 起跑线（右侧直道）
    obs.append(strip("StartLine", (R_IN + 0.06, 1.92), (R_OUT - 0.03, 1.92), 0.032, z_line, M_WHITE, col=col))
    # 道次编号
    for k in range(1, 9):
        x = R_IN + (k - 0.5) * LANE_W
        t = text_mesh("LaneNum%d" % k, str(k), 0.105, (x, 2.18, z_line + 0.002),
                      (0, 0, math.radians(-90)), M_WHITE, col=col)
        if t:
            obs.append(t)

    stage_group(obs[:1], 20, 2, 12, 'pop')
    stage_group(obs[1:3], 24, 3, 12, 'pop')
    stage_group(obs[3:], 30, 0.8, 12, 'pop')
    return obs


# ================================================================
#  足球场（人工草皮）
# ================================================================
PITCH_CX, PITCH_CY = 0.0, 0.55
PITCH_W, PITCH_D = 2.90, 4.60
GOAL_Y = (PITCH_CY - PITCH_D / 2, PITCH_CY + PITCH_D / 2)


def build_pitch(col):
    obs = []
    z_turf = TOP_Z + 0.008
    z_stripe = TOP_Z + 0.0095
    z_line = TOP_Z + 0.014

    obs.append(stadium_fill("Turf", TRACK_CX, TRACK_CY, R_IN, S_HALF, z_turf,
                            M_TURF, arcs=40, sides=8, col=col))
    # 剪草条纹
    n = 12
    y0 = TRACK_CY - 2.05
    step = 4.1 / n
    for i in range(n):
        if i % 2 == 0:
            continue
        obs.append(rect("Mow%d" % i, 0, y0 + step * (i + 0.5), 3.2, step,
                        z_stripe, M_TURF_D, col=col))

    # 场地白线
    obs += rect_outline("PitchLine", PITCH_CX, PITCH_CY, PITCH_W, PITCH_D, 0.034, z_line, M_WHITE, col=col)
    obs.append(strip("Halfway", (-PITCH_W / 2, PITCH_CY), (PITCH_W / 2, PITCH_CY), 0.03, z_line, M_WHITE, col=col))
    obs.append(flat_ring("CenterCircle", PITCH_CX, PITCH_CY, 0.625, 0.593, z_line, M_WHITE, seg=40, col=col))
    obs.append(cyl("CenterSpot", 0.045, 0.045, 0.006, (PITCH_CX, PITCH_CY, z_line + 0.003),
                   M_WHITE, seg=12, col=col))

    for s, y in ((-1, GOAL_Y[0]), (1, GOAL_Y[1])):
        sign = -1 if s < 0 else 1
        # 禁区
        obs += rect_outline("Penalty%d" % s, 0, y - sign * 0.36, 1.72, 0.72, 0.03, z_line, M_WHITE, col=col)
        # 小禁区
        obs += rect_outline("GoalArea%d" % s, 0, y - sign * 0.12, 0.78, 0.24, 0.026, z_line, M_WHITE, col=col)
        # 点球点
        obs.append(cyl("PenaltySpot%d" % s, 0.032, 0.032, 0.006, (0, y - sign * 0.47, z_line + 0.003),
                       M_WHITE, seg=10, col=col))
        # 罚球弧
        if s < 0:
            obs.append(arc_ring("PenArc%d" % s, 0, y - 0.47, 0.60, 0.028, z_line, 30, 150, M_WHITE, seg=16, col=col))
        else:
            obs.append(arc_ring("PenArc%d" % s, 0, y - 0.47, 0.60, 0.028, z_line, 210, 330, M_WHITE, seg=16, col=col))

    stage_group(obs[:1], 28, 2, 12, 'rise')
    stage_group(obs[1:7], 32, 1.2, 12, 'pop')
    stage_group(obs[7:], 40, 1.0, 12, 'pop')
    return obs


# ================================================================
#  球门 / 角旗
# ================================================================
def build_goals(col):
    obs = []
    z = TOP_Z + 0.008
    for s, y in ((-1, GOAL_Y[0]), (1, GOAL_Y[1])):
        sign = -1 if s < 0 else 1
        hw = 0.44
        # 门柱
        obs.append(cyl("GoalPostL%d" % s, 0.016, 0.016, 0.32, (-hw, y, z + 0.16), M_NET, seg=10, col=col))
        obs.append(cyl("GoalPostR%d" % s, 0.016, 0.016, 0.32, (hw, y, z + 0.16), M_NET, seg=10, col=col))
        obs.append(cyl("GoalBar%d" % s, 0.014, 0.014, hw * 2, (0, y, z + 0.315), M_NET,
                       seg=10, ry=math.radians(90), col=col))
        # 后柱与斜撑
        by = y + sign * 0.26
        obs.append(cyl("GoalBackL%d" % s, 0.012, 0.012, 0.16, (-hw, by, z + 0.08), M_NET, seg=8, col=col))
        obs.append(cyl("GoalBackR%d" % s, 0.012, 0.012, 0.16, (hw, by, z + 0.08), M_NET, seg=8, col=col))
        obs.append(cyl("GoalTopBack%d" % s, 0.011, 0.011, hw * 2, (0, by, z + 0.16), M_NET,
                       seg=8, ry=math.radians(90), col=col))
        # 侧网
        for side in (-1, 1):
            obs.append(tube("GoalSideNet%d_%d" % (s, side),
                            [(side * hw, y, z + 0.31), (side * hw, by, z + 0.16),
                             (side * hw, by, z + 0.01)], 0.006, M_NET, col=col))
        # 背网竖线
        for i in range(5):
            gx = -hw + 0.88 * i / 4
            obs.append(tube("GoalNet%d_%d" % (s, i),
                            [(gx, by, z + 0.16), (gx, by, z + 0.01)], 0.005, M_NET, col=col))
        for i in range(3):
            gz = z + 0.05 + i * 0.05
            obs.append(tube("GoalNetH%d_%d" % (s, i),
                            [(-hw, by, gz), (hw, by, gz)], 0.005, M_NET, col=col))
    stage_group(obs, 44, 1.2, 12, 'pop')
    return obs


def build_flags(col):
    obs = []
    z = TOP_Z + 0.008
    for i, (x, y) in enumerate([(-PITCH_W / 2, GOAL_Y[0]), (PITCH_W / 2, GOAL_Y[0]),
                                (-PITCH_W / 2, GOAL_Y[1]), (PITCH_W / 2, GOAL_Y[1])]):
        obs.append(cyl("FlagPole%d" % i, 0.008, 0.007, 0.34, (x, y, z + 0.17), M_NET, seg=8, col=col))
        f = quad("Flag%d" % i, [(x, y, z + 0.34), (x, y, z + 0.24),
                                (x + 0.12, y + 0.055, z + 0.27), (x + 0.11, y + 0.05, z + 0.325)],
                 toon_mat("FlagRed", "#d8553f"), col)
        obs.append(f)
    stage_group(obs, 48, 1.5, 12, 'pop')
    return obs


# ================================================================
#  跳远沙坑
# ================================================================
def build_long_jump(col):
    obs = []
    z = TOP_Z + 0.007
    cx, cy = -1.45, -3.25
    obs.append(rect("JumpRunway", cx + 1.55, cy, 1.30, 0.46, z, toon_mat("Runway", "#b96a57"), col=col))
    obs.append(rect("JumpPit", cx, cy, 1.15, 0.62, z + 0.004, M_SAND, col=col))
    obs += rect_outline("JumpPitEdge", cx, cy, 1.20, 0.67, 0.035, z + 0.008, M_CONCRETE, col=col)
    obs.append(rect("JumpBoard", cx + 0.62, cy, 0.09, 0.62, z + 0.01, M_WHITE, col=col))
    # 沙面刮痕
    for i in range(4):
        obs.append(rect("SandMark%d" % i, cx - 0.1 + i * 0.08, cy - 0.12 + i * 0.09,
                        0.5, 0.02, z + 0.009, toon_mat("SandMark", "#cdb37b"), rz=0.06 * i, col=col))
    stage_group(obs, 52, 1.0, 12, 'pop')
    return obs


# ================================================================
#  落叶
# ================================================================
def build_leaves(col):
    obs = []
    spots = [(-4.9, -3.9), (-3.5, 4.5), (2.4, 4.2), (4.6, -3.5), (4.9, 2.2),
             (-2.5, -3.6), (0.4, 4.7), (5.0, 4.4), (-5.0, 1.4)]
    for i in range(30):
        bx, by = spots[i % len(spots)]
        x = bx + (random.random() - 0.5) * 1.1
        y = by + (random.random() - 0.5) * 1.1
        s = 0.035 + random.random() * 0.03
        ob = rect("Leaf%d" % i, x, y, s * 1.8, s, TOP_Z + 0.005,
                  M_LEAF_A if i % 3 else M_LEAF_B, rz=random.random() * 3.14, col=col)
        obs.append(ob)
    stage_group(obs, 140, 0.6, 10, 'pop')
    return obs

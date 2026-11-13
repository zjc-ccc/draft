# -*- coding: utf-8 -*-
"""小型篮球场：拼色地胶 / 场线 / 篮球架 / 围网"""

import math

import bpy

from campus_core import (TOP_Z, toon_mat, emit_mat, box, cyl, sphere, rect, quad,
                         torus, tube, strip, flat_ring, arc_ring, rect_outline,
                         text_mesh, stage_group, link)

CCX, CCY = 4.24, 0.10
CW, CD = 2.30, 2.90      # 场地界线尺寸
HALF_W, HALF_D = CW / 2, CD / 2

M_CBASE = toon_mat("CourtBase", "#3d7aa4")
M_CCOURT = toon_mat("CourtFloor", "#4f9a86")
M_CKEY = toon_mat("CourtKey", "#c9694c")
M_CLINE = toon_mat("CourtLine", "#f3f1e7")
M_STEEL = toon_mat("Steel", "#b6bec7")
M_POLE = toon_mat("CourtPole", "#5b6470")
M_BOARD = toon_mat("Backboard", "#eceeea")
M_RIM = toon_mat("Rim", "#d9673f")
M_NET = toon_mat("NetWhite", "#eef2f4")


def net_panel(name, p0, p1, z0, z1, step, mat, col, radius=0.0035):
    """一张由多根竖线组成的围网（单个曲线对象）"""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = 0
    x0, y0 = p0
    x1, y1 = p1
    ln = math.hypot(x1 - x0, y1 - y0)
    n = max(2, int(ln / step) + 1)
    for i in range(n):
        t = i / (n - 1)
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        sp = cu.splines.new('POLY')
        sp.points.add(1)
        sp.points[0].co = (x, y, z0, 1.0)
        sp.points[1].co = (x, y, z1, 1.0)
    ob = bpy.data.objects.new(name, cu)
    link(ob, col)
    cu.materials.append(mat)
    return ob


def build_court(col):
    obs = []
    z_base = TOP_Z + 0.006
    z_floor = TOP_Z + 0.010
    z_line = TOP_Z + 0.015

    obs.append(rect("CourtBase", CCX, CCY, CW + 0.26, CD + 0.26, z_base, M_CBASE, col=col))
    obs.append(rect("CourtFloor", CCX, CCY, CW, CD, z_floor, M_CCOURT, col=col))
    # 拼色：两侧禁区
    for s, y in ((-1, CCY - HALF_D), (1, CCY + HALF_D)):
        sign = -1 if s < 0 else 1
        obs.append(rect("CourtKey%d" % s, CCX, y - sign * 0.33, 0.66, 0.66, z_floor + 0.002, M_CKEY, col=col))
        # 三分弧
        if s < 0:
            obs.append(arc_ring("CourtArc%d" % s, CCX, y, 0.66, 0.03, z_line, 0, 180, M_CLINE, seg=22, col=col))
        else:
            obs.append(arc_ring("CourtArc%d" % s, CCX, y, 0.66, 0.03, z_line, 180, 360, M_CLINE, seg=22, col=col))
        # 罚球圈
        obs.append(flat_ring("CourtFT%d" % s, CCX, y - sign * 0.66, 0.21, 0.19, z_line, M_CLINE, seg=24, col=col))

    obs += rect_outline("CourtLine", CCX, CCY, CW, CD, 0.03, z_line, M_CLINE, col=col)
    obs.append(strip("CourtCenter", (CCX - HALF_W, CCY), (CCX + HALF_W, CCY), 0.028, z_line, M_CLINE, col=col))
    obs.append(flat_ring("CourtCircle", CCX, CCY, 0.27, 0.242, z_line, M_CLINE, seg=28, col=col))

    stage_group(obs, 84, 1.0, 12, 'pop')
    return obs


def build_hoops(col):
    obs = []
    for s in (-1, 1):
        sign = -1 if s < 0 else 1
        base_y = CCY + sign * (HALF_D + 0.16)
        pole_h = 0.62
        obs.append(cyl("HoopPole%d" % s, 0.032, 0.026, pole_h, (CCX, base_y + sign * 0.10, TOP_Z + pole_h / 2),
                       M_POLE, seg=10, col=col))
        # 悬臂
        obs.append(box("HoopArm%d" % s, (0.05, 0.18, 0.04),
                       (CCX, base_y + sign * 0.02, TOP_Z + 0.52), M_POLE, col=col))
        # 篮板
        by = base_y - sign * 0.08
        obs.append(box("Backboard%d" % s, (0.34, 0.025, 0.22), (CCX, by, TOP_Z + 0.50), M_BOARD, col=col))
        obs.append(box("BoardMark%d" % s, (0.13, 0.006, 0.09), (CCX, by - sign * 0.016, TOP_Z + 0.46),
                       M_CKEY, col=col))
        # 篮筐
        rim_y = by - sign * 0.10
        obs.append(torus("Rim%d" % s, 0.075, 0.009, (CCX, rim_y, TOP_Z + 0.38), M_RIM,
                         seg_major=16, seg_minor=6, col=col))
        # 网
        for k in range(8):
            a = 2 * math.pi * k / 8
            px = CCX + 0.072 * math.cos(a)
            py = rim_y + 0.072 * math.sin(a)
            obs.append(tube("HoopNet%d_%d" % (s, k),
                            [(px, py, TOP_Z + 0.375), (CCX + 0.03 * math.cos(a), rim_y + 0.03 * math.sin(a),
                                                       TOP_Z + 0.28)], 0.0035, M_NET, col=col))
    stage_group(obs, 92, 0.8, 12, 'pop')
    return obs


def build_fence(col):
    obs = []
    z0 = TOP_Z + 0.004
    top = 0.72
    lines = [((5.62, CCY - HALF_D - 0.30), (5.62, CCY + HALF_D + 0.30)),
             ((CCX - HALF_W - 0.20, CCY - HALF_D - 0.30), (5.62, CCY - HALF_D - 0.30)),
             ((CCX - HALF_W - 0.20, CCY + HALF_D + 0.30), (5.62, CCY + HALF_D + 0.30))]
    for i, (p0, p1) in enumerate(lines):
        obs.append(net_panel("CourtNet%d" % i, p0, p1, z0 + 0.05, z0 + top - 0.05, 0.16, M_NET, col))
        obs.append(tube("CourtRailA%d" % i, [(p0[0], p0[1], z0 + top), (p1[0], p1[1], z0 + top)],
                        0.012, M_STEEL, col=col))
        obs.append(tube("CourtRailB%d" % i, [(p0[0], p0[1], z0 + 0.05), (p1[0], p1[1], z0 + 0.05)],
                        0.012, M_STEEL, col=col))
        ln = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        n = max(2, int(ln / 0.62) + 1)
        for k in range(n):
            t = k / (n - 1)
            x = p0[0] + (p1[0] - p0[0]) * t
            y = p0[1] + (p1[1] - p0[1]) * t
            obs.append(cyl("CourtPost%d_%d" % (i, k), 0.02, 0.02, top, (x, y, z0 + top / 2),
                           M_STEEL, seg=8, col=col))
    stage_group(obs, 98, 0.5, 12, 'pop')
    return obs

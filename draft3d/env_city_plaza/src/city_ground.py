# -*- coding: utf-8 -*-
"""城市中心广场 · 地面层：底座 / 车行道 / 人行道 / 斑马线 / 广场铺装"""

import math

import campus_core as core
import city_base as base

m = base.mat


def build_base(col):
    obs = []
    obs.append(core.box("BaseSlab", (base.HALF * 2, base.HALF * 2, 0.46),
                        (0, 0, base.TOP_Z - 0.23), m("slab"), col=col))
    obs.append(core.box("BasePlinth", (base.HALF * 2 + 0.5, base.HALF * 2 + 0.5, 0.14),
                        (0, 0, -0.10), m("slab_d"), col=col))
    obs.append(core.box("BaseLip", (base.HALF * 2 + 0.16, base.HALF * 2 + 0.16, 0.05),
                        (0, 0, -0.035), m("slab"), col=col))
    return obs


def build_roads(col):
    obs = []
    obs.append(core.rect("RoadEW", 0, 0, base.HALF * 2, base.ROAD_Y * 2,
                         base.ROAD_Z, m("asphalt"), col=col))
    obs.append(core.rect("RoadNS", 0, 0, base.ROAD_X * 2, base.HALF * 2,
                         base.ROAD_Z + 0.0008, m("asphalt"), col=col))
    # 沥青补丁
    for i, (x, y, w, d) in enumerate([(-3.6, 0.55, 1.10, 0.42), (2.40, -0.52, 0.90, 0.34),
                                      (0.34, 3.60, 0.48, 0.90), (-0.30, -4.20, 0.52, 0.80)]):
        obs.append(core.rect("RoadPatch%d" % i, x, y, w, d, base.ROAD_Z + 0.002,
                             m("asphalt_d"), col=col))
    # 井盖
    for i, (x, y) in enumerate([(-2.60, 0.78), (3.20, -0.86), (0.42, -2.95), (-0.48, 4.35)]):
        obs.append(core.cyl("Manhole%d" % i, 0.075, 0.075, 0.006,
                            (x, y, base.ROAD_Z + 0.004), m("metal_d"), seg=16, col=col))
        obs.append(core.flat_ring("ManholeRim%d" % i, x, y, 0.085, 0.072,
                                  base.ROAD_Z + 0.005, m("metal"), seg=16, col=col))
    return obs


def build_sidewalks(col):
    obs = []
    h = 0.058
    for s in (-1, 1):
        obs.append(core.box("WalkEW%d" % s, (base.HALF * 2, base.WALK, h),
                            (0, s * (base.ROAD_Y + base.WALK / 2), base.PAVE_Z - h / 2),
                            m("walk"), col=col))
        obs.append(core.box("CurbEW%d" % s, (base.HALF * 2, 0.05, 0.022),
                            (0, s * (base.ROAD_Y + 0.018), base.PAVE_Z - 0.011),
                            m("curb"), col=col))
    for s in (-1, 1):
        obs.append(core.box("WalkNS%d" % s, (base.WALK, base.HALF * 2, h),
                            (s * (base.ROAD_X + base.WALK / 2), 0, base.PAVE_Z - h / 2),
                            m("walk"), col=col))
        obs.append(core.box("CurbNS%d" % s, (0.05, base.HALF * 2, 0.022),
                            (s * (base.ROAD_X + 0.018), 0, base.PAVE_Z - 0.011),
                            m("curb"), col=col))
    # 四个街区铺装
    bw = base.HALF - base.BLOCK_X
    bd = base.HALF - base.BLOCK_Y
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx = sx * (base.BLOCK_X + bw / 2)
            cy = sy * (base.BLOCK_Y + bd / 2)
            obs.append(core.box("Block%d%d" % (sx, sy), (bw, bd, h),
                                (cx, cy, base.PAVE_Z - h / 2), m("walk_d"), col=col))
    # 斑马线两端的盲道
    for x, y, w, d in ((1.37, 1.72, 0.42, 0.10), (1.37, -1.72, 0.42, 0.10),
                       (-1.37, 1.72, 0.42, 0.10), (-1.37, -1.72, 0.42, 0.10),
                       (1.86, 1.55, 0.10, 0.42), (-1.86, 1.55, 0.10, 0.42),
                       (1.86, -1.55, 0.10, 0.42), (-1.86, -1.55, 0.10, 0.42)):
        obs.append(core.rect("Tactile_%s_%s" % (x, y), x, y, w, d, base.PAVE_Z + 0.002,
                             m("line_y"), col=col))
    return obs


def build_markings(col):
    obs = []
    line = m("line")
    # 跨主干道的斑马线（条纹沿 x）
    for cx in (-1.37, 1.37):
        for i in range(7):
            obs.append(core.rect("ZebraEW_%d_%d" % (int(cx * 10), i), cx, -1.05 + i * 0.35,
                                 0.42, 0.10, base.LINE_Z, line, col=col))
    # 跨南北向道路的斑马线（条纹沿 y）
    for cy in (-1.55, 1.55):
        for i in range(7):
            obs.append(core.rect("ZebraNS_%d_%d" % (int(cy * 10), i), -1.05 + i * 0.35, cy,
                                 0.10, 0.42, base.LINE_Z, line, col=col))
    # 停止线
    obs.append(core.rect("StopNS_S", 0.54, -2.02, 1.02, 0.06, base.LINE_Z, line, col=col))
    obs.append(core.rect("StopNS_N", -0.54, 2.02, 1.02, 0.06, base.LINE_Z, line, col=col))
    obs.append(core.rect("StopEW_W", -2.06, -0.66, 0.06, 1.20, base.LINE_Z, line, col=col))
    obs.append(core.rect("StopEW_E", 2.06, 0.66, 0.06, 1.20, base.LINE_Z, line, col=col))
    # 车道虚线：主干道沿 x，南北路沿 y
    x = 2.30
    while x < 5.70:
        for s in (-1, 1):
            obs.append(core.rect("DashEW_%s_%d" % (s, int(x * 100)), s * x, 0.0,
                                 0.42, 0.045, base.LINE_Z, line, col=col))
        x += 0.72
    y = 2.30
    while y < 5.70:
        for s in (-1, 1):
            obs.append(core.rect("DashNS_%s_%d" % (s, int(y * 100)), 0.0, s * y,
                                 0.045, 0.42, base.LINE_Z, line, col=col))
        y += 0.72
    # 路缘边线
    for s in (-1, 1):
        obs.append(core.rect("EdgeEW%d" % s, 0, s * (base.ROAD_Y - 0.07),
                             base.HALF * 2, 0.028, base.LINE_Z, line, col=col))
        obs.append(core.rect("EdgeNS%d" % s, s * (base.ROAD_X - 0.07), 0,
                             0.028, base.HALF * 2, base.LINE_Z, line, col=col))
    # 导向箭头（简化为两条斜线 + 一根横杆）
    for i, (ax, ay, flip) in enumerate([(0.55, -3.20, 1), (-0.55, 3.20, -1)]):
        obs.append(core.strip("ArrowStem%d" % i, (ax, ay - 0.22 * flip), (ax, ay + 0.14 * flip),
                              0.05, base.LINE_Z, line, col=col))
        obs.append(core.strip("ArrowL%d" % i, (ax, ay + 0.14 * flip),
                              (ax - 0.11, ay + 0.02 * flip), 0.05, base.LINE_Z, line, col=col))
        obs.append(core.strip("ArrowR%d" % i, (ax, ay + 0.14 * flip),
                              (ax + 0.11, ay + 0.02 * flip), 0.05, base.LINE_Z, line, col=col))
    return obs


def build_plaza_paving(col):
    obs = []
    cx, cy = base.PLAZA_C
    R = base.PLAZA_R
    z = base.PAVE_Z
    obs.append(core.cyl("PlazaBase", R, R, 0.008, (cx, cy, z + 0.004), m("plaza_d"),
                        seg=64, col=col))
    obs.append(core.cyl("PlazaTop", R - 0.10, R - 0.10, 0.008, (cx, cy, z + 0.008),
                        m("plaza"), seg=64, col=col))
    obs.append(core.flat_ring("PlazaRingA", cx, cy, R, R - 0.10, z + 0.013,
                              m("plaza_ring"), seg=64, col=col))
    obs.append(core.flat_ring("PlazaRingB", cx, cy, R * 0.56, R * 0.56 - 0.055,
                              z + 0.013, m("plaza_ring"), seg=64, col=col))
    for i in range(8):
        a = math.radians(22.5 + i * 45)
        obs.append(core.strip("PlazaRay%d" % i,
                              (cx + math.cos(a) * R * 0.14, cy + math.sin(a) * R * 0.14),
                              (cx + math.cos(a) * (R - 0.13), cy + math.sin(a) * (R - 0.13)),
                              0.022, z + 0.014, m("plaza_ring"), col=col))
    obs.append(core.torus("PlazaBorder", R + 0.015, 0.024, (cx, cy, z + 0.006),
                          m("curb"), seg_major=64, seg_minor=6, col=col))
    return obs

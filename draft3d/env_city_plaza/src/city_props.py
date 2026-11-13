# -*- coding: utf-8 -*-
"""城市中心广场 · 街具：喷泉 / 行道树 / 路灯 / 红绿灯 / 长椅 / 垃圾桶 / 车辆"""

import math

import campus_core as core
import city_base as base

m = base.mat


def _rot(dx, dy, deg):
    a = math.radians(deg)
    return (dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a))


# ---------------------------------------------------------------- 广场喷泉
def build_fountain(col):
    cx, cy = base.PLAZA_C
    z = base.PAVE_Z
    obs = []
    obs.append(core.cyl("FountainBasin", 0.64, 0.64, 0.12, (cx, cy, z + 0.06),
                        m("concrete_l"), seg=8, col=col))
    obs.append(core.torus("FountainRim", 0.64, 0.022, (cx, cy, z + 0.12),
                          m("curb"), seg_major=8, seg_minor=6, col=col))
    obs.append(core.cyl("FountainWater", 0.55, 0.55, 0.02, (cx, cy, z + 0.118),
                        base.glow("Water", "#63d8ea", 0.9), seg=32, col=col))
    obs.append(core.cyl("FountainStem", 0.085, 0.060, 0.42, (cx, cy, z + 0.30),
                        m("concrete_d"), seg=16, col=col))
    obs.append(core.torus("FountainRing", 0.22, 0.030, (cx, cy, z + 0.56),
                          base.glow("Ring", "#57e8ff", 1.5),
                          seg_major=32, seg_minor=8,
                          rot=(math.radians(24), math.radians(14), 0.0), col=col))
    for i in range(8):
        a = math.radians(i * 45)
        x = cx + math.cos(a) * 0.40
        y = cy + math.sin(a) * 0.40
        obs.append(core.cyl("Jet%d" % i, 0.008, 0.004, 0.12, (x, y, z + 0.18),
                            base.glow("Jet", "#e6fbff", 1.8), seg=6, col=col))
        obs.append(core.sphere("Drop%d" % i, 0.014, (x, y, z + 0.25),
                               base.glow("Drop", "#e6fbff", 1.8), seg=8, col=col))
    return obs


# ---------------------------------------------------------------- 行道树
def tree(name, x, y, scale, col):
    z = base.PAVE_Z
    obs = []
    obs.append(core.flat_ring(name + "_Pit", x, y, 0.17, 0.14, z + 0.002,
                              m("concrete"), seg=16, col=col))
    obs.append(core.cyl(name + "_Trunk", 0.030 * scale, 0.024 * scale, 0.26 * scale,
                        (x, y, z + 0.13 * scale), m("trunk"), seg=8, col=col))
    for i, (r, hz, key) in enumerate(((0.165, 0.33, "tree"), (0.140, 0.45, "tree_l"),
                                      (0.105, 0.55, "tree_d"))):
        obs.append(core.sphere("%s_Foliage%d" % (name, i), r * scale,
                               (x, y, z + hz * scale), m(key), seg=12, col=col))
    return obs


def build_trees(col):
    groups = []
    spots = []
    for x in (-5.30, -4.20, -3.10):
        spots.append((x, 1.58))
        spots.append((x, -1.58))
    for x in (3.10, 4.30, 5.30):
        spots.append((x, -1.58))
    for y in (3.00, 4.20, 5.30):
        spots.append((-1.38, y))
    for y in (-4.90, -5.60):
        spots.append((1.38, y))
    for i, (x, y) in enumerate(spots):
        groups.append((tree("Tree%d" % i, x, y, 1.0 if i % 2 == 0 else 0.88, col), "Tree%d" % i))
    # 广场环树
    cx, cy = base.PLAZA_C
    for i, deg in enumerate((35, 110, 185, 260, 335)):
        a = math.radians(deg)
        groups.append((tree("PlazaTree%d" % i, cx + math.cos(a) * 1.20,
                            cy + math.sin(a) * 1.20, 0.9, col), "PlazaTree%d" % i))
    return groups


# ---------------------------------------------------------------- 路灯
def street_lamp(name, x, y, dx, dy, col):
    z = base.PAVE_Z
    obs = []
    obs.append(core.cyl(name + "_Pole", 0.016, 0.012, 0.82, (x, y, z + 0.41),
                        m("metal_d"), seg=10, col=col))
    ax, ay = x + dx * 0.10, y + dy * 0.10
    if dx:
        obs.append(core.cyl(name + "_Arm", 0.009, 0.009, 0.20, (ax, ay, z + 0.80),
                            m("metal_d"), seg=8, ry=90, col=col))
    else:
        obs.append(core.cyl(name + "_Arm", 0.009, 0.009, 0.20, (ax, ay, z + 0.80),
                            m("metal_d"), seg=8, rx=90, col=col))
    dims = (0.10, 0.055, 0.026) if dx else (0.055, 0.10, 0.026)
    obs.append(core.box(name + "_Head", dims, (x + dx * 0.21, y + dy * 0.21, z + 0.80),
                        m("metal_d"), col=col))
    obs.append(core.box(name + "_Bulb", (dims[0] * 0.7, dims[1] * 0.7, 0.008),
                        (x + dx * 0.21, y + dy * 0.21, z + 0.785),
                        base.glow("LampWarm", "#ffd79a", 2.2), col=col))
    return obs


def build_lamps(col):
    groups = []
    plan = [(-5.40, 1.62, 0, -1), (-3.20, 1.62, 0, -1), (5.00, 1.62, 0, -1),
            (-5.40, -1.62, 0, 1), (-3.20, -1.62, 0, 1), (5.00, -1.62, 0, 1),
            (-1.42, -4.60, 1, 0), (-1.42, 3.00, 1, 0),
            (1.42, -4.90, -1, 0), (1.42, 4.20, -1, 0)]
    for i, (x, y, dx, dy) in enumerate(plan):
        groups.append((street_lamp("Lamp%d" % i, x, y, dx, dy, col), "Lamp%d" % i))
    return groups


# ---------------------------------------------------------------- 红绿灯
def traffic_light(name, x, y, arm_dx, arm_dy, face_sign, green_on, col):
    z = base.PAVE_Z
    obs = []
    obs.append(core.cyl(name + "_Pole", 0.018, 0.015, 0.60, (x, y, z + 0.30),
                        m("metal_d"), seg=10, col=col))
    obs.append(core.sphere(name + "_Base", 0.032, (x, y, z + 0.03),
                           m("metal_d"), seg=10, col=col))
    hx, hy = x + arm_dx * 0.17, y + arm_dy * 0.17
    if arm_dx:
        obs.append(core.cyl(name + "_Arm", 0.009, 0.009, 0.34, (hx, hy, z + 0.58),
                            m("metal_d"), seg=8, ry=90, col=col))
    else:
        obs.append(core.cyl(name + "_Arm", 0.009, 0.009, 0.34, (hx, hy, z + 0.58),
                            m("metal_d"), seg=8, rx=90, col=col))
    bx, by = x + arm_dx * 0.34, y + arm_dy * 0.34
    obs.append(core.box(name + "_Head", (0.05, 0.06, 0.16), (bx, by, z + 0.49),
                        m("metal_d"), col=col))
    lamp_z = (0.545, 0.49, 0.435)
    on = green_on
    for i, key in enumerate(("Red", "Yellow", "Green")):
        lit = (i == 2) if on else (i == 0)
        col_hex = {"Red": ("#ff4d4d", "#4a2226"), "Yellow": ("#ffcf4d", "#4a4526"),
                   "Green": ("#5effa0", "#224a34")}[key]
        material = (core.emit_mat("Traffic" + key, col_hex[0], 2.2) if lit
                    else m("metal_d"))
        cx = bx + face_sign * (0.025 if True else 0.0)
        obs.append(core.cyl(name + "_Lens" + key, 0.015, 0.015, 0.008,
                            (cx, by, z + lamp_z[i]), material, seg=10, ry=90, col=col))
    return obs


def build_traffic_lights(col):
    groups = []
    plan = [(1.55, 1.70, 0, -1, -1, True), (-1.55, 1.70, 0, -1, 1, True),
            (1.55, -1.70, 0, 1, -1, False), (-1.55, -1.70, 0, 1, 1, False)]
    for i, (x, y, adx, ady, fs, green) in enumerate(plan):
        groups.append((traffic_light("Signal%d" % i, x, y, adx, ady, fs, green, col),
                       "Signal%d" % i))
    return groups


# ---------------------------------------------------------------- 广场与街边家具
def bench(name, x, y, yaw, col):
    z = base.PAVE_Z
    obs = []
    obs.append(core.box(name + "_Seat", (0.28, 0.10, 0.022), (x, y, z + 0.085),
                        m("bench"), rz=math.radians(yaw), col=col))
    ox, oy = _rot(0.0, 0.048, yaw)
    obs.append(core.box(name + "_Back", (0.28, 0.014, 0.052), (x + ox, y + oy, z + 0.132),
                        m("bench"), rz=math.radians(yaw), col=col))
    for s in (-1, 1):
        lx, ly = _rot(s * 0.105, 0.0, yaw)
        obs.append(core.box(name + "_Leg%d" % s, (0.02, 0.088, 0.075),
                            (x + lx, y + ly, z + 0.042), m("metal_d"),
                            rz=math.radians(yaw), col=col))
    return obs


def planter(name, x, y, col):
    z = base.PAVE_Z
    obs = [core.box(name + "_Box", (0.34, 0.18, 0.10), (x, y, z + 0.05),
                    m("concrete_l"), col=col),
           core.box(name + "_Soil", (0.30, 0.14, 0.02), (x, y, z + 0.095),
                    m("trunk"), col=col)]
    colors = ("#e05a63", "#f0c14a", "#e88bb4")
    for i in range(4):
        obs.append(core.sphere("%s_Flower%d" % (name, i), 0.028,
                               (x - 0.10 + i * 0.066, y, z + 0.115),
                               core.toon_mat("Flower%d" % (i % 3), colors[i % 3]),
                               seg=8, col=col))
    return obs


def build_furniture(col):
    groups = []
    cx, cy = base.PLAZA_C
    # 广场环凳（背朝外）
    for i, deg in enumerate((70, 145, 215, 290)):
        a = math.radians(deg)
        bx = cx + math.cos(a) * 1.22
        by = cy + math.sin(a) * 1.22
        groups.append((bench("PlazaBench%d" % i, bx, by, deg - 90, col), "PlazaBench%d" % i))
    # 街边长椅
    groups.append((bench("WalkBench0", -4.20, -1.72, 180, col), "WalkBench0"))
    groups.append((bench("WalkBench1", 4.60, 1.72, 0, col), "WalkBench1"))
    # 垃圾桶
    for i, (x, y) in enumerate([(2.15, 1.95), (-2.15, -1.95), (1.55, -4.40),
                                (-1.60, 3.60), (5.55, -1.95)]):
        obs = [core.cyl("Bin%d" % i, 0.055, 0.048, 0.14, (x, y, base.PAVE_Z + 0.07),
                        m("tree_d"), seg=12, col=col),
               core.cyl("BinLid%d" % i, 0.058, 0.058, 0.014,
                        (x, y, base.PAVE_Z + 0.147), m("metal_d"), seg=12, col=col)]
        groups.append((obs, "Bin%d" % i))
    # 广场护柱
    for i, deg in enumerate((10, 50, 130, 170, 210, 310, 350)):
        a = math.radians(deg)
        bx = cx + math.cos(a) * (base.PLAZA_R + 0.24)
        by = cy + math.sin(a) * (base.PLAZA_R + 0.24)
        obs = [core.cyl("Bollard%d" % i, 0.016, 0.014, 0.16, (bx, by, base.PAVE_Z + 0.08),
                        m("metal"), seg=8, col=col)]
        groups.append((obs, "Bollard%d" % i))
    # 广场铭牌
    z = base.PAVE_Z
    plaque = [core.box("PlazaPlaque", (0.56, 0.12, 0.14), (4.42, 1.98, z + 0.07),
                       m("concrete_d"), col=col)]
    txt = core.text_mesh("PlazaPlaqueTxt", "中心广场", 0.072,
                         (4.42, 1.915, z + 0.07), (90.0, 0.0, 0.0),
                         m("white"), col=col)
    if txt:
        plaque.append(txt)
    groups.append((plaque, "PlazaPlaque"))
    # 花箱
    for i, (x, y) in enumerate([(2.55, 1.99), (4.15, 1.99), (-3.00, 1.99),
                                (2.62, -2.02), (-1.98, -4.30)]):
        groups.append((planter("Planter%d" % i, x, y, col), "Planter%d" % i))
    return groups


# ---------------------------------------------------------------- 车辆
def car(name, x, y, yaw, body_key, col, taxi=False):
    z = base.ROAD_Z
    obs = []
    obs.append(core.box(name + "_Body", (0.60, 0.30, 0.10), (x, y, z + 0.075),
                        m(body_key), rz=math.radians(yaw), col=col))
    ox, oy = _rot(-0.03, 0.0, yaw)
    obs.append(core.box(name + "_Cabin", (0.30, 0.26, 0.075), (x + ox, y + oy, z + 0.16),
                        m("glass"), rz=math.radians(yaw), col=col))
    for sx in (-1, 1):
        for sy in (-1, 1):
            wx, wy = _rot(sx * 0.17, sy * 0.135, yaw)
            obs.append(core.cyl("%s_Wheel%d%d" % (name, sx, sy), 0.042, 0.042, 0.028,
                                (x + wx, y + wy, z + 0.042), m("metal_d"),
                                seg=12, rx=90, rz=math.radians(yaw), col=col))
    fx, fy = _rot(0.302, 0.0, yaw)
    for s in (-1, 1):
        lx, ly = _rot(0.302, s * 0.095, yaw)
        obs.append(core.box("%s_Head%d" % (name, s), (0.012, 0.05, 0.024),
                            (x + lx, y + ly, z + 0.09),
                            base.glow("CarHead", "#fff3cf", 2.0),
                            rz=math.radians(yaw), col=col))
        tx, ty = _rot(-0.302, s * 0.095, yaw)
        obs.append(core.box("%s_Tail%d" % (name, s), (0.012, 0.05, 0.022),
                            (x + tx, y + ty, z + 0.09),
                            base.glow("CarTail", "#ff4d5e", 2.0),
                            rz=math.radians(yaw), col=col))
    if taxi:
        obs.append(core.box(name + "_Top", (0.10, 0.10, 0.03), (x, y, z + 0.215),
                            base.glow("TaxiTop", "#8fffc8", 1.6),
                            rz=math.radians(yaw), col=col))
    return obs


def build_cars(col):
    groups = []
    groups.append((car("CarTaxi", -3.70, 0.62, 0, "car_yellow", col, taxi=True), "CarTaxi"))
    groups.append((car("CarBlue", 3.50, -0.62, 180, "car_blue", col), "CarBlue"))
    groups.append((car("CarRed", -2.90, -0.62, 180, "car_red", col), "CarRed"))
    groups.append((car("CarGray", 0.55, -3.95, 90, "car_gray", col), "CarGray"))
    return groups

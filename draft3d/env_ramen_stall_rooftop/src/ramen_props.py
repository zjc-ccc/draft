# -*- coding: utf-8 -*-
"""天台散件：纸箱、盆栽、猫窝、煤气罐、积水、雨、杂项"""

import math
import random
import bpy
import bmesh
from mathutils import Matrix
from ramen_core import (ROOF_Z, toon_mat, emit_mat, box, cyl, sphere, plane, quad,
                        torus, tube, text_mesh, stage, stage_group, link)

random.seed(12)

M_CARD = toon_mat("Cardboard", "#a67b44")
M_CARD_D = toon_mat("CardboardDark", "#7d5a30")
M_TAPE = toon_mat("Tape", "#c9b78c")
M_PLANT = toon_mat("Plant", "#3f6b4a")
M_PLANT_D = toon_mat("PlantDark", "#2c4d36")
M_POT = toon_mat("Pot", "#8a5b45")
M_METAL = toon_mat("Metal", "#7d8798")
M_METAL_D = toon_mat("MetalDark", "#2a3240")
M_WOOD = toon_mat("Wood", "#6a4a35")
M_WOOD_D = toon_mat("WoodDark", "#453026")
M_CUSHION = toon_mat("Cushion", "#a8505a")
M_CAT = toon_mat("CatFur", "#cfa87a")
M_CAT_D = toon_mat("CatFurDark", "#a87f55")
M_DARK = toon_mat("DarkPanel", "#141a26")
M_PUDDLE = toon_mat("Puddle", "#1a2436")
M_PLASTIC = toon_mat("PlasticRed", "#b23530")
M_GLASS2 = emit_mat("WarmPaper", "#ffcf92", 1.4)


# ================================================================
#  纸箱 / 杂物
# ================================================================
def build_boxes(col):
    obs = []
    stacks = [
        (-1.62, -2.62, 0.0, 0.66, 0.52, 0.48, 0.12),
        (-1.60, -2.58, 0.48, 0.56, 0.46, 0.42, -0.18),
        (-2.15, -1.72, 0.0, 0.5, 0.42, 0.38, 0.34),
        (-4.35, -1.75, 0.0, 0.58, 0.44, 0.36, -0.08),
    ]
    for i, (x, y, z, w, d, h, rz) in enumerate(stacks):
        obs.append(box("Carton%d" % i, (w, d, h), (x, y, ROOF_Z + z + h / 2), M_CARD,
                       rz=rz, col=col))
        obs.append(box("CartonTape%d" % i, (w * 0.16, d + 0.01, h + 0.01),
                       (x, y, ROOF_Z + z + h / 2), M_TAPE, rz=rz, col=col))
    # 折叠塑料筐
    for i in range(2):
        obs.append(box("Crate%d" % i, (0.52, 0.38, 0.3), (1.95, -2.35, ROOF_Z + 0.15 + i * 0.3),
                       M_PLASTIC if i == 0 else M_METAL, rz=-0.12 + i * 0.2, col=col))
    stage_group(obs, 104, 1.2, 14, 'pop')
    return obs


def build_gas(col):
    obs = []
    obs.append(cyl("GasTank", 0.21, 0.21, 0.66, (2.18, 0.28, ROOF_Z + 0.33), M_METAL, seg=16, col=col))
    obs.append(cyl("GasTop", 0.21, 0.12, 0.1, (2.18, 0.28, ROOF_Z + 0.71), M_METAL_D, seg=16, col=col))
    obs.append(cyl("GasValve", 0.05, 0.05, 0.12, (2.18, 0.28, ROOF_Z + 0.82), M_METAL_D, seg=8, col=col))
    obs.append(torus("GasRing", 0.21, 0.025, (2.18, 0.28, ROOF_Z + 0.5), M_METAL_D,
                     seg_major=16, seg_minor=6, col=col))
    obs.append(tube("GasHose", [(2.18, 0.28, ROOF_Z + 0.78), (1.95, 0.5, ROOF_Z + 0.95),
                                (1.6, 0.62, ROOF_Z + 1.0)], 0.022,
                    toon_mat("Hose", "#1d1f24"), col=col))
    stage_group(obs, 100, 1.2, 14, 'pop')
    return obs


# ================================================================
#  盆栽
# ================================================================
def build_plants(col):
    obs = []
    specs = [(4.3, 3.8, 1.0, 0.0), (-4.35, 1.42, 0.85, 0.4), (-1.75, 3.95, 0.7, -0.5)]
    for i, (x, y, s, rz) in enumerate(specs):
        obs.append(cyl("Pot%d" % i, 0.19 * s, 0.23 * s, 0.3 * s,
                       (x, y, ROOF_Z + 0.15 * s), M_POT, seg=12, col=col))
        obs.append(cyl("PotRim%d" % i, 0.245 * s, 0.235 * s, 0.06 * s,
                       (x, y, ROOF_Z + 0.3 * s), M_POT, seg=12, col=col))
        obs.append(cyl("PotSoil%d" % i, 0.2 * s, 0.2 * s, 0.03 * s,
                       (x, y, ROOF_Z + 0.31 * s), M_PLANT_D, seg=12, col=col))
        obs.append(cyl("Trunk%d" % i, 0.03 * s, 0.025 * s, 0.45 * s,
                       (x, y, ROOF_Z + 0.52 * s), M_WOOD_D, seg=6, col=col))
        for j in range(4):
            a = rz + j * math.pi / 2
            ox, oy = math.cos(a) * 0.13 * s, math.sin(a) * 0.13 * s
            obs.append(sphere("Leaf%d_%d" % (i, j), 0.2 * s,
                              (x + ox, y + oy, ROOF_Z + (0.72 + 0.06 * j) * s),
                              M_PLANT if j % 2 == 0 else M_PLANT_D, seg=10, col=col))
    stage_group(obs, 108, 1.1, 14, 'pop')
    return obs


# ================================================================
#  猫窝（含小猫）
# ================================================================
def build_cat_house(col):
    x, y = 3.95, 2.5
    obs = []
    obs.append(box("CatHouseFloor", (0.66, 0.58, 0.06), (x, y, ROOF_Z + 0.03), M_WOOD, col=col))
    obs.append(box("CatHouseBack", (0.66, 0.05, 0.5), (x, y - 0.265, ROOF_Z + 0.28), M_WOOD, col=col))
    obs.append(box("CatHouseL", (0.05, 0.58, 0.5), (x - 0.305, y, ROOF_Z + 0.28), M_WOOD, col=col))
    obs.append(box("CatHouseR", (0.05, 0.58, 0.5), (x + 0.305, y, ROOF_Z + 0.28), M_WOOD_D, col=col))
    obs.append(box("CatHouseTopF", (0.66, 0.05, 0.16), (x, y + 0.265, ROOF_Z + 0.45), M_WOOD_D, col=col))
    obs.append(box("CatHouseLintelL", (0.13, 0.05, 0.34), (x - 0.265, y + 0.265, ROOF_Z + 0.22), M_WOOD, col=col))
    obs.append(box("CatHouseLintelR", (0.13, 0.05, 0.34), (x + 0.265, y + 0.265, ROOF_Z + 0.22), M_WOOD, col=col))
    obs.append(box("CatRoofA", (0.42, 0.72, 0.05), (x - 0.15, y, ROOF_Z + 0.61), M_PLASTIC, rz=0.0, col=col))
    obs.append(box("CatRoofB", (0.42, 0.72, 0.05), (x + 0.15, y, ROOF_Z + 0.61), M_PLASTIC, rz=0.0, col=col))
    obs[-2].rotation_euler[1] = math.radians(-18)
    obs[-1].rotation_euler[1] = math.radians(18)
    # 垫子
    obs.append(cyl("CatCushion", 0.24, 0.24, 0.07, (x, y - 0.02, ROOF_Z + 0.09), M_CUSHION, seg=14, col=col))
    # 小猫（蜷着睡）
    body = sphere("CatBody", 0.14, (x - 0.03, y - 0.05, ROOF_Z + 0.18), M_CAT, seg=12, col=col)
    body.scale = (1.25, 0.95, 0.72)
    obs.append(body)
    obs.append(sphere("CatHead", 0.085, (x - 0.13, y + 0.08, ROOF_Z + 0.19), M_CAT, seg=10, col=col))
    obs.append(cyl("CatEarL", 0.03, 0.001, 0.07, (x - 0.17, y + 0.07, ROOF_Z + 0.255),
                   M_CAT_D, seg=6, rx=math.radians(12), col=col))
    obs.append(cyl("CatEarR", 0.03, 0.001, 0.07, (x - 0.09, y + 0.1, ROOF_Z + 0.255),
                   M_CAT_D, seg=6, rx=math.radians(-12), col=col))
    obs.append(tube("CatTail", [(x + 0.12, y - 0.14, ROOF_Z + 0.15), (x + 0.18, y + 0.02, ROOF_Z + 0.13),
                                (x + 0.12, y + 0.14, ROOF_Z + 0.12)], 0.028, M_CAT_D, col=col))
    # 小碗
    obs.append(cyl("CatBowl", 0.09, 0.07, 0.06, (x - 0.38, y + 0.2, ROOF_Z + 0.03), M_METAL, seg=12, col=col))
    # 门口小灯
    obs.append(box("CatLamp", (0.09, 0.08, 0.05), (x, y + 0.25, ROOF_Z + 0.56), emit_mat("WarmSmall", "#ffbe78", 2.0), col=col))
    obs.append(tube("CatLampWire", [(x, y + 0.25, ROOF_Z + 0.58), (x, y + 0.05, ROOF_Z + 0.64),
                                    (x - 0.3, y - 0.2, ROOF_Z + 0.64)], 0.008, M_DARK, col=col))
    stage_group(obs, 112, 1.0, 14, 'pop')
    return obs


# ================================================================
#  积水 / 霓虹倒影
# ================================================================
def _blob(name, rx, ry, rz, loc, mat, col, seg=20, seed=0):
    """不规则水洼轮廓"""
    rnd = random.Random(seed)
    verts = []
    ca, sa = math.cos(rz), math.sin(rz)
    for i in range(seg):
        a = 2 * math.pi * i / seg
        k = 0.78 + rnd.random() * 0.34
        x, y = math.cos(a) * rx * k, math.sin(a) * ry * k
        verts.append((x * ca - y * sa, x * sa + y * ca, 0.0))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], [tuple(range(seg))])
    me.update()
    ob = bpy.data.objects.new(name, me)
    link(ob, col)
    ob.location = loc
    if mat:
        me.materials.append(mat)
    return ob


def build_puddles(col):
    obs = []
    specs = [
        (2.55, 2.95, 0.95, 0.6, 0.3),
        (-2.35, 2.55, 0.8, 0.5, -0.2),
        (3.6, -0.35, 0.62, 0.88, 0.15),
        (0.95, 3.85, 0.55, 0.35, 0.4),
        (-3.9, 3.6, 0.65, 0.4, -0.3),
    ]
    for i, (x, y, rx, ry, rz) in enumerate(specs):
        obs.append(_blob("Puddle%d" % i, rx, ry, rz, (x, y, ROOF_Z + 0.008),
                         M_PUDDLE, col, seg=22, seed=i * 7 + 3))

    # 霓虹倒影（细长色块）
    refl = [
        (2.6, 3.1, 0.9, 0.09, emit_mat("RefPink", "#ff5f9e", 1.0), 0.2),
        (2.35, 2.78, 0.6, 0.05, emit_mat("RefCyan", "#5fd8ff", 0.9), -0.1),
        (-2.45, 2.7, 0.7, 0.06, emit_mat("RefPink2", "#ff7fb2", 0.8), 0.15),
        (-2.1, 2.4, 0.42, 0.04, emit_mat("RefWarm", "#ffb066", 0.8), 0.3),
        (3.55, -0.15, 0.5, 0.06, emit_mat("RefCyan2", "#5fd8ff", 0.8), 0.25),
        (3.7, 0.2, 0.35, 0.04, emit_mat("RefPink3", "#ff5f9e", 0.7), -0.3),
        (1.0, 3.9, 0.45, 0.05, emit_mat("RefWarm2", "#ffc36a", 0.7), 0.4),
    ]
    for i, (x, y, w, d, mat, rz) in enumerate(refl):
        obs.append(box("Refl%d" % i, (w, d, 0.008), (x, y, ROOF_Z + 0.017), mat, rz=rz, col=col))

    stage_group(obs, 150, 1.4, 12, 'pop')
    return obs


# ================================================================
#  雨
# ================================================================
def build_rain(col):
    me = bpy.data.meshes.new("Rain")
    bm = bmesh.new()
    for i in range(520):
        x = (random.random() - 0.5) * 9.8
        y = (random.random() - 0.5) * 9.8
        z = ROOF_Z + random.random() * 8.6
        ln = 0.1 + random.random() * 0.2
        m = Matrix.Translation((x, y, z)) @ Matrix.Diagonal((0.004, 0.004, ln, 1.0))
        bmesh.ops.create_cube(bm, size=1.0, matrix=m)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("Rain", me)
    col.objects.link(ob)
    me.materials.append(emit_mat("RainMat", "#7fa8e8", 0.45))
    stage(ob, 165, 20, 'pop')
    return ob

# -*- coding: utf-8 -*-
"""
雨夜便利店 · 街角微缩模型（Blender 5.x 程序化构建）
- 12x12 正方形底座，全部元素搭建其上
- 三渲二：Diffuse -> Shader to RGB -> ColorRamp(常量) -> 乘底色 -> Emission
- 反向壳描边：Solidify(flip normals, material_offset)
- 入场组装动画：分组错峰 keyframe

用法：
    blender -b -P build_konbini.py
    blender -b -P build_konbini.py -- --render     # 额外渲染预览图
"""

import bpy
import bmesh
import math
import os
import random
import sys
from mathutils import Vector, Matrix

ROOT = r"E:\app_ideas\godot-game\Draft\draft3d\env_konbini_night"
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "export")

STD = dict(x0=-5.2, x1=0.9, y0=-5.2, y1=-1.4, h=3.8)   # 便利店占地 / 层高
BASE_Z = 0.14                                           # 人行道抬高

random.seed(20261112)

# ---------------------------------------------------------------- 场景清理
def wipe():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.curves,
                  bpy.data.lights, bpy.data.cameras, bpy.data.collections):
        for b in list(block):
            if b.users == 0:
                block.remove(b)


def new_collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


# ---------------------------------------------------------------- 颜色
def srgb(hex_str):
    """#rrggbb -> 线性 RGBA"""
    h = hex_str.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (out[0], out[1], out[2], 1.0)


# ---------------------------------------------------------------- 材质
MATS = {}

RAMP_STOPS = [(0.00, 0.30), (0.14, 0.48), (0.33, 0.72), (0.58, 1.0)]


def _ramp(nt):
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.interpolation = 'CONSTANT'
    while len(cr.elements) > 1:
        cr.elements.remove(cr.elements[-1])
    first = cr.elements[0]
    first.position = RAMP_STOPS[0][0]
    v = RAMP_STOPS[0][1]
    first.color = (v, v, v, 1.0)
    for pos, val in RAMP_STOPS[1:]:
        e = cr.elements.new(pos)
        e.color = (val, val, val, 1.0)
    return ramp


def toon_mat(name, hex_color, emit=0.0):
    """三渲二材质：阶梯光。emit>0 时叠加自发光（用于灯箱/玻璃）。"""
    key = name
    if key in MATS:
        return MATS[key]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)
    emis = nt.nodes.new("ShaderNodeEmission")
    emis.location = (400, 0)
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.blend_type = 'MULTIPLY'
    mix.location = (200, 0)
    mix.inputs["Fac"].default_value = 1.0
    mix.inputs["Color1"].default_value = srgb(hex_color)

    diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
    diff.location = (-420, 0)
    diff.inputs["Color"].default_value = (1, 1, 1, 1)
    s2rgb = nt.nodes.new("ShaderNodeShaderToRGB")
    s2rgb.location = (-240, 0)
    ramp = _ramp(nt)
    ramp.location = (-60, 0)

    nt.links.new(diff.outputs["BSDF"], s2rgb.inputs["Shader"])
    nt.links.new(s2rgb.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], mix.inputs["Color2"])
    nt.links.new(mix.outputs["Color"], emis.inputs["Color"])
    emis.inputs["Strength"].default_value = 1.0
    nt.links.new(emis.outputs["Emission"], out.inputs["Surface"])

    if emit > 0.0:
        # 自发光叠加：在 Emission 前用 Add 混入底色
        add = nt.nodes.new("ShaderNodeMixRGB")
        add.blend_type = 'ADD'
        add.location = (300, -200)
        add.inputs["Fac"].default_value = min(1.0, emit)
        add.inputs["Color2"].default_value = srgb(hex_color)
        nt.links.new(mix.outputs["Color"], add.inputs["Color1"])
        nt.links.new(add.outputs["Color"], emis.inputs["Color"])

    MATS[key] = mat
    return mat


def emit_mat(name, hex_color, strength=1.0):
    if name in MATS:
        return MATS[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = srgb(hex_color)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    MATS[name] = mat
    return mat


def make_outline_mat():
    mat = bpy.data.materials.new("Outline")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = srgb("#0a0e17")
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    mat.use_backface_culling = True
    return mat


OUTLINE = None


# ---------------------------------------------------------------- 几何
def _finish(me, name, loc, mat, rz, col, outline, outline_w):
    ob = bpy.data.objects.new(name, me)
    (col or bpy.context.scene.collection).objects.link(ob)
    ob.location = loc
    ob.rotation_euler[2] = rz
    if mat:
        me.materials.append(mat)
    if outline:
        pass  # 描边交给 Freestyle 统一处理（见 setup_freestyle）
    return ob


def make_outline(ob, w):
    """（已弃用）反向外壳描边，现由 Freestyle 统一生成墨线。"""


def box(name, dims, loc, mat=None, rz=0.0, col=None, outline=False, outline_w=0.012):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(me)
    bm.free()
    me.transform(Matrix.Diagonal((dims[0], dims[1], dims[2], 1.0)))
    return _finish(me, name, loc, mat, rz, col, outline, outline_w)


def cyl(name, r1, r2, h, loc, mat=None, seg=16, rz=0.0, rx=0.0, col=None,
        outline=False, outline_w=0.012):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    try:
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                              radius1=r1, radius2=r2, depth=h)
    except TypeError:
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                              diameter1=r1 * 2, diameter2=r2 * 2, depth=h)
    bm.to_mesh(me)
    bm.free()
    ob = _finish(me, name, loc, mat, rz, col, outline, outline_w)
    ob.rotation_euler[0] = rx
    return ob


def sphere(name, r, loc, mat=None, seg=14, col=None, outline=False, outline_w=0.012):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    try:
        bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(6, seg // 2), radius=r)
    except TypeError:
        bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(6, seg // 2), diameter=r * 2)
    bm.to_mesh(me)
    bm.free()
    return _finish(me, name, loc, mat, 0.0, col, outline, outline_w)


def plane(name, w, d, loc, mat, rz=0.0, col=None):
    me = bpy.data.meshes.new(name)
    verts = [(-w / 2, -d / 2, 0), (w / 2, -d / 2, 0), (w / 2, d / 2, 0), (-w / 2, d / 2, 0)]
    me.from_pydata(verts, [], [(0, 1, 2, 3)])
    me.update()
    return _finish(me, name, loc, mat, rz, col, False, 0.0)


def quad(name, verts, mat, col=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], [(0, 1, 2, 3)])
    me.update()
    ob = bpy.data.objects.new(name, me)
    (col or bpy.context.scene.collection).objects.link(ob)
    if mat:
        me.materials.append(mat)
    return ob


def torus(name, R, r, loc, mat, seg_major=20, seg_minor=8, rot=(0, 0, 0), col=None):
    me = bpy.data.meshes.new(name)
    verts, faces = [], []
    for i in range(seg_major):
        a = 2 * math.pi * i / seg_major
        ca, sa = math.cos(a), math.sin(a)
        for j in range(seg_minor):
            b = 2 * math.pi * j / seg_minor
            rr = R + r * math.cos(b)
            verts.append((rr * ca, rr * sa, r * math.sin(b)))
    for i in range(seg_major):
        for j in range(seg_minor):
            a0 = i * seg_minor + j
            a1 = i * seg_minor + (j + 1) % seg_minor
            b0 = ((i + 1) % seg_major) * seg_minor + j
            b1 = ((i + 1) % seg_major) * seg_minor + (j + 1) % seg_minor
            faces.append((a0, b0, b1, a1))
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    (col or bpy.context.scene.collection).objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    if mat:
        me.materials.append(mat)
    return ob


def tube(name, points, radius, mat, col=None, res=8):
    """沿折线的管道（电线/护栏）"""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = 1
    cu.resolution_u = res
    sp = cu.splines.new('POLY')
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    ob = bpy.data.objects.new(name, cu)
    (col or bpy.context.scene.collection).objects.link(ob)
    if mat:
        cu.materials.append(mat)
    return ob


def text_mesh(name, body, size, loc, rot, mat, col=None, extrude=0.0):
    """生成文字并转成网格；找不到日文字体则返回 None"""
    font = None
    for path in (r"C:\Windows\Fonts\YuGothM.ttc",
                 r"C:\Windows\Fonts\YuGothB.ttc",
                 r"C:\Windows\Fonts\meiryo.ttc",
                 r"C:\Windows\Fonts\msgothic.ttc"):
        if os.path.exists(path):
            try:
                font = bpy.data.fonts.load(path)
                break
            except Exception:
                font = None
    if font is None:
        return None
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = body
    cu.size = size
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    cu.extrude = extrude
    cu.font = font
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    bpy.context.scene.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.curves.remove(cu)
    ob = bpy.data.objects.new(name, me)
    (col or bpy.context.scene.collection).objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    if mat:
        me.materials.append(mat)
    return ob


# ---------------------------------------------------------------- 动画登记
STAGE = []      # (object, frame_start, duration, mode)


def stage(ob, f0, dur=14, mode='pop'):
    STAGE.append((ob, f0, dur, mode))
    return ob


def stage_group(objs, f0, step=1.5, dur=14, mode='pop'):
    f = f0
    for ob in objs:
        stage(ob, f, dur, mode)
        f += step
    return objs


# ================================================================
#  1. 底座
# ================================================================
def build_base(col):
    m_plinth = toon_mat("Plinth", "#161b26")
    m_trim = toon_mat("PlinthTrim", "#232c3c")
    m_rim = emit_mat("PlinthRim", "#3f6fa8", 1.6)
    obs = []
    obs.append(box("Plinth", (12.2, 12.2, 0.74), (0, 0, -0.37), m_plinth,
                   col=col, outline=True, outline_w=0.016))
    obs.append(box("PlinthTrim", (12.56, 12.56, 0.12), (0, 0, -0.74), m_trim, col=col))
    # 底座侧面的一道冷色反光条
    obs.append(box("RimLineF", (12.0, 0.02, 0.05), (0, 6.1, -0.05), m_rim, col=col))
    obs.append(box("RimLineB", (12.0, 0.02, 0.05), (0, -6.1, -0.05), m_rim, col=col))
    obs.append(box("RimLineR", (0.02, 12.0, 0.05), (6.1, 0, -0.05), m_rim, col=col))
    obs.append(box("RimLineL", (0.02, 12.0, 0.05), (-6.1, 0, -0.05), m_rim, col=col))
    stage_group(obs, 1, 1.0, 16, 'rise')
    return obs


# ================================================================
#  2. 街道
# ================================================================
def build_street(col):
    m_asphalt = toon_mat("Asphalt", "#2a3142")
    m_walk = toon_mat("Sidewalk", "#4f5666")
    m_curb = toon_mat("Curb", "#4b5468")
    m_paint = toon_mat("Paint", "#e2e9f3")
    m_paintY = toon_mat("PaintY", "#d8b264")
    m_concrete = toon_mat("AlleyConcrete", "#3a4152")
    obs = []

    # 沥青顶面
    obs.append(box("Asphalt", (12.0, 12.0, 0.06), (0, 0, -0.03), m_asphalt, col=col))

    # 人行道
    walk_specs = [
        ("WalkA", (9.0, 2.8, BASE_Z), (-1.5, 0.0, BASE_Z / 2)),
        ("WalkB", (2.1, 4.6, BASE_Z), (1.95, -3.7, BASE_Z / 2)),
        ("WalkFarR", (0.5, 12.0, BASE_Z), (5.75, 0.0, BASE_Z / 2)),
        ("WalkFarF", (12.0, 0.8, BASE_Z), (0.0, 5.6, BASE_Z / 2)),
        ("Alley", (0.8, 4.6, BASE_Z), (-5.6, -3.7, BASE_Z / 2)),
    ]
    for name, dims, loc in walk_specs:
        mat = m_concrete if name == "Alley" else m_walk
        obs.append(box(name, dims, loc, mat, col=col, outline=True, outline_w=0.008))

    # 路缘石
    curbs = [
        ((9.0, 0.16, 0.06), (-1.5, 1.4, BASE_Z + 0.01)),
        ((0.16, 4.6, 0.06), (3.0, -3.7, BASE_Z + 0.01)),
        ((12.0, 0.16, 0.06), (0.0, 5.2, BASE_Z + 0.01)),
        ((0.16, 12.0, 0.06), (5.5, 0.0, BASE_Z + 0.01)),
    ]
    for i, (d, l) in enumerate(curbs):
        obs.append(box("Curb%d" % i, d, l, m_curb, col=col))

    # 斑马线（横街，沿 y 排列）
    for i in range(6):
        y = 1.75 + i * 0.62
        obs.append(plane("ZebraH%d" % i, 1.9, 0.34, (2.0, y, 0.004), m_paint, col=col))
    # 斑马线（竖街，沿 x 排列）
    for i in range(4):
        x = 3.45 + i * 0.62
        obs.append(box("ZebraV%d" % i, (0.34, 1.9, 0.004), (x, 0.45, 0.004), m_paint, col=col))

    # 车道中心虚线
    for i in range(5):
        y = 1.95 + i * 0.85
        obs.append(plane("LaneMarkH%d" % i, 0.62, 0.12, (-3.4, y, 0.004), m_paintY, col=col))
    for i in range(5):
        x = 3.45 + i * 0.85
        obs.append(plane("LaneMarkV%d" % i, 0.12, 0.62, (x, 3.9, 0.004), m_paintY, col=col))

    # 停止线
    obs.append(plane("StopLine", 0.18, 2.6, (1.05, 3.6, 0.004), m_paint, col=col))

    # 停车位白线
    obs.append(plane("ParkA", 2.4, 0.08, (-4.2, 3.15, 0.004), m_paint, col=col))
    obs.append(plane("ParkB", 2.4, 0.08, (-4.2, 4.65, 0.004), m_paint, col=col))
    obs.append(plane("ParkC", 0.08, 1.5, (-3.0, 3.9, 0.004), m_paint, col=col))

    # 排水沟格栅
    m_grate = toon_mat("Grate", "#20262f")
    for i in range(4):
        obs.append(box("GrateH%d" % i, (0.42, 0.14, 0.02), (-2.9 + i * 1.5, 1.32, 0.005),
                       m_grate, col=col))
    for i in range(3):
        obs.append(box("GrateV%d" % i, (0.14, 0.42, 0.02), (2.92, -4.4 + i * 1.5, 0.005),
                       m_grate, col=col))
    # 井盖
    obs.append(cyl("Manhole", 0.36, 0.36, 0.02, (-1.2, 3.9, 0.006), m_grate, seg=20, col=col))

    stage_group(obs, 18, 0.8, 16, 'rise')
    return obs


# ================================================================
#  3. 便利店（壳体 / 玻璃框 / 招牌 / 雨棚）
# ================================================================
def build_store(col):
    cx = (STD["x0"] + STD["x1"]) / 2.0
    cy = (STD["y0"] + STD["y1"]) / 2.0
    W = STD["x1"] - STD["x0"]
    D = STD["y1"] - STD["y0"]
    H = STD["h"]

    m_wall = toon_mat("Wall", "#8e8a7c")
    m_wallD = toon_mat("WallDark", "#4a4a44")
    m_roof = toon_mat("Roof", "#3c4354")
    m_metal = toon_mat("Metal", "#7b8494")
    m_metalD = toon_mat("MetalDark", "#2d3542")
    m_white = toon_mat("StoreWhite", "#f0e6cc")
    m_awning = toon_mat("AwningCream", "#d8d1bb")
    m_blue = toon_mat("BrandBlue", "#2f63b5")
    m_red = toon_mat("BrandRed", "#d8453c")
    m_lamp = emit_mat("StripLamp", "#ffe6b8", 3.0)
    m_signface = emit_mat("SignFace", "#f4f1e6", 0.9)

    obs = []
    z = BASE_Z

    # 地台 / 店内地面
    obs.append(box("StorePad", (W + 0.2, D + 0.2, 0.16), (cx, cy, z - 0.08), m_metalD, col=col))
    obs.append(box("StoreFloor", (W - 0.1, D - 0.1, 0.04), (cx, cy, z + 0.0),
                   toon_mat("FloorIn", "#c19a6b"), col=col))

    # 后墙 / 左墙
    obs.append(box("BackWall", (W, H, 0.16), (cx, STD["y0"] - 0.08, z + H / 2), m_wall,
                   col=col, outline=True, outline_w=0.014))
    obs.append(box("LeftWall", (0.16, D, H), (STD["x0"] - 0.08, cy, z + H / 2), m_wall,
                   col=col, outline=True, outline_w=0.014))

    # 正面：下裙 + 上檐
    obs.append(box("FrontSkirt", (W, 0.52, 0.16), (cx, STD["y1"] + 0.08, z + 0.26), m_wall,
                   col=col, outline=True, outline_w=0.012))
    obs.append(box("FrontTop", (W, 0.42, 0.2), (cx, STD["y1"] + 0.06, z + 3.0), m_wall,
                   col=col, outline=True, outline_w=0.012))
    # 右侧面：下裙 + 上檐
    obs.append(box("SideSkirt", (0.16, D, 0.52), (STD["x1"] + 0.08, cy, z + 0.26), m_wall,
                   col=col, outline=True, outline_w=0.012))
    obs.append(box("SideTop", (0.2, D, 0.42), (STD["x1"] + 0.06, cy, z + 3.0), m_wall,
                   col=col, outline=True, outline_w=0.012))
    # 转角柱
    obs.append(box("CornerCol", (0.3, 0.3, H), (STD["x1"] - 0.02, STD["y1"] - 0.02, z + H / 2),
                   m_wallD, col=col, outline=True, outline_w=0.012))

    # 屋顶 / 女儿墙
    obs.append(box("Roof", (W + 0.24, D + 0.24, 0.18), (cx, cy, z + H + 0.09), m_roof,
                   col=col, outline=True, outline_w=0.014))
    for name, dims, loc in [
        ("ParapetF", (W + 0.24, 0.1, 0.32), (cx, STD["y1"] + 0.12, z + H + 0.32)),
        ("ParapetB", (W + 0.24, 0.1, 0.32), (cx, STD["y0"] - 0.12, z + H + 0.32)),
        ("ParapetR", (0.1, D + 0.24, 0.32), (STD["x1"] + 0.12, cy, z + H + 0.32)),
        ("ParapetL", (0.1, D + 0.24, 0.32), (STD["x0"] - 0.12, cy, z + H + 0.32)),
    ]:
        obs.append(box(name, dims, loc, m_roof, col=col))

    # 室内吊顶
    obs.append(box("Ceiling", (W - 0.2, D - 0.2, 0.06), (cx, cy, z + H - 0.06), m_white, col=col))

    # 屋顶设备
    obs.append(box("RoofAC1", (1.0, 0.8, 0.6), (cx - 1.3, cy - 0.5, z + H + 0.48), m_metal,
                   col=col, outline=True, outline_w=0.01))
    obs.append(cyl("RoofFan", 0.3, 0.3, 0.06, (cx - 1.3, cy - 0.5, z + H + 0.79), m_metalD,
                   seg=18, col=col))
    obs.append(box("RoofBox", (0.6, 0.5, 0.4), (cx + 0.6, cy + 0.6, z + H + 0.38), m_metal, col=col))
    obs.append(cyl("Pipe1", 0.07, 0.07, 1.0, (cx + 1.6, cy - 0.9, z + H + 0.6), m_metalD, seg=10, col=col))
    obs.append(cyl("Pipe2", 0.07, 0.07, 0.7, (cx + 1.9, cy - 0.7, z + H + 0.45), m_metalD, seg=10, col=col))

    # 雨棚（正面）
    obs.append(box("AwningF", (W + 0.5, 0.62, 0.09), (cx, STD["y1"] + 0.42, z + 2.72), m_awning,
                   col=col, outline=True, outline_w=0.012))
    obs.append(box("AwnEdgeBlueF", (W + 0.5, 0.07, 0.05), (cx, STD["y1"] + 0.71, z + 2.615), m_blue, col=col))
    obs.append(box("AwnEdgeRedF", (W + 0.5, 0.07, 0.045), (cx, STD["y1"] + 0.712, z + 2.565), m_red, col=col))
    obs.append(box("AwnLightF", (W - 0.4, 0.06, 0.05), (cx, STD["y1"] + 0.66, z + 2.66), m_lamp, col=col))
    # 雨棚（右侧）
    obs.append(box("AwningR", (0.62, D + 0.5, 0.09), (STD["x1"] + 0.42, cy, z + 2.72), m_awning,
                   col=col, outline=True, outline_w=0.012))
    obs.append(box("AwnEdgeBlueR", (0.07, D + 0.5, 0.05), (STD["x1"] + 0.71, cy, z + 2.615), m_blue, col=col))
    obs.append(box("AwnEdgeRedR", (0.07, D + 0.5, 0.045), (STD["x1"] + 0.712, cy, z + 2.565), m_red, col=col))
    obs.append(box("AwnLightR", (0.06, D - 0.4, 0.05), (STD["x1"] + 0.66, cy, z + 2.66), m_lamp, col=col))
    # 雨棚支撑
    for i, x in enumerate((STD["x0"] + 0.5, STD["x1"] - 0.5)):
        obs.append(cyl("AwnStrut%d" % i, 0.025, 0.025, 0.7, (x, STD["y1"] + 0.62, z + 2.42),
                       m_metal, seg=8, col=col))

    # ---------- 玻璃框（不做透明玻璃，保证店内清晰可见）
    y0, y1 = z + 0.5, z + 2.7
    cgy = (y0 + y1) / 2
    gh = y1 - y0
    mframe = m_metalD

    # 正面竖框
    for i, x in enumerate((-5.0, -3.8, -2.62, -1.18, -0.2, 0.72)):
        obs.append(box("MullionF%d" % i, (0.07, 0.09, gh + 0.08), (x, STD["y1"] + 0.02, cgy), mframe, col=col))
    # 右侧竖框
    for i, y in enumerate((-5.0, -3.5, -2.1, -1.55)):
        obs.append(box("MullionR%d" % i, (0.09, 0.07, gh + 0.08), (STD["x1"] + 0.02, y, cgy), mframe, col=col))
    # 上下横框
    obs.append(box("RailFin0", (6.0, 0.1, 0.07), (cx, STD["y1"] + 0.02, y0), mframe, col=col))
    obs.append(box("RailFin1", (6.0, 0.1, 0.07), (cx, STD["y1"] + 0.02, y1), mframe, col=col))
    obs.append(box("RailSid0", (0.1, 3.6, 0.07), (STD["x1"] + 0.02, -3.3, y0), mframe, col=col))
    obs.append(box("RailSid1", (0.1, 3.6, 0.07), (STD["x1"] + 0.02, -3.3, y1), mframe, col=col))

    # 自动门
    dz = STD["y1"] + 0.01
    obs.append(box("DoorL", (0.09, 0.14, gh), (-2.55, dz, cgy), mframe, col=col))
    obs.append(box("DoorR", (0.09, 0.14, gh), (-1.25, dz, cgy), mframe, col=col))
    obs.append(box("DoorTop", (1.4, 0.16, 0.1), (-1.9, dz, y1 + 0.03), mframe, col=col))
    obs.append(box("DoorMid", (0.05, 0.1, gh - 0.16), (-1.94, dz + 0.02, cgy), m_metal, col=col))
    obs.append(box("DoorHandle", (0.04, 0.05, 0.5), (-1.66, dz + 0.08, z + 1.45), m_metal, col=col))
    obs.append(box("DoorSill", (1.6, 0.24, 0.05), (-1.9, dz + 0.06, z + 0.03), mframe, col=col))

    # 门口地垫
    obs.append(plane("Mat", 1.5, 0.75, (-1.9, -1.0, BASE_Z + 0.002),
                     toon_mat("Doormat", "#333b4d"), col=col))

    # ---------- 招牌
    sz = z + 3.44
    obs.append(box("SignBoxF", (W + 0.3, 0.28, 0.72), (cx, STD["y1"] + 0.02, sz), m_white,
                   col=col, outline=True, outline_w=0.014))
    obs.append(box("SignFaceF", (W + 0.24, 0.02, 0.66), (cx, STD["y1"] + 0.17, sz), m_signface, col=col))
    obs.append(box("SignBoxR", (0.28, D + 0.3, 0.72), (STD["x1"] + 0.02, cy, sz), m_white,
                   col=col, outline=True, outline_w=0.014))
    obs.append(box("SignFaceR", (0.02, D + 0.24, 0.66), (STD["x1"] + 0.17, cy, sz), m_signface, col=col))
    # 招牌上的品牌色条
    obs.append(box("SignStripeB", (W + 0.24, 0.01, 0.05), (cx, STD["y1"] + 0.185, sz + 0.29), m_blue, col=col))
    obs.append(box("SignStripeR", (W + 0.24, 0.01, 0.05), (cx, STD["y1"] + 0.185, sz - 0.29), m_red, col=col))

    # 招牌文字
    t1 = text_mesh("SignTextJP", "コンビニ", 0.40, (-3.55, STD["y1"] + 0.20, sz),
                   (math.pi / 2, 0, math.pi), emit_mat("TextNavy", "#1b3766", 1.2), col=col)
    if t1:
        obs.append(t1)
    t2 = text_mesh("SignText24", "24時間営業", 0.20, (-0.95, STD["y1"] + 0.20, sz + 0.10),
                   (math.pi / 2, 0, math.pi), emit_mat("TextRed", "#c8372c", 1.2), col=col)
    if t2:
        obs.append(t2)

    stage_group(obs, 40, 1.0, 16, 'rise')
    return obs


# ================================================================
#  4. 店内陈设
# ================================================================
def build_interior(col):
    cx = (STD["x0"] + STD["x1"]) / 2.0
    W = STD["x1"] - STD["x0"]
    z = BASE_Z
    m_shelf = toon_mat("Shelf", "#ded4bd")
    m_frame = toon_mat("ShelfFrame", "#b0a68f")
    m_counter = toon_mat("Counter", "#e6dcc6")
    m_metalD = toon_mat("MetalDark", "#2d3542")
    m_cool = emit_mat("CoolPanel", "#dcefff", 1.6)
    m_warm = emit_mat("WarmPanel", "#ffeccb", 2.2)
    candy = ["#f26d6d", "#f2b23e", "#6fc4f0", "#7fd68a", "#f07fc0",
             "#f7f4ea", "#9d8bf2", "#4fbfae", "#e86a3c", "#ffd75e"]
    obs = []

    # ---- 冷柜（后墙）
    fw, fh = 4.6, 2.25
    fy = STD["y0"] + 0.42
    obs.append(box("Fridge", (fw, 0.62, fh), (cx - 0.1, fy, z + fh / 2), m_frame,
                   col=col, outline=True, outline_w=0.01))
    # 冷柜门：5 扇，带饮料色块
    door_w = (fw - 0.1) / 5.0
    for i in range(5):
        x = cx - 0.1 - fw / 2 + 0.05 + door_w * (i + 0.5)
        obs.append(box("FridgeDoor%d" % i, (door_w - 0.04, 0.02, fh - 0.12),
                       (x, STD["y0"] + 0.735, z + fh / 2), m_cool, col=col))
        for r in range(4):
            for k in range(3):
                c = candy[(i * 7 + r * 3 + k) % len(candy)]
                obs.append(box("Bottle%d_%d_%d" % (i, r, k),
                               (door_w * 0.18, 0.02, 0.10),
                               (x - door_w * 0.26 + k * door_w * 0.26,
                                STD["y0"] + 0.745, z + 0.45 + r * 0.42),
                               emit_mat("Bottle" + str((i * 7 + r * 3 + k) % len(candy)),
                                        c, 1.0), col=col))
    obs.append(box("FridgeLamp", (fw - 0.2, 0.1, 0.06), (cx - 0.1, STD["y0"] + 0.66, z + fh - 0.06),
                   m_warm, col=col))

    # ---- 三组货架
    levels = [0.18, 0.42, 0.66, 0.9, 1.14]
    unit_x = [-3.95, -2.62, -1.29]
    unit_y = -3.15
    unit_l = 2.5
    for u, x in enumerate(unit_x):
        obs.append(box("ShelfSide%da" % u, (0.05, unit_l, 1.22), (x - 0.31, unit_y, z + 0.61), m_frame, col=col))
        obs.append(box("ShelfSide%db" % u, (0.05, unit_l, 1.22), (x + 0.31, unit_y, z + 0.61), m_frame, col=col))
        for i, lv in enumerate(levels):
            obs.append(box("Shelf%d_%d" % (u, i), (0.62, unit_l, 0.03), (x, unit_y, z + lv), m_shelf, col=col))
            obs.append(box("Price%d_%d" % (u, i), (0.015, unit_l, 0.04),
                           (x + 0.315, unit_y, z + lv + 0.04), m_shelf, col=col))
        obs.append(box("ShelfTop%d" % u, (0.64, unit_l + 0.04, 0.05), (x, unit_y, z + 1.24), m_frame, col=col))

        # 商品
        for l_i, lv in enumerate(levels):
            for k in range(10):
                side = -0.145 if k % 2 == 0 else 0.145
                row = k // 2
                ci = (u * 11 + l_i * 5 + k) % len(candy)
                obs.append(box("Prod%d_%d_%d" % (u, l_i, k), (0.12, 0.10, 0.16),
                               (x + side, unit_y - 1.05 + row * 0.52, z + lv + 0.095),
                               toon_mat("Candy" + str(ci), candy[ci]), col=col))

    # ---- 收银台
    obs.append(box("Counter", (0.72, 2.1, 0.92), (0.5, -2.6, z + 0.46), m_counter,
                   col=col, outline=True, outline_w=0.01))
    obs.append(box("CounterTop", (0.8, 2.2, 0.06), (0.5, -2.6, z + 0.95), toon_mat("CounterTop", "#f0f2f5"), col=col))
    obs.append(box("Register", (0.3, 0.26, 0.22), (0.52, -3.15, z + 1.09), m_metalD, col=col))
    obs.append(box("RegisterScreen", (0.22, 0.02, 0.16), (0.52, -3.02, z + 1.13), m_cool, col=col))
    obs.append(box("HotCase", (0.42, 0.4, 0.34), (0.52, -2.55, z + 1.15), toon_mat("Metal", "#7b8494"), col=col))
    obs.append(box("HotCaseIn", (0.34, 0.32, 0.24), (0.52, -2.55, z + 1.15),
                   emit_mat("HotGlow", "#ffb765", 1.4), col=col))
    obs.append(box("Coffee", (0.3, 0.32, 0.44), (0.52, -1.95, z + 1.2), m_metalD, col=col))
    obs.append(box("CoffeeLed", (0.24, 0.06, 0.06), (0.52, -1.8, z + 1.28),
                   emit_mat("CoffeeLed", "#ffcf6a", 1.6), col=col))

    # ---- 杂志架（前窗）
    obs.append(box("MagRack", (1.9, 0.42, 0.62), (-3.7, -1.95, z + 0.31),
                   toon_mat("MagRack", "#b8bcc6"), col=col, outline=True, outline_w=0.008))
    for i in range(9):
        obs.append(box("Mag1_%d" % i, (0.16, 0.02, 0.24), (-4.55 + i * 0.19, -1.735, z + 0.44),
                       toon_mat("Mag1_%d" % i, candy[i % len(candy)]), col=col))
    for i in range(9):
        obs.append(box("Mag2_%d" % i, (0.16, 0.02, 0.20), (-4.55 + i * 0.19, -1.735, z + 0.17),
                       toon_mat("Mag2_%d" % i, candy[(i * 3 + 1) % len(candy)]), col=col))

    # ---- 复印机 / ATM
    obs.append(box("ATM", (0.6, 0.48, 1.45), (-4.85, -2.9, z + 0.72),
                   toon_mat("ATM", "#8a909c"), col=col, outline=True, outline_w=0.008))
    obs.append(box("ATMScreen", (0.5, 0.04, 0.3), (-4.85, -2.655, z + 1.1), m_cool, col=col))

    # ---- 吊顶灯管
    for i in range(3):
        for k in range(2):
            obs.append(box("CeilLamp%d_%d" % (i, k), (1.25, 0.2, 0.05),
                           (-4.1 + i * 1.45, -4.1 + k * 1.45, z + STD["h"] - 0.13), m_warm, col=col))

    # ---- 吊牌
    for i, (txt, x, y) in enumerate((("おでん", -3.6, -2.2), ("COFFEE", -1.6, -2.9), ("ATM", -4.6, -3.0))):
        t = text_mesh("Hang%d" % i, txt, 0.16, (x, y, z + 2.86), (math.pi / 2, 0, math.pi),
                      emit_mat("HangTxt%d" % i, "#4a3a28", 1.2), col=col)
        if t:
            obs.append(t)
        obs.append(cyl("HangRod%d" % i, 0.01, 0.01, 0.5, (x, y, z + 3.2), m_metalD, seg=6, col=col))

    stage_group(obs, 58, 0.35, 14, 'pop')
    return obs


# ================================================================
#  5. 街角道具
# ================================================================
def group(name, loc, rz=0.0, col=None):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.3
    (col or bpy.context.scene.collection).objects.link(e)
    e.location = loc
    e.rotation_euler[2] = rz
    return e


def attach(parent, ob):
    ob.parent = parent
    ob.matrix_parent_inverse = Matrix.Identity(4)
    return ob


def build_vending(x, y, rz, col, body_hex, accent_hex, tag):
    g = group("Vending" + tag, (x, y, BASE_Z), rz, col)
    m_body = toon_mat("VendBody" + tag, body_hex)
    m_dark = toon_mat("VendDark", "#2c3444")
    m_face = emit_mat("VendFace" + tag, "#f7f4ea", 0.75)
    attach(g, box("VendBody" + tag, (0.94, 0.72, 1.9), (0, 0, 0.95), m_body,
                  col=col, outline=True, outline_w=0.012))
    attach(g, box("VendFace" + tag, (0.86, 0.02, 1.74), (0, 0.365, 0.98), m_face, col=col))
    # 商品展示格
    candy = ["#ef6a6a", "#f5b53f", "#64c0ee", "#7ed489", "#ef7dc0", "#fff3d9"]
    for r in range(4):
        for k in range(4):
            c = candy[(r * 4 + k) % len(candy)]
            attach(g, box("VendItem%s_%d_%d" % (tag, r, k), (0.17, 0.02, 0.13),
                          (-0.29 + k * 0.195, 0.375, 1.52 - r * 0.19),
                          emit_mat("VendC%d" % ((r * 4 + k) % len(candy)), c, 1.1), col=col))
    attach(g, box("VendPanel" + tag, (0.86, 0.03, 0.34), (0, 0.37, 0.42), m_dark, col=col))
    attach(g, box("VendSlot" + tag, (0.5, 0.05, 0.12), (0, 0.38, 0.22), m_dark, col=col))
    attach(g, box("VendStrip" + tag, (0.8, 0.06, 0.04), (0, 0.36, 0.06),
                  emit_mat("VendLight" + tag, accent_hex, 1.4), col=col))
    attach(g, box("VendSide" + tag, (0.04, 0.72, 1.9), (0.48, 0, 0.95), m_dark, col=col))
    attach(g, box("VendSide2" + tag, (0.04, 0.72, 1.9), (-0.48, 0, 0.95), m_dark, col=col))
    stage(g, 104, 14, 'pop')


def build_bicycle(x, y, rz, col):
    g = group("Bicycle", (x, y, BASE_Z), rz, col)
    m_frame = toon_mat("BikeFrame", "#3f74a8")
    m_tire = toon_mat("BikeTire", "#1c222c")
    m_metal = toon_mat("BikeMetal", "#b3bcc9")
    for i, wx in enumerate((-0.52, 0.52)):
        attach(g, torus("Wheel%d" % i, 0.32, 0.026, (wx, 0, 0.32), m_tire,
                        rot=(math.pi / 2, 0, 0), col=col))
        for k in range(4):
            attach(g, box("Spoke%d_%d" % (i, k), (0.62, 0.012, 0.012),
                          (wx, 0, 0.32), m_metal, rz=0.0, col=col))
    attach(g, box("BikeBar1", (1.0, 0.05, 0.05), (0, 0, 0.52), m_frame, col=col))
    attach(g, box("BikeBar2", (0.7, 0.045, 0.045), (-0.1, 0, 0.36), m_frame, rz=0.0, col=col))
    attach(g, box("BikeFork", (0.05, 0.05, 0.5), (0.55, 0, 0.58), m_frame, col=col))
    attach(g, box("BikeHandle", (0.05, 0.42, 0.28), (0.6, 0, 0.86), m_metal, col=col))
    attach(g, box("BikeSeat", (0.24, 0.14, 0.06), (-0.32, 0, 0.78),
                  toon_mat("BikeSeat", "#232a36"), col=col))
    attach(g, box("BikeRack", (0.42, 0.26, 0.04), (-0.42, 0, 0.66), m_metal, col=col))
    attach(g, box("BikeBasket", (0.34, 0.3, 0.24), (0.6, 0, 0.98),
                  toon_mat("BikeBasket", "#9aa2b0"), col=col, outline=True, outline_w=0.008))
    stage(g, 112, 14, 'pop')


def build_umbrella(col):
    g = group("UmbrellaStand", (-2.35, -1.02, BASE_Z), 0.0, col)
    attach(g, cyl("UmbBody", 0.13, 0.11, 0.5, (0, 0, 0.25),
                  toon_mat("UmbBody", "#4a5568"), seg=14, col=col, outline=True, outline_w=0.008))
    attach(g, cyl("UmbRim", 0.12, 0.12, 0.03, (0, 0, 0.5),
                  toon_mat("UmbRim", "#a8b6c8"), seg=14, col=col))
    cols = ["#3d6fa8", "#c4553f", "#4a4a58"]
    for i in range(3):
        px = math.cos(i * 2.1) * 0.05
        py = math.sin(i * 2.1) * 0.05
        attach(g, cyl("UmbShaft%d" % i, 0.012, 0.012, 1.0, (px, py, 0.75),
                      toon_mat("UmbC%d" % i, cols[i]), seg=6, col=col))
        attach(g, cyl("UmbTip%d" % i, 0.02, 0.07, 0.42, (px, py, 0.62),
                      toon_mat("UmbCone%d" % i, cols[i]), seg=10, col=col))
    stage(g, 108, 14, 'pop')


def build_bins(col):
    g = group("Bins", (2.55, -3.0, BASE_Z), 0.0, col)
    for i, x in enumerate((-0.24, 0.24)):
        attach(g, cyl("Bin%d" % i, 0.17, 0.15, 0.62, (x, 0, 0.31),
                      toon_mat("BinC%d" % i, "#2f6a5c" if i == 0 else "#4a5464"),
                      seg=14, col=col, outline=True, outline_w=0.008))
        attach(g, cyl("BinLid%d" % i, 0.18, 0.18, 0.04, (x, 0, 0.64),
                      toon_mat("MetalDark", "#2d3542"), seg=14, col=col))
    stage(g, 110, 14, 'pop')


def build_street_lamp(col):
    g = group("StreetLamp", (2.15, 1.1, BASE_Z), 0.0, col)
    m_metal = toon_mat("Metal", "#7b8494")
    m_dark = toon_mat("MetalDark", "#2d3542")
    attach(g, cyl("LampPole", 0.06, 0.09, 4.3, (0, 0, 2.15), m_metal,
                  seg=12, col=col, outline=True, outline_w=0.01))
    attach(g, box("LampBase", (0.34, 0.34, 0.1), (0, 0, 0.05), m_dark, col=col))
    attach(g, box("LampArm", (0.62, 0.07, 0.07), (-0.28, 0, 4.24), m_metal, col=col))
    attach(g, box("LampHead", (0.46, 0.3, 0.16), (-0.6, 0, 4.1), m_dark,
                  col=col, outline=True, outline_w=0.01))
    attach(g, box("LampGlow", (0.38, 0.24, 0.05), (-0.6, 0, 4.0),
                  emit_mat("LampGlow", "#fff2cf", 3.0), col=col))
    stage(g, 100, 14, 'pop')


def build_poles_and_wires(col):
    m_pole = toon_mat("PoleConcrete", "#9a968a")
    m_dark = toon_mat("MetalDark", "#2d3542")
    pts = [(2.95, -5.75, 6.4), (5.75, 2.6, 5.9)]
    obs = []
    for i, (x, y, h) in enumerate(pts):
        g = group("Pole%d" % i, (x, y, BASE_Z), 0.0, col)
        attach(g, cyl("PoleBody%d" % i, 0.11, 0.15, h, (0, 0, h / 2), m_pole,
                      seg=12, col=col, outline=True, outline_w=0.01))
        for k in range(2):
            zz = h - 0.5 - k * 0.75
            attach(g, box("Crossarm%d_%d" % (i, k), (1.5, 0.1, 0.08), (0, 0, zz), m_dark, col=col))
            for s in (-0.6, 0.6):
                attach(g, cyl("Insulator%d_%d%s" % (i, k, s), 0.05, 0.05, 0.12,
                              (s, 0, zz + 0.11), toon_mat("Insulator", "#5f6b7d"), seg=8, col=col))
        # 变压器
        attach(g, cyl("Trans%d" % i, 0.16, 0.16, 0.5, (0.28, 0, h - 1.55), m_dark, seg=12, col=col))
        # 爬梯
        for k in range(5):
            attach(g, box("Rung%d_%d" % (i, k), (0.34, 0.04, 0.03),
                          (-0.18, 0.06, 1.2 + k * 0.36), m_dark, col=col))
        obs.append(g)
        stage(g, 116 + i * 4, 14, 'pop')

    # 悬链电线
    m_wire = toon_mat("Wire", "#222a36")
    for i in range(5):
        a = Vector((2.95 + (i - 2) * 0.16, -5.63, 6.15 - (i % 2) * 0.2))
        b = Vector((5.75 + (i - 2) * 0.14, 2.48, 5.62 - (i % 2) * 0.18))
        pts_w = []
        for s in range(9):
            t = s / 8.0
            p = a.lerp(b, t)
            p.z -= math.sin(t * math.pi) * (0.55 + 0.12 * i)
            pts_w.append(p)
        w = tube("Wire%d" % i, pts_w, 0.016, m_wire, col=col)
        obs.append(w)
        stage(w, 122, 10, 'pop')
    return obs


def build_guardrail(col):
    g = group("Guardrail", (1.62, 1.0, BASE_Z), 0.0, col)
    m = toon_mat("GuardMetal", "#9aa3b2")
    xs = [-0.62, -0.16, 0.3, 0.76]
    for i, x in enumerate(xs):
        attach(g, cyl("GrPost%d" % i, 0.03, 0.03, 0.62, (x, 0, 0.31), m, seg=8, col=col))
    attach(g, box("GrRail0", (1.5, 0.05, 0.05), (0.07, 0, 0.56), m, col=col))
    attach(g, box("GrRail1", (1.5, 0.05, 0.05), (0.07, 0, 0.31), m, col=col))
    stage(g, 118, 14, 'pop')


def build_stop_sign(col):
    g = group("StopSign", (2.62, 0.55, BASE_Z), 0.0, col)
    m_red = emit_mat("SignRed", "#cf3b30", 0.8)
    m_white = emit_mat("SignWhite", "#f2eee2", 1.0)
    attach(g, cyl("SignPole", 0.03, 0.03, 1.9, (0, 0, 0.95),
                  toon_mat("Metal", "#7b8494"), seg=8, col=col))
    tri = cyl("SignTri", 0.30, 0.30, 0.04, (0, 0, 1.72), m_red, seg=3,
              rx=math.pi / 2, col=col, outline=True, outline_w=0.01)
    attach(g, tri)
    attach(g, box("SignBar", (0.26, 0.02, 0.05), (0, -0.03, 1.70), m_white, col=col))
    stage(g, 120, 14, 'pop')


def build_poster(col):
    g = group("PosterBoard", (2.62, -1.95, BASE_Z), -math.pi / 2, col)
    attach(g, box("PosterFrame", (0.98, 0.08, 1.25), (0, 0, 1.0),
                  toon_mat("PosterFrame", "#6b5a44"), col=col, outline=True, outline_w=0.01))
    attach(g, box("PosterFace", (0.86, 0.02, 1.13), (0, 0.05, 1.0),
                  emit_mat("PosterFace", "#e9e2cf", 0.5), col=col))
    candy = ["#d8604a", "#3f74a8", "#e0b04a", "#4f9c74"]
    for i in range(4):
        attach(g, box("Poster%d" % i, (0.3, 0.012, 0.36),
                      (-0.2 + (i % 2) * 0.4, 0.062, 1.28 - (i // 2) * 0.44),
                      toon_mat("PosterC%d" % i, candy[i]), col=col))
    attach(g, box("PosterLeg0", (0.06, 0.06, 0.5), (-0.4, 0, 0.25),
                  toon_mat("MetalDark", "#2d3542"), col=col))
    attach(g, box("PosterLeg1", (0.06, 0.06, 0.5), (0.4, 0, 0.25),
                  toon_mat("MetalDark", "#2d3542"), col=col))
    stage(g, 114, 14, 'pop')


def build_alley(col):
    obs = []
    m_wall = toon_mat("NeighborWall", "#4b5266")
    m_metal = toon_mat("Metal", "#7b8494")
    m_dark = toon_mat("MetalDark", "#2d3542")
    obs.append(box("NeighborWall", (0.4, 5.1, 4.3), (-5.85, -3.55, 2.15), m_wall,
                   col=col, outline=True, outline_w=0.014))
    for i in range(3):
        obs.append(box("NBWindow%d" % i, (0.03, 0.5, 0.42), (-5.64, -2.6 - i * 1.1, 2.9),
                       emit_mat("NBWindow", "#ffc98a", 1.1), col=col))
    obs.append(box("ACUnit", (0.62, 0.5, 0.4), (-5.4, -2.05, 0.35), m_metal,
                   col=col, outline=True, outline_w=0.01))
    obs.append(cyl("ACFan", 0.16, 0.16, 0.04, (-5.08, -2.05, 0.35), m_dark,
                   seg=14, rx=math.pi / 2, col=col))
    obs.append(cyl("DrainPipe", 0.035, 0.035, 3.4, (-5.62, -1.65, 1.7), m_dark, seg=8, col=col))
    obs.append(box("AlleyStep", (0.7, 0.5, 0.12), (-5.62, -5.0, 0.2),
                   toon_mat("AlleyStep", "#4a5265"), col=col))
    # 巷口挂灯 + 青色霓虹
    obs.append(sphere("AlleyBulb", 0.05, (-5.6, -1.75, 2.55),
                      emit_mat("AlleyBulb", "#fff0c0", 3.0), col=col))
    obs.append(box("NeonTube", (0.05, 0.05, 1.5), (-5.62, -1.35, 1.9),
                   emit_mat("NeonCyan", "#6fe6ff", 2.4), col=col))
    obs.append(box("NeonPink", (0.05, 0.9, 0.22), (-5.62, -4.4, 2.6),
                   emit_mat("NeonPink", "#ff6fae", 2.0), col=col))
    stage_group(obs, 124, 2.0, 14, 'pop')
    return obs


def build_far_side(col):
    obs = []
    m_wall = toon_mat("FarWall", "#3a4254")
    m_bush = toon_mat("Bush", "#37543f")
    obs.append(box("FarWall", (11.0, 0.3, 1.1), (0.0, 5.85, 0.55), m_wall,
                   col=col, outline=True, outline_w=0.012))
    for i in range(4):
        obs.append(sphere("Bush%d" % i, 0.36, (-1.6 + i * 1.5, 5.7, 1.15), m_bush,
                          seg=12, col=col, outline=True, outline_w=0.01))
    # 对街小霓虹灯箱，增加色彩层次
    obs.append(box("FarNeon", (0.9, 0.16, 0.5), (-3.4, 5.7, 0.85),
                   emit_mat("FarNeonPink", "#ff7ab8", 1.8), col=col))
    obs.append(box("FarNeon2", (0.7, 0.16, 0.34), (2.6, 5.7, 0.8),
                   emit_mat("FarNeonBlue", "#5ec8ff", 1.8), col=col))
    stage_group(obs, 128, 2.0, 14, 'pop')
    return obs


def build_wet(col):
    m_puddle = toon_mat("Puddle", "#151e30", emit=0.0)
    obs = []
    specs = []
    for i, (x, y, rx, ry) in enumerate(specs):
        ob = cyl("Puddle%d" % i, 1.0, 1.0, 0.012, (x, y, 0.005), m_puddle, seg=24, col=col)
        ob.scale = (rx, ry, 1.0)
        obs.append(ob)
    stage_group(obs, 150, 2.5, 12, 'pop')
    return obs


def build_rain(col):
    me = bpy.data.meshes.new("Rain")
    bm = bmesh.new()
    for i in range(520):
        x = (random.random() - 0.5) * 11.6
        y = (random.random() - 0.5) * 11.6
        z = random.random() * 10.0
        ln = 0.12 + random.random() * 0.2
        m = Matrix.Translation((x, y, z)) @ Matrix.Diagonal((0.0042, 0.0042, ln, 1.0))
        bmesh.ops.create_cube(bm, size=1.0, matrix=m)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("Rain", me)
    col.objects.link(ob)
    me.materials.append(emit_mat("RainMat", "#7fa8e8", 0.5))
    stage(ob, 165, 20, 'pop')
    return ob


# ================================================================
#  6. 灯光 / 世界 / 相机
# ================================================================
def build_lights():
    scene = bpy.context.scene

    world = bpy.data.worlds.new("KonbiniWorld")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = srgb("#1b2a4a")
    bg.inputs["Strength"].default_value = 0.30
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    def add_light(name, kind, loc, energy, color_hex, size=1.0, rot=None):
        ld = bpy.data.lights.new(name, kind)
        ld.energy = energy
        ld.color = srgb(color_hex)[:3]
        if kind == 'AREA':
            ld.size = size
        if kind == 'POINT':
            ld.shadow_soft_size = size
        if kind == 'SUN':
            ld.angle = 0.15
        ob = bpy.data.objects.new(name, ld)
        scene.collection.objects.link(ob)
        ob.location = loc
        if rot:
            ob.rotation_euler = rot
        return ob

    # 月光（主光）
    moon = add_light("Moon", 'SUN', (-9, -10, 15), 4.2, "#9db9ff")
    d = Vector((0, 0, 2)) - moon.location
    moon.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

    # 背面冷色轮廓补光
    rim = add_light("Rim", 'SUN', (9, 11, 8), 1.4, "#5f9dff")
    d = Vector((0, 0, 2)) - rim.location
    rim.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

    # 店内暖光
    for i, (x, y, z, e) in enumerate([
        (-3.4, -3.6, BASE_Z + 3.0, 480),
        (-1.2, -2.6, BASE_Z + 2.9, 360),
        (-4.4, -4.4, BASE_Z + 2.6, 220),
    ]):
        add_light("InnerLight%d" % i, 'POINT', (x, y, z), e, "#ffc07a", size=1.2)

    # 雨棚下的面光，把店前地面照亮
    add_light("AwningLight", 'AREA', (-2.15, -1.1, BASE_Z + 2.6), 120, "#ffd7a0", size=4.0,
              rot=(0, 0, 0))

    # 路灯
    add_light("StreetLight", 'POINT', (1.55, 1.05, BASE_Z + 3.95), 150, "#ffe0b0", size=0.6)

    # 正面冷色补光，托起店面朝向观众的立面
    fill = add_light("FacadeFill", 'AREA', (2.6, 9.5, 6.2), 160, "#a8c4ff", size=10.0)
    fd = Vector((-2.15, -3.3, 2.2)) - fill.location
    fill.rotation_euler = fd.to_track_quat('-Z', 'Y').to_euler()

    # 霓虹补光
    add_light("NeonPink", 'POINT', (-4.6, 1.8, 3.4), 90, "#ff6fae", size=2.0)
    add_light("NeonCyan", 'POINT', (-4.8, -1.6, 2.0), 45, "#6fe6ff", size=1.2)


def setup_camera():
    scene = bpy.context.scene
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 35
    cam = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam)
    target = Vector((0.0, 0.1, 1.7))
    direction = Vector((0.567, 0.701, 0.400)).normalized()
    cam.location = target + direction * 24.4
    look = (target - cam.location)
    cam.rotation_euler = look.to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam
    return cam


def setup_render():
    scene = bpy.context.scene
    for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try:
            scene.render.engine = eng
            break
        except Exception:
            continue
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False
    try:
        scene.view_settings.view_transform = 'Standard'
        scene.view_settings.look = 'None'
    except Exception:
        pass
    try:
        scene.eevee.taa_render_samples = 64
    except Exception:
        pass


def setup_freestyle():
    """动漫墨线：Freestyle 轮廓 + 折边"""
    scene = bpy.context.scene
    scene.render.use_freestyle = True
    scene.render.line_thickness_mode = 'ABSOLUTE'
    scene.render.line_thickness = 1.4
    vl = scene.view_layers[0]
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    if len(fs.linesets) == 0:
        fs.linesets.new("LineSet")
    ls = fs.linesets[0]
    for attr in ("select_silhouette", "select_border", "select_crease",
                 "select_external_contour", "select_contour"):
        setattr(ls, attr, True)
    ls.select_edge_mark = False
    style = ls.linestyle
    if style is None:
        style = bpy.data.linestyles.new("InkLine")
        ls.linestyle = style
    style.color = (0.02, 0.02, 0.03)
    style.thickness = 1.7


def setup_compositor():
    """合成器 Bloom，让霓虹/灯箱有光晕"""
    scene = bpy.context.scene
    try:
        ng = bpy.data.node_groups.new("KonbiniComp", 'CompositorNodeTree')
        ng.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
        scene.compositing_node_group = ng
        rl = ng.nodes.new('CompositorNodeRLayers')
        gl = ng.nodes.new('CompositorNodeGlare')
        gout = ng.nodes.new('NodeGroupOutput')
        for val in ('Bloom', 'Fog Glow', 'FOG_GLOW'):
            try:
                gl.inputs['Type'].default_value = val
                break
            except Exception:
                continue
        for key, val in (('Threshold', 0.6), ('Strength', 0.85), ('Size', 0.75)):
            try:
                gl.inputs[key].default_value = val
            except Exception:
                pass
        ng.links.new(rl.outputs['Image'], gl.inputs['Image'])
        ng.links.new(gl.outputs['Image'], gout.inputs['Image'])
    except Exception as e:
        print("COMP_FAIL", e)


# ================================================================
#  7. 动画
# ================================================================
def apply_animation():
    scene = bpy.context.scene
    scene.render.fps = 24
    end = 1
    for ob, f0, dur, mode in STAGE:
        base = ob.location.copy()
        if mode == 'rise':
            ob.location = base - Vector((0, 0, 0.85))
            ob.scale = (1, 1, 1)
        else:
            ob.location = base
            ob.scale = (0.001, 0.001, 0.001)
        ob.keyframe_insert('location', frame=f0)
        ob.keyframe_insert('scale', frame=f0)
        ob.location = base
        ob.scale = (1, 1, 1)
        ob.keyframe_insert('location', frame=f0 + dur)
        ob.keyframe_insert('scale', frame=f0 + dur)
        end = max(end, f0 + dur)
    scene.frame_start = 1
    scene.frame_end = end + 24
    scene.frame_set(scene.frame_end)


# ================================================================
#  8. 主流程
# ================================================================
def main():
    global OUTLINE
    wipe()
    OUTLINE = make_outline_mat()

    c_base = new_collection("Base")
    c_street = new_collection("Street")
    c_store = new_collection("Store")
    c_inner = new_collection("Interior")
    c_props = new_collection("Props")
    c_wet = new_collection("Wet")
    c_rain = new_collection("Rain")

    build_base(c_base)
    build_street(c_street)
    build_store(c_store)
    build_interior(c_inner)

    build_vending(1.72, -2.55, -math.pi / 2, c_props, "#c4342b", "#9fd8ff", "Red")
    build_vending(1.72, -3.62, -math.pi / 2, c_props, "#24518f", "#bfe6ff", "Blue")
    build_bicycle(2.42, -1.05, math.pi / 2 + 0.1, c_props)
    build_umbrella(c_props)
    build_bins(c_props)
    build_street_lamp(c_props)
    build_poles_and_wires(c_props)
    build_guardrail(c_props)
    build_stop_sign(c_props)
    build_poster(c_props)
    build_alley(c_props)
    build_far_side(c_props)
    build_wet(c_wet)
    build_rain(c_rain)

    build_lights()
    setup_camera()
    setup_render()
    setup_freestyle()
    setup_compositor()
    apply_animation()

    os.makedirs(OUT, exist_ok=True)
    blend_path = os.path.join(SRC, "env_konbini_night.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("SAVED", blend_path)

    try:
        glb_path = os.path.join(OUT, "env_konbini_night.glb")
        bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB')
        print("EXPORTED", glb_path)
    except Exception as e:
        print("GLB_EXPORT_FAIL", e)

    if "--render" in sys.argv:
        scene = bpy.context.scene
        scene.render.filepath = os.path.join(OUT, "preview.png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", scene.render.filepath)


main()

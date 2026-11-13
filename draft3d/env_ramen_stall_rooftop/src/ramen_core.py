# -*- coding: utf-8 -*-
"""
赛博朋克天台拉面摊 · 公共层（Blender 5.x）
- 三渲二材质 / 基础几何 / 分组入场动画 / 灯光相机渲染 / 合成器
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix

ROOT = r"E:\app_ideas\godot-game\Draft\draft3d\env_ramen_stall_rooftop"
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "export")

ROOF_Z = 0.35          # 天台地面高度
PARAPET_H = 0.95       # 女儿墙高度（含压顶）
BASE = 10.0            # 天台可布置范围 10x10


# ---------------------------------------------------------------- 场景 / 集合
def wipe():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.curves,
                  bpy.data.lights, bpy.data.cameras, bpy.data.collections,
                  bpy.data.node_groups):
        for b in list(block):
            if b.users == 0:
                block.remove(b)


def new_collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def link(ob, col):
    (col or bpy.context.scene.collection).objects.link(ob)
    return ob


# ---------------------------------------------------------------- 颜色
def srgb(hex_str):
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
    """三渲二材质：阶梯光；emit>0 时叠加自发光。"""
    if name in MATS:
        return MATS[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (640, 0)
    emis = nt.nodes.new("ShaderNodeEmission")
    emis.location = (440, 0)
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.blend_type = 'MULTIPLY'
    mix.location = (220, 0)
    mix.inputs["Fac"].default_value = 1.0
    mix.inputs["Color1"].default_value = srgb(hex_color)

    diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
    diff.location = (-440, 0)
    diff.inputs["Color"].default_value = (1, 1, 1, 1)
    s2rgb = nt.nodes.new("ShaderNodeShaderToRGB")
    s2rgb.location = (-250, 0)
    ramp = _ramp(nt)
    ramp.location = (-60, 0)

    nt.links.new(diff.outputs["BSDF"], s2rgb.inputs["Shader"])
    nt.links.new(s2rgb.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], mix.inputs["Color2"])
    nt.links.new(mix.outputs["Color"], emis.inputs["Color"])
    emis.inputs["Strength"].default_value = 1.0
    nt.links.new(emis.outputs["Emission"], out.inputs["Surface"])

    if emit > 0.0:
        add = nt.nodes.new("ShaderNodeMixRGB")
        add.blend_type = 'ADD'
        add.location = (330, -190)
        add.inputs["Fac"].default_value = min(1.0, emit)
        add.inputs["Color2"].default_value = srgb(hex_color)
        nt.links.new(mix.outputs["Color"], add.inputs["Color1"])
        nt.links.new(add.outputs["Color"], emis.inputs["Color"])

    MATS[name] = mat
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


# ---------------------------------------------------------------- 基础几何
def _finish(me, name, loc, mat, rz, col):
    ob = bpy.data.objects.new(name, me)
    link(ob, col)
    ob.location = loc
    ob.rotation_euler[2] = rz
    if mat:
        me.materials.append(mat)
    return ob


def box(name, dims, loc, mat=None, rz=0.0, col=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(me)
    bm.free()
    me.transform(Matrix.Diagonal((dims[0], dims[1], dims[2], 1.0)))
    return _finish(me, name, loc, mat, rz, col)


def cyl(name, r1, r2, h, loc, mat=None, seg=16, rz=0.0, rx=0.0, ry=0.0, col=None):
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
    ob = _finish(me, name, loc, mat, rz, col)
    ob.rotation_euler[0] = rx
    ob.rotation_euler[1] = ry
    return ob


def sphere(name, r, loc, mat=None, seg=14, col=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    try:
        bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(6, seg // 2), radius=r)
    except TypeError:
        bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(6, seg // 2), diameter=r * 2)
    bm.to_mesh(me)
    bm.free()
    return _finish(me, name, loc, mat, 0.0, col)


def plane(name, w, d, loc, mat, rz=0.0, col=None):
    me = bpy.data.meshes.new(name)
    verts = [(-w / 2, -d / 2, 0), (w / 2, -d / 2, 0), (w / 2, d / 2, 0), (-w / 2, d / 2, 0)]
    me.from_pydata(verts, [], [(0, 1, 2, 3)])
    me.update()
    return _finish(me, name, loc, mat, rz, col)


def quad(name, verts, mat, col=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], [(0, 1, 2, 3)])
    me.update()
    ob = bpy.data.objects.new(name, me)
    link(ob, col)
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
    link(ob, col)
    ob.location = loc
    ob.rotation_euler = rot
    if mat:
        me.materials.append(mat)
    return ob


def tube(name, points, radius, mat, col=None, res=8, close=False):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = 1
    cu.resolution_u = res
    sp = cu.splines.new('POLY')
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    sp.use_cyclic_u = close
    ob = bpy.data.objects.new(name, cu)
    link(ob, col)
    if mat:
        cu.materials.append(mat)
    return ob


def text_mesh(name, body, size, loc, rot, mat, col=None, extrude=0.0):
    """文字转网格；没有日文字体时返回 None"""
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
    link(ob, col)
    ob.location = loc
    ob.rotation_euler = rot
    if mat:
        me.materials.append(mat)
    return ob


# ---------------------------------------------------------------- 动画登记
STAGE = []


def stage(ob, f0, dur=14, mode='pop'):
    STAGE.append((ob, f0, dur, mode))
    return ob


def stage_group(objs, f0, step=1.5, dur=14, mode='pop'):
    f = f0
    for ob in objs:
        stage(ob, f, dur, mode)
        f += step
    return objs


# ---------------------------------------------------------------- 灯光
def build_lights():
    scene = bpy.context.scene

    world = bpy.data.worlds.new("RamenWorld")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = srgb("#151f38")
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

    # 月光主光
    moon = add_light("Moon", 'SUN', (-9, -11, 16), 3.6, "#93b2ff")
    moon.rotation_euler = (Vector((0, 0, 2)) - moon.location).to_track_quat('-Z', 'Y').to_euler()

    # 背面冷色轮廓
    rim = add_light("Rim", 'SUN', (10, 12, 9), 1.5, "#5f9dff")
    rim.rotation_euler = (Vector((0, 0, 2)) - rim.location).to_track_quat('-Z', 'Y').to_euler()

    # 摊位内部暖光（主视觉核心）
    for i, (x, y, z, e) in enumerate([
        (0.0, 0.75, 2.90, 420),
        (-1.05, 0.35, 2.35, 260),
        (1.10, 0.35, 2.30, 240),
        (0.0, -0.10, 2.05, 180),
    ]):
        add_light("StallInner%d" % i, 'POINT', (x, y, z), e, "#ffbf7a", size=0.55)

    # 雨棚下的面光，照亮操作台与地面
    add_light("AwningFill", 'AREA', (0.0, 2.15, 2.85), 170, "#ffd2a0", size=3.4,
              rot=(math.radians(-58), 0, 0))
    # 台面正前方的补光，把锅与碗提亮
    add_light("CounterFill", 'POINT', (0.0, 1.55, 2.25), 110, "#ffcf96", size=0.7)

    # 灯笼串暖光
    add_light("LanternGlow", 'POINT', (0.0, 1.55, 2.55), 55, "#ff8a5a", size=0.9)
    # 正面冷光，照亮暖帘
    add_light("NorenFill", 'POINT', (0.0, 3.7, 2.95), 50, "#cfe0ff", size=1.1)
    # 灯箱
    add_light("BoxLight", 'POINT', (2.35, 1.55, 1.45), 35, "#ffd9a8", size=0.5)

    # 霓虹补光
    add_light("NeonPink", 'POINT', (-2.4, -2.6, 4.2), 150, "#ff5f9e", size=2.2)
    add_light("NeonCyan", 'POINT', (3.1, -3.0, 3.4), 90, "#5fe0ff", size=1.8)
    add_light("StairLight", 'POINT', (-3.35, -2.15, 2.35), 70, "#ffcf8a", size=0.5)

    # 正面冷补光，托起立面
    fill = add_light("FacadeFill", 'AREA', (6.5, 9.0, 7.5), 220, "#9fc0ff", size=9.0)
    fill.rotation_euler = (Vector((0, 0, 1.6)) - fill.location).to_track_quat('-Z', 'Y').to_euler()
    # 左上侧补光，避免背光面全黑
    fill2 = add_light("TopFill", 'AREA', (-7.0, -3.0, 8.0), 120, "#b9c9ff", size=7.0)
    fill2.rotation_euler = (Vector((0, 0, 1.8)) - fill2.location).to_track_quat('-Z', 'Y').to_euler()


# ---------------------------------------------------------------- 相机
def setup_camera():
    scene = bpy.context.scene
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 44
    cam = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam)
    target = Vector((0.0, 0.3, 1.62))
    direction = Vector((0.54, 0.70, 0.46)).normalized()
    cam.location = target + direction * 19.6
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam
    return cam


# ---------------------------------------------------------------- 渲染设置
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
    scene = bpy.context.scene
    try:
        ng = bpy.data.node_groups.new("RamenComp", 'CompositorNodeTree')
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
        for key, val in (('Threshold', 0.65), ('Strength', 0.9), ('Size', 0.8)):
            try:
                gl.inputs[key].default_value = val
            except Exception:
                pass
        ng.links.new(rl.outputs['Image'], gl.inputs['Image'])
        ng.links.new(gl.outputs['Image'], gout.inputs['Image'])
    except Exception as e:
        print("COMP_FAIL", e)


# ---------------------------------------------------------------- 入场动画
def apply_animation():
    scene = bpy.context.scene
    scene.render.fps = 24
    end = 1
    for ob, f0, dur, mode in STAGE:
        base = ob.location.copy()
        if mode == 'rise':
            ob.location = base - Vector((0, 0, 0.9))
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

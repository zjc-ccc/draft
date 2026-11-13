# -*- coding: utf-8 -*-
"""
黄昏大学校园操场 · 公共层（Blender 5.x）
- 三渲二材质 / 基础几何 / 操场环形几何 / 分组入场动画 / 灯光相机渲染 / 合成器
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix

ROOT = r"E:\app_ideas\godot-game\Draft\draft3d\env_campus_field"
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "export")

TOP_Z = 0.30          # 底座顶面高度
HALF = 6.0            # 底座半宽

# 操场主轴：南北向直道（沿 Y），东西向半圆
TRACK_CX = 0.0
TRACK_CY = 0.55
R_OUT = 2.50          # 外道半径（X 方向半宽）
S_HALF = 1.30         # 直道半长（沿 Y）
LANE_W = 0.1025       # 单条分道宽
TRACK_W = LANE_W * 8  # 跑道总宽
R_IN = R_OUT - TRACK_W


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
RAMP_STOPS = [(0.00, 0.30), (0.14, 0.50), (0.33, 0.76), (0.58, 1.0)]


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


def rect(name, cx, cy, w, d, z, mat, rz=0.0, col=None):
    return plane(name, w, d, (cx, cy, z), mat, rz=rz, col=col)


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


FONT_CACHE = []


def get_font():
    if FONT_CACHE:
        return FONT_CACHE[0]
    for path in (r"C:\Windows\Fonts\msyh.ttc",
                 r"C:\Windows\Fonts\msyhbd.ttc",
                 r"C:\Windows\Fonts\simhei.ttf",
                 r"C:\Windows\Fonts\YuGothM.ttc",
                 r"C:\Windows\Fonts\msgothic.ttc"):
        if os.path.exists(path):
            try:
                FONT_CACHE.append(bpy.data.fonts.load(path))
                return FONT_CACHE[0]
            except Exception:
                continue
    FONT_CACHE.append(None)
    return None


def text_mesh(name, body, size, loc, rot, mat, col=None, extrude=0.0, align='CENTER'):
    """文字转网格；缺字体返回 None"""
    font = get_font()
    if font is None:
        return None
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = body
    cu.size = size
    cu.align_x = align
    cu.align_y = 'CENTER'
    cu.extrude = extrude
    cu.font = font
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    bpy.context.scene.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.curves.remove(cu)
    if len(me.vertices) == 0:
        bpy.data.meshes.remove(me)
        return None
    ob = bpy.data.objects.new(name, me)
    link(ob, col)
    ob.location = loc
    ob.rotation_euler = rot
    if mat:
        me.materials.append(mat)
    return ob


# ---------------------------------------------------------------- 环形几何
def stadium_pts(cx, cy, R, S, arcs=24, sides=6):
    """体育场跑道轮廓（CCW）：直道沿 Y，两端半圆。"""
    pts = []
    for i in range(arcs + 1):
        t = math.pi * i / arcs
        pts.append((cx + R * math.cos(t), cy + S + R * math.sin(t)))
    for i in range(1, sides + 1):
        k = i / sides
        pts.append((cx - R, cy + S - 2 * S * k))
    for i in range(1, arcs + 1):
        t = math.pi + math.pi * i / arcs
        pts.append((cx + R * math.cos(t), cy - S + R * math.sin(t)))
    for i in range(1, sides):
        k = i / sides
        pts.append((cx + R, cy - S + 2 * S * k))
    return pts


def _mesh_xy(name, verts, faces, z, mat, col):
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x, y, z) for x, y in verts], [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    link(ob, col)
    if mat:
        me.materials.append(mat)
    return ob


def ring_strip(name, cx, cy, R, S, w, z, mat, arcs=26, sides=6, col=None):
    """跑道形环带（等宽），用于塑胶跑道 / 分道线 / 路缘"""
    outer = stadium_pts(cx, cy, R, S, arcs, sides)
    inner = stadium_pts(cx, cy, R - w, S, arcs, sides)
    n = len(outer)
    verts = outer + inner
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    return _mesh_xy(name, verts, faces, z, mat, col)


def stadium_fill(name, cx, cy, R, S, z, mat, arcs=26, sides=6, col=None):
    pts = stadium_pts(cx, cy, R, S, arcs, sides)
    return _mesh_xy(name, pts, [tuple(range(len(pts)))], z, mat, col)


def flat_ring(name, cx, cy, r_out, r_in, z, mat, seg=36, col=None):
    verts, faces = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        verts.append((cx + r_out * math.cos(a), cy + r_out * math.sin(a)))
    for i in range(seg):
        a = 2 * math.pi * i / seg
        verts.append((cx + r_in * math.cos(a), cy + r_in * math.sin(a)))
    for i in range(seg):
        j = (i + 1) % seg
        faces.append((i, j, seg + j, seg + i))
    return _mesh_xy(name, verts, faces, z, mat, col)


def arc_ring(name, cx, cy, r, width, z, a0, a1, mat, seg=20, col=None):
    """圆弧线（角度制，逆时针）"""
    inner = r - width / 2
    outer = r + width / 2
    n = seg + 1
    verts = []
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * i / seg)
        verts.append((cx + outer * math.cos(a), cy + outer * math.sin(a)))
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * i / seg)
        verts.append((cx + inner * math.cos(a), cy + inner * math.sin(a)))
    faces = []
    for i in range(seg):
        faces.append((i, i + 1, n + i + 1, n + i))
    return _mesh_xy(name, verts, faces, z, mat, col)


def strip(name, p0, p1, width, z, mat, col=None):
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy) or 1e-6
    nx, ny = -dy / ln * width / 2, dx / ln * width / 2
    verts = [(x0 + nx, y0 + ny), (x0 - nx, y0 - ny), (x1 - nx, y1 - ny), (x1 + nx, y1 + ny)]
    return _mesh_xy(name, verts, [(0, 1, 2, 3)], z, mat, col)


def rect_outline(name, cx, cy, w, d, lw, z, mat, col=None):
    """矩形白线框"""
    obs = []
    obs.append(strip(name + "_T", (cx - w / 2, cy + d / 2), (cx + w / 2, cy + d / 2), lw, z, mat, col))
    obs.append(strip(name + "_B", (cx - w / 2, cy - d / 2), (cx + w / 2, cy - d / 2), lw, z, mat, col))
    obs.append(strip(name + "_L", (cx - w / 2, cy - d / 2), (cx - w / 2, cy + d / 2), lw, z, mat, col))
    obs.append(strip(name + "_R", (cx + w / 2, cy - d / 2), (cx + w / 2, cy + d / 2), lw, z, mat, col))
    return obs


# ---------------------------------------------------------------- 动画登记
STAGE = []


def stage(ob, f0, dur=14, mode='pop'):
    STAGE.append((ob, f0, dur, mode))
    return ob


def stage_group(objs, f0, step=1.5, dur=14, mode='pop'):
    f = f0
    for ob in objs:
        if ob is not None:
            stage(ob, f, dur, mode)
            f += step
    return objs


# ---------------------------------------------------------------- 灯光
def add_light(name, kind, loc, energy, color_hex, size=1.0, rot=None):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = srgb(color_hex)[:3]
    if kind == 'AREA':
        ld.size = size
    if kind == 'POINT':
        ld.shadow_soft_size = size
    if kind == 'SUN':
        ld.angle = math.radians(2.2)
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    if rot:
        ob.rotation_euler = rot
    else:
        ob.rotation_euler = (Vector((0, 0, 0.4)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


def build_lights():
    scene = bpy.context.scene

    world = bpy.data.worlds.new("CampusWorld")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 1.0
    # 相机看到的天空亮、参与照明的环境光暗，避免整体发灰
    lp = nt.nodes.new("ShaderNodeLightPath")
    mixw = nt.nodes.new("ShaderNodeMixRGB")
    mixw.blend_type = 'MIX'
    mixw.inputs["Color1"].default_value = srgb("#24304d")
    mixw.inputs["Color2"].default_value = srgb("#a9bedb")
    nt.links.new(lp.outputs["Is Camera Ray"], mixw.inputs["Fac"])
    nt.links.new(mixw.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    # 黄昏低角度主光（暖橙，侧前方，长阴影横过场地）
    sun = add_light("DuskSun", 'SUN', (9.0, -3.5, 6.0), 9.5, "#ff9f4d")
    sun.rotation_euler = (Vector((0, 0, 0.6)) - sun.location).to_track_quat('-Z', 'Y').to_euler()

    # 反向冷光，托出轮廓
    rim = add_light("Rim", 'SUN', (-9, 10, 7), 1.2, "#7fa8ff")
    rim.rotation_euler = (Vector((0, 0, 0.5)) - rim.location).to_track_quat('-Z', 'Y').to_euler()

    # 正面大面积冷补光（天空反射）
    fill = add_light("SkyFill", 'AREA', (9.0, 11.0, 9.5), 26, "#b9cdf0", size=11.0)
    fill.rotation_euler = (Vector((0, 0, 0.6)) - fill.location).to_track_quat('-Z', 'Y').to_euler()

    # 左侧补光，避免看台全暗
    fill2 = add_light("SideFill", 'AREA', (-10.0, 2.0, 7.0), 34, "#ffd0a6", size=8.0)
    fill2.rotation_euler = (Vector((-2.0, 0.6, 0.8)) - fill2.location).to_track_quat('-Z', 'Y').to_euler()

    # 路灯暖光
    for i, (x, y) in enumerate([(-3.9, -4.1), (1.4, -4.1), (4.9, 2.6), (-0.9, 4.9)]):
        add_light("LampPoint%d" % i, 'POINT', (x, y, TOP_Z + 1.15), 42, "#ffcf8f", size=0.35)


# ---------------------------------------------------------------- 相机
def setup_camera(lens=45.0, dist=22.6, target=(0.0, 0.35, 0.60),
                 direction=(0.54, 0.70, 0.46)):
    scene = bpy.context.scene
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam)
    tgt = Vector(target)
    cam.location = tgt + Vector(direction).normalized() * dist
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
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
    scene.render.line_thickness = 1.7
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
    style.color = (0.05, 0.045, 0.06)
    style.thickness = 1.5


def setup_compositor():
    scene = bpy.context.scene
    try:
        ng = bpy.data.node_groups.new("CampusComp", 'CompositorNodeTree')
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
        for key, val in (('Threshold', 0.88), ('Strength', 0.35), ('Size', 0.6)):
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
    scene.frame_end = int(end) + 24
    scene.frame_set(int(end) + 24)

# -*- coding: utf-8 -*-
"""
白色火柴人 · 校园操场比例参照（Blender 5.x）
- 跑道外圈 7.6 场景单位 = 200 m → 1 单位 = 26.32 m
- 身高 1.7 m → 0.0646 场景单位，脚底在原点
用法：
    blender -b -P build_stickman.py -- --render
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy
import bmesh
from mathutils import Vector

import campus_core as core

core.wipe()

# ---------------------------------------------------------------- 比例
TRACK_LEN = 7.60          # env_campus_field 跑道外圈长（场景单位）
REAL_LEN = 200.0          # 视作 200 米
HUMAN_M = 1.70
UNIT_M = REAL_LEN / TRACK_LEN     # 每场景单位多少米
H = HUMAN_M / UNIT_M              # 火柴人总高（场景单位）

M_WHITE = core.toon_mat("StickWhite", "#ffffff", emit=0.18)
M_WHITE_SOFT = core.toon_mat("StickWhiteDim", "#f2f2f2", emit=0.10)


def limb(name, p0, p1, r, mat, col, seg=10):
    """两点之间的圆柱（肢体）"""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    ln = d.length
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r, radius2=r, depth=ln)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    ob.location = (a + b) / 2
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    me.materials.append(mat)
    return ob


def build_stickman(col):
    o = []
    # 关键高度（按 H 推导，头身比 1:7.5）
    head_r = H * 0.0667
    head_z = H - head_r
    neck_z0, neck_z1 = H * 0.845, H * 0.872
    sh_z = H * 0.820            # 肩线
    sh_x = H * 0.101            # 半肩宽
    hip_z = H * 0.542           # 髋
    hip_x = H * 0.035
    knee_z = H * 0.287
    knee_x = H * 0.043
    ankle_z = H * 0.034
    ankle_x = H * 0.050
    elbow = (H * 0.163, H * 0.673)
    hand = (H * 0.209, H * 0.534)

    o.append(core.sphere("Head", head_r, (0, 0, head_z), M_WHITE, seg=24, col=col))
    o.append(limb("Neck", (0, 0, neck_z0), (0, 0, neck_z1), H * 0.019, M_WHITE, col))
    # 躯干（略微上宽下窄）
    o.append(limb("Chest", (0, 0, sh_z), (0, 0, H * 0.640), H * 0.030, M_WHITE, col))
    o.append(limb("Waist", (0, 0, H * 0.640), (0, 0, hip_z), H * 0.024, M_WHITE, col))
    o.append(limb("ShoulderBar", (-sh_x, 0, sh_z), (sh_x, 0, sh_z), H * 0.020, M_WHITE, col))
    o.append(limb("HipBar", (-hip_x, 0, hip_z), (hip_x, 0, hip_z), H * 0.022, M_WHITE, col))
    # 关节球
    for s in (-1, 1):
        o.append(core.sphere("ShoulderBall%d" % s, H * 0.030, (s * sh_x, 0, sh_z), M_WHITE, seg=14, col=col))
        o.append(core.sphere("HipBall%d" % s, H * 0.026, (s * hip_x, 0, hip_z), M_WHITE, seg=14, col=col))
        o.append(core.sphere("ElbowBall%d" % s, H * 0.027, (s * elbow[0], 0, elbow[1]), M_WHITE, seg=12, col=col))
        o.append(core.sphere("KneeBall%d" % s, H * 0.024, (s * knee_x, 0, knee_z), M_WHITE, seg=12, col=col))
        o.append(core.sphere("AnkleBall%d" % s, H * 0.020, (s * ankle_x, 0, ankle_z), M_WHITE, seg=10, col=col))
        # 手臂：肩 -> 肘 -> 手（加粗版）
        o.append(limb("UpperArm%d" % s, (s * sh_x, 0, sh_z), (s * elbow[0], 0, elbow[1]),
                      H * 0.026, M_WHITE, col))
        o.append(limb("ForeArm%d" % s, (s * elbow[0], 0, elbow[1]), (s * hand[0], 0, hand[1]),
                      H * 0.024, M_WHITE, col))
        o.append(core.sphere("Hand%d" % s, H * 0.031, (s * hand[0], 0, hand[1]), M_WHITE, seg=12, col=col))
        # 腿：髋 -> 膝 -> 踝
        o.append(limb("Thigh%d" % s, (s * hip_x, 0, hip_z), (s * knee_x, 0, knee_z),
                      H * 0.025, M_WHITE, col))
        o.append(limb("Shin%d" % s, (s * knee_x, 0, knee_z), (s * ankle_x, 0, ankle_z),
                      H * 0.021, M_WHITE, col))
        # 脚掌
        o.append(core.box("Foot%d" % s, (H * 0.040, H * 0.082, H * 0.020),
                          (s * ankle_x, H * 0.012, H * 0.010), M_WHITE_SOFT, col=col))
    return o


def build_stage(col):
    """预览用：小地台 + 尺寸标注"""
    M_GROUND = core.toon_mat("Ground", "#ded7c7")
    M_DIM = core.toon_mat("DimLine", "#5a6472")
    o = []
    o.append(core.cyl("Ground", H * 1.55, H * 1.55, H * 0.012, (0, 0, -H * 0.006), M_GROUND, seg=48, col=col))
    x = H * 0.255
    o.append(limb("DimLine", (x, 0, 0), (x, 0, H), H * 0.005, M_DIM, col, seg=6))
    for z in (0.0, H):
        o.append(limb("DimTick%s" % z, (x - H * 0.035, 0, z + (H * 0.008 if z == 0 else 0)),
                      (x + H * 0.035, 0, z - (H * 0.008 if z > 0 else 0)), H * 0.005, M_DIM, col, seg=6))
    t = core.text_mesh("DimText", "1.7 m", H * 0.100, (x + H * 0.115, -H * 0.02, H * 0.52),
                       (math.radians(90), 0, math.radians(45)), M_DIM, col=col)
    if t:
        o.append(t)
    return o


def setup_preview():
    sc = bpy.context.scene
    world = bpy.data.worlds.new("StickWorld")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = core.srgb("#b9c9dd")
    bg.inputs["Strength"].default_value = 0.9
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    core.add_light("Key", 'AREA', (H * 1.6, -H * 1.9, H * 2.2), 0.35, "#fff0dc", size=H * 1.2)
    core.add_light("Rim", 'AREA', (-H * 1.8, H * 1.4, H * 1.6), 0.20, "#bcd2ff", size=H * 1.2)
    core.add_light("Sun", 'SUN', (H * 2.0, -H * 2.4, H * 3.4), 1.9, "#ffd9b0")

    cd = bpy.data.cameras.new("Camera")
    cd.lens = 50.0
    cam = bpy.data.objects.new("Camera", cd)
    sc.collection.objects.link(cam)
    tgt = Vector((H * 0.02, 0, H * 0.48))
    cam.location = tgt + Vector((0.42, -1.35, 0.10)).normalized() * (H * 2.0)
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam

    sc.render.resolution_x = 900
    sc.render.resolution_y = 1200
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'
    for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try:
            sc.render.engine = eng
            break
        except Exception:
            continue
    try:
        sc.eevee.taa_render_samples = 64
    except Exception:
        pass
    try:
        sc.view_settings.view_transform = 'Standard'
    except Exception:
        pass
    core.setup_freestyle()


def main():
    root = core.new_collection("Stickman")
    stage = core.new_collection("Preview")
    build_stickman(root)
    setup_preview()

    os.makedirs(core.OUT, exist_ok=True)
    blend_path = os.path.join(core.SRC, "stickman.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("SAVED", blend_path, "H", round(H, 5), "UNIT_M", round(UNIT_M, 3))

    import export_glb
    glb = os.path.join(core.OUT, "stickman_white.glb")
    export_glb.export_engine(glb)
    print("EXPORTED", glb)

    if "--render" in sys.argv:
        build_stage(stage)
        sc = bpy.context.scene
        sc.render.filepath = os.path.join(core.OUT, "stickman_preview.png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", sc.render.filepath)


main()

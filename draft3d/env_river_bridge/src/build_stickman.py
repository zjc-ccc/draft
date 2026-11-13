# -*- coding: utf-8 -*-
"""
白色火柴人 · 跨河桥比例参照 + 骨架动画（Blender 5.x）
- 比例：马路 2.40 单位 = 7.0 m → 1 单位 = 2.9167 m，身高 1.7 m = 0.583 单位
- 骨架 17 根，每个部件 100% 刚性绑定到单根骨骼（不让圆柱发生形变）
- 动作：idle / walk / run / jump / wave，全部按世界轴角度书写
用法：
    blender -b -P build_stickman.py -- --render
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy
import bmesh
from mathutils import Vector, Matrix

import bridge_core as core

core.wipe()

# ---------------------------------------------------------------- 比例
ROAD_W = 2.40             # env_river_bridge 马路宽（场景单位）
REAL_ROAD_M = 7.00        # 视作双向两车道 7 米
HUMAN_M = 1.70
UNIT_M = REAL_ROAD_M / ROAD_W     # 每场景单位多少米
H = HUMAN_M / UNIT_M              # 火柴人总高（场景单位）
S = H / 0.0646                    # 相对校园版的缩放比，用于预览灯光

# 关键高度（按 H 推导，头身比 1:7.5）
HEAD_R = H * 0.0667
HEAD_Z = H - HEAD_R
NECK_Z0, NECK_Z1 = H * 0.845, H * 0.872
SH_Z = H * 0.820
SH_X = H * 0.101
HIP_Z = H * 0.542
HIP_X = H * 0.035
KNEE_Z = H * 0.287
KNEE_X = H * 0.043
ANKLE_Z = H * 0.034
ANKLE_X = H * 0.050
ELBOW = (H * 0.163, H * 0.673)
HAND = (H * 0.209, H * 0.534)

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


# ---------------------------------------------------------------- 几何
def build_stickman(col):
    o = []
    head_r = HEAD_R
    head_z = HEAD_Z
    neck_z0, neck_z1 = NECK_Z0, NECK_Z1
    sh_z, sh_x = SH_Z, SH_X
    hip_z, hip_x = HIP_Z, HIP_X
    knee_z, knee_x = KNEE_Z, KNEE_X
    ankle_z, ankle_x = ANKLE_Z, ANKLE_X
    elbow, hand = ELBOW, HAND

    o.append(core.sphere("Head", head_r, (0, 0, head_z), M_WHITE, seg=24, col=col))
    o.append(limb("Neck", (0, 0, neck_z0), (0, 0, neck_z1), H * 0.019, M_WHITE, col))
    o.append(limb("Chest", (0, 0, sh_z), (0, 0, H * 0.640), H * 0.030, M_WHITE, col))
    o.append(limb("Waist", (0, 0, H * 0.640), (0, 0, hip_z), H * 0.024, M_WHITE, col))
    o.append(limb("ShoulderBar", (-sh_x, 0, sh_z), (sh_x, 0, sh_z), H * 0.020, M_WHITE, col))
    o.append(limb("HipBar", (-hip_x, 0, hip_z), (hip_x, 0, hip_z), H * 0.022, M_WHITE, col))
    for s in (-1, 1):
        o.append(core.sphere("ShoulderBall%d" % s, H * 0.026, (s * sh_x, 0, sh_z), M_WHITE, seg=14, col=col))
        o.append(core.sphere("HipBall%d" % s, H * 0.026, (s * hip_x, 0, hip_z), M_WHITE, seg=14, col=col))
        o.append(core.sphere("ElbowBall%d" % s, H * 0.022, (s * elbow[0], 0, elbow[1]), M_WHITE, seg=12, col=col))
        o.append(core.sphere("KneeBall%d" % s, H * 0.024, (s * knee_x, 0, knee_z), M_WHITE, seg=12, col=col))
        o.append(core.sphere("AnkleBall%d" % s, H * 0.020, (s * ankle_x, 0, ankle_z), M_WHITE, seg=10, col=col))
        o.append(limb("UpperArm%d" % s, (s * sh_x, 0, sh_z), (s * elbow[0], 0, elbow[1]),
                      H * 0.019, M_WHITE, col))
        o.append(limb("ForeArm%d" % s, (s * elbow[0], 0, elbow[1]), (s * hand[0], 0, hand[1]),
                      H * 0.017, M_WHITE, col))
        o.append(core.sphere("Hand%d" % s, H * 0.023, (s * hand[0], 0, hand[1]), M_WHITE, seg=12, col=col))
        o.append(limb("Thigh%d" % s, (s * hip_x, 0, hip_z), (s * knee_x, 0, knee_z),
                      H * 0.025, M_WHITE, col))
        o.append(limb("Shin%d" % s, (s * knee_x, 0, knee_z), (s * ankle_x, 0, ankle_z),
                      H * 0.021, M_WHITE, col))
        o.append(core.box("Foot%d" % s, (H * 0.040, H * 0.082, H * 0.020),
                          (s * ankle_x, H * 0.012, H * 0.010), M_WHITE_SOFT, col=col))
    return o


# ---------------------------------------------------------------- 骨架
BONES = [
    # name, head, tail, parent, connected
    ("hips", (0, 0, HIP_Z), (0, 0, H * 0.640), None, False),
    ("spine", (0, 0, H * 0.640), (0, 0, SH_Z), "hips", True),
    ("chest", (0, 0, SH_Z), (0, 0, NECK_Z0), "spine", True),
    ("neck", (0, 0, NECK_Z0), (0, 0, NECK_Z1), "chest", True),
    ("head", (0, 0, NECK_Z1), (0, 0, H * 0.995), "neck", True),
]
for _s, _sfx in ((-1, ".L"), (1, ".R")):
    BONES += [
        ("upperarm" + _sfx, (_s * SH_X, 0, SH_Z), (_s * ELBOW[0], 0, ELBOW[1]), "chest", False),
        ("forearm" + _sfx, (_s * ELBOW[0], 0, ELBOW[1]), (_s * HAND[0], 0, HAND[1]),
         "upperarm" + _sfx, True),
        ("hand" + _sfx, (_s * HAND[0], 0, HAND[1]),
         (_s * (HAND[0] + H * 0.030), 0, HAND[1] - H * 0.020), "forearm" + _sfx, True),
        ("thigh" + _sfx, (_s * HIP_X, 0, HIP_Z), (_s * KNEE_X, 0, KNEE_Z), "hips", False),
        ("shin" + _sfx, (_s * KNEE_X, 0, KNEE_Z), (_s * ANKLE_X, 0, ANKLE_Z), "thigh" + _sfx, True),
        ("foot" + _sfx, (_s * ANKLE_X, 0, ANKLE_Z), (_s * ANKLE_X, H * 0.06, 0), "shin" + _sfx, True),
    ]

# 部件 -> 骨骼（关节球跟随下游骨骼，保证关节处不脱开）
def bone_of(name):
    if name == "Head":
        return "head"
    if name == "Neck":
        return "neck"
    if name == "Chest":
        return "spine"
    if name == "Waist":
        return "hips"
    if name == "ShoulderBar":
        return "chest"
    if name == "HipBar":
        return "hips"
    for s, sfx in ((-1, ".L"), (1, ".R")):
        tail = str(s)
        if name.endswith(tail):
            base = name[:-len(tail)]
            table = {"ShoulderBall": "upperarm", "HipBall": "thigh", "ElbowBall": "forearm",
                     "KneeBall": "shin", "AnkleBall": "foot", "UpperArm": "upperarm",
                     "ForeArm": "forearm", "Hand": "hand", "Thigh": "thigh",
                     "Shin": "shin", "Foot": "foot"}
            if base in table:
                return table[base] + sfx
    return "hips"


def build_rig(mesh_objects, col):
    arm_data = bpy.data.armatures.new("StickArmature")
    arm = bpy.data.objects.new("StickRig", arm_data)
    col.objects.link(arm)

    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    ebs = arm_data.edit_bones
    for name, head, tail, parent, connected in BONES:
        eb = ebs.new(name)
        eb.head = head
        eb.tail = tail
        eb.roll = 0.0
        if parent:
            eb.parent = ebs[parent]
            eb.use_connect = connected
    bpy.ops.object.mode_set(mode='OBJECT')

    for pb in arm.pose.bones:
        pb.rotation_mode = 'QUATERNION'

    # 每个部件烘焙世界变换 -> 单顶点组满权重 -> Armature 修改器
    for ob in mesh_objects:
        ob.data.transform(ob.matrix_world)
        ob.matrix_world = Matrix.Identity(4)
        bname = bone_of(ob.name)
        vg = ob.vertex_groups.new(name=bname)
        vg.add(list(range(len(ob.data.vertices))), 1.0, 'REPLACE')
        mod = ob.modifiers.new("Armature", 'ARMATURE')
        mod.object = arm
        mod.use_vertex_groups = True
        ob.parent = arm
        ob.matrix_parent_inverse = Matrix.Identity(4)
    return arm


# ---------------------------------------------------------------- 动作
def rest(arm):
    for pb in arm.pose.bones:
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)


def set_rot(arm, bone, pairs):
    """按世界轴角度设置骨骼局部旋转：local = M⁻¹ · R · M"""
    pb = arm.pose.bones[bone]
    M = pb.bone.matrix_local.to_3x3()
    R = Matrix.Identity(3)
    for axis, deg in pairs:
        R = Matrix.Rotation(math.radians(deg), 3, axis) @ R
    pb.rotation_quaternion = (M.inverted() @ R @ M).to_quaternion()


def build_actions(arm):
    """每个动作：[(frame, {骨骼: [(axis, deg)...]}, hips 位移(H 为单位))]"""
    idle = []
    for f, bob, chest, head, arm_sw in ((1, 0.0, 0.0, 0.0, 0.0),
                                          (13, 0.004, -1.6, -1.2, 1.2),
                                          (25, 0.0, 0.0, 0.0, 0.0),
                                          (37, -0.004, 1.4, 1.0, -1.2),
                                          (49, 0.0, 0.0, 0.0, 0.0)):
        idle.append((f, {"spine": [("X", chest)], "head": [("X", head)],
                         "upperarm.L": [("X", arm_sw)], "upperarm.R": [("X", arm_sw)]}, bob))

    walk = []
    for f, pose, bob in (
            (1, {"thigh.L": [("X", 24)], "shin.L": [("X", -6)],
                 "thigh.R": [("X", -22)], "shin.R": [("X", 26)],
                 "upperarm.L": [("X", -20)], "upperarm.R": [("X", 20)],
                 "forearm.L": [("X", 8)], "forearm.R": [("X", 8)]}, 0.0),
            (7, {"thigh.L": [("X", 4)], "shin.L": [("X", -26)],
                 "thigh.R": [("X", 2)], "shin.R": [("X", 2)],
                 "upperarm.L": [("X", -6)], "upperarm.R": [("X", 6)]}, 0.012),
            (13, {"thigh.L": [("X", -22)], "shin.L": [("X", 26)],
                  "thigh.R": [("X", 24)], "shin.R": [("X", -6)],
                  "upperarm.L": [("X", 20)], "upperarm.R": [("X", -20)],
                  "forearm.L": [("X", 8)], "forearm.R": [("X", 8)]}, 0.0),
            (19, {"thigh.L": [("X", 2)], "shin.L": [("X", 2)],
                  "thigh.R": [("X", 4)], "shin.R": [("X", -26)],
                  "upperarm.L": [("X", 6)], "upperarm.R": [("X", -6)]}, 0.012),
            (25, {"thigh.L": [("X", 24)], "shin.L": [("X", -6)],
                  "thigh.R": [("X", -22)], "shin.R": [("X", 26)],
                  "upperarm.L": [("X", -20)], "upperarm.R": [("X", 20)],
                  "forearm.L": [("X", 8)], "forearm.R": [("X", 8)]}, 0.0)):
        walk.append((f, pose, bob))

    run = []
    for f, pose, bob in (
            (1, {"thigh.L": [("X", 46)], "shin.L": [("X", -34)],
                 "thigh.R": [("X", -34)], "shin.R": [("X", 62)],
                 "upperarm.L": [("X", -36)], "upperarm.R": [("X", 36)],
                 "forearm.L": [("X", 62)], "forearm.R": [("X", 62)],
                 "spine": [("X", -8)]}, 0.0),
            (6, {"thigh.L": [("X", 8)], "shin.L": [("X", -60)],
                 "thigh.R": [("X", -4)], "shin.R": [("X", 10)],
                 "upperarm.L": [("X", -10)], "upperarm.R": [("X", 10)],
                 "forearm.L": [("X", 62)], "forearm.R": [("X", 62)],
                 "spine": [("X", -8)]}, 0.045),
            (11, {"thigh.L": [("X", -34)], "shin.L": [("X", 62)],
                  "thigh.R": [("X", 46)], "shin.R": [("X", -34)],
                  "upperarm.L": [("X", 36)], "upperarm.R": [("X", -36)],
                  "forearm.L": [("X", 62)], "forearm.R": [("X", 62)],
                  "spine": [("X", -8)]}, 0.0),
            (16, {"thigh.L": [("X", -4)], "shin.L": [("X", 10)],
                  "thigh.R": [("X", 8)], "shin.R": [("X", -60)],
                  "upperarm.L": [("X", 10)], "upperarm.R": [("X", -10)],
                  "forearm.L": [("X", 62)], "forearm.R": [("X", 62)],
                  "spine": [("X", -8)]}, 0.045),
            (21, {"thigh.L": [("X", 46)], "shin.L": [("X", -34)],
                  "thigh.R": [("X", -34)], "shin.R": [("X", 62)],
                  "upperarm.L": [("X", -36)], "upperarm.R": [("X", 36)],
                  "forearm.L": [("X", 62)], "forearm.R": [("X", 62)],
                  "spine": [("X", -8)]}, 0.0)):
        run.append((f, pose, bob))

    jump = [
        (1, {}, 0.0),
        (7, {"thigh.L": [("X", 40)], "shin.L": [("X", -70)],
             "thigh.R": [("X", 40)], "shin.R": [("X", -70)],
             "upperarm.L": [("X", 30)], "upperarm.R": [("X", 30)],
             "forearm.L": [("X", 20)], "forearm.R": [("X", 20)],
             "spine": [("X", -10)], "foot.L": [("X", -20)], "foot.R": [("X", -20)]}, -0.085),
        (13, {"thigh.L": [("X", -8)], "thigh.R": [("X", -8)],
              "upperarm.L": [("X", 100)], "upperarm.R": [("X", 100)],
              "spine": [("X", 4)]}, 0.02),
        (20, {"thigh.L": [("X", 46)], "shin.L": [("X", -80)],
              "thigh.R": [("X", 34)], "shin.R": [("X", -60)],
              "upperarm.L": [("X", 62)], "upperarm.R": [("X", 62)],
              "forearm.L": [("X", 45)], "forearm.R": [("X", 45)],
              "spine": [("X", -6)]}, 0.0),
        (28, {"thigh.L": [("X", 34)], "shin.L": [("X", -62)],
              "thigh.R": [("X", 34)], "shin.R": [("X", -62)],
              "upperarm.L": [("X", 24)], "upperarm.R": [("X", 24)],
              "forearm.L": [("X", 18)], "forearm.R": [("X", 18)],
              "spine": [("X", -8)], "foot.L": [("X", -16)], "foot.R": [("X", -16)]}, -0.07),
        (37, {}, 0.0),
    ]

    wave = [
        (1, {}, 0.0),
        (9, {"upperarm.R": [("Y", -95), ("X", -14)], "forearm.R": [("Y", -18)],
             "head": [("Y", 6)], "spine": [("Y", -3)]}, 0.0),
        (17, {"upperarm.R": [("Y", -100), ("X", -14)], "forearm.R": [("Y", -34)],
              "head": [("Y", 6)], "spine": [("Y", -3)]}, 0.0),
        (25, {"upperarm.R": [("Y", -95), ("X", -14)], "forearm.R": [("Y", -6)],
              "head": [("Y", 6)], "spine": [("Y", -3)]}, 0.0),
        (33, {"upperarm.R": [("Y", -100), ("X", -14)], "forearm.R": [("Y", -34)],
              "head": [("Y", 6)], "spine": [("Y", -3)]}, 0.0),
        (41, {"upperarm.R": [("Y", -95), ("X", -14)], "forearm.R": [("Y", -18)],
              "head": [("Y", 6)], "spine": [("Y", -3)]}, 0.0),
        (49, {}, 0.0),
    ]

    hips = arm.pose.bones["hips"]
    for name, keys in (("idle", idle), ("walk", walk), ("run", run),
                       ("jump", jump), ("wave", wave)):
        act = bpy.data.actions.new(name)
        act.use_fake_user = True
        if arm.animation_data is None:
            arm.animation_data_create()
        arm.animation_data.action = act
        for frame, pose, bob in keys:
            rest(arm)
            for bname, pairs in pose.items():
                set_rot(arm, bname, pairs)
            hips.location = (0, 0, bob * H)
            for pb in arm.pose.bones:
                pb.keyframe_insert("rotation_quaternion", frame=frame, group=pb.name)
            hips.keyframe_insert("location", frame=frame, group="hips")
        act.frame_range  # 触发范围刷新
        n_curves = 0
        try:
            for layer in act.layers:
                for strip in layer.strips:
                    for cb in strip.channelbags:
                        n_curves += len(cb.fcurves)
        except Exception:
            pass
        print("ACTION", name, "fcurves", n_curves, "range", tuple(act.frame_range))
    rest(arm)
    arm.animation_data.action = bpy.data.actions["idle"]
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 49
    bpy.context.scene.frame_set(1)


# ---------------------------------------------------------------- 预览
def build_stage(col):
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

    core.add_light("Key", 'AREA', (H * 1.6, -H * 1.9, H * 2.2), 0.35 * S * S, "#fff0dc", size=H * 1.2)
    core.add_light("Rim", 'AREA', (-H * 1.8, H * 1.4, H * 1.6), 0.20 * S * S, "#bcd2ff", size=H * 1.2)
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
    rig_col = core.new_collection("Rig")
    stage = core.new_collection("Preview")

    objs = build_stickman(root)
    arm = build_rig(objs, rig_col)
    build_actions(arm)
    setup_preview()

    os.makedirs(core.OUT, exist_ok=True)
    blend_path = os.path.join(core.SRC, "stickman.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("SAVED", blend_path, "H", round(H, 5), "UNIT_M", round(UNIT_M, 3),
          "BONES", len(arm.pose.bones))

    import export_stickman
    glb = os.path.join(core.OUT, "stickman_white.glb")
    export_stickman.export_animated(glb)
    print("EXPORTED", glb)

    if "--render" in sys.argv:
        build_stage(stage)
        sc = bpy.context.scene
        sc.render.filepath = os.path.join(core.OUT, "stickman_preview.png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", sc.render.filepath)


main()

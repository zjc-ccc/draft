# -*- coding: utf-8 -*-
"""env_water_pond - 程序化生成低多边形水面块（可无缝平铺）+ 泡沫硬边
运行: blender --background --python gen_env_water_pond.py

结构:
  1) 16x16 网格水面(4m x 4m, 0.25m/格), 顶点高度 = 4 组整数波数正弦叠加(周期 4m -> 可平铺)
  2) 边界向下 0.02m 裙边(替代 Solidify, 省一半面数)
  3) 外圈 0.15m 宽泡沫硬边带, 整体抬高 0.015m 防 z-fighting
  全部 use_smooth=False, 零 UV 零贴图, 2 个纯色材质槽。
"""
import bpy
import math
import os
from mathutils import Vector

TAU = 2.0 * math.pi

SRC = r"E:\app_ideas\godot-game\Draft\draft3d\env_water_pond\src"
EXPORT = r"E:\app_ideas\godot-game\Draft\draft3d\env_water_pond\export"
PREVIEW = r"C:\Users\admin\AppData\Local\Temp\env_water_preview"
NAME = "env_water_pond"

DO_RENDER = True

# ---------------------------------------------------------------- 水面参数
SIZE = 4.0          # 边长 m
N = 16              # 每边分段 -> 17x17 顶点
STEP = SIZE / N     # 0.25 m
HALF = SIZE * 0.5
SKIRT = 0.02        # 向下裙边厚度
FOAM_W = 0.15       # 泡沫带宽
FOAM_LIFT = 0.015   # 泡沫抬高

# 4 组正弦叠加: 波数(kx, ky) 均为整数 -> 以 SIZE 为周期, 无缝平铺
WAVES = [
    (1.0, 1.0, 0.022, 0.45),
    (2.0, -1.0, 0.016, 1.15),
    (1.0, 3.0, 0.011, 2.30),
    (3.0, 2.0, 0.008, 0.70),
]
# 波高范围约 -0.057 ~ +0.057 m


def wave_h(x, y):
    h = 0.0
    for kx, ky, amp, phase in WAVES:
        h += amp * math.sin(TAU * (kx * x + ky * y) / SIZE + phase)
    return h


# ---------------------------------------------------------------- 工具
def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hexcol(h):
    h = h.lstrip("#")
    return tuple(srgb_to_linear(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4)) + (1.0,)


def set_in(bsdf, names, value):
    for n in names:
        if n in bsdf.inputs:
            bsdf.inputs[n].default_value = value
            return True
    return False


def make_mat(name, hexv, metallic=0.0, rough=0.5, spec=1.0, transmission=0.0, ior=1.33):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = hexcol(hexv)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    set_in(bsdf, ("Specular IOR Level", "Specular"), spec)
    set_in(bsdf, ("Transmission Weight", "Transmission"), transmission)
    set_in(bsdf, ("IOR",), ior)
    m.use_backface_culling = False
    return m


def reset_scene():
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras,
                 bpy.data.lights, bpy.data.images):
        for b in list(coll):
            coll.remove(b)


reset_scene()
os.makedirs(SRC, exist_ok=True)
os.makedirs(EXPORT, exist_ok=True)
os.makedirs(PREVIEW, exist_ok=True)

MAT_WATER = make_mat("env_water_surface", "#3FA9A0", 0.0, 0.08, 0.75, 0.85, 1.33)
MAT_FOAM = make_mat("env_water_foam", "#DCEFEF", 0.0, 0.65, 0.35, 0.0, 1.33)

# ---------------------------------------------------------------- 顶点
verts = []
VID = {}          # (i,j) -> index（顶面网格）
for j in range(N + 1):
    for i in range(N + 1):
        x = -HALF + i * STEP
        y = -HALF + j * STEP
        VID[(i, j)] = len(verts)
        verts.append((x, y, wave_h(x, y)))

faces = []
mats = []

# 顶面(水面): 逆时针 -> +Z
for j in range(N):
    for i in range(N):
        a = VID[(i, j)]
        b = VID[(i + 1, j)]
        c = VID[(i + 1, j + 1)]
        d = VID[(i, j + 1)]
        faces.append((a, b, c, d))
        mats.append(0)

# 边界环(俯视逆时针): 下 -> 右 -> 上 -> 左
loop = ([VID[(i, 0)] for i in range(N)]
        + [VID[(N, j)] for j in range(N)]
        + [VID[(i, N)] for i in range(N, 0, -1)]
        + [VID[(0, j)] for j in range(N, 0, -1)])

# 裙边: 每个边界顶点复制一份下沉 0.02
n0 = len(verts)
for vi in loop:
    x, y, z = verts[vi]
    verts.append((x, y, z - SKIRT))
for k in range(len(loop)):
    ta = loop[k]
    tb = loop[(k + 1) % len(loop)]
    da = n0 + k
    db = n0 + (k + 1) % len(loop)
    faces.append((ta, da, db, tb))
    mats.append(0)

# 泡沫带: 外环=水面边界(抬高), 内环=向内缩 FOAM_W
foam_out = []
foam_in = []
for vi in loop:
    x, y, z = verts[vi]
    foam_out.append(len(verts))
    verts.append((x, y, z + FOAM_LIFT))
    ix = x if abs(x) > HALF - STEP else x
    # 向内缩: 取各分量朝原点方向的位移
    dx = -FOAM_W if x > HALF - 1e-6 else (FOAM_W if x < -HALF + 1e-6 else 0.0)
    dy = -FOAM_W if y > HALF - 1e-6 else (FOAM_W if y < -HALF + 1e-6 else 0.0)
    nx, ny = x + dx, y + dy
    foam_in.append(len(verts))
    verts.append((nx, ny, wave_h(nx, ny) + FOAM_LIFT))

m = len(loop)
for k in range(m):
    oa = foam_out[k]
    ob = foam_out[(k + 1) % m]
    ib = foam_in[(k + 1) % m]
    ia = foam_in[k]
    faces.append((oa, ob, ib, ia))
    mats.append(1)

# ---------------------------------------------------------------- 建对象
me = bpy.data.meshes.new(NAME)
me.from_pydata(verts, [], faces)
me.validate(verbose=False)
ob = bpy.data.objects.new(NAME, me)
bpy.context.scene.collection.objects.link(ob)

me.materials.append(MAT_WATER)
me.materials.append(MAT_FOAM)
for p, mi in zip(me.polygons, mats):
    p.material_index = mi
    p.use_smooth = False

# 自定义属性: 平铺信息
ob["tile_size"] = SIZE
ob["wave_amplitude"] = 0.057

# 统计
tri = sum(len(p.vertices) - 2 for p in me.polygons)
print("[env_water_pond] verts=%d faces=%d tris=%d" % (len(me.vertices), len(me.polygons), tri))
print("[env_water_pond] bbox z: %.4f ~ %.4f" % (
    min(v.co.z for v in me.vertices), max(v.co.z for v in me.vertices)))

# ---------------------------------------------------------------- 保存 + 导出
blend_path = os.path.join(SRC, NAME + ".blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

bpy.ops.object.select_all(action="DESELECT")
ob.select_set(True)
bpy.context.view_layer.objects.active = ob
glb_path = os.path.join(EXPORT, NAME + ".glb")
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_yup=True,
    export_materials="EXPORT",
)
print("[env_water_pond] glb -> %s (%.1f KB)" % (glb_path, os.path.getsize(glb_path) / 1024.0))

# ---------------------------------------------------------------- 预览
if DO_RENDER:
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 960
    scene.render.resolution_y = 720
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Filmic" if "Filmic" in [
        v.name for v in scene.view_settings.bl_rna.properties["view_transform"].enum_items] else "Standard"

    # 世界
    world = bpy.data.worlds.new("preview_world")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.45, 0.62, 0.80, 1.0)
    bg.inputs[1].default_value = 1.6
    scene.world = world

    # 地面(深色石底) 衬托透明感
    bpy.ops.mesh.primitive_plane_add(size=14.0, location=(0, 0, -0.30))
    gnd = bpy.context.object
    gnd.name = "preview_ground"
    gm = bpy.data.materials.new("preview_ground_mat")
    gm.use_nodes = True
    gb = next(n for n in gm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    gb.inputs["Base Color"].default_value = hexcol("#5A6468")
    gb.inputs["Roughness"].default_value = 0.55
    gnd.data.materials.append(gm)

    # 光
    bpy.ops.object.light_add(type="SUN", location=(3, -2, 6))
    sun = bpy.context.object
    sun.data.energy = 4.0
    sun.data.angle = math.radians(6.0)
    sun.rotation_euler = (math.radians(38), math.radians(12), math.radians(35))

    bpy.ops.object.camera_add(location=(0, 0, 9))
    cam = bpy.context.object
    cam.data.lens = 45
    scene.camera = cam

    VIEWS = {
        "top": ((0.0, 0.0, 9.0), (0.0, 0.0, 0.0), 45, "ORTHO"),
        "q34": ((3.55, 3.55, 3.05), (0.0, 0.0, 0.0), 52, "PERSP"),
        "side": ((5.60, 0.35, 0.90), (0.0, 0.0, 0.10), 70, "PERSP"),
    }
    for key, (loc, target, lens, typ) in VIEWS.items():
        cam.location = Vector(loc)
        cam.data.type = typ
        cam.data.lens = lens
        if typ == "ORTHO":
            cam.data.ortho_scale = 5.8
        d = Vector(target) - Vector(loc)
        cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = os.path.join(PREVIEW, "%s_%s.png" % (NAME, key))
        bpy.ops.render.render(write_still=True)
        print("[env_water_pond] preview -> %s" % scene.render.filepath)

print("[env_water_pond] done")

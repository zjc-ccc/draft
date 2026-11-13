# -*- coding: utf-8 -*-
"""把 glb 重新导入空场景渲染，核对引擎内实际颜色"""
import bpy
import math
from mathutils import Vector

for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

bpy.ops.import_scene.gltf(filepath=r"E:\app_ideas\godot-game\Draft\draft3d\env_river_bridge\export\env_river_bridge.glb")

scene = bpy.context.scene
for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
    try:
        scene.render.engine = eng
        break
    except Exception:
        continue
scene.render.resolution_x = 1400
scene.render.resolution_y = 880
scene.view_settings.view_transform = 'Standard'
scene.eevee.taa_render_samples = 24

world = bpy.data.worlds.new("W")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.42, 0.52, 0.68, 1.0)
bg.inputs["Strength"].default_value = 1.1

ld = bpy.data.lights.new("Sun", 'SUN')
ld.energy = 3.6
ld.color = (1.0, 0.85, 0.68)
sun = bpy.data.objects.new("Sun", ld)
scene.collection.objects.link(sun)
sun.rotation_euler = (Vector((0, 0, 0.4)) - Vector((8.6, -5.0, 6.2))).to_track_quat('-Z', 'Y').to_euler()

ld2 = bpy.data.lights.new("Fill", 'AREA')
ld2.energy = 400
ld2.size = 12
ld2.color = (0.72, 0.80, 1.0)
fill = bpy.data.objects.new("Fill", ld2)
scene.collection.objects.link(fill)
fill.location = (-8, 10, 9)
fill.rotation_euler = (Vector((0, 0, 0.5)) - fill.location).to_track_quat('-Z', 'Y').to_euler()

cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 40
cam = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam)
tgt = Vector((0.0, 0.0, 0.52))
cam.location = tgt + Vector((0.64, 0.62, 0.46)).normalized() * 26.2
cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam

scene.render.filepath = r"E:\app_ideas\godot-game\Draft\draft3d\env_river_bridge\export\glb_check.png"
bpy.ops.render.render(write_still=True)
print("CHECK_RENDERED", len(bpy.data.objects))

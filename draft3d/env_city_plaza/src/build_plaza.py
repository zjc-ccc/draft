# -*- coding: utf-8 -*-
"""
城市中心广场（十字路口）· 微缩场景（Blender 5.x 程序化构建）
- 12x12 底座，十字路口居中，右前街区为市民广场
- 三个地铁站出入口、四角高楼群、裙房商铺、街具
- 三渲二 + Freestyle 墨线 + Bloom，黄昏冷暖对撞
用法：
    blender -b -P build_plaza.py
    blender -b -P build_plaza.py -- --render
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy

import city_base as base          # 先 import 以注入 campus_core 路径
import campus_core as core        # noqa: E402

core.wipe()

import city_ground as ground      # noqa: E402
import city_buildings as buildings  # noqa: E402
import city_metro as metro        # noqa: E402
import city_props as props        # noqa: E402
import export_glb                 # noqa: E402


def build_lights():
    scene = bpy.context.scene
    world = bpy.data.worlds.new("CityWorld")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 1.0
    lp = nt.nodes.new("ShaderNodeLightPath")
    mixw = nt.nodes.new("ShaderNodeMixRGB")
    mixw.blend_type = 'MIX'
    mixw.inputs["Color1"].default_value = core.srgb("#2a3550")
    mixw.inputs["Color2"].default_value = core.srgb("#aec3e0")
    nt.links.new(lp.outputs["Is Camera Ray"], mixw.inputs["Fac"])
    nt.links.new(mixw.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    sun = core.add_light("DuskSun", 'SUN', (10.0, -6.0, 4.8), 13.0, "#ff9e4f")
    sun.rotation_euler = (core.Vector((0, 0, 0.7)) - sun.location).to_track_quat('-Z', 'Y').to_euler()
    rim = core.add_light("Rim", 'SUN', (-9.0, 9.0, 7.0), 2.0, "#7f9dff")
    rim.rotation_euler = (core.Vector((0, 0, 0.6)) - rim.location).to_track_quat('-Z', 'Y').to_euler()
    fill = core.add_light("SkyFill", 'AREA', (8.0, 10.0, 9.0), 32, "#a9c4ea", size=10.0)
    fill.rotation_euler = (core.Vector((0, 0, 0.7)) - fill.location).to_track_quat('-Z', 'Y').to_euler()
    fill2 = core.add_light("SideFill", 'AREA', (-9.0, 2.0, 7.0), 42, "#ffc89a", size=7.0)
    fill2.rotation_euler = (core.Vector((-2.0, 0.0, 0.8)) - fill2.location).to_track_quat('-Z', 'Y').to_euler()

    fc = base.PLAZA_C
    core.add_light("FountainLight", 'POINT', (fc[0], fc[1], base.PAVE_Z + 0.7), 8.0,
                   "#6ff0ff", size=0.18)
    core.add_light("MetroLight", 'POINT', (2.0, 2.4, base.PAVE_Z + 0.5), 5.0,
                   "#3dffa7", size=0.14)
    core.add_light("ShopLightN", 'POINT', (-2.6, 2.2, base.PAVE_Z + 0.45), 9.0,
                   "#ffcf8a", size=0.20)
    core.add_light("ShopLightS", 'POINT', (2.8, -2.2, base.PAVE_Z + 0.45), 7.0,
                   "#ff9ad0", size=0.20)


def stage_all(obs, f0, step=0.8, dur=12, mode='pop'):
    core.stage_group(obs, f0, step, dur, mode)


def main():
    c_base = core.new_collection("Base")
    c_road = core.new_collection("Roads")
    c_plaza = core.new_collection("Plaza")
    c_build = core.new_collection("Buildings")
    c_metro = core.new_collection("Metro")
    c_props = core.new_collection("Props")

    c_base_obs = ground.build_base(c_base)
    roads = ground.build_roads(c_road)
    walks = ground.build_sidewalks(c_road)
    marks = ground.build_markings(c_road)
    paving = ground.build_plaza_paving(c_plaza)
    fountain = props.build_fountain(c_plaza)

    tower_groups = buildings.build_towers(c_build)
    annex_groups = buildings.build_annexes(c_build)
    podium_groups = buildings.build_podiums(c_build)
    sign_groups = buildings.build_signs(c_build)

    metro_groups = metro.build_metro(c_metro)

    tree_groups = props.build_trees(c_props)
    lamp_groups = props.build_lamps(c_props)
    signal_groups = props.build_traffic_lights(c_props)
    furniture_groups = props.build_furniture(c_props)
    car_groups = props.build_cars(c_props)

    # ---------------- 入场动画
    stage_all(c_base_obs, 1, 0.6, 14, 'rise')
    stage_all(roads, 6, 0.5, 10, 'pop')
    stage_all(walks, 10, 0.5, 10, 'pop')
    stage_all(marks, 14, 0.5, 8, 'pop')
    stage_all(paving, 18, 0.9, 10, 'pop')
    stage_all(fountain, 22, 0.7, 12, 'pop')

    for i, (obs, _name) in enumerate(tower_groups):
        stage_all(obs, 26 + i * 4, 0.55, 16, 'rise')
    for i, (obs, _name) in enumerate(podium_groups):
        stage_all(obs, 34 + i * 2, 0.5, 10, 'pop')
    for i, (obs, _name) in enumerate(annex_groups):
        stage_all(obs, 38 + i * 2, 0.5, 10, 'pop')
    for i, (obs, _name) in enumerate(sign_groups):
        stage_all(obs, 46 + i * 3, 0.6, 12, 'pop')

    for i, (obs, _name) in enumerate(metro_groups):
        stage_all(obs, 62 + i * 4, 0.6, 12, 'pop')
    for i, (obs, _name) in enumerate(tree_groups):
        stage_all(obs, 70 + i * 0.8, 0.5, 10, 'pop')
    for i, (obs, _name) in enumerate(lamp_groups):
        stage_all(obs, 78 + i * 1.2, 0.5, 10, 'pop')
    for i, (obs, _name) in enumerate(signal_groups):
        stage_all(obs, 82 + i * 1.2, 0.5, 10, 'pop')
    for i, (obs, _name) in enumerate(furniture_groups):
        stage_all(obs, 86 + i * 1.0, 0.5, 10, 'pop')
    for i, (obs, _name) in enumerate(car_groups):
        stage_all(obs, 92 + i * 2, 0.5, 10, 'pop')

    build_lights()
    core.setup_camera(lens=40.0, dist=20.8, target=(0.22, 0.22, 0.95),
                      direction=(0.56, 0.64, 0.46))
    core.setup_render()
    core.setup_freestyle()
    core.setup_compositor()
    core.apply_animation()

    os.makedirs(base.OUT, exist_ok=True)
    os.makedirs(base.SRC, exist_ok=True)
    blend_path = os.path.join(base.SRC, "env_city_plaza.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("SAVED", blend_path)
    print("OBJECTS", len(bpy.data.objects))

    try:
        glb_path = os.path.join(base.OUT, "env_city_plaza.glb")
        export_glb.export_engine(glb_path)
        print("EXPORTED", glb_path)
    except Exception as e:
        print("GLB_EXPORT_FAIL", e)

    if "--render" in sys.argv:
        scene = bpy.context.scene
        scene.render.filepath = os.path.join(base.OUT, "preview.png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", scene.render.filepath)


main()

# -*- coding: utf-8 -*-
"""
黄昏大学校园操场 · 微缩场景（Blender 5.x 程序化构建）
- 12x12 方形底座，跑道 / 看台 / 篮球场 / 行道树全部落座其上
- 三渲二 + Freestyle 墨线 + 合成器 Bloom
- 入场组装动画：底座 -> 场地 -> 看台 -> 篮球场 -> 树木道具

用法：
    blender -b -P build_campus.py
    blender -b -P build_campus.py -- --render
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy

import campus_core as core

core.wipe()

import campus_ground as ground
import campus_stands as stands
import campus_court as court
import campus_props as props
import export_glb


def main():
    c_base = core.new_collection("Base")
    c_ground = core.new_collection("Field")
    c_stand = core.new_collection("Stands")
    c_court = core.new_collection("Court")
    c_props = core.new_collection("GreeneryProps")

    ground.build_base(c_base)
    ground.build_road(c_ground)
    ground.build_track(c_ground)
    ground.build_pitch(c_ground)
    ground.build_goals(c_ground)
    ground.build_flags(c_ground)
    ground.build_long_jump(c_ground)

    stands.build_stand(c_stand)
    stands.build_seats(c_stand)
    stands.build_railing(c_stand)
    stands.build_canopy(c_stand)
    stands.build_scoreboard(c_stand)
    stands.build_podium(c_stand)
    stands.build_floodlights(c_stand)

    court.build_court(c_court)
    court.build_hoops(c_court)
    court.build_fence(c_court)

    props.build_trees(c_props)
    props.build_lamps(c_props)
    props.build_street_furniture(c_props)
    props.build_signs(c_props)
    props.build_bike_shed(c_props)
    ground.build_leaves(c_props)

    core.build_lights()
    core.setup_camera()
    core.setup_render()
    core.setup_freestyle()
    core.setup_compositor()
    core.apply_animation()

    os.makedirs(core.OUT, exist_ok=True)
    blend_path = os.path.join(core.SRC, "env_campus_field.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("SAVED", blend_path)
    print("OBJECTS", len(bpy.data.objects))

    try:
        glb_path = os.path.join(core.OUT, "env_campus_field.glb")
        export_glb.export_engine(glb_path)
        print("EXPORTED", glb_path)
    except Exception as e:
        print("GLB_EXPORT_FAIL", e)

    if "--render" in sys.argv:
        scene = bpy.context.scene
        scene.render.filepath = os.path.join(core.OUT, "preview.png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", scene.render.filepath)


main()

# -*- coding: utf-8 -*-
"""
赛博朋克天台拉面摊 · 微缩场景（Blender 5.x 程序化构建）
- 10x10 方形天台底座，全部元素落于其上
- 三渲二 + Freestyle 墨线 + 合成器 Bloom
- 入场组装动画：底座 -> 建筑 -> 摊位 -> 道具 -> 雨

用法：
    blender -b -P build_ramen.py
    blender -b -P build_ramen.py -- --render
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy

import ramen_core as core

# 先清场，再导入内容模块：模块级材质在 wipe 之后创建，避免被清掉
core.wipe()

import ramen_roof as roof
import ramen_props as props
import ramen_stall as stall
import export_glb


def main():
    c_base = core.new_collection("Base")
    c_build = core.new_collection("Building")
    c_stall = core.new_collection("Stall")
    c_inner = core.new_collection("Interior")
    c_props = core.new_collection("Props")
    c_wet = core.new_collection("Wet")

    roof.build_base(c_base)
    roof.build_stairwell(c_build)
    roof.build_water_tank(c_build)
    roof.build_billboard(c_build)
    roof.build_ac(c_build)
    roof.build_clothesline(c_build)

    stall.build_stall(c_stall)
    stall.build_lanterns(c_stall)
    stall.build_signs(c_stall)
    stall.build_seating(c_stall)

    props.build_gas(c_props)
    props.build_boxes(c_props)
    props.build_plants(c_props)
    props.build_cat_house(c_props)

    props.build_puddles(c_wet)
    props.build_rain(c_wet)

    core.build_lights()
    core.setup_camera()
    core.setup_render()
    core.setup_freestyle()
    core.setup_compositor()
    core.apply_animation()

    os.makedirs(core.OUT, exist_ok=True)
    blend_path = os.path.join(core.SRC, "env_ramen_stall_rooftop.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("SAVED", blend_path)

    try:
        glb_path = os.path.join(core.OUT, "env_ramen_stall_rooftop.glb")
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

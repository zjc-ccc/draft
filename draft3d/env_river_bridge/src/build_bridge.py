# -*- coding: utf-8 -*-
"""
黄昏滨河跨河桥 · 微缩场景（Blender 5.x 程序化构建）
- 12x12 方形台基，河道横贯中部，两侧柏油马路 + 人行道 + 绿化带
- 跨河人行桥架空在马路上方，两端平台经楼梯下到人行道
- 三渲二 + Freestyle 墨线 + 合成器 Bloom
- 入场组装动画：底座 -> 河道 -> 护岸 -> 马路 -> 桥台钢拱 -> 桥面栏杆 -> 楼梯 -> 绿化街具

用法：
    blender -b -P build_bridge.py
    blender -b -P build_bridge.py -- --render
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy

import bridge_core as core

core.wipe()

import bridge_ground as ground
import bridge_bridge as bridge
import bridge_props as props
import bridge_shop as shop
import export_glb


def main():
    c_base = core.new_collection("Base")
    c_river = core.new_collection("River")
    c_road = core.new_collection("Road")
    c_bridge = core.new_collection("Bridge")
    c_green = core.new_collection("Greenery")
    c_shop = core.new_collection("Shop")

    ground.build_base(c_base)
    ground.build_river(c_river)
    ground.build_banks(c_river)
    ground.build_river_detail(c_river)

    ground.build_roads(c_road)
    ground.build_markings(c_road)
    ground.build_walkways(c_road)

    bridge.build_bridge(c_bridge)

    props.build_hedges(c_green)
    props.build_trees(c_green)
    props.build_flowers(c_green)
    props.build_lamps(c_green)
    props.build_furniture(c_green)
    props.build_signs(c_green)
    props.build_mooring(c_green)

    shop.build_shop(c_shop)

    core.build_lights()
    core.setup_camera()
    core.setup_render()
    core.setup_freestyle()
    core.setup_compositor()
    core.apply_animation()

    os.makedirs(core.OUT, exist_ok=True)
    blend_path = os.path.join(core.SRC, "env_river_bridge.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("SAVED", blend_path)
    print("OBJECTS", len(bpy.data.objects))

    try:
        glb_path = os.path.join(core.OUT, "env_river_bridge.glb")
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

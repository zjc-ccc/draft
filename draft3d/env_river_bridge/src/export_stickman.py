# -*- coding: utf-8 -*-
"""
导出带骨架动画的火柴人 glb。

与 env_river_bridge 场景用的 export_glb.py 区别：
- 不做 strip_animation（那会把动作全部清掉）
- 走 Principled 材质替换，导出后还原
- export_animation_mode='ACTIONS'，每个 Action 导成一个动画片段

用法：
    blender -b src/stickman.blend -P src/export_stickman.py
"""

import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import export_glb


def export_animated(filepath):
    pairs, created = export_glb.swap_materials()
    print("MAT_SWAPPED", len(pairs), len(created))
    arm = next((o for o in bpy.data.objects if o.type == 'ARMATURE'), None)
    if arm and arm.animation_data:
        arm.animation_data.action = bpy.data.actions.get("idle")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        export_animations=True,
        export_animation_mode='ACTIONS',
        export_skins=True,
        export_apply=False,
        export_yup=True,
        export_def_bones=False,
        export_optimize_animation_size=False,
    )
    export_glb.restore(pairs, created)
    print("ANIM_GLB", filepath, os.path.getsize(filepath))
    return filepath


def main():
    root = r"E:\app_ideas\godot-game\Draft\draft3d\env_river_bridge"
    export_animated(os.path.join(root, "export", "stickman_white.glb"))


if __name__ == "__main__":
    main()

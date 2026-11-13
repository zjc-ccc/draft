# -*- coding: utf-8 -*-
"""
导出引擎友好版 glb。

glTF 不支持 Shader to RGB，直接导出三渲二材质会得到
baseColor=黑 + emissive=白。本脚本临时把材质替换为
Principled（底色=作者色，自发光仅保留桥灯/路灯），导出后还原。

用法：
    blender -b src/env_river_bridge.blend -P src/export_glb.py
"""

import os

import bpy

ROOT = r"E:\app_ideas\godot-game\Draft\draft3d\env_river_bridge"
OUT = os.path.join(ROOT, "export", "env_river_bridge.glb")

SAT_BOOST = 1.24
VAL_BOOST = 1.04


def _lin_to_srgb(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def _srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def punch(color):
    import colorsys
    r, g, b = (_lin_to_srgb(c) for c in color[:3])
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    s = min(1.0, s * SAT_BOOST)
    v = min(1.0, v * VAL_BOOST)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (_srgb_to_lin(r), _srgb_to_lin(g), _srgb_to_lin(b), 1.0)


def read_color(mat):
    nt = mat.node_tree
    for n in nt.nodes:
        if n.type == 'MIX_RGB' and n.blend_type == 'MULTIPLY':
            return tuple(n.inputs['Color1'].default_value)
    for n in nt.nodes:
        if n.type == 'EMISSION':
            return tuple(n.inputs['Color'].default_value)
    return (0.5, 0.5, 0.5, 1.0)


def read_emit(mat):
    for n in mat.node_tree.nodes:
        if n.type == 'EMISSION' and not n.inputs['Color'].is_linked:
            try:
                return float(n.inputs['Strength'].default_value)
            except Exception:
                return 0.0
    return 0.0


def make_engine_mat(mat):
    color = punch(read_color(mat))
    es = read_emit(mat)

    new = bpy.data.materials.new(mat.name + "_engine")
    new.use_nodes = True
    new.diffuse_color = color
    nt = new.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (300, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.75
    bsdf.inputs["Metallic"].default_value = 0.0
    if es > 0.0:
        for name in ("Emission Color", "Emission"):
            if name in bsdf.inputs:
                bsdf.inputs[name].default_value = color
                break
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = min(1.0, es)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return new


def swap_materials():
    cache = {}
    pairs = []
    for ob in bpy.data.objects:
        for slot in ob.material_slots:
            src = slot.material
            if src is None:
                continue
            if src.name not in cache:
                cache[src.name] = make_engine_mat(src)
            pairs.append((slot, src))
            slot.material = cache[src.name]
    return pairs, list(cache.values())


def restore(pairs, created):
    for slot, src in pairs:
        slot.material = src
    for mat in created:
        bpy.data.materials.remove(mat)


def strip_animation():
    """把入场动画定格到末帧并清除动画数据，避免导出成 scale=0.001 的空场景"""
    scene = bpy.context.scene
    scene.frame_set(scene.frame_end)
    bpy.context.view_layer.update()
    for ob in bpy.data.objects:
        if ob.animation_data:
            mw = ob.matrix_world.copy()
            ob.animation_data_clear()
            ob.matrix_world = mw
    for act in list(bpy.data.actions):
        bpy.data.actions.remove(act)
    bpy.context.view_layer.update()


def export_engine(filepath=OUT):
    strip_animation()
    pairs, created = swap_materials()
    print("MAT_SWAPPED", len(pairs), len(created))
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=filepath, export_format='GLB',
                              export_animations=False, export_apply=True)
    restore(pairs, created)
    print("ENGINE_GLB", filepath, os.path.getsize(filepath))
    return filepath


def main():
    export_engine(OUT)


if __name__ == "__main__":
    main()

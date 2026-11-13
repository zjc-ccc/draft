# -*- coding: utf-8 -*-
"""
导出引擎友好版 glb。

glTF 不支持 Shader to RGB，直接导出三渲二材质会得到
baseColor=黑 + emissive=白。本脚本临时把材质替换为
Principled（底色=作者色，自发光仅保留霓虹/灯笼等发光件），
导出后再还原，不修改 .blend。

用法（Blender 中打开 env_ramen_stall_rooftop.blend 后）：
    blender -b src/env_ramen_stall_rooftop.blend -P src/export_glb.py
"""

import os

import bpy

ROOT = r"E:\app_ideas\godot-game\Draft\draft3d\env_ramen_stall_rooftop"
OUT = os.path.join(ROOT, "export", "env_ramen_stall_rooftop_engine.glb")


def read_color(mat):
    """从三渲二 / 自发光材质里取作者色（线性 RGBA）"""
    nt = mat.node_tree
    for n in nt.nodes:
        if n.type == 'MIX_RGB' and n.blend_type == 'MULTIPLY':
            return tuple(n.inputs['Color1'].default_value)
    for n in nt.nodes:
        if n.type == 'EMISSION':
            return tuple(n.inputs['Color'].default_value)
    return (0.5, 0.5, 0.5, 1.0)


def read_emit(mat):
    """自发光强度；三渲二材质的 Emission 颜色是连线，返回 0"""
    for n in mat.node_tree.nodes:
        if n.type == 'EMISSION' and not n.inputs['Color'].is_linked:
            try:
                return float(n.inputs['Strength'].default_value)
            except Exception:
                return 0.0
    return 0.0


def make_engine_mat(mat):
    color = read_color(mat)
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
    bsdf.inputs["Roughness"].default_value = 0.9
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


def export_engine(filepath=OUT):
    """临时换引擎材质导出 glb，导出后还原材质"""
    pairs, created = swap_materials()
    print("MAT_SWAPPED", len(pairs), len(created))
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=filepath, export_format='GLB')
    restore(pairs, created)
    print("ENGINE_GLB", filepath, os.path.getsize(filepath))
    return filepath


def main():
    export_engine(OUT)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""城市中心广场 · 公共层：路径、尺度常量、调色板（复用 campus_core 的几何/材质/渲染工具）"""

import os
import sys

CITY_ROOT = r"E:\app_ideas\godot-game\Draft\draft3d\env_city_plaza"
SRC = os.path.join(CITY_ROOT, "src")
OUT = os.path.join(CITY_ROOT, "export")
CAMPUS_SRC = r"E:\app_ideas\godot-game\Draft\draft3d\env_campus_field\src"

for _p in (CAMPUS_SRC, SRC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import campus_core as core  # noqa: E402

TOP_Z = core.TOP_Z          # 底座顶面 0.30
HALF = core.HALF            # 底座半宽 6.0

ROAD_Y = 1.30               # 东西向主干道半宽
ROAD_X = 1.10               # 南北向道路半宽
WALK = 0.55                 # 人行道宽

PAVE_Z = TOP_Z + 0.058      # 人行道 / 街区地坪
ROAD_Z = TOP_Z + 0.004      # 车行道
LINE_Z = TOP_Z + 0.010      # 路面标线

BLOCK_X = ROAD_X + WALK     # 1.65 街区起始 |x|
BLOCK_Y = ROAD_Y + WALK     # 1.85 街区起始 |y|

PLAZA_C = (3.35, 3.40)      # 广场圆心
PLAZA_R = 1.42

PALETTE = {
    "slab": "#5b616d",
    "slab_d": "#565c67",
    "asphalt": "#474d58",
    "asphalt_d": "#3c424c",
    "walk": "#d5cebf",
    "walk_d": "#c2baa9",
    "curb": "#e6dfd0",
    "line": "#fdfaf0",
    "line_y": "#e8c457",
    "plaza": "#e8ddca",
    "plaza_d": "#d3c7b1",
    "plaza_ring": "#b09d84",
    "recess": "#14161b",
    "glass": "#4a76a4",
    "glass_l": "#5b8cbd",
    "tower_a": "#a3b3c7",
    "tower_b": "#bcb5c6",
    "tower_c": "#93a5bc",
    "tower_d": "#d5c3ac",
    "tower_e": "#8c9db4",
    "concrete": "#a8b2c1",
    "concrete_d": "#8792a3",
    "concrete_l": "#d0d7e1",
    "metal": "#646d7c",
    "metal_d": "#49505c",
    "tree": "#43864b",
    "tree_l": "#61aa63",
    "tree_d": "#356a3d",
    "trunk": "#7a5540",
    "green": "#0f9b6c",
    "white": "#f7f5ef",
    "bench": "#96724d",
    "car_red": "#d45144",
    "car_blue": "#4577c2",
    "car_yellow": "#eab33a",
    "car_gray": "#a6aeb9",
}


def mat(key, emit=0.0):
    """按调色板键取三渲二材质（按名字缓存）"""
    return core.toon_mat("City_" + key, PALETTE[key], emit=emit)


def glow(key, color_hex, strength=1.4):
    return core.emit_mat("CityGlow_" + key, color_hex, strength)

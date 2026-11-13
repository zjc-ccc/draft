# -*- coding: utf-8 -*-
"""城市中心广场 · 地铁站出入口：雨棚 / 下行楼梯 / 栏杆 / 站牌 / 立牌 / 通风井"""

import campus_core as core
import city_base as base

m = base.mat

GREEN = "#12a97a"


def _p(cx, cy, axis, facing, f, s):
    if axis == "y":
        return (cx + s, cy + facing * f)
    return (cx + facing * f, cy + s)


def _d(axis, fwd, lat, h):
    if axis == "y":
        return (lat, fwd, h)
    return (fwd, lat, h)


def _face_rot(axis, facing):
    if axis == "y":
        return (90.0, 0.0, 0.0) if facing < 0 else (90.0, 0.0, 180.0)
    return (90.0, 0.0, -90.0) if facing < 0 else (90.0, 0.0, 90.0)


def entrance(name, cx, cy, axis, facing, col, flip=False):
    """axis: 楼梯行进方向；facing: 出入口朝向（-1 / +1）；flip: 立牌与通风井左右互换"""
    obs = []
    z = base.PAVE_Z
    totem_s = 0.56 if flip else -0.56
    vent_s = -0.56 if flip else 0.56
    green = core.emit_mat("MetroGreen", GREEN, 1.2)
    white_glow = core.emit_mat("MetroWhite", "#eafff6", 1.6)
    rail = m("metal")
    glass = core.toon_mat("CityMetroGlass", base.PALETTE["glass_l"], emit=0.12)

    def add_box(tag, fwd, lat, h, f, zc, material):
        x, y = _p(cx, cy, axis, facing, f, 0.0)
        obs.append(core.box("%s_%s" % (name, tag), _d(axis, fwd, lat, h),
                            (x, y, zc), material, col=col))

    def add_box_s(tag, fwd, lat, h, f, s, zc, material):
        x, y = _p(cx, cy, axis, facing, f, s)
        obs.append(core.box("%s_%s" % (name, tag), _d(axis, fwd, lat, h),
                            (x, y, zc), material, col=col))

    # 楼梯井（暗色）+ 四级踏步
    add_box("Pit", 0.46, 0.72, 0.10, 0.01, z - 0.052, m("recess"))
    for i in range(4):
        add_box("Step%d" % i, 0.115, 0.62, 0.022, 0.17 - i * 0.115,
                z - 0.014 - i * 0.028, m("concrete_l"))
    # 两侧矮墙 + 扶手
    for s in (-1, 1):
        add_box_s("Wall%d" % s, 0.62, 0.045, 0.11, 0.02, s * 0.355, z + 0.035,
                  m("concrete_l"))
        add_box_s("HandRail%d" % s, 0.66, 0.012, 0.012, 0.02, s * 0.355, z + 0.11,
                  rail)
        for i, f in enumerate((-0.26, 0.0, 0.26)):
            x, y = _p(cx, cy, axis, facing, f, s * 0.355)
            obs.append(core.cyl("%s_Post%d%d" % (name, s, i), 0.007, 0.007, 0.09,
                                (x, y, z + 0.065), rail, seg=6, col=col))
    # 雨棚立柱
    for sf in (-1, 1):
        for ss in (-1, 1):
            x, y = _p(cx, cy, axis, facing, sf * 0.34, ss * 0.30)
            obs.append(core.cyl("%s_CanopyPost%d%d" % (name, sf, ss),
                                0.010, 0.010, 0.36, (x, y, z + 0.18),
                                rail, seg=8, col=col))
    # 玻璃雨棚 + 边框
    add_box("Roof", 0.84, 0.72, 0.014, 0.0, z + 0.38, glass)
    add_box_s("RoofEdgeF", 0.05, 0.76, 0.03, 0.42, 0.0, z + 0.395, rail)
    add_box_s("RoofEdgeB", 0.05, 0.76, 0.03, -0.42, 0.0, z + 0.395, rail)
    for s in (-1, 1):
        add_box_s("RoofEdge%d" % s, 0.88, 0.04, 0.03, 0.0, s * 0.355, z + 0.395, rail)
    # 门头绿色站牌
    add_box("Header", 0.035, 0.70, 0.135, 0.455, z + 0.445, green)
    x, y = _p(cx, cy, axis, facing, 0.478, 0.0)
    txt = core.text_mesh(name + "_HeaderTxt", "地铁 M", 0.058, (x, y, z + 0.445),
                         _face_rot(axis, facing), white_glow, col=col)
    if txt:
        obs.append(txt)
    # 棚下灯带
    add_box_s("DownLight", 0.52, 0.045, 0.008, 0.04, 0.0, z + 0.362,
              core.emit_mat("MetroDownLight", "#ffe6b8", 2.0))
    # 立牌（M 标志）
    x, y = _p(cx, cy, axis, facing, 0.06, totem_s)
    obs.append(core.cyl(name + "_TotemPole", 0.014, 0.014, 0.46, (x, y, z + 0.23),
                        m("metal_d"), seg=8, col=col))
    add_box_s("TotemPanel", 0.022, 0.17, 0.24, 0.06, totem_s, z + 0.52, green)
    x, y = _p(cx, cy, axis, facing, 0.082, totem_s)
    mtxt = core.text_mesh(name + "_M", "M", 0.125, (x, y, z + 0.52),
                          _face_rot(axis, facing), white_glow, col=col)
    if mtxt:
        obs.append(mtxt)
    # 通风井
    add_box_s("Vent", 0.18, 0.14, 0.10, -0.12, vent_s, z + 0.05, m("metal"))
    for i in range(3):
        add_box_s("VentSlat%d" % i, 0.16, 0.012, 0.008, -0.12,
                  vent_s - 0.045 + i * 0.045, z + 0.075, m("metal_d"))
    return obs


def build_metro(col):
    groups = []
    groups.append((entrance("Metro1", 2.00, 2.48, "y", -1, col, flip=True), "Metro1"))
    groups.append((entrance("Metro2", -2.62, -2.48, "y", 1, col), "Metro2"))
    groups.append((entrance("Metro3", 1.95, -3.45, "x", -1, col), "Metro3"))
    return groups

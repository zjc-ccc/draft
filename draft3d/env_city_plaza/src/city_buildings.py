# -*- coding: utf-8 -*-
"""城市中心广场 · 建筑：塔楼 / 裙房商铺 / 广告牌 / 市民中心"""

import campus_core as core
import city_base as base

m = base.mat

# 面板/文字朝向：rx=90 让文字竖立，rz 决定法线方向
FACE_ROT = {
    "S": (90.0, 0.0, 0.0),     # 法线 -Y
    "N": (90.0, 0.0, 180.0),   # 法线 +Y
    "E": (90.0, 0.0, 90.0),    # 法线 +X
    "W": (90.0, 0.0, -90.0),   # 法线 -X
}

FACE_NORMAL = {"S": (0, -1), "N": (0, 1), "E": (1, 0), "W": (-1, 0)}


def _panel_dims(face, w, d, t):
    """返回面板在某个朝向上的 (x尺寸, y尺寸)"""
    if face in ("S", "N"):
        return (w, t)
    return (t, w)


def wall_sign(name, cx, cy, cz, w, h, face, text, neon_hex, col, text_size=None):
    """贴墙霓虹招牌：发光底板 + 深色文字"""
    nx, ny = FACE_NORMAL[face]
    px, py = cx + nx * 0.035, cy + ny * 0.035
    t = 0.035
    dims = _panel_dims(face, w, 0, t)
    obs = [core.box(name, (dims[0], dims[1], h), (px, py, cz),
                    core.emit_mat("Neon_" + name, neon_hex, 1.6), col=col)]
    tx = px + nx * 0.022
    ty = py + ny * 0.022
    txt = core.text_mesh(name + "_Txt", text, text_size or min(h * 0.42, w / max(1, len(text)) * 0.8),
                         (tx, ty, cz), FACE_ROT[face], m("metal_d"), col=col)
    if txt:
        obs.append(txt)
    return obs


def tower(name, cx, cy, w, d, h, body_key, glass_key, seed, col):
    """玻璃幕墙塔楼：主体 + 四面幕墙 + 转角线脚 + 楼层线 + 屋顶设备"""
    obs = []
    z0 = base.PAVE_Z
    body = m(body_key)
    glass = core.toon_mat("CityGlassLit_" + glass_key, base.PALETTE[glass_key], emit=0.08)
    trim = m("concrete_l")
    obs.append(core.box(name, (w, d, h), (cx, cy, z0 + h / 2), body, col=col))
    # 女儿墙 + 屋顶机房 + 天线 + 航空障碍灯
    obs.append(core.box(name + "_Cornice", (w + 0.05, d + 0.05, 0.045),
                        (cx, cy, z0 + h + 0.022), trim, col=col))
    obs.append(core.box(name + "_RoofBox", (w * 0.40, d * 0.40, 0.10),
                        (cx, cy, z0 + h + 0.092), m("concrete_d"), col=col))
    obs.append(core.cyl(name + "_Antenna", 0.011, 0.005, 0.26,
                        (cx + w * 0.16, cy + d * 0.16, z0 + h + 0.20),
                        m("metal"), seg=8, col=col))
    obs.append(core.sphere(name + "_Beacon", 0.015,
                           (cx + w * 0.16, cy + d * 0.16, z0 + h + 0.34),
                           core.emit_mat("BeaconRed", "#ff5a5a", 2.0), seg=8, col=col))
    # 四面幕墙（略凸出主体）
    gh = h - 0.16
    gz = z0 + 0.08 + gh / 2
    obs.append(core.box(name + "_GlassS", (w - 0.10, 0.02, gh),
                        (cx, cy - d / 2 - 0.004, gz), glass, col=col))
    obs.append(core.box(name + "_GlassN", (w - 0.10, 0.02, gh),
                        (cx, cy + d / 2 + 0.004, gz), glass, col=col))
    obs.append(core.box(name + "_GlassW", (0.02, d - 0.10, gh),
                        (cx - w / 2 - 0.004, cy, gz), glass, col=col))
    obs.append(core.box(name + "_GlassE", (0.02, d - 0.10, gh),
                        (cx + w / 2 + 0.004, cy, gz), glass, col=col))
    # 四角竖向线脚
    for i, (sx, sy) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1))):
        obs.append(core.box("%s_Mullion%d" % (name, i), (0.045, 0.045, h),
                            (cx + sx * (w / 2 - 0.012), cy + sy * (d / 2 - 0.012),
                             z0 + h / 2), trim, col=col))
    # 楼层线
    for k in (1, 2):
        obs.append(core.box("%s_Band%d" % (name, k), (w + 0.035, d + 0.035, 0.026),
                            (cx, cy, z0 + h * k / 3.0), trim, col=col))
    # 部分楼层亮灯（两面暖光、两面冷光）
    warm = core.emit_mat("WindowWarm", "#ffc374", 2.1)
    cool = core.emit_mat("WindowCool", "#cfe6ff", 1.7)
    for k, zb in ((0.28, z0 + h * 0.28), (0.52, z0 + h * 0.52), (0.76, z0 + h * 0.76)):
        if (seed + int(k * 100)) % 3 == 0:
            continue
        zz = zb + 0.012
        obs.append(core.box("%s_LitS%d" % (name, int(k * 100)), (w - 0.12, 0.006, 0.045),
                            (cx, cy - d / 2 - 0.018, zz), warm, col=col))
        obs.append(core.box("%s_LitN%d" % (name, int(k * 100)), (w - 0.12, 0.006, 0.045),
                            (cx, cy + d / 2 + 0.018, zz), cool, col=col))
        obs.append(core.box("%s_LitW%d" % (name, int(k * 100)), (0.006, d - 0.12, 0.045),
                            (cx - w / 2 - 0.018, cy, zz), cool, col=col))
        obs.append(core.box("%s_LitE%d" % (name, int(k * 100)), (0.006, d - 0.12, 0.045),
                            (cx + w / 2 + 0.018, cy, zz), warm, col=col))
    return obs


def podium(name, cx, cy, w, d, face, sign_text, neon_hex, awning_hex, col):
    """沿街裙房：体块 + 店面发光带 + 雨棚 + 门头招牌"""
    obs = []
    h = 0.30
    z0 = base.PAVE_Z
    nx, ny = FACE_NORMAL[face]
    obs.append(core.box(name, (w, d, h), (cx, cy, z0 + h / 2), m("concrete_l"), col=col))
    obs.append(core.box(name + "_Cornice", (w + 0.05, d + 0.05, 0.03),
                        (cx, cy, z0 + h + 0.015), m("concrete_d"), col=col))
    # 店面玻璃带
    band_dims = _panel_dims(face, (w if face in ("S", "N") else d) - 0.22, 0, 0.02)
    band_x = cx + nx * ((d if face in ("S", "N") else w) / 2 + 0.006)
    band_y = cy + ny * ((d if face in ("S", "N") else w) / 2 + 0.006)
    obs.append(core.box(name + "_ShopBand", (band_dims[0], band_dims[1], 0.14),
                        (band_x, band_y, z0 + 0.15),
                        core.emit_mat("ShopGlow", "#ffd8a2", 2.2), col=col))
    # 门头雨棚
    aw_w = (w if face in ("S", "N") else d) - 0.30
    aw_dims = _panel_dims(face, aw_w, 0, 0.14)
    obs.append(core.box(name + "_Awning", (aw_dims[0], aw_dims[1], 0.014),
                        (cx + nx * ((d if face in ("S", "N") else w) / 2 + 0.075),
                         cy + ny * ((d if face in ("S", "N") else w) / 2 + 0.075),
                         z0 + 0.245),
                        core.toon_mat("CityAwning_" + name, awning_hex), col=col))
    if sign_text:
        sw = min(aw_w * 0.72, 0.62)
        obs.extend(wall_sign(name + "_Sign", cx, cy, z0 + 0.345, sw, 0.075, face,
                             sign_text, neon_hex, col, text_size=0.052))
    return obs


def roof_billboard(name, cx, cy, z0, w, h, face, text, neon_hex, col):
    """楼顶广告牌：支架 + 发光板 + 文字"""
    obs = []
    nx, ny = FACE_NORMAL[face]
    obs.append(core.box(name + "_LegL", (0.035, 0.035, 0.26),
                        (cx - w * 0.32, cy, z0 + 0.13), m("metal_d"), col=col))
    obs.append(core.box(name + "_LegR", (0.035, 0.035, 0.26),
                        (cx + w * 0.32, cy, z0 + 0.13), m("metal_d"), col=col))
    dims = _panel_dims(face, w, 0, 0.05)
    obs.append(core.box(name + "_Panel", (dims[0], dims[1], h),
                        (cx, cy, z0 + 0.26 + h / 2),
                        core.emit_mat("Neon_" + name, neon_hex, 1.7), col=col))
    txt = core.text_mesh(name + "_Txt", text, min(h * 0.46, w / max(1, len(text)) * 0.82),
                         (cx + nx * 0.04, cy + ny * 0.04, z0 + 0.26 + h / 2),
                         FACE_ROT[face], m("metal_d"), col=col)
    if txt:
        obs.append(txt)
    return obs


def civic_hall(col):
    """广场北侧的市民中心：柱廊 + 玻璃前厅 + 台阶"""
    obs = []
    cx, cy = 2.55, 5.32
    w, d, h = 1.95, 0.78, 0.52
    z0 = base.PAVE_Z
    obs.append(core.box("CivicHall", (w, d, h), (cx, cy, z0 + h / 2), m("concrete_l"), col=col))
    obs.append(core.box("CivicHall_Roof", (w + 0.14, d + 0.14, 0.05),
                        (cx, cy, z0 + h + 0.025), m("concrete_d"), col=col))
    obs.append(core.box("CivicHall_RoofGarden", (w - 0.30, d - 0.30, 0.02),
                        (cx, cy, z0 + h + 0.058), m("tree"), col=col))
    # 北侧背墙的竖向分格 + 玻璃带
    obs.append(core.box("CivicHall_BackGlass", (w - 0.26, 0.015, 0.24),
                        (cx, cy + d / 2 + 0.005, z0 + 0.30),
                        core.emit_mat("CivicGlowBack", "#ffd8a2", 1.8), col=col))
    for i in range(5):
        obs.append(core.box("CivicHall_Fin%d" % i, (0.035, 0.02, h),
                            (cx - 0.76 + i * 0.38, cy + d / 2 + 0.008, z0 + h / 2),
                            m("concrete_l"), col=col))
    # 北侧实墙 + 南侧玻璃前厅
    obs.append(core.box("CivicHall_Glass", (w - 0.24, 0.02, 0.42),
                        (cx, cy - d / 2 - 0.006, z0 + 0.28),
                        core.emit_mat("CivicGlow", "#cfe4ff", 1.0), col=col))
    # 柱廊
    for i in range(6):
        px = cx - 0.78 + i * 0.312
        obs.append(core.cyl("CivicCol%d" % i, 0.034, 0.030, 0.52,
                            (px, cy - d / 2 - 0.10, z0 + 0.26), m("concrete_l"),
                            seg=12, col=col))
    # 檐口
    obs.append(core.box("CivicHall_Porch", (w - 0.10, 0.26, 0.04),
                        (cx, cy - d / 2 - 0.11, z0 + 0.54), m("concrete_l"), col=col))
    # 台阶
    for i in range(3):
        obs.append(core.box("CivicStep%d" % i, (w - 0.30, 0.16, 0.02),
                            (cx, cy - d / 2 - 0.32 - i * 0.10, z0 + 0.045 - i * 0.015),
                            m("curb"), col=col))
    obs.extend(wall_sign("CivicSign", cx, cy + 0.0, z0 + h + 0.10, 1.0, 0.11, "S",
                         "市民中心", "#4fd6ff", col, text_size=0.075))
    return obs


def build_towers(col):
    """返回 [(对象列表, 塔楼名), ...]，方便分组做生长动画"""
    plan = [
        ("TowerNW1", -4.55, 4.45, 1.55, 1.55, 3.35, "tower_a", "glass", 3),
        ("TowerNW2", -2.55, 5.00, 1.05, 1.05, 2.35, "tower_b", "glass_l", 7),
        ("TowerNW3", -4.95, 2.62, 1.05, 1.05, 2.75, "tower_c", "glass", 11),
        ("TowerSW1", -4.60, -4.50, 1.60, 1.60, 4.05, "tower_c", "glass", 17),
        ("TowerSW2", -2.60, -5.05, 1.10, 1.10, 2.25, "tower_b", "glass_l", 19),
        ("TowerSW3", -5.10, -2.45, 1.00, 1.00, 2.95, "tower_e", "glass", 23),
        ("TowerSE1", 4.60, -4.50, 1.45, 1.45, 3.15, "tower_a", "glass", 29),
        ("TowerSE2", 2.62, -5.05, 1.10, 1.10, 2.30, "tower_d", "glass_l", 31),
        ("TowerSE3", 4.95, -2.50, 1.00, 1.00, 2.65, "tower_e", "glass", 37),
        ("TowerPlazaN", 5.35, 5.05, 1.10, 1.10, 1.95, "tower_b", "glass_l", 41),
        ("TowerPlazaE", 5.45, 2.55, 0.95, 0.95, 1.55, "tower_d", "glass", 43),
    ]
    groups = []
    for name, cx, cy, w, d, h, body, glass, seed in plan:
        groups.append((tower(name, cx, cy, w, d, h, body, glass, seed, col), name))
    return groups


def annex(name, cx, cy, w, d, h, body_key, col):
    """街区内的低层附楼：体块 + 屋顶花园 + 空调外机"""
    obs = []
    z0 = base.PAVE_Z
    obs.append(core.box(name, (w, d, h), (cx, cy, z0 + h / 2), m(body_key), col=col))
    obs.append(core.box(name + "_Cornice", (w + 0.04, d + 0.04, 0.025),
                        (cx, cy, z0 + h + 0.012), m("concrete_l"), col=col))
    obs.append(core.box(name + "_RoofGarden", (w - 0.16, d - 0.16, 0.02),
                        (cx, cy - 0.02, z0 + h + 0.033), m("tree"), col=col))
    obs.append(core.box(name + "_Glass", (w * 0.6, 0.015, h * 0.5),
                        (cx, cy - d / 2 - 0.005, z0 + h * 0.45),
                        core.emit_mat("ShopGlow", "#ffd8a2", 2.2), col=col))
    for i, (sx, sy) in enumerate(((-1, 1), (1, 1))):
        obs.append(core.box("%s_AC%d" % (name, i), (0.16, 0.12, 0.07),
                            (cx + sx * w * 0.26, cy + sy * d * 0.26, z0 + h + 0.07),
                            m("concrete_d"), col=col))
    obs.append(core.cyl(name + "_Vent", 0.05, 0.05, 0.06,
                        (cx + w * 0.30, cy - d * 0.30, z0 + h + 0.065),
                        m("metal"), seg=10, col=col))
    return obs


def build_annexes(col):
    plan = [
        ("AnnexNW", -3.20, 3.20, 1.20, 1.00, 0.55, "tower_d"),
        ("AnnexSW", -3.25, -3.15, 1.20, 1.00, 0.62, "tower_b"),
        ("AnnexSE", 3.20, -3.20, 1.20, 1.00, 0.50, "tower_d"),
    ]
    groups = []
    for args in plan:
        groups.append((annex(*args, col=col), args[0]))
    return groups


def build_podiums(col):
    plan = [
        ("PodiumNW", -3.62, 2.12, 3.70, 0.50, "S", "便利店", "#ffcf6b", "#c9564a"),
        ("PodiumSW", -3.62, -2.12, 3.80, 0.50, "N", "咖啡", "#ff8fb8", "#3f7f63"),
        ("PodiumSE", 3.70, -2.12, 3.90, 0.50, "N", "银行", "#6fd4ff", "#4a6591"),
        ("PodiumSE_E", 1.98, -3.85, 0.50, 3.30, "W", "便利店", "#8fffbf", "#c99a3c"),
        ("PodiumNW_W", -1.98, 3.85, 0.50, 3.30, "E", "书店", "#ffd76b", "#a05a7a"),
        ("PodiumCafe", 5.15, 3.52, 0.55, 1.05, "W", "咖啡", "#ff9fd0", "#3f8c8c"),
    ]
    groups = []
    for args in plan:
        groups.append((podium(*args, col=col), args[0]))
    return groups


def build_signs(col):
    groups = []
    groups.append((wall_sign("SignTowerNW", -4.55, 4.45 - 0.775, base.PAVE_Z + 2.30,
                             0.78, 0.46, "S", "城市之光", "#ff5ea8", col, text_size=0.13),
                   "SignNW"))
    groups.append((wall_sign("SignTowerSE", 4.60 - 0.725, -4.50, base.PAVE_Z + 1.90,
                             0.72, 0.40, "W", "CBD 中心", "#57e8ff", col, text_size=0.10),
                   "SignSE"))
    groups.append((roof_billboard("BillboardSW", -4.60, -4.50, base.PAVE_Z + 4.07,
                                  1.20, 0.42, "S", "星河大厦", "#ffa54d", col),
                   "BillboardSW"))
    groups.append((civic_hall(col), "Civic"))
    return groups

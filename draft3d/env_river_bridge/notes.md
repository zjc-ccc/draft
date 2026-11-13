# 黄昏滨河跨河桥 · 微缩场景

三渲二收藏级微缩模型：16×12 长方形台基（沿马路方向延长），河道横贯中部，两侧柏油马路各带人行道与绿化带；跨河人行桥架空在马路上方，两端平台经楼梯下到人行道，桥下马路可通行。S 侧人行道上有外卖店门面，N 侧人行道是收货点，为送外卖玩法提供两端锚点。

## 交付文件

| 文件 | 说明 |
| --- | --- |
| `export/preview.png` | 主预览图（1600×1000，EEVEE + Freestyle + Bloom，48 samples） |
| `export/glb_check.png` | glb 重新导入空场景的渲染，用于核对引擎内实际颜色 |
| `src/env_river_bridge.blend` | 完整工程（材质 / 灯光 / 相机 / 入场动画） |
| `export/env_river_bridge.glb` | 引擎友好版 glb（静态终态、Principled 底色、灯箱 / 橱窗 / 桥灯 / 路灯 / 光圈保留自发光），1.86 MB / 771 节点 / 63 材质 |
| `src/bridge_core.py` | 公共层：三渲二材质、基础几何、桥梁专用几何、灯光相机、Freestyle、合成器、入场动画 |
| `src/bridge_ground.py` | 底座台基 / 河道水面 / 石砌护岸 / 柏油马路与标线 / 人行道 / 绿化带地面 |
| `src/bridge_bridge.py` | 桥台立柱 / 钢拱吊杆 / 木板桥面 / 白色栏杆 / 两端平台与楼梯 / 桥灯牌匾 |
| `src/bridge_props.py` | 行道树 / 绿篱 / 花坛 / 路灯 / 长椅 / 垃圾桶 / 路牌 / 滨河系船柱 |
| `src/bridge_shop.py` | 外卖店门面 / 灯箱招牌 / 遮阳棚 / 橱窗 / 取餐窗口 / 外卖架 / 送餐电动车 / 取餐光圈 / 收货点 |
| `src/build_bridge.py` | 组装入口 |
| `src/export_glb.py` | 引擎材质替换导出 |
| `src/check_glb.py` | glb 回导渲染校验 |
| `export/stickman_white.glb` | 白色火柴人（桥场景比例，身高 0.583 单位 = 1.7 m），28 网格 / 17 骨 / 5 动作 / 435 KB |
| `export/stickman_preview.png` | 火柴人单体预览（900×1200，含 1.7 m 尺寸标注） |
| `src/build_stickman.py` | 火柴人生成脚本：几何 + 骨架 + 刚性蒙皮 + 五个 Action |
| `src/export_stickman.py` | 保留动画的 glb 导出（不做 `strip_animation`） |
| `src/stickman.blend` | 火柴人工程（骨架 / 五个 Action / 材质 / 预览相机） |
| `stickman_prompt.md` | 火柴人七段制作描述、比例速查、骨架与动作要点 |
| `godotdemo/` | Godot 4.6 预览工程（第三人称越肩相机，V 切第一人称：W/S 行走 / Shift 跑 / Space 跳跃 / F·E·左键 挥手） |

## 场景尺寸与高差关系

- 底座：`16 × 12`（`HALF_X = 8.0` / `HALF = 6.0`），台面高 `0.30`，双层台基（下层 `-0.54~-0.30`，上层 `-0.30~0.30`），全部元素落在台基上。
- 横向分带（Y）：河道 `±1.40` → 滨河步道 `1.40~1.98` → 柏油马路 `1.98~4.38`（宽 2.40）→ 人行道 `4.38~5.38` → 绿化带 `5.38~6.00`；南北对称，沿 X 全长 `±8.00`。
- 河道：河床 `-0.30`，水面 `-0.06`，石砌护岸 + 压顶 + 两道砌缝 + 水线深色带，两端为断面封口。
- 桥面：`1.45`，比马路高 `1.15`；桥宽 `1.70`，沿 Y 向跨 `±4.36`，覆盖河道并越过两侧马路。桥下净空由两根圆柱在马路内缘（`y = ±2.32`）支撑。
- 桥台：`x ±1.03 / y ±1.24~1.96`，从河床砌到桥面板底；拱肋 `x = ±0.72`，起拱 `z = 0.36`、拱顶 `z = 1.21`，13 组吊杆。
- 楼梯：每端 9 级，踏面 `0.25`、踢面 `0.12`、水平投影 `2.25`，从平台 `z = 1.45` 落到人行道 `z = 0.37`；南北两端分列左右（`+Y` 端向 `+X`、`-Y` 端向 `-X`），构图平衡。
- 平台：`1.70 × 1.06`，位于桥端人行道上方，两根圆立柱落地，外沿带栏杆。

## 外卖店与收货点（玩法锚点）

| 元素 | Blender 坐标 | Godot 坐标 | 说明 |
| --- | --- | --- | --- |
| 外卖店主体 | `x -7.30~-4.50`，`y -6.00~-5.06`，`z 0.30~1.36` | `x -7.30~-4.50`，`z 5.06~6.00`，`y 0.30~1.36` | 宽 2.80 / 深 0.94 / 净高 1.06（约 3.1 m），占满绿化带并压进人行道 0.32 |
| 取餐光圈 | `(-4.98, -4.62)`，`z 0.377` | `(-4.98, 4.62)`，`y 0.377` | 取餐窗口正前方，半径 0.235，暖光发光环 |
| 收货点光圈 | `(5.55, 4.86)`，`z 0.377` | `(5.55, -4.86)`，`y 0.377` | N 侧人行道，半径 0.255，薄荷色发光环 |
| 收货立牌 | `(5.07, 4.84)` | `(5.07, -4.84)` | 文字「收货点」 |

- 店招灯箱「麦香外卖」、遮阳棚「取餐窗口」、菜单立牌「取餐」用系统字体转网格；灯箱、橱窗、取餐窗口、两个光圈保留自发光，其余材质走 Principled 底色。
- 店面占位区（`SHOP_X0/X1`）内的行道树、绿篱、花坛自动跳过；S 侧「望江桥」路牌移到 `x = -3.25`，避免挡住取餐光圈。
- 桥头两侧各有一道斑马线（`x = ±4.62`），外卖店门前与楼梯落地处都能直接过街。
- Godot 端 `_ground_at()` 把店面矩形（`x -7.30~-4.50, z ≥ 5.06`）当作实心不可站立，其余地面高度不变。

## 渲染设置

- EEVEE，`Standard` 视图变换，1600×1000，48–64 samples。
- 三渲二：Diffuse → ShaderToRGB → ColorRamp（CONSTANT，0.30 / 0.50 / 0.76 / 1.00）→ MULTIPLY 底色 → Emission。
- 描边：Freestyle，绝对线宽 1.6，线色近黑。
- 合成：Glare Bloom（Threshold 0.88 / Strength 0.32 / Size 0.6）。
- 灯光：暖橙低角度主光 `#ffa054`；冷色轮廓光；天空补光 + 侧补光；桥面 2 盏、路口 4 盏暖色点光。
- 世界：Light Path `Is Camera Ray` 分层——相机看到亮天空 `#b6c6dd`，照明用暗环境 `#2a3550`。

## 入场动画

逐组 `pop` / `rise` 错峰出现，约 150 帧：

底座 → 河道水面与石块 → 护岸砌体 → 马路与路缘 → 标线斑马线 → 人行道与绿化带地面 → 桥台立柱 → 钢拱吊杆 → 桥面板 → 桥面栏杆 → 平台 → 楼梯 → 楼梯栏杆 → 桥灯牌匾 → 绿篱 → 行道树 → 花坛 → 路灯 → 长椅垃圾桶 → 路牌 → 系船柱 → 外卖店门面 → 取餐口与外卖架 → 电动车 → 收货点。

## 重建

```bat
"D:\Blender\blender.exe" -b -P "E:\app_ideas\godot-game\Draft\draft3d\env_river_bridge\src\build_bridge.py"
```

渲染预览：

```bat
"D:\Blender\blender.exe" -b "...\src\env_river_bridge.blend" --python-expr "import bpy; s=bpy.context.scene; s.eevee.taa_render_samples=48; s.render.filepath=r'...\export\preview.png'; bpy.ops.render.render(write_still=True)"
```

单独重导 glb：

```bat
"D:\Blender\blender.exe" -b "...\src\env_river_bridge.blend" -P "...\src\export_glb.py"
```

## 可调项

- 构图：`bridge_core.setup_camera(lens, dist, target, direction)`，当前 `lens 40 / dist 26.2`（场景从 12 宽改成 16 宽后同步拉远、换广角）
- 高差：`bridge_core.DECK_Z`（桥面高）；连带影响楼梯踏步数 `bridge_bridge.STAIR_STEPS`
- 桥宽：`bridge_core.DECK_W`；桥长：`bridge_core.DECK_END`
- 河道宽窄：`bridge_core.RIVER_HALF`；马路宽度：`bridge_core.ROAD_Y1`
- 台基长短：`bridge_core.HALF_X`（16 宽）/ `HALF`（12 深）；只改 `HALF_X` 会自动延长台基、河道、马路、人行道、绿化带与铺装缝
- 外卖店：`bridge_core.SHOP_X0/SHOP_X1`、`SHOP_BACK_Y/SHOP_FRONT_Y`、`SHOP_H`、`SHOP_PICK_X/Y`、`DROP_X/DROP_Y`
- 光比与色温：`bridge_core.build_lights()` 里 `DuskSun` / `SkyFill` 的 energy 与 color
- 三渲二阶梯：`bridge_core.RAMP_STOPS`

## 火柴人（从 `env_campus_field` 移植）

- 比例不是直接照搬：校园版按跑道长度换算，身高只有 `0.0646` 单位；桥场景按马路宽 `2.40 单位 = 7.0 m` 重算，`1 单位 ≈ 2.917 m`，身高改为 `0.583` 单位（`= 1.7 m`），否则在 12 单位见方的场景里只有约 2 cm，等于看不见。
- 模型结构、材质、关节比例与校园版完全一致，只改了 `H`；脚底严格在 `z = 0`，回导实测包围盒 `Z 0 ~ 0.5829`。
- 桥面 `z = 1.45`，Godot 里火柴人初始 `position.y = 1.45`；`player.gd` 不再夹取活动范围，而是用 `_ground_at()` 按区域解析出地面高度：桥面 `1.45`、平台 `1.45`、楼梯（9 级 × `0.12` 踢面，-Z 端向 +X、+Z 端向 -X）、人行道 `0.37`、绿化带 `0.40`、马路 `0.304`、滨河步道 `0.35`，河道返回 `NAN` 不可站立。活动范围按 `BASE_HALF_X = 8.0 / BASE_HALF_Z = 6.0` 限制；外卖店矩形（`x -7.30~-4.50, z ≥ 5.06`）返回 `NAN`，人不会穿进店面。同一 XZ 有多层时按当前高度取最近的一层，所以桥下马路可以穿行；台阶高于 `MAX_STEP = 0.22` 视为墙，被挡时按轴拆分歧出滑动。
- 重建火柴人（会同时生成 `src/stickman.blend` 与带动画的 `export/stickman_white.glb`）：

```bat
"D:\Blender\blender.exe" -b -P "...\src\build_stickman.py" -- --render
```

- 单独重导动画 glb（材质替换 + 保留动画，**不能**用 `export_glb.py`，里面的 `strip_animation()` 会清空动作）：

```bat
"D:\Blender\blender.exe" -b "...\src\stickman.blend" -P "...\src\export_stickman.py"
```

## 骨架与动作

- 17 根骨骼：`hips → spine → chest → neck → head`，两侧 `upperarm → forearm → hand`、`thigh → shin → foot`；骨骼头部对准原有关节球圆心。
- 刚性蒙皮：每个部件 1 个顶点组、权重 1.0，圆柱不变形；肘球/膝球/踝球/髋球跟下游骨骼，弯折处不露缝。
- 五个 Action（24 fps）：`idle` 49 帧循环、`walk` 25 帧循环、`run` 21 帧循环、`jump` 37 帧一次性、`wave` 49 帧一次性。
- 姿势用世界轴角度书写，`set_rot()` 内部用 `M⁻¹ · R · M` 转成局部四元数：`+X` 正向为向前摆（角色朝 `+Y`），挥手的抬臂绕 `Y` 轴。
- 下蹲的髋部下沉量按腿长反算（约 `0.09H`），保证脚掌不陷进桥面。
- 竖直跳跃位移由 `player.gd` 的 `JUMP_SPEED / GRAVITY` 驱动，动画只提供姿势，避免与代码位移打架。

## 说明

- glTF 不支持 Shader to RGB，直接导出会得到 `baseColor` 黑 + `emissive` 白；`export_glb.py` 在导出时临时替换为 Principled 材质并做 `SAT_BOOST 1.24 / VAL_BOOST 1.04` 提饱和，导出后还原，不修改 .blend。
- 导出前 `strip_animation()` 定格末帧并清动画，避免节点带着入场动画的 `scale=0.001` 导出。
- 已验证：Godot 载入 771 节点全部带底色，仅桥灯 `M_BridgeLamp`、路灯 `M_LampGlow`、店招 `M_ShopSign`、橱窗 / 取餐口 `M_ShopGlass`、取餐光圈 `M_ShopGlow`、收货光圈 `M_DropRing` 带自发光，节点无缩放，glb 1.86 MB。
- glb 里没有 Freestyle 墨线、Bloom 与三渲二阶梯光；Godot 端要靠 Environment 环境光 + glow 还原，想要纯平涂可把材质设为 `Unshaded`。
- 文字（望江桥 / 滨河路 / 麦香外卖 / 取餐窗口 / 取餐 / 收货点）用系统字体 `msyh.ttc` 转网格，换机器若缺字体需替换路径。

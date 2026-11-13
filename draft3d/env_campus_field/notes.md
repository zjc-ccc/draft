# 黄昏大学校园操场 · 微缩场景

三渲二风格的收藏级微缩模型：12×12 正方形底座，环形塑胶跑道 + 足球场居中，看台沿一侧展开，篮球场收在另一角，人行道与行道树围合，带入场组装动画。

## 交付文件

| 文件 | 说明 |
| --- | --- |
| `export/preview.png` | 主预览图（1600×1000，EEVEE + Freestyle + Bloom，48 samples） |
| `export/glb_check.png` | glb 重新导入空场景的渲染，用于核对引擎内实际颜色 |
| `src/env_campus_field.blend` | 完整工程（材质 / 灯光 / 相机 / 入场动画） |
| `export/env_campus_field.glb` | 引擎友好版 glb（静态终态、Principled 底色、发光件保留自发光） |
| `src/campus_core.py` | 公共层：三渲二材质、环形几何、灯光相机、Freestyle、合成器、入场动画 |
| `src/campus_ground.py` | 底座 / 道路 / 塑胶跑道 / 足球场 / 球门 / 角旗 / 跳远沙坑 / 落叶 |
| `src/campus_stands.py` | 阶梯看台 / 座椅 / 金属栏杆 / 顶棚 / 主席台 / 计分牌 / 场地投光灯 |
| `src/campus_court.py` | 小型篮球场：拼色地胶 / 场线 / 篮架 / 围网 |
| `src/campus_props.py` | 行道树与树池 / 长椅 / 垃圾桶 / 饮水台 / 公告栏 / 校训石 / 指示牌 / 自行车棚 / 路灯 |
| `src/build_campus.py` | 组装入口 |
| `src/export_glb.py` | 引擎材质替换导出 |

## 场景尺寸与布局

- 底座：`12 × 12`，台面高 `0.30`，双层台基；全部元素落在台面上。
- 跑道：体育场形（直道沿 Y），外半径 `2.50`、直道半长 `1.30`，8 道、单道宽 `0.1025`，中心 `(0, 0.55)`。
- 足球场：`2.90 × 4.60` 人工草皮，带剪草条纹、禁区、点球弧、球门、角旗。
- 看台：`-X` 侧 5 级台阶（踏面 0.5 / 踢面 0.22），蓝色座椅、金属栏杆、前檐带「主席台 / 阳光体育 / 3:2 计分」的顶棚。
- 篮球场：`+X` 侧 `2.30 × 2.90`，双篮架 + 三面围网。
- 道路：`-Y` 侧沥青路（12 宽、虚线）＋人行道＋路缘石；`+Y` 侧步道串起车棚、长椅、饮水台。

## 渲染设置

- EEVEE，`Standard` 视图变换，1600×1000，48–64 samples。
- 三渲二：Diffuse → ShaderToRGB → ColorRamp（CONSTANT，0.30 / 0.50 / 0.76 / 1.00）→ MULTIPLY 底色 → Emission。
- 描边：Freestyle，绝对线宽 1.7，线色近黑。
- 合成：Glare Bloom（Threshold 0.88 / Strength 0.35 / Size 0.6）。
- 灯光：暖橙低角度主光 `#ff9f4d`；冷色轮廓光；天空补光 + 看台侧补光；4 盏路灯点光。
- 世界：Light Path `Is Camera Ray` 分层——相机看到亮天空 `#a9bedb`，照明用暗环境 `#24304d`，避免整体发灰。

## 入场动画

逐组 `pop`（缩放入场）/ `rise`（抬升）错峰出现，约 191 帧：

底座 → 道路 → 跑道与分道线 → 草皮与场线 → 球门角旗 → 跳远沙坑 → 看台台阶与座椅 → 顶棚与计分牌 → 主席台 → 投光灯 → 篮球场 → 篮架围网 → 树木 → 路灯 → 街道家具 → 标牌车棚 → 落叶。

## 重建

```bat
"D:\Blender\blender.exe" -b -P "E:\app_ideas\godot-game\Draft\draft3d\env_campus_field\src\build_campus.py"
```

渲染预览：

```bat
"D:\Blender\blender.exe" -b "...\src\env_campus_field.blend" --python-expr "import bpy; s=bpy.context.scene; s.render.resolution_percentage=100; s.eevee.taa_render_samples=48; s.render.filepath=r'...\export\preview.png'; bpy.ops.render.render(write_still=True)"
```

## 可调项

- 构图：`campus_core.setup_camera(lens, dist, target, direction)`
- 光比与色温：`campus_core.build_lights()` 里 `DuskSun` / `SkyFill` 的 energy 与 color
- 三渲二阶梯：`campus_core.RAMP_STOPS`
- 跑道尺寸：`campus_core.R_OUT / S_HALF / LANE_W`
- 看台层数：`campus_stands.ROWS / ROW_TREAD / ROW_RISE`

## 说明

- glb 导出前会 `strip_animation()`：定格末帧并清掉动画数据，否则节点会带着入场动画的 `scale=0.001` 初始态导出，导入引擎后看起来像空场景/没上色。
- 导出时对底色做 `punch()` 处理（`SAT_BOOST = 1.24` / `VAL_BOOST = 1.04`，`Roughness 0.75`），抵消查看器 Filmic/ACES 色调映射造成的发灰；想要更艳可直接调这两个系数。
- 预览图鲜艳是因为三渲二阶梯光 + 暖色主光 + Freestyle 墨线 + Bloom；glb 里只有纯底色，观感天然更平。Godot 里若想还原平涂感，把材质 Shading Mode 设为 `Unshaded`（或给场景加 Environment 环境光）即可。
- 导出后已验证：699 个节点、63 个材质全部带 `baseColorFactor`，路灯/计分牌/投光灯带 `emissiveFactor`，节点缩放均为 1。
- 文字（主席台 / 阳光体育 / 明德笃学 / 社团招新 / 操场）使用系统字体 `msyh.ttc` 转网格，换机器若缺字体需要替换路径。
- glb 由 `export_glb.py` 临时替换 Principled 材质导出，因此颜色与预览一致（三渲二 ShaderToRGB 无法写入 glTF）。单独重导：

```bat
"D:\Blender\blender.exe" -b "...\src\env_campus_field.blend" -P "...\src\export_glb.py"
```

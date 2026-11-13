# env_water_pond

## 基本参数

| 项 | 值 |
| --- | --- |
| 类型 | 3D 静止水面块（池塘 / 水洼 / 泳池水面），静态单模型 |
| 尺寸 | 4.0 m × 4.0 m，泡沫带在边界内侧 0.15 m 宽 |
| 高度 | z = -0.02 m（裙边底）～ +0.065 m（泡沫顶），水面起伏约 ±0.057 m |
| 网格 | 16×16 段（0.25 m/格），17×17 = 289 个顶面顶点 |
| 面数 | 384 面 / 768 三角面（水面 256 四边形 + 裙边 64 + 泡沫带 64） |
| 原点 | 水面中心，z=0 为平均水位（可直接贴到地形上） |
| 源文件 | `src/env_water_pond.blend` |
| 导出 | `export/env_water_pond.glb`（39.8 KB，glTF 2.0，2 个 primitive） |
| 配套着色器 | `export/water_pond.gdshader`（Godot 4.x，水效果的正式实现） |

## 结构

- **水面**：16×16 网格平面，顶点高度由 4 组正弦叠加而成（见下），幅度合计峰值 0.057 m。
- **裙边**：整圈边界顶点向下复制 0.02 m 形成薄壳，替代 Blender Solidify —— 面数只有一半，仍保留"有厚度的水池块"观感，同时从侧面看不到内部空腔。
- **泡沫带**：贴着边界的 0.15 m 宽四边形环带，整体抬高 0.015 m 防止与水面 z-fighting；硬白色低多边形边，正好是"池塘硬边"的视觉标签。
- **全部面 `use_smooth = False`**，与 `env_tree` 的体素硬边风格一致；**零贴图、零 UV**。

### 可无缝平铺的波浪

波数取整数即可保证以 4 m 为空间周期，相邻拼块接缝处高度与斜率完全连续：

```
h(x,y) = 0.022·sin(2π(1x+1y)/4 + 0.45)
       + 0.016·sin(2π(2x−1y)/4 + 1.15)
       + 0.011·sin(2π(1x+3y)/4 + 2.30)
       + 0.008·sin(2π(3x+2y)/4 + 0.70)
```

注意：**泡沫带是每块一份的**，所以把多块拼成大面积水域时会出现网格状白色接缝。拼大海面时请隐藏泡沫带（材质槽 1 的面），或只用 shader 版本的水面。

## 材质

| 材质 | 色值 | Metallic | Roughness | 其它 |
| --- | --- | --- | --- | --- |
| `env_water_surface` | `#3FA9A0` | 0 | 0.08 | Transmission 0.85，IOR 1.33 |
| `env_water_foam` | `#DCEFEF` | 0 | 0.65 | 硬边白 |

- 无贴图无 UV；glb 里的材质**只是兜底**（glTF 用 `KHR_materials_transmission`，Godot 导入后不一定完整还原）。
- 正式效果请用 `water_pond.gdshader`。

## Godot 用法

```gdscript
var pond = preload("res://draft3d/env_water_pond/export/env_water_pond.glb").instantiate()
add_child(pond)

var water := pond as MeshInstance3D
var mat := ShaderMaterial.new()
mat.shader = preload("res://draft3d/env_water_pond/export/water_pond.gdshader")
water.set_surface_override_material(0, mat)   # 0 = 水面
# 1 = 泡沫带：保留 glb 自带白色材质，或换成 StandardMaterial3D（albedo #DCEFEF, roughness 0.65）
```

- 模型 Y 轴向上（glTF 标准），Godot 里无需旋转；`z=0` 为平均水位。
- **渲染器**：需要 Forward+（Mobile 也可），因为 shader 用到 `hint_depth_texture` + `hint_screen_texture`；Compatibility 渲染器下深度纹理可能不可用，岸边泡沫会失效。
- 材质槽 0 挂 shader 后水面不再需要 glb 的透明材质；透明排序交给 shader 的 `blend_mix` 即可。

### 着色器参数

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `shallow_color` | `#3FA9A0` | 正视角的水色（浅水/俯视） |
| `deep_color` | `#18606A` | 斜视角偏深的水色，与浅色按视角混合 |
| `foam_color` | `#DCEFEF` | 泡沫色 |
| `surface_alpha` | 1.0 | 水面混合不透明度，1.0 = 完全用屏幕折射色 |
| `fresnel_power` / `fresnel_max` | 5.0 / 0.92 | 菲涅尔曲线，越大掠射角越晚变白 |
| `refraction_strength` | 0.018 | 屏幕 UV 扰动强度（0 = 完全不折射） |
| `refraction_tint` | 0.45 | 折射画面被水色染色的比例 |
| `noise_scale` | 3.2 | 程序噪声的空间频率（每 4 m 多少个噪声周期） |
| `normal_scale` | 0.22 | 噪声法线强度，0 = 镜面平水 |
| `flow_speed` | 1.0 | 两层噪声的滚动速度，0 = 静止 |
| `wave_amp` | 0.025 | 顶点位移幅度（上限 0.03，保持硬边） |
| `wave_speed` | 1.0 | 顶点波浪速度 |
| `shore_foam_enabled` | true | 深度差岸边泡沫开关 |
| `foam_depth` | 0.25 | 距离池底小于该深度（m）算岸边，生成泡沫 |
| `foam_breakup` | 0.55 | 泡沫破碎程度 |
| `water_roughness` / `water_specular` | 0.06 / 0.75 | 水面镜面强度 |

> **岸边泡沫的前提**：`hint_depth_texture` 的差值需要水面之下有真实的池底/地形网格。如果只是把水片平铺在地面上（水面离地 1~2 cm），整块水面都会被判成"岸边"，此时请把 `shore_foam_enabled` 关掉，靠模型自带的白色泡沫带出边。

## 生成逻辑

`src/gen_env_water_pond.py` 全程序化生成，无手工建模：

- 顶点高度由 `wave_h(x, y)` 计算，改 `WAVES` 里的（波数、幅度、相位）即可换浪形；波数必须是整数才能保持可平铺。
- 分段数 `N`、边长 `SIZE`、裙边 `SKIRT`、泡沫宽度 `FOAM_W`、抬升 `FOAM_LIFT` 都是文件顶部常量。
- 一次 `from_pydata` 写入全部顶点/面，再按面写 `material_index`（0 水、1 泡沫），最后统一 `use_smooth = False`。
- 脚本同时保存 `.blend`、导出 `.glb`，并用 Cycles（CPU，64 samples）渲染 top / 45° / side 三视图到 `%TEMP%\env_water_preview\`。

## 验收状态

- Blender 端已渲染三视图确认：几何闭合、无破面、泡沫带完整、硬边可见。
- **Godot 端未实机验证**：本机没有找到 Godot 可执行文件，`water_pond.gdshader` 仅做了静态语法审查。首次在工程里使用时，请留意 `hint_depth_texture`（需要池底网格）与 Forward+ 渲染器这两点。

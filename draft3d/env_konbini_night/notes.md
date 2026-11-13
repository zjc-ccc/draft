# env_konbini_night

雨夜便利店街角微缩场景（Blender 5.2 / EEVEE / 三渲二）。

## 文件

| 路径 | 说明 |
| --- | --- |
| `src/build_konbini.py` | 唯一构建脚本，程序化生成全部几何、材质、灯光、相机、动画 |
| `src/env_konbini_night.blend` | 生成结果，可直接打开渲染 |
| `export/env_konbini_night.glb` | glTF 2.0 导出（含入场动画） |
| `export/preview.png` | 1600×1000 主视觉预览 |

## 重建

```powershell
# 构建 + 保存 .blend + 导出 glb
D:\Blender\blender.exe -b -P src\build_konbini.py

# 渲染主视觉
D:\Blender\blender.exe -b src\env_konbini_night.blend -o //../export/preview_#### -f 200
```

脚本会把 `.blend` 存回 `src/`，并覆盖 `export/` 下的 glb。

## 场景规格

- 单位：米。底座 12 × 12（含台座总高 0.80），全部元素搭建其上，无人物。
- 便利店占地 `x[-5.2, 0.9] × y[-5.2, -1.4]`，层高 3.8，玻璃面朝 +Y 与 +X。
- 街道：横街 `y[1.4, 5.2]`，竖街 `x[3.0, 5.5]`，人行道抬高 0.14，含斑马线、中心黄虚线、停止线、停车位、排水格栅、井盖。
- 相机：35 mm，机位由 `(0.567, 0.701, 0.400)` 方向 × 24.4 m 决定，注视 `(0, 0.1, 1.7)`。

## 材质与风格

- 三渲二：`Diffuse BSDF → Shader to RGB → ColorRamp（常量插值，4 级）→ 乘底色 → Emission`。
  光源只决定落在哪一阶，颜色由作者值直出，因此材质色即画面色。
- 墨线：Freestyle（silhouette / border / crease / contour），绝对线宽 1.4 px，线色 `#050508`。
- 发光件（招牌、灯管、冷柜、贩卖机、霓虹）用纯 Emission，配合合成器 Bloom（Threshold 0.6 / Strength 0.85）产生光晕。
- 色彩管理 `Standard`，不做 AgX 压缩，保证霓虹不被去饱和。

## 动画

- 帧率 24 fps，`frame_end = 209`。
- 分组错峰入场：底座(1) → 街道(18) → 建筑壳体(40) → 店内陈设(58) → 招牌/雨棚(40 组内) → 道具(100~128) → 湿地(150) → 雨(165)。
- `rise` = 从地面下方 0.85 m 升起；`pop` = 从 0.001 缩放弹入。

## 已知取舍

- 未使用透明玻璃：保留窗框与竖挺，让店内陈设完全可见（符合"透过大面积玻璃窗清楚看到店内"的要求）。
- 积水仅保留极少量深色湿痕；无实时反射，湿地靠明度差与墨线区分。
- 描边依赖 Freestyle，只在 Blender 渲染中出现；`.glb` 不含墨线，导入引擎需自行加描边后处理。
- 店内商品为纯色块（无贴图），远看成立，近看是抽象色块。

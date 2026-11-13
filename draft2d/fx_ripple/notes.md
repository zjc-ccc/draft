# fx_ripple

## 基本参数

| 项 | 值 |
| --- | --- |
| 画布 | 32×32，8 帧循环动画 |
| 视角 | 俯视正交（正上方向下看水面），不带透视变形 |
| 色深 | 32bpp RGBA，透明背景 |
| 帧时长 | 120ms/帧（与 `env_pond` 一致），整循环 960ms |
| 锚点 | **画布居中**（Godot 默认 `Sprite2D`/`AnimatedSprite2D` 居中） |
| tag | `loop`，区间 `0-7`，`forward` |
| 源文件 | `src/fx_ripple.aseprite` |
| 导出 | `export/fx_ripple_00.png` ~ `_07.png`、`_sheet.png`、`_sheet.json` |

## 动画设计

- 第 1 帧＝第 8 帧：仅中心 2×2 亮点（`#E8FFFF`），逐字节相同（PNG 哈希一致），循环无接缝。
- 第一圈环：f2 r3 → f3 r5 → f4 r7 → f5 r9 → f6 加宽（2px 环带）→ f7 最宽且最淡。
- 第二圈环错相一拍：f4 r2 出现 → f5 r4 → f6 r6 → f7 r8。
- f6/f7 的外圈是 2px 实心环带（用整数半径索引逐像素生成，保证环带连续、无孔洞），形成“环变宽”的观感。
- 淡出靠明暗层级而非透明度：亮度从 `#C9F2EF` 一路压到 `#37868A`，最后两帧的颜色直接取自 `env_pond` 的水色，叠在水面上时自然融入。
- 全片无半透明像素：只有完全不透明或完全透明两种，符合规范“硬边像素”要求。

## 用色

- 亮点：`#E8FFFF`
- 环：`#E0FBF8 #C9F2EF #A8E0DA #8FD2CC #6FBDB8 #5AA9A4`（淡出到水色）`#4A9A96 #37868A #2E787D`
- `#4A9A96`、`#37868A`、`#2E787D` 与 `env_pond` 的水面色 `#2C7279` / `#37868A` / `#4A9A96` 同源，所以末尾帧的环几乎看不出，只留“涟漪消失”的信号。

## tag 说明

`loop` **不在** §3 状态词表里（词表是 `idle/on/off/open/close/full/half/empty/low/medium/high`）。本素材是纯循环特效、没有状态语义，词表里没有等价词，故选 `loop` 并在 `assets_convention.md` 的资产清单条目里注明；是否要把 `loop` 正式加进词表，待确认。

## 图层

自下而上：`spark`（中心亮点，8 帧恒定）/ `rings`（两圈扩散环，逐帧变化）。

## Godot 用法

```gdscript
$AnimatedSprite2D.sprite_frames = preload("res://draft2d/godot_spriteframes/fx_ripple.tres")
$AnimatedSprite2D.play("loop")
$AnimatedSprite2D.z_index = 1   # 叠在 env_pond 的水面之上
```

- `godot_spriteframes/fx_ripple.tres` 用 `AtlasTexture` 切 `_sheet.png`，动画名 `loop` 与 tag 一致，帧时长 0.12s，`loop = true`。
- 也可以直接用单帧序列：`export/fx_ripple_00.png` ~ `_07.png`，造型更可控（比如随机偏移、不同帧率）。
- 纹理过滤 Nearest；不要开 mipmap/线性插值，否则环会糊。

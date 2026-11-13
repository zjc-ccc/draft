# prop_coffee_table

## 基本参数

| 项 | 值 |
| --- | --- |
| 画布 | 96×96，单帧静态 |
| 视角 | 3/4 俯视，与 `prop_sofa` 同一套透视；光源在左上 |
| 色深 | 32bpp RGBA |
| 锚点 | **画布居中**（Godot 默认 `Sprite2D` 居中，无自定义 offset） |
| 源文件 | `src/prop_coffee_table.aseprite` |
| 导出 | `export/prop_coffee_table.png` |

## 结构

- 梯形桌面（顶面 polygon）+ 左右两条厚度侧面 + 正面立面，形成 3/4 俯视的桌板。
- 四条腿：前后错位，后腿被桌面遮去上半段，前腿完整可见。
- 桌下搁板：顶面 + 前立面 + 一条高光线，位置在桌面与地面之间。
- 轻微木纹：桌面上是分段断开的短横线，不做连续花纹或拼板图案。

## 用色

木色严格复用统一 ramp，未引入新木色：

`#3E2A18`（描边） `#94663A`（暗面/背光） `#9A6E3C`（中间暗调/木纹） `#C08E4E`（受光面） `#DEB274`（高光） `#E9CD94` / `#F0D39A`（左上镜面高光）

- 描边为 1px 深色硬边，无抗锯齿。
- 投影：`#00000033` 椭圆，与 `prop_sofa` 的软投影处理保持一致（本素材唯一的半透明区域）。

## 图层

自下而上：`shadow` / `back_legs` / `shelf` / `front_legs` / `tabletop`。

## Godot 用法

静态单图，不需要 `SpriteFrames`：

```gdscript
$Sprite2D.texture = preload("res://draft2d/prop_coffee_table/export/prop_coffee_table.png")
```

- 纹理过滤设为 Nearest（项目级 `rendering/textures/canvas_textures/default_texture_filter = 0` 或材质覆盖），避免放大糊边。
- 锚点是画布中心，摆位时按桌面中心点放即可；若要和角色脚底/地面线对齐，用 `offset.y` 做一次偏移。

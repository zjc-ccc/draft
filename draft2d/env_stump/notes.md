# env_stump

## 基本参数

| 项 | 值 |
| --- | --- |
| 画布 | 64×64，单帧静态 |
| 视角 | 3/4 俯视，与 `item_branch` / `env_pond` 同属野外簇；光源左上 |
| 色深 | 32bpp RGBA |
| 锚点 | **画布居中**（Godot 默认 `Sprite2D` 居中，无自定义 offset） |
| 源文件 | `src/env_stump.aseprite` |
| 导出 | `export/env_stump.png` |

## 结构

- 顶部大椭圆截面（俯视可见），截面内有同心年轮线，中心一个深色小点。
- 桶状侧体：上宽下略窄，带竖向树皮纹理和左侧高光/右侧暗面。
- 根部外扩：左、右、前三处根突，让木桩“扎在地上”。
- 苔藓/绿叶只点缀在根部左右，面积控制在约 30 像素，不遮主体轮廓。

## 用色

木色沿用统一 ramp（与 `item_stick` / `prop_coffee_table` 同一套）：

`#3E2A18`（描边/年轮） `#94663A`（侧体暗面） `#9A6E3C`（树皮纹理/截面内圈） `#C08E4E`（截面主色/受光） `#DEB274`（高光） `#E9CD94` / `#F0D39A`（左上镜面高光）

苔藓绿复用藤绿系 4 色：

`#4A5824`（暗部） `#6E7C34`（主体） `#9AAE52`（高光） `#B4C466`（最亮点缀）

- 全部硬边、1px 深色描边、无抗锯齿。
- 投影：`#00000033` 椭圆（与 `prop_sofa` 一致）。

## 图层

自下而上：`shadow` / `stump_base` / `top` / `rings` / `moss`。年轮单独一层，方便后续换树龄或做 `stump_old` 变体。

## Godot 用法

静态单图，不需要 `SpriteFrames`：

```gdscript
$Sprite2D.texture = preload("res://draft2d/env_stump/export/env_stump.png")
```

- 纹理过滤设为 Nearest。
- 锚点是画布中心；底部投影已含在画布里，与 `env_pond` 同场景时按地面线放即可。

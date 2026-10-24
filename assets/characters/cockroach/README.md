---
id: cockroach
category: characters
status: wip
size: 64x64
frames: 8
fps: 8
palette:
license: own
author: zjc-ccc
created: 2026-10-24
tags: [角色, 昆虫, 害虫, 蟑螂, 贴地]
---

# cockroach

## 用途

一只蟑螂，俯视视角，头朝画面下方。镜头压得很低、几乎贴在蟑螂背上往下看，所以两根长触角从画面下沿探进来——正好当"虫眼看地面"的压迫感素材，也能直接当普通小怪/害虫贴地爬行。

适合贴地板爬、从踢脚线缝里钻出来、被灯一照四散跑开的场景。

## 规格

| 项 | 值 |
| --- | --- |
| 画布 | 64x64 |
| 状态 | `walk` 1 个状态，8 帧 |
| 帧率 | 8 fps |
| 动画时长 | 1 秒 / 循环 |
| 调色板 | 翅 `#5E4024` / 高光 `#7C5832` / 中调 `#48301A` / 翅缝 `#22160C`；前胸背板 `#4A311D` / 亮边 `#9E7C50`；头 `#4C3420`；腿 `#503923` / 高光 `#80623E`；触角 `#5E4026` |
| 锚点 | 身体中心（x=32, y≈30）；触角末端是故意伸出画布下沿的，摆到场景里时别按"完整轮廓"对齐 |

## 文件

| 路径 | 说明 |
| --- | --- |
| `export/cockroach_walk_00..07.png` | 8 帧，爬行循环 |
| `preview/cockroach_icon_32.png` | 32x32 简化版，物品栏图标 |
| `source/` | 暂无手绘源文件，当前由脚本生成 |

生成脚本：

- `tools/art/cockroach.py` → `walk` 全部 8 帧
- `tools/art/cockroach_icon.py` → 物品栏图标

## 动画状态

| 状态 | 帧数 | 文件前缀 | 说明 |
| --- | --- | --- | --- |
| walk | 8 | `cockroach_walk_` | 三角步态：左前 / 右中 / 左后一组，另一组反相，六条腿交替往前扒；触角同时轻摆 |

身体本身不动（不抖、不缩放），只有腿和触角在动，所以贴在地板上不会有"飘"的感觉。第 0 帧和第 8 帧首尾相接，循环无缝。

## 细节

| 位置 | 说明 |
| --- | --- |
| 朝向 | 头在画面下方（y≈47~53），尾尖在上方（y≈8）；两根触角从头部两侧往下、往外弯，一路伸出画布下沿 |
| 身体 | 上窄下宽的椭圆，最宽 18px 左右；尾端收成尖，翅尖压暗两行，像两片叠着的翅 |
| 翅 | 左右两片，中间 1px 翅缝；翅面靠缝处一道高光、往外逐渐压暗到翅缘，尾端再加两粒反光 |
| 前胸背板 | 盖住翅根的一块近椭圆盾片，前缘（靠头那侧）一道亮边，中间偏暗、两侧各一条暗斑 |
| 头 | 比背板窄一圈，两侧两颗小复眼（深色 + 一点高光），正前方两颗下颚须 |
| 腿 | 六条，大腿 2px、胫节前段 2px 后端收成 1px；膝盖有一个 2x2 关节块，胫节上带两根小刺，末端一小节跗节 |
| 触角 | 每边一条二次贝塞尔曲线，根部两像素宽，往尖端收成 1px，中间几处亮斑当反光 |
| 描边 | 身体、背板、头描墨色边；腿和触角太细，不描边，靠自身颜色读数 |
| 尾须 | 尾尖两侧各两根 1px 短须 |

## 图标

| 尺寸 | 文件 | 用途 |
| --- | --- | --- |
| 32x32 | `preview/cockroach_icon_32.png` | 物品栏 / 背包列表 |

简化处理：身体压到 10px 宽，腿只留大腿 + 胫节两段（去掉小刺和跗节），翅面只保留缝、亮边和两侧暗部，触角留到画布下沿；眼睛保留，方便在背包里一眼认出是虫。

## 在 Godot 里怎么用

```gdscript
var frames := SpriteFrames.new()
frames.add_animation("walk")
frames.set_animation_speed("walk", 8.0)
frames.set_animation_loop("walk", true)
for i in 8:
    frames.add_frame("walk", load("res://assets/characters/cockroach/export/cockroach_walk_%02d.png" % i))

var roach := AnimatedSprite2D.new()
roach.sprite_frames = frames
roach.centered = true
roach.play("walk")
```

爬向不同方向时**不要直接 flip_h**：这张图是"头朝下"的固定朝向，左右翻转只会让它在原地扭。要往左/右/上爬，直接用 `rotation` 转（贴地小怪一般是 `rotation = 0` 往下爬、`rotation = PI` 往上爬），或者按你的移动方向设 `roach.rotation = velocity.angle() - PI/2`。

## 备注

- 触角末端是故意被画布下沿切掉的（"从画面下方伸进来"），所以别把这张图放进会裁边的大图集里再二次对齐，容易把触角切得更短
- 身体没有画影子：贴地物件建议在场景里放一个单独的阴影 sprite 或 `Light2D` 遮挡，这样换地面材质时不用重画
- `status` 还是 `wip`：后续想加 `dead`（翻肚）或 `scurry`（突然加速）状态的话，`dead` 单独画一帧就够，`scurry` 可以直接把 `walk` 的 fps 提到 16

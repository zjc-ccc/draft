# Draft 素材规范（现行）

> 本文件只记录已核实的现状与本次固化的约定，适用于 `e:\app_ideas\godot-game\Draft` 下全部素材。日期：2026-11-04。

## 1. 目录与命名

- 本库分两层：`Draft/draft2d/`（像素 2D 素材）、`Draft/draft3d/`（3D 素材）；层内一个素材一个文件夹、扁平存放，不再加分类层，即 `Draft/draft2d/<type>_<subject>[_<variant>]/`、`Draft/draft3d/<type>_<subject>[_<variant>]/`。
- 每个素材文件夹固定两层：`src/` 放 Aseprite 等源文件，`export/` 放交付给 Godot 的 PNG/JSON；源文件不被 Godot 直接引用。
- 源文件与导出文件同名：`<asset>.aseprite` → `<asset>.png`；动画单帧补两位序号 `<asset>_00.png`。
- 图集固定 `<asset>_sheet.png` + `<asset>_sheet.json`；多挡位、多变体用后缀区分（`_low/_medium/_high`、`_a~_e`、`_glass`）。
- 类型前缀：`chr` 角色、`env` 场景、`prop` 固定陈设、`item` 可拾取物/道具、`ui` 界面、`fx` 特效、`sfx` 音效、`bgm` 音乐、`font` 字体。
- 文件夹名全小写 snake_case、仅 ASCII、无空格；变体用 `_a/_b`，序列用两位补零（`chr_slime_01`）。
- 现存反例：`prop_pendant_lamp` 的 PNG 仍为旧名 `_up/_down`（规范方向后缀为 `_u/_d`）；`prop_wooden_door` 单帧名 `_open/_closed` 与 tag 名 `open/close` 词形不一致。为避免破坏引用，本次只改 JSON tag，未重命名 PNG。

## 2. 画布与像素风格

- 源文件均为 32bpp RGBA。现有画布尺寸：32×32、32×48、48×80、64×64、64×96、64×112、96×96、128×96、128×128。
- 像素画硬边，无抗锯齿；逐张 PNG 核对后，半透明像素只出现在玻璃杯（约 780~802 像素/帧）、吊灯亮灯帧（约 489~503）、沙发投影（533）和吊扇中/高挡残影（7049 / 14102）；其余素材只有完全不透明或完全透明像素。
- 统一使用深色 1px 描边，主体按材质做 4~6 级明暗 ramp。
- 每帧尺寸恒定、不裁剪：所有 JSON 均 `trimmed=false`、`rotated=false`、`sourceSize == frame`。
- 本库没有定义锚点字段；因为每帧等大且图集为等距单行，实际锚点等价于**整幅画布居中**（`portal-gate` 中树枝也用默认居中的 `Sprite2D`）。

## 3. 状态词表（本次固化）

- 通用状态：`idle / on / off / open / close / full / half / empty / low / medium / high`。
- 方向后缀：`_u / _d / _l / _r`（上下左右），禁止 `_up/_down/_left/_right` 写法。
- 组合顺序：`<asset>_<state>_<direction>`（如 `prop_pendant_lamp_off_u.png`）；单帧序列仍用两位序号。
- 本次按上述口径新建了 `prop_pendant_lamp_sheet.json` 的 tag：`off_u / off_d / on_u / on_d`；对应 PNG 文件名保持旧名未动。

## 4. 图集与 JSON

- 图集一律单行横向拼接，帧间距等于帧宽，无留白。
- JSON 使用 Aseprite array 格式，字段固定：
  - `frames[]`：`filename`、`frame{x,y,w,h}`、`rotated`、`trimmed`、`spriteSourceSize`、`sourceSize`、`duration`（毫秒）。
  - `meta`：`app`、`version`、`image`、`format`（RGBA8888）、`size`、`scale`，可选 `frameTags`。
  - `frameTags[]`：`name`、`from`、`to`、`direction`、`color`。
- `meta.size` 必须等于实际图集的像素尺寸，且最后一帧 `x + w == meta.size.w`。
- 一个图集可含多个 tag，但任何 tag 的 `from/to` 必须落在 `0 .. frames.Count-1` 内；拆分导出成独立图集时，tag 区间要**重映射到 0 基**（如 `medium` 独立图集为 `0-11`，不是 `12-23`）。
- 状态切换与关门/收拢等反向播放交给引擎（`AnimatedSprite2D` 反向播放或按 tag 区间播放），JSON 只描述正向序列。
- 所有 tag 的 `direction` 现状均为 `forward`；不使用 `pingpong`。

## 5. Godot 接入现状

- `Draft` 不是 Godot 工程（无 `project.godot/.tscn/.import`），PNG 目前只在 `portal-gate` 中镜像了 `item_branch` 一组。
- `draft2d/godot_spriteframes/` 每件动画素材一个 `.tres`；`ext_resource` 路径按 `Draft` 作为工程根写成 `res://draft2d/<asset>/export/<file>.png`，若放入其他工程需改前缀。
- `.tres` 用 `AtlasTexture` 区域切帧，不复制、不改写 PNG；动画名与 JSON `frameTags` 一致，帧时长取 JSON 的毫秒值换算为秒（`speed=1.0`）。
- 只给有帧序列/状态帧的素材生成 `.tres`；`item_stick`、`item_vine`、`item_spiked_stick`、`item_spiked_stick_long`、`prop_sofa` 以及 `item_branch` 的 5 个变体是单张静态图，没有帧数据，直接用 `Sprite2D` 加载即可，未生成 `.tres`。

## 6. 已知偏差与待办

- `item_water_cup` 一个文件夹装了塑料杯、玻璃杯两个独立素材（2 个源、2 套图集/JSON），与“一素材一文件夹”不符；建议后续拆为 `item_water_cup_plastic`、`item_water_cup_glass`。
- `item_branch` 源文件含通用图层 `Layer 1`，与其他素材的语义化图层命名不一致。
- 木色 ramp 不统一：`item_branch` 为 5 色（`#2E1E12 #6B4423 #8C5A2B #B77B3F #D9A45F`），`item_stick` 系为 7 色（`#3E2A18 #94663A #9A6E3C #C08E4E #DEB274 #E9CD94 #F0D39A`）。
- 全库仍缺 `notes.md`；尺寸、帧率、锚点目前只能从 JSON 的 `duration` 与画布推断。
- `prop_ceiling_fan` 只有三张 12 帧挡位图集，没有单帧 PNG；`prop_wooden_door` 单帧只有 `open/closed` 两端点。
- `env_pond`、`prop_elevator` 的 JSON 没有 `frameTags`，动画名在 `.tres` 中统一用 `default`。

## 7. 资产清单（2026-11-04 新增批次）

| 资产 | 类型 | 画布 | 帧 | tag | 说明 |
| --- | --- | --- | --- | --- | --- |
| `prop_coffee_table` | 静态 | 96×96 | 1 | — | 室内茶几，复用 `item_stick` 的 7 色木 ramp，锚点画布居中 |
| `env_stump` | 静态 | 64×64 | 1 | — | 野外木桩，同木 ramp + 藤绿系苔藓，锚点画布居中 |
| `fx_ripple` | 循环特效 | 32×32 | 8（120ms） | `loop` 0-7 | 水面涟漪，叠加在 `env_pond` 之上；`loop` 为特效循环语义，未收录进 §3 状态词表 |

- 三条均建 `src/` + `export/` 两层，并附 `notes.md`；`fx_ripple` 另在 `godot_spriteframes/` 生成 `.tres`（`loop = true`）。

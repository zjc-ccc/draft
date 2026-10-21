# 素材规范

这套规范的目标只有三个：**找得到**、**能复用**、**不把仓库搞乱**。

## 1. 一个素材一个文件夹

```
assets/<分类>/<素材名>/
```

素材名是唯一的，分类只是为了让列表好看。判断标准：如果两样东西需要分别导出给游戏用，它们就是两个素材。

| 目录/文件 | 放什么 | 会不会进游戏 |
| --- | --- | --- |
| `source/` | `.aseprite` / `.psd` / `.kra` 可编辑源文件 | 否 |
| `export/` | 最终 PNG（透明背景） | 是 |
| `preview.png` | 缩略图，给 INDEX 和 GitHub 页面看 | 否 |
| `archive/` | 废弃稿、旧版本、实验稿 | 否 |

`source/` 和 `export/` 一定要分开：源文件以后还要改，导出图随时可以重新生成；混在一起时间长了就分不清哪个是用来交付的。

## 2. 分类

默认六个，不够就加，但**保持扁平**（`assets/分类/素材名`，不要再套一层）：

| 分类 | 内容 |
| --- | --- |
| `characters` | 角色、NPC、怪物（含动画帧） |
| `props` | 场景道具、可交互物件、武器 |
| `tiles` | 地图图块、地形、装饰拼图 |
| `ui` | 按钮、面板、图标、血条 |
| `backgrounds` | 背景、远景、视差层 |
| `vfx` | 特效帧、光效、粒子贴图 |

## 3. 命名

- 素材名：小写英文 + 连字符，`^[a-z0-9]+(-[a-z0-9]+)*$`，例如 `slime`、`wooden-door`。
- 不用中文、空格、大写、下划线（Godot 能处理，但跨平台和命令行容易出问题）。
- 同类多个素材加两位编号：`stone-wall-01`、`stone-wall-02`。
- 同一素材的多套尺寸/版本，加后缀而不是建新目录：`slime` → `slime_32x32` 放在导出文件名里，或直接用 `-v2` 建新素材。
- 帧号两位补零：`_00`、`_01` … `_10`，保证文件排序正确。

导出文件命名：

| 类型 | 命名 |
| --- | --- |
| 单张 | `<素材名>.png` |
| 动画帧 | `<素材名>_<状态>_<两位帧号>.png` |
| 图集 | `<素材名>_<状态>_sheet.png` |
| 变体 | `<素材名>_<状态>_<两位帧号>_<变体>.png` |

例：`slime_idle_00.png`、`slime_walk_03.png`、`slime_walk_sheet.png`。

## 4. 元数据

每个素材的 `README.md` 开头是一段 YAML front matter，脚本和索引都读它：

```yaml
---
id: slime
category: characters
status: wip
size: 32x32
frames: 4
fps: 8
palette: slime-4c
license: own
author: zjc-ccc
created: 2026-10-21
tags: 史莱姆, 敌人, 低像素
---
```

| 字段 | 说明 |
| --- | --- |
| `id` | 必须和文件夹名一致 |
| `category` | 必须和上级目录名一致 |
| `status` | `idea` / `wip` / `review` / `done` / `dropped` |
| `size` | 单帧画布尺寸，如 `32x32` |
| `frames` | 总帧数 |
| `fps` | 动画帧率（静帧写 0） |
| `palette` | 使用的调色板名称（可选） |
| `license` | `own` / `cc0` / `cc-by` / `third-party` |
| `author` | 作者 |
| `created` | 创建日期，`YYYY-MM-DD` |
| `tags` | 逗号分隔，方便搜索 |

字段值不要加引号（脚本按纯文本读），需要冒号的内容换成 `-`。

## 5. 状态流转

`idea` → `wip` → `review` → `done`，放弃就标 `dropped`。

- `done` 才算可复用：导出完整、README 补齐、能在游戏里直接用。
- 改一个已 `done` 的素材，先把旧导出移到 `archive/`，再更新 `export/`。
- 不确定要不要的素材，放 `_scratch/`（已被 gitignore），确定了再搬进 `assets/`。

## 6. 绘制与导出

- 画布从 `16x16` / `32x32` / `48x48` / `64x64` 开始，先定尺寸再画，避免后期缩放糊掉。
- 导出用 **PNG、透明背景、1:1 原始尺寸**，不要放大或压缩。
- 像素画导出用最近邻缩放（Aseprite 导出时不要开滤镜）。
- 动画帧统一锚点（例如底部居中），并在 README 里写清楚，接进游戏才不会跳。
- 需要图集时额外导出一份 `_sheet.png`，但单帧文件保留，方便单独调整。

## 7. Git

- 一次提交一个素材：`添加素材：slime`（源文件 + 导出 + README 一起）。
- 修改已交付素材：`修改素材：slime - 走路帧补齐`。
- 单文件超过 50 MB 用 LFS：`.psd`、`.psb`、`.kra`。超过 100 MB 的文件 GitHub 直接拒收。
- `.godot/`、`*.import`、导出配置、绘制软件的备份文件都已经在 `.gitignore` 里，不要强行提交。

## 8. 第三方素材

- 来源不是自己画的，`license` 必须写明，并在根目录 [SOURCES.md](../SOURCES.md) 登记来源和授权。
- **不允许再分发的素材不要进这个仓库**（仓库是公开的）。多数付费素材包都禁止再分发，买了就本地存着，别推上来。

## 9. 常用命令

```powershell
# 新建素材
.\tools\new-asset.ps1 -Id slime -Category characters

# 查看当前素材清单
.\tools\build-index.ps1

# 提交
git add -A
git commit -m "添加素材：slime"
git push
```

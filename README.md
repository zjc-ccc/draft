# Draft · 游戏素材库

我绘制游戏素材的工作目录。**一个素材一个文件夹**：源文件、导出文件、元数据都放在素材自己的目录里，互不干扰。

## 目录结构

```
assets/
└── <分类>/<素材名>/
    ├── README.md      元数据 + 说明（由模板生成）
    ├── source/        可编辑源文件（.aseprite / .psd / .kra）
    ├── export/        交付给 Godot 的 PNG
    ├── preview/       简化版：物品栏图标（每个素材默认必带）
    └── archive/       可选，废弃稿 / 旧版本
```

默认分类（可以自己加）：`characters` `props` `tiles` `ui` `backgrounds` `vfx`

## 新建素材

```powershell
.\tools\new-asset.ps1 -Id slime -Category characters
```

会生成 `assets/characters/slime/`，带好 `source/`、`export/` 和填好日期的 `README.md`。

## 重建索引

```powershell
.\tools\build-index.ps1
```

扫描所有素材的 README，重新生成 [INDEX.md](INDEX.md)（素材清单 + 状态 + 导出数量），并检查命名和元数据是否规范。

## 预览

用 Godot 4.6 打开 `preview/project.godot`，按 F5。左边选分类和素材，右边看图和播放动画；素材改完点「重新扫描」即可，不需要复制素材。

左下角的「试玩（WASD 控制蟑螂）」会进一个可操作的小房间：WASD / 方向键移动，Esc 返回。预制体在 `preview/prefabs/`。

细节见 [preview/README.md](preview/README.md)。

## 三条核心约定

1. **素材名用英文 kebab-case**：`wooden-door`、`slime`，不用中文、空格、大写。
2. **源文件与导出分离**：`source/` 只放可编辑源文件，`export/` 只放最终 PNG。游戏只导入 `export/`。
3. **每个素材都要有简化图标**：`preview/<素材名>_icon_32.png`，给物品栏、背包列表这种小尺寸界面用。
4. **一个提交一个素材**：素材说明和源文件、导出图一起提交，历史清晰。

导出帧命名：`<素材名>_<状态>_<两位帧号>.png`，例如 `slime_idle_00.png`。

完整规范见 [docs/asset-guide.md](docs/asset-guide.md)，第三方素材登记见 [SOURCES.md](SOURCES.md)。

## 大文件（可选）

```powershell
git lfs install
git lfs track "*.psd" "*.kra" "*.psb"
```

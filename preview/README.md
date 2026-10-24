# 素材预览工程

用 Godot 4.6 打开这个目录（`preview/project.godot`），按 F5 运行。

它**不存放素材**，运行时直接读取 `../assets/`，所以素材改完点一下「重新扫描」就能看到，不用复制或导入。

## 功能

- 左侧按分类列出全部素材
- 右侧显示 `export/` 里的 PNG
- 文件名符合 `<素材名>_<状态>_<两位帧号>.png` 时自动识别状态，右上角可切换，多帧会自动循环播放
- 播放帧率取素材 `README.md` 的 `fps` 字段，没填就按 8 fps
- `preview/` 里的简化图标会在右上角多出一个「图标」选项
- `export/` 和 `preview/` 都为空时，右侧留空
- 左下角「试玩（WASD 控制蟑螂）」会切到 `play.tscn`，可以真的用键盘驱动一只蟑螂

## 试玩场景

```
preview/
├── play.tscn / play.gd        试玩房间（地板、墙、跟随相机、HUD）
└── prefabs/
    ├── cockroach.tscn         CharacterBody2D + AnimatedSprite2D + 碰撞胶囊
    └── cockroach.gd           读取 8 帧、WASD 移动 + 按方向转向
```

- **操作**：`WASD` 或方向键移动，`Esc` 返回素材预览
- **帧图来源**：运行时从 `../assets/characters/cockroach/export/` 直接读 PNG，素材重画后重开试玩就生效，不用重新导入
- **朝向**：蟑螂是「头朝下」画的，脚本用 `rotation = 方向角 - 90°` 转向，**没有用 `flip_h`**
- **输入**：`move_left/right/up/down` 在 `cockroach.gd` 的 `_ensure_actions()` 里运行时注册；如果工程里已经手动配了同名 action，就不会覆盖
- **参数**：速度、加速度、刹车、转向速度、帧率都做成 `@export`，在检查器里能直接调

单独运行试玩场景：在 Godot 里打开 `play.tscn` 按 F6。

## 注意

- 素材本体永远留在 `assets/`，不要往这里放。
- 第一次用编辑器打开会生成 `.godot/`，已经被 gitignore。
- 这个工程只在编辑器/桌面运行；导出成游戏时读不到外部目录，也不需要导出。

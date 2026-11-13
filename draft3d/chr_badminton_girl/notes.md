# chr_badminton_girl — 羽毛球社团少女

Blender 5.2 程序化建模 + 2D 设定图投影贴图，羽球类第三人称游戏用。

## 文件

| 路径 | 内容 |
|---|---|
| `src/chr_badminton_girl.blend` | Blender 工程（独立场景 `chr_badminton_girl`，未改动原校园场景） |
| `src/ref_turnaround.jpg` | AI 生成的角色设定三视图（正 / 侧 / 背），贴图来源 |
| `src/head_crop.png` | 头部裁剪图，用于校准脸部投影坐标 |
| `export/chr_badminton_girl.glb` | 游戏用模型，含骨骼、蒙皮与脸部贴图，无动画 |
| `export/preview*.png` | 预览图（正 / 三分之四 / 背） |
| `export/face_closeup.png` | 面部特写 |
| `godotdemo/` | Godot 4.6 预览工程（环绕相机 + 三点布光） |

## 规格

- 身高 168 cm，7.5 头身，脚底对齐 z = 0，面朝 -Y（Godot 中为 -Z 前方）
- A-Pose 初始姿态，顶点 6879，9 个材质、1 张贴图（打包进 glb，861 KB）
- 9 个材质：肤色、脸部贴图、红发、白校服、金色校徽、白鞋、灰鞋底、藏青裙、白袜

## 贴图方案

脸部不是平面贴图，而是**把设定图正视图的脸按像素投影到头部网格**：

- 横向比例 1065 px/m，以脸部中心 x=611 为基准
- 纵向比例 531 px/m，以下巴 y=1165 为基准
- 只对 z > 1.428 的头部多边形赋 UV，其余仍用纯色肤色材质

这样投影跟随头部曲面，比整体投影稳定，也避免了四肢姿态差异导致的错位。
裙子原本也做了投影，但因为模型裙摆比设定图宽，UV 溢出到白底，已回退为纯色。

## 动画（24 fps，4 段）

| 动作 | 帧范围 | 循环 | 说明 |
|---|---|---|---|
| `idle` | 1–48 | 是 | 呼吸起伏、头部微动、发梢摆动 |
| `run` | 1–25 | 是 | 24 帧一个完整步循环，含躯干前倾、重心起伏 |
| `jump` | 1–36 | 否 | 下蹲→蹬地→滞空（双臂举过头顶）→落地缓冲→复位 |
| `wave` | 1–44 | 否 | 右臂抬至体侧、小臂竖直，来回挥动 3 次后放下 |

每段动作在第 1 帧都给全部 61 根骨打了基础关键帧，切换动作时不会残留上一个动作的姿态。
`run` 的首尾帧姿态一致，可无缝循环；`jump` 的实际位移交给游戏物理，动画只做下蹲与滞空姿态。

## 骨架（61 根）

- 躯干：`Hips / Spine / Chest / Neck / Head`
- 胸部辅助骨：`Breast.L / Breast.R`
- 手臂：`Shoulder / UpperArm / LowerArm / Hand`
- 手指（每侧 14 根）：`Index / Middle / Ring / Pinky` 各 3 节 + `Thumb` 2 节
- 腿脚：`UpperLeg / LowerLeg / Foot / Toe`
- 头发：`HairTail1~3.L / HairTail1~3.R`（马尾已加长至臀部，末端半径收细）
- 裙摆：`SkirtF / SkirtB / SkirtL / SkirtR`

## 蒙皮策略

- `CHR_Body`、`CHR_Shirt`：自动权重（骨骼热扩散）
- `CHR_HairHead`：刚性绑定 `Head`
- `CHR_HairTail_*`：按到三节发骨的距离加权
- `CHR_Skirt`：腰部权重给 `Hips`，下摆按方位角分配给四根裙摆骨
- `CHR_Sock_*`：按高度在 `UpperLeg` / `LowerLeg` / `Foot` 之间过渡
- `CHR_Shoe_*`、`Cloth_Shorts`、`CHR_SkirtBand2`、`Cloth_Collar2`：刚性绑定

## 已知限制

- 脸部贴图是正视图平面投影，转到 3/4 侧脸时边缘会被拉伸
- 头发仍是整块几何，没有发束分层，近看偏"塑料"
- 动画为关键帧手摆，没有动作捕捉数据，跑动时手脚幅度偏保守
- 未附羽毛球拍；建议新建 `prop_racket` 素材，按局部坐标偏移挂到 `Hand.R`

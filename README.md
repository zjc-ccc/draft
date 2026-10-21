# Draft — 个人素材库

存放个人美术、音频、字体、Shader、参考图等素材的仓库（不包含完整游戏工程）。

## 建议的目录约定

```
draft/
├── 2d/            贴图、精灵、UI 素材
├── 3d/            模型、贴图、HDRI
├── audio/         音效与音乐
├── fonts/         字体文件
├── shaders/       Shader 与材质参考
├── refs/          参考图、灵感收集
└── tools/         自己写的小工具/脚本
```

目录可以按需增删，保持「一类素材一个目录」即可。

## 素材使用约定

- 每个素材目录放一个 `SOURCES.md`，记录来源、授权（CC0 / 购买 / 自制）和原始链接。
- 文件名用英文 + 连字符，避免空格和特殊字符，跨平台、跨工具更安全。
- 大文件（PSD、BLEND、EXR、FBX、WAV 等）单个不要超过 100 MB，超过请用 Git LFS。

## 大文件（可选）

```bash
git lfs install
git lfs track "*.psd" "*.blend" "*.exr" "*.fbx" "*.wav"
git add .gitattributes
```

## 提交

```bash
git add -A
git commit -m "添加素材：xxx"
git push
```

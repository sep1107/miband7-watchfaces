# Xiaomi Smart Band 10 Pro 表盘开发目录

本目录用于开发 TIME FLIES 的 Xiaomi Smart Band 10 Pro 版本。

## v0.6.0 目标策略

项目提供两个可切换目标：

```text
主要候选：compat-336x480
实验候选：experimental-400x480
```

`336 × 480` 的依据来自公开的 Mi Band 9 Pro 真机验证项目：作者使用 MiCreate `.fprj` 工程、`336 × 480` 示例图和 Mi Band 8 Pro 目标生成 `.face` 文件，并在 Mi Band 9 Pro 上测试。它不能直接证明 10 Pro 一定兼容，但比单纯媒体规格更接近真实 Pro 表盘工具链。

## 目录

```text
miband10pro/
├── README.md
├── reference/
│   ├── amazfit-band7/
│   └── mi-band-9-pro/
├── project/
│   ├── README.md
│   ├── COMPILER_RESEARCH.md
│   ├── TARGET_RESEARCH.md
│   ├── required-assets.json
│   ├── targets/
│   └── device/
└── tools/
    ├── prepare_assets.py
    ├── validate_project.py
    ├── build_app_json.py
    └── apply_target_profile.py
```

## 当前状态

- 默认开发画布已切换为 `336 × 480`。
- 保留 `400 × 480` 实验配置，可一条命令切换。
- 已接入图片时间、日期、星期、天气、步数、心率、电量与节日。
- 已整理并验证 157 个 RGBA PNG 资源。
- 尚未获得可确认的 10 Pro `deviceSource`、官方编译配置或真机测试。
- 当前项目还不是可安装成品。

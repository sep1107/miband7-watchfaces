# 小米手环 NFC 自制表盘

这个仓库用于整理和维护小米手环 NFC 自制表盘资源。

## 下载表盘

成品 `.bin` 文件放在 GitHub Releases 中，主分支不保存可安装成品文件。

- Release：`v1.0.0`
- 下载页面：https://github.com/sep1107/miband-watchfaces/releases/tag/v1.0.0

| 文件 | 说明 |
| --- | --- |
| `miband7.bin` | 小米手环 7 NFC 原始表盘 |

## 仓库结构

```text
miband-watchfaces/
├── README.md
├── .github/workflows/
│   ├── validate-watchface.yml
│   └── validate-band10pro.yml
└── source/
    ├── README.md
    ├── app.json
    ├── app.bin
    └── miband10pro/
        ├── README.md
        ├── MICREATE_FORMAT.md
        ├── micreate-probe/
        ├── reference/
        │   └── real-device/
        │       └── M2551B1.json
        ├── project/
        │   ├── PACKAGE_INSPECTION.md
        │   └── targets/
        └── tools/
            └── inspect_watchface_package.py
```

## Xiaomi Smart Band 10 Pro 开发状态

当前研究版本为 `v0.7.2`。用户提供的实机照片已经确认：

```text
设备：小米手环10 Pro
型号：M2551B1
系统：Xiaomi HyperOS
OS 版本：3.101.030
```

原始照片不提交到仓库，只保存非敏感设备事实。

项目对候选目标采用三类独立证据：

- 屏幕或画布硬件证据。
- 编辑器与编译链证据。
- Smart Band 10 Pro 真机目标证据。

当前候选：

- `compat-336x480`：Mi Band 8/9 Pro 的 MiCreate 构建链参考更强，实机屏幕比例也提供视觉支持，但不是 10 Pro 安装证明。
- `experimental-400x480`：对应发布前报道的面板参数，但没有公开编译器目标或包元数据。

目前源码已实现图片时间、日期、星期、天气、步数、心率、电量和节日信息，并加入：

- target profile schema
- profile 几何与证据校验
- 目标配置切换
- 项目与资源校验
- `app.json` 生成器
- GitHub Actions 自动检查全部候选 profile
- MiCreate `.fprj` 格式探针
- 递归表盘包检查器，可读取 ZIP、嵌套 `.zpk`、JSON/XML、PNG/TGA 和设备标识
- 真实设备记录 `M2551B1.json`

下一关键步骤是从这台实机配套的 Mi Fitness 中取得一个原厂或第三方表盘包。拿到后即可检查真实画布、`deviceSource`、`DeviceType` 和包格式。

当前项目仍是研究与开发源码，不是可安装成品。

## 文件信息

- `miband7.bin`：约 209 KB
- SHA-256：`8caf6df2d77a6829545ddfbe3ec6ff8f9e380e2bfebdaeb76dcb1a75352df1e4`

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
└── source/
    ├── README.md
    ├── app.json
    ├── app.bin
    └── miband10pro/
        ├── README.md
        ├── reference/
        │   └── amazfit-band7/
        ├── project/
        └── tools/
```

- `source/app.json`、`source/app.bin`：原 TIME FLIES 表盘保留下来的核心配置和编译组件。
- `source/miband10pro/reference/`：保存拆出的 Zepp OS 参考工程。
- `source/miband10pro/project/`：Xiaomi Smart Band 10 Pro 表盘开发工程。
- `source/miband10pro/tools/`：资源转换与构建辅助工具。

## Xiaomi Smart Band 10 Pro 开发状态

本项目按你指定的 Xiaomi Smart Band 10 Pro 作为目标设备继续开发。由于尚未获得可核实的正式 SDK、`deviceSource` 和编译配置，当前开发画布暂用 `400 × 480`，并保留切换为其他方向或尺寸的能力。

目前源码已接入时间、日期、步数、心率、电量和节日信息；TIME FLIES 图片资源已开始按宽屏双栏布局迁移。

## 使用说明

1. 打开 Releases 页面。
2. 下载对应设备的 `.bin` 文件。
3. 使用支持该设备和包格式的工具进行安装。
4. 安装前建议先备份原表盘文件。

## 文件信息

- `miband7.bin`：约 209 KB
- SHA-256：`8caf6df2d77a6829545ddfbe3ec6ff8f9e380e2bfebdaeb76dcb1a75352df1e4`

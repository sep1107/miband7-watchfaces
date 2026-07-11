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
├── .github/workflows/validate-watchface.yml
└── source/
    ├── README.md
    ├── app.json
    ├── app.bin
    └── miband10pro/
        ├── README.md
        ├── reference/
        │   ├── amazfit-band7/
        │   └── mi-band-9-pro/
        ├── project/
        │   └── targets/
        └── tools/
```

## Xiaomi Smart Band 10 Pro 开发状态

当前开发版本为 `v0.6.0`。项目不再把媒体报道的 `400 × 480` 当成唯一默认值，而是采用双目标配置：

- `compat-336x480`：主要兼容候选，依据是真机验证过的 Mi Band 9 Pro MiCreate 工程。
- `experimental-400x480`：保留用于对比媒体报道中的面板参数。

目前源码已实现图片时间、日期、星期、天气、步数、心率、电量和节日信息，并加入目标配置切换、项目校验和 GitHub Actions 自动检查。

> 仍未获得 Smart Band 10 Pro 的正式 SDK、`deviceSource`、官方表盘包或真机验证，因此当前项目是研究与开发源码，不是可安装成品。

## 文件信息

- `miband7.bin`：约 209 KB
- SHA-256：`8caf6df2d77a6829545ddfbe3ec6ff8f9e380e2bfebdaeb76dcb1a75352df1e4`

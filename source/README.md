# Source

这个目录保存表盘开发相关的配置、编译组件和适配工程。

## 目录说明

```text
source/
├── README.md
├── app.json
├── app.bin
└── miband10plus/
    ├── README.md
    ├── reference/
    │   └── amazfit-band7/
    └── project/
```

- `app.json`：原 TIME FLIES 表盘保留的核心配置。
- `app.bin`：原 TIME FLIES 表盘保留的编译组件。
- `miband10plus/reference/`：拆出的参考工程，尽量保持原始代码和配置。
- `miband10plus/project/`：正在开发的 Mi Band 10 适配工程。

## 注意

`source/app.json` 和 `source/app.bin` 并不是完整可重新编译的原工程。Mi Band 10 适配会结合原 TIME FLIES 图片资源、参考工程 API 结构和新的 212 × 520 布局重新建立。

可安装成品继续从 GitHub Releases 下载。

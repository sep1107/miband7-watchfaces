# Source

这个目录保存表盘开发相关的配置、编译组件和适配工程。

## 目录说明

```text
source/
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

- `app.json`：原 TIME FLIES 表盘保留的核心配置。
- `app.bin`：原 TIME FLIES 表盘保留的编译组件。
- `miband10pro/reference/`：拆出的 Zepp OS 参考工程。
- `miband10pro/project/`：Xiaomi Smart Band 10 Pro 适配工程。
- `miband10pro/tools/`：资源转换与构建辅助工具。

## 注意

`source/app.json` 和 `source/app.bin` 不是完整可重新编译的原工程。Smart Band 10 Pro 版本会结合原 TIME FLIES 图片资源、参考工程 API 结构和新的宽屏布局重新建立。

当前画布暂按 `400 × 480` 纵向处理；如果正式 SDK 使用 `480 × 400` 横向坐标，可通过统一画布常量和资源转换脚本调整。

可安装成品继续从 GitHub Releases 下载。

# Source

这个目录保存表盘开发配置、编译组件和适配工程。

```text
source/
├── README.md
├── app.json
├── app.bin
└── miband10pro/
    ├── reference/real-device/P67-baseline/
    ├── project/targets/p67-336x480.json
    └── tools/extract_p67_profile.py
```

- `app.json`、`app.bin`：原 TIME FLIES 表盘保留的核心文件，不是 Smart Band 10 Pro 的 P67 编译输入。
- `miband10pro/reference/real-device/`：真实 M2551B1 设备信息和脱敏 P67 包基准。
- `miband10pro/project/`：336×480 布局原型、P67 目标 profile 和格式研究。
- `miband10pro/tools/`：资源处理、P67 元数据提取、项目校验和包检查工具。

Smart Band 10 Pro 的唯一正式目标为 `P67 / vela / 336×480 / BIN`。

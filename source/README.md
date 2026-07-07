# Source

这个目录用于存放表盘原始资源中的核心配置与编译组件。

整理规则：

- 原始压缩包里的 `7677/` 外层目录不保留。
- `7677.bin` 不上传；成品表盘按设备放在 `watchfaces/` 目录下。
- `__MACOSX/` 不上传。
- `app.json` 已精简为 watchface-only 配置，只保留实际需要的 `watchface` 模块。
- 已删除原配置里没有对应源码目录的 `page`、`app-widget`、`app-side`、`setting` 等模块引用。

说明：

- 仓库中的可安装成品表盘以 `watchfaces/*.bin` 为准。
- `source/` 用于后续适配和整理原始资源。

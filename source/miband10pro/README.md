# Xiaomi Smart Band 10 Pro 表盘开发目录

本目录用于开发 TIME FLIES 的 Xiaomi Smart Band 10 Pro 版本。

## 目标设备

当前公开资料显示 Smart Band 10 Pro 使用 1.74 英寸 AMOLED 屏幕，面板分辨率通常写作 `480 × 400`。本工程暂按表盘坐标：

```text
width: 400
height: 480
```

最终画布方向、`deviceSource`、编译器配置和安装包格式仍需等待正式 SDK、可用编译器配置或真机验证。

## 目录

```text
miband10pro/
├── README.md
├── reference/
│   └── amazfit-band7/
├── project/
│   ├── README.md
│   ├── ASSET_INVENTORY.md
│   └── device/
└── tools/
    └── prepare_assets.py
```

## 设计策略

原 TIME FLIES 画布是 `192 × 490`，而 10 Pro 的屏幕明显更宽。资源不能直接横向拉伸到 400 像素，否则数字和图标会严重变形。

当前采用：

1. 保持时间数字和状态图标宽高比。
2. 将主时间放在左侧大区域。
3. 将日期、步数、心率、电量放到右侧数据栏。
4. 背景单独重做或使用裁切、留黑方式扩展。
5. 最后根据真实设备圆角和安全区域微调。

## 当前状态

- 已建立 400 × 480 代码骨架。
- 已接入时间、日期、步数、心率、电量与节日数据。
- 已整理原 TIME FLIES 资源清单。
- 尚未获得可确认的 10 Pro `deviceSource` 和正式编译配置。
- 当前项目还不是可安装成品。

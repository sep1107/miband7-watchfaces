# Xiaomi Smart Band 10 Pro 表盘开发目录

本目录用于开发 TIME FLIES 的 Xiaomi Smart Band 10 Pro 版本。

## 目标设备

按你指定的 Smart Band 10 Pro 继续开发。由于目前尚未获得可核实的正式 SDK、平台 ID、编译配置和真机信息，本工程先使用下面的暂定画布：

```text
width: 400
height: 480
```

这个尺寸仅用于当前布局和素材迁移，不代表已经确认的最终设备规格。代码把屏幕尺寸集中定义在文件开头，后续可以整体切换画布方向和坐标。

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

原 TIME FLIES 画布是 `192 × 490`。当前 10 Pro 暂定画布更宽，因此资源不能直接横向拉伸，否则数字和图标会严重变形。

当前采用：

1. 保持时间数字和状态图标宽高比。
2. 将主时间放在左侧大区域。
3. 将日期、步数、心率、电量放到右侧数据栏。
4. 背景使用等比例缩放并扩展画布。
5. 最后根据正式 SDK、模拟器或真机的安全区域微调。

## 当前状态

- 已建立暂定 400 × 480 代码骨架。
- 已接入时间、日期、步数、心率、电量与节日数据。
- 已整理原 TIME FLIES 的 157 个资源。
- 已生成第一版 400 × 480 开发素材包。
- 尚未获得可确认的 10 Pro `deviceSource` 和正式编译配置。
- 当前项目还不是可安装成品。

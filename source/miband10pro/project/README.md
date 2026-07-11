# TIME FLIES — Xiaomi Smart Band 10 Pro P67 project

## v0.8.0 目标

项目唯一正式目标是：

```text
M2551B1 / P67 / vela / 336x480 / XMHD03 / BIN
```

这一结论来自真实设备和 Mi Fitness 表盘缓存，而不是媒体规格或相关型号推断。

## 已验证的官方包结构

```text
capability.json
├── protocol = 1.9.4
├── resolution = XMHD03
├── region = CN
└── packet = BIN

description.xml
├── deviceType = P67
├── size = 336x480
├── watchOS = vela
├── imageFormat = indexed8
└── imageCompression = true

manifest.xml
├── width = 336
├── height = 480
├── compressMethod = RLEReversed
└── editable = true

resource.bin
├── magic = 0x1234A55A
├── embedded package ID = 120917384229
└── theme count = 3
```

## 当前代码定位

`device/` 下的 JavaScript 工程是布局和数据展示原型，不是 P67 编译器输入。P67 工作集中在：

- `targets/p67-336x480.json`
- `REAL_DEVICE_PACKAGE.md`
- `../reference/real-device/P67-baseline/`
- `../tools/extract_p67_profile.py`
- `../tools/validate_target_profiles.py`

## 下一里程碑

1. 完整解析 `resource.bin` 的主题表、记录表和资源地址；
2. 将 TIME FLIES 素材转换为 `indexed8`；
3. 实现 `RLEReversed` 编码；
4. 生成最小单主题 P67 BIN；
5. 在 M2551B1 真机上测试安装。

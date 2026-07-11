# Xiaomi Smart Band 10 Pro 表盘开发目录

## v0.8.0：P67 真机包目标已确认

真实 M2551B1 设备与 Mi Fitness 缓存共同确认：

```text
Device type: P67
Watch OS: vela
Canvas: 336x480
Resolution code: XMHD03
Packet: BIN
Capability protocol: 1.9.4
Image format: indexed8
Compression: RLEReversed
```

非敏感事实记录在 `reference/real-device/M2551B1.json`，脱敏包基准位于 `reference/real-device/P67-baseline/`。原始照片、账号数据、日志、官方图片和原始 `resource.bin` 不进入仓库。

## 路线

```text
TIME FLIES 素材
    ↓
P67 manifest / data source / UID 映射
    ↓
indexed8 + RLEReversed 资源编码
    ↓
resource.bin
    ↓
P67 BIN 包
    ↓
M2551B1 真机测试
```

旧 Zepp OS JavaScript 工程只作为视觉布局原型；MiCreate 探针只作为相关 Pro 产品的历史格式参考。二者都不是正式 P67 编译目标。

## 当前状态

- 官方目标与画布已验证；
- 官方 `resource.bin` 头部与包 ID 已解析；
- P67 profile 可从脱敏基准自动重建；
- 自制 BIN 的生成与真机安装仍待完成。

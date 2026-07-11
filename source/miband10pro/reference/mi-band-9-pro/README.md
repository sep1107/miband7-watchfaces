# Mi Band 9 Pro MiCreate 参考

参考仓库：

```text
https://github.com/aaskorohodov/mi_band_9_pro_pip_girl_fallout_watchface
```

这是目前找到的、比 Amazfit Band 7 更接近 Smart Band 10 Pro 宽屏形态的公开开发参考。

## 可确认信息

- 作者说明表盘已经在 Mi Band 9 Pro 真机测试。
- 工程使用 MiCreate，而不是 EasyFace。
- MiCreate 工程要求 `example.png` 为 `336 × 480`。
- 输出目录包含 `.face` 表盘、`.fprj` 工程和 `.info` 元数据。
- 示例 `.info` 中出现：

```xml
<FaceInfo DeviceVersion="7.1.0" DeciceTypeName="MiBand8Pro" />
```

这表明 Mi Band 9 Pro 社区开发链可能沿用 Mi Band 8 Pro 目标元数据。

## 对本项目的意义

- `336 × 480` 现作为主要兼容候选画布。
- MiCreate `.face` 路线需要作为 EasyFace/Zepp OS 路线之外的另一条构建路径研究。
- 该证据不能证明 Smart Band 10 Pro 一定兼容 Mi Band 8/9 Pro 包格式；仍需 10 Pro 官方表盘包或真机确认。

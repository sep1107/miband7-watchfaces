# Smart Band 10 Pro assets

这里是 TIME FLIES 的 Smart Band 10 Pro 图片资源目录说明。

## 双目标画布

```text
主要候选：336 × 480
实验候选：400 × 480
```

`336 × 480` 目前优先使用，因为公开的 Mi Band 9 Pro 真机项目和 MiCreate 工程采用该尺寸；`400 × 480` 仅保留为媒体规格对比档。两者都需要 Smart Band 10 Pro 官方包或真机进一步确认。

## 已完成的开发素材

已从原 TIME FLIES 包整理并转换 157 个资源：

- 背景：188 × 480，作为左侧原仪表区域。
- 时间数字：64 × 97。
- 星期图片：48 × 25。
- 天气图标：48 × 48。
- 电量图：50 × 20。
- 其他状态、数据、等级和月相资源按分组保持宽高比处理。

所有开发素材都已转换成真正的 32 位 RGBA PNG，并通过格式验证。

## 仓库与完整包

GitHub 中保存布局源码、配置模板、生成工具和资源说明；完整开发 ZIP 中包含 `device/assets/` 下的全部 157 个 PNG。

v0.6.0 完整开发包 SHA-256：

```text
544307e63a5e70333a3c92b8a5de6e5bfd02a35efc3f85e27d0bc7d9142b006e
```

## 资源路径

```text
assets/bg/
assets/time/
assets/week/
assets/weather/
assets/battery/
assets/status/
assets/date/
assets/data/
assets/smdata/
assets/level/
assets/moon/
```

`../../tools/prepare_assets.py` 可用于重新生成素材；`../../tools/apply_target_profile.py` 用于切换目标画布配置。

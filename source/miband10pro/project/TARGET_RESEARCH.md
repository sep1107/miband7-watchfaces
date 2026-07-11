# Smart Band 10 Pro target research

## Verified device

```text
Marketing name: Xiaomi Smart Band 10 Pro / 小米手环10 Pro
Model: M2551B1
Device OS: Xiaomi HyperOS 3.101.030
```

## Verified official watchface target

A Mi Fitness cache export from the paired device contains mutually consistent metadata:

| Field | Value | Evidence |
| --- | --- | --- |
| Canvas | `336x480` | `description.xml`, `manifest.xml`, six previews |
| Device type | `P67` | `description.xml` |
| Watch OS | `vela` | `description.xml` |
| Resolution code | `XMHD03` | `capability.json` |
| Packet | `BIN` | `capability.json` |
| Region | `CN` | `capability.json` |
| Capability protocol | `1.9.4` | `capability.json` |
| Image format | `indexed8` | `description.xml` |
| Compression | `RLEReversed` | `manifest.xml` |
| Binary magic | `0x1234A55A` | `resource.bin` header |

The active official profile is `targets/p67-336x480.json`.

## Evidence boundary

The cache proves the official target and package format. It does not prove that a custom-generated package will be accepted. That requires a reproducible build and a physical-device installation test.

## Historical references

The Mi Band 8/9 Pro MiCreate path and the Zepp OS JavaScript prototype remain useful for layout and data-source research only. They are not Smart Band 10 Pro compiler targets.

## Decision

All new work targets `P67 / vela / 336x480 / BIN`. The next technical blocker is reproducing the binary generation path, not identifying the screen geometry.

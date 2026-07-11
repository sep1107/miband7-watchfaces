# M2551B1 / P67 real-device watchface package

## Source and privacy

A Mi Fitness cache directory was exported from an Android device paired with a physical Xiaomi Smart Band 10 Pro. The watchface was already present on the real device.

The repository stores only derived metadata and a sanitized fixture. It does not store the user's photographs, account material, Bluetooth address, serial number, application logs, official artwork, or the original compiled binary.

## Verified target

The package independently confirms the following values:

| Field | Value | Source |
| --- | --- | --- |
| Device model | `M2551B1` | real-device About screen |
| Device type | `P67` | `description.xml` |
| Watchface OS | `vela` | `description.xml` |
| Canvas | `336x480` | `description.xml` and `manifest.xml` |
| Resolution code | `XMHD03` | `capability.json` |
| Packet type | `BIN` | `capability.json` |
| Region | `CN` | `capability.json` |
| Capability protocol | `1.9.4` | `capability.json` |
| Image format | `indexed8` | `description.xml` |
| Image compression | enabled | `description.xml` |
| Manifest compression | `RLEReversed` | `manifest.xml` |

The verified P67 metadata replaces all earlier screen-size guesses and related-device target assumptions.

## Watchface identity

```text
Name: 效率时刻 / Stat block
Author: 小米
Package name: 120917384229
Watchface version: 1.0.12
Themes: 3
Editable: true
```

Six exported preview images are all `336x480`.

## Manifest structure

The real manifest contains:

| Element | Count |
| --- | ---: |
| `Theme` | 3 |
| `Layout` | 60 |
| `Widget` | 16 |
| `Slot` | 2 |
| `DataItemImageNumber` | 17 |
| `DataItemImageValues` | 4 |
| `ImageArray` | 12 |
| `Image` | 157 |
| `Translation` | 4 |

Observed data sources include:

```text
timeHour
timeMinute
dateMonth
dateDay
dateWeek
systemStatusBattery
healthHeartRate
healthStepCount
healthStepTarget
healthCalorieValue
healthCalorieTarget
weatherCurrentTemperature
weatherCurrentTemperatureFahrenheit
weatherCurrentWeather
weatherCurrentWindLevel
miscTimeSection
```

The manifest also defines jump targets such as weather, heart rate, sleep, sport and activities.

## `resource.bin` header

The first four bytes decode as the little-endian magic word:

```text
0x1234A55A
```

A public watchface implementation uses the same magic for its binary watchface header and defines the header version fields in the same order:

```text
https://github.com/mokshjain-cmd/watchface-merged/blob/main/ZhouHaiWatchFace/WatchBin/Model/BinFileHeader.cs
```

Decoded fields from this real P67 package:

| Field | Value |
| --- | --- |
| Watchface version | `1.0.12` |
| Editor version | `0.0.0` |
| Generator version | `0.0.0` |
| Binary protocol version | `0.9.3` |
| Firmware version | `1.0.0` |
| Theme count | `3` |
| Flags | `0x0002` |
| Preview image address | `5465` |
| Embedded package ID | `120917384229` |
| Size | `250850` bytes |
| SHA-256 | `a3c1f2e59346117b2885bd06a36a358b525aeaa70ecad8c7e51bf6ac00fc9669` |

The capability protocol `1.9.4` and binary-header protocol `0.9.3` are separate fields and must not be treated as the same value.

## UID map

`uidmap.map` contains 75 entries. Prefixes align with resource classes observed in the manifest:

```text
2: standalone images
3: image arrays
6: translations
7: data items
8: slots
9: widgets
```

## Toolchain decision

The verified Smart Band 10 Pro path is now:

```text
P67 + vela + 336x480 + indexed8/RLEReversed -> resource.bin -> BIN package
```

The old Zepp OS `app.json` project remains useful as a visual/layout prototype only. `deviceSource` is not part of the verified P67 package metadata and should no longer be treated as the main blocker.

## Remaining blocker

The official package target is verified, but the custom build target is not. The next milestone is to reproduce a BIN with the same header, manifest semantics, image encoding and package identity rules, then install it on the physical device.

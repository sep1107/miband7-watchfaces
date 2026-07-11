# Target profile research

## Evidence model used by this project

A display size and an installable watchface target are different things. Each target profile records three independent evidence axes:

- `hardware`: evidence for the physical screen or canvas.
- `buildChain`: evidence that a tool can produce a package for a related device.
- `deviceTarget`: evidence that the generated package is actually accepted by Smart Band 10 Pro.

Only a profile with `deviceTarget: verified` may be described as a confirmed 10 Pro build target.

## Verified real-device evidence

A physical Xiaomi Smart Band 10 Pro was photographed on `2026-07-11`. The about-device screen verifies:

```text
Device name: 小米手环10 Pro / Xiaomi Smart Band 10 Pro
Model number: M2551B1
Operating system: Xiaomi HyperOS
OS version: 3.101.030
```

The photos are not committed to the repository. The derived facts are stored in:

```text
reference/real-device/M2551B1.json
```

The active watchface visible on the device confirms a tall portrait display and support for rich data and shortcuts, including weather, air quality, battery, time, lunar date, weekday, health data, steps, distance, calories and heart rate.

This evidence materially improves confidence in the device identity and firmware family, but does **not** reveal:

- exact pixel resolution;
- watchface package type;
- `deviceSource`;
- MiCreate `DeviceType`;
- whether a custom package is accepted by the firmware.

The photographed display shape appears closer to the 336:480 aspect ratio than to 400:480, but perspective and rounded corners prevent treating this as pixel-resolution proof.

## Public launch evidence

Xiaomi Smart Band 10 Pro was publicly launched in May 2026. Launch coverage reports a 1.74-inch AMOLED display, HyperOS 3, GNSS and a 21-day battery estimate.

The `480 × 400` resolution was reported before launch, but a public compiler profile, official SDK entry, stock watchface package or target metadata confirming that canvas has not been found.

Relevant public reports:

```text
https://cincodias.elpais.com/smartlife/gadgets/2026-05-22/xiaomi-band-10-pro-oficial-caracteristicas.html
https://cincodias.elpais.com/smartlife/gadgets/2026-05-05/xiaomi-smart-band-10-pro-filtrado-diseno-bateria.html
```

## Pro build-chain evidence

A public Mi Band 9 Pro watchface repository contains source projects and watchface files tested on a real Mi Band 9 Pro. Its author reports:

- MiCreate is used instead of EasyFace for these project files.
- The editor requires `example.png` at `336 × 480`.
- Projects can be built using the Mi Band 8 Pro target and work on Mi Band 9 Pro.
- Generated `.info` metadata includes `DeviceTypeName="MiBand8Pro"` and `DeviceVersion="7.1.0"`.

Reference:

```text
https://github.com/aaskorohodov/mi_band_9_pro_pip_girl_fallout_watchface
```

## Current profiles

### `compat-336x480`

- Hardware evidence: indirect, now visually supported by the real-device display proportions.
- Build-chain evidence: tested on the related Mi Band 8/9 Pro path.
- Smart Band 10 Pro target evidence: reference only.
- Purpose: default profile for toolchain and MiCreate-format experiments.

### `experimental-400x480`

- Hardware evidence: reported before launch.
- Build-chain evidence: none.
- Smart Band 10 Pro target evidence: unverified.
- Purpose: comparison layout candidate matching reported `480 × 400` panel data.

## Project decision

- Keep `compat-336x480` as the default research profile because it has the strongest build-chain evidence and is visually plausible on the real device.
- Keep `experimental-400x480` as a secondary hardware-layout candidate.
- Record `M2551B1` and HyperOS `3.101.030` as verified device identifiers.
- Do not label either output as a Smart Band 10 Pro release.
- Promote a profile to `verified-build-target` only after package metadata and installation are confirmed.

## Evidence still needed

The next decisive artifact is one of the following:

1. A stock Smart Band 10 Pro `.face`, `.bin`, `.zpk` or equivalent package.
2. A Mi Fitness cache entry containing a 10 Pro watchface package.
3. EasyFace or MiCreate target metadata explicitly naming Smart Band 10 Pro or model `M2551B1`.
4. Firmware/device metadata containing a watchface package identifier.
5. A reproducible custom-watchface installation test on the physical device.

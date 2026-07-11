# Target profile research

## Evidence model used by this project

A display size and an installable watchface target are different things. Each target profile now records three independent evidence axes:

- `hardware`: evidence for the physical screen or canvas.
- `buildChain`: evidence that a tool can produce a package for a related device.
- `deviceTarget`: evidence that the generated package is actually accepted by Smart Band 10 Pro.

Only a profile with `deviceTarget: verified` may be described as a confirmed 10 Pro build target.

## Smart Band 10 Pro launch evidence

Xiaomi Smart Band 10 Pro was publicly launched in May 2026. Launch coverage consistently reports a 1.74-inch AMOLED display, HyperOS 3, GNSS and a 21-day battery estimate.

The `480 × 400` resolution was reported before launch, but a public compiler profile, official SDK entry, stock watchface package or target metadata confirming that canvas has not been found.

Relevant public reports:

```text
https://cincodias.elpais.com/smartlife/gadgets/2026-05-22/xiaomi-band-10-pro-oficial-caracteristicas.html
https://cincodias.elpais.com/smartlife/gadgets/2026-05-05/xiaomi-smart-band-10-pro-filtrado-diseno-bateria.html
https://www.t3.com/tech/smartwatches/xiaomi-watch-s5-smart-band-10-pro-launch-0526
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

- Hardware evidence: indirect.
- Build-chain evidence: tested on the related Mi Band 8/9 Pro path.
- Smart Band 10 Pro target evidence: reference only.
- Purpose: default profile for toolchain and MiCreate-format experiments.

### `experimental-400x480`

- Hardware evidence: reported.
- Build-chain evidence: none.
- Smart Band 10 Pro target evidence: unverified.
- Purpose: visual/layout candidate matching the reported `480 × 400` panel orientation.

## Project decision

- Keep `compat-336x480` as the default research profile because it has the strongest build-chain evidence.
- Keep `experimental-400x480` as the strongest hardware-layout candidate.
- Do not label either output as a Smart Band 10 Pro release.
- Promote a profile to `verified-build-target` only after package metadata and installation are confirmed.

## Evidence still needed

Any one of the following would materially improve confidence:

1. A stock Smart Band 10 Pro `.face`, `.bin`, `.zpk` or equivalent package.
2. A Mi Fitness cache entry containing a 10 Pro watchface package.
3. EasyFace or MiCreate target metadata explicitly naming Smart Band 10 Pro.
4. Firmware/device metadata containing a product code or package identifier.
5. A real-device installation report with a reproducible build profile.

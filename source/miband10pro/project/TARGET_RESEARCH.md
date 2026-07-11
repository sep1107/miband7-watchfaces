# Target profile research

## Strongest developer evidence found

A public Mi Band 9 Pro watchface repository contains source projects and watchface files tested on a real Mi Band 9 Pro. Its author reports:

- MiCreate is used instead of EasyFace for these project files.
- The editor requires `example.png` at `336 × 480`.
- Projects can be built using the Mi Band 8 Pro target and work on Mi Band 9 Pro.
- Generated `.info` metadata includes `DeviceTypeName="MiBand8Pro"` and `DeviceVersion="7.1.0"`.

Reference:

```text
https://github.com/aaskorohodov/mi_band_9_pro_pip_girl_fallout_watchface
```

## Conflict with media reports

Some 2026 media reports describe Smart Band 10 Pro resolution as `480 × 400`, but no public 10 Pro compiler profile, exported stock watchface, `.info`, firmware identifier or `deviceSource` was found to corroborate it.

## Project decision

- `compat-336x480` is now the primary development profile because it is based on a real-device-tested Pro watchface toolchain.
- `experimental-400x480` remains available for comparison.
- Neither profile is claimed as final Smart Band 10 Pro compatibility until an actual 10 Pro package or compiler target is obtained.

## Evidence still needed

Any one of the following would materially improve confidence:

1. A stock Smart Band 10 Pro `.face`, `.bin`, `.zpk` or equivalent package.
2. A Mi Fitness cache entry containing a 10 Pro watchface package.
3. EasyFace or MiCreate target metadata explicitly naming Smart Band 10 Pro.
4. Firmware/device metadata containing a product code or package identifier.
5. A real-device installation report with a reproducible build profile.

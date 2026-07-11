# P67 probe package scaffold

## Status

The repository can generate a complete watchface package-directory and ZIP scaffold from scratch for the verified Xiaomi Smart Band 10 Pro target:

```text
M2551B1 / P67 / vela / 336x480 / XMHD03 / BIN
```

The directory and ZIP are editor/cache artifacts. The direct Xiaomi installation protocol sends the raw `resource.bin`, not this ZIP. See `P67_DIRECT_TRANSFER.md`.

This remains a **structural probe**, not yet a device-verified installable watchface.

## Generated package contents

`tools/p67_probe_package.py` produces:

```text
capability.json
description.xml
manifest.xml
uidmap.map
resource.bin
preview/aod-preview.png
preview/market-preview.png
preview/preview.png
preview/style_1_static.png
resources/_preview/probe.png
resources/probe.png
```

The package uses a new numeric package ID and contains only generated artwork. It does not redistribute Xiaomi artwork or the user's original `resource.bin`.

## Verified relationships

The generator and regression tests verify:

- `description.xml` declares `P67`, `vela`, `336x480`, `indexed8` and compressed images;
- `capability.json` declares `XMHD03`, `CN`, protocol `1.9.4` and packet type `BIN`;
- `manifest.xml` declares `RLEReversed`, one theme, one preview image and one display image;
- preview-only `Image1` is not emitted as a RecordBase entry;
- visible `Image2` maps to UID `0x02000001`, matching the real-device numbering convention;
- `uidmap.map`, the layout payload and the image RecordBase agree on that UID;
- `resource.bin` contains a 168-byte header, one 176-byte P67 theme entry, one layout record and one image record;
- both preview and display image records decode to the generated 336x480 indexed8 image;
- all internal offsets and lengths remain within the file and the final file is four-byte aligned;
- the complete directory can be archived as a valid ZIP without host-specific paths.

## Tools

```text
tools/p67_minimal_builder.py
tools/test_p67_minimal_builder.py
tools/p67_probe_package.py
tools/test_p67_probe_package.py
tools/p67_transfer_protocol.py
tools/test_p67_transfer_protocol.py
```

GitHub Actions now performs two independent validation paths:

1. generate and reverse-inspect the raw `resource.bin`;
2. build its MD5/CRC32 direct-upload envelope and chunk plan;
3. generate the editor/cache package scaffold and validate its XML, UID map and ZIP.

## Remaining uncertainty

The cache package itself does not prove device acceptance. The main remaining questions are now transport and firmware behavior:

- whether M2551B1 exposes the same Xiaomi watchface and data-upload command services;
- whether the generated binary passes the band's install-status check;
- whether unnamed P67 theme-extension fields affect firmware acceptance;
- which authenticated phone-side implementation will perform the controlled upload.

The opaque Mi Fitness cache-directory hash is documented separately in `P67_CACHE_HASH_RESEARCH.md`. It is not part of the known direct BLE upload envelope and is no longer considered a primary blocker.

## Next milestone

1. Add a transport adapter or use a compatible open-source Xiaomi client to list faces on M2551B1 without writing anything.
2. Confirm command type `4` and data-upload type `22` are accepted by the device.
3. Preserve a stock face and prepare a unique-ID rollback-safe probe.
4. Attempt the first controlled upload only after the read-only compatibility check succeeds.

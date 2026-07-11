# P67 indexed8 image format

## Status

This document records values verified against the `resource.bin` extracted from the real M2551B1 Mi Fitness cache package. It describes the image payload used by the verified `P67 / vela / 336x480 / BIN` target.

## Single-image record

A single image record begins with a 12-byte little-endian header:

```text
byte   format
byte   flags
uint16 reserved
uint16 width
uint16 height
uint32 payloadSize
```

Observed P67 indexed8 values:

```text
format = 16
flags  = 0x04
reserved = 0
```

The payload begins with:

```text
uint32 magic       = 0x5AA521E0
uint32 descriptor  = (uncompressedSize << 4) | bytesPerUnit
```

For indexed8 images:

```text
bytesPerUnit = 1
uncompressedSize = 1024 + width * height
```

The uncompressed bytes are:

```text
1024-byte palette: 256 RGBA entries
width*height bytes: palette indices
```

The palette channel order was verified by decoding the real 336x480 background image and reproducing the visible preview.

## RLEReversed stream

Each command starts with one control byte. The low seven bits contain a count from 1 to 127.

- bit 7 set: copy `count` literal units that follow;
- bit 7 clear: repeat the following unit `count` times.

For indexed8, one unit is one byte. The same codec implementation supports larger units for other image formats.

This convention is called `RLEReversed` in `manifest.xml`; it is the reverse of the common PackBits choice for the high bit.

## ImageArray record

An image-array record begins with:

```text
byte   format       = 16
byte   imageCount
uint16 flags        = 0x0004
uint16 width
uint16 height
uint32 totalPayloadSize
uint32 itemLength[imageCount]
byte   itemPayloads[]
```

Every item payload is an independent `0x5AA521E0` compressed indexed8 payload with its own 1024-byte RGBA palette and index plane.

A real ten-image digit array was decoded successfully; its length table summed exactly to the declared total payload size, and all ten payloads expanded to the expected dimensions.

## Implemented tooling

- `tools/p67_image_codec.py`: encode/decode compressed payloads, single-image records and image arrays;
- `tools/test_p67_image_codec.py`: deterministic round-trip tests for literal runs, repeated runs, indexed8 images and image arrays.

## Evidence boundary

The image encoding is now reproducible. This alone does not make a complete installable watchface. A valid P67 BIN still requires correct Header, extended Theme tables, RecordBase tables, layout/data/widget payloads, UIDs, package identity and final alignment.
# TIME FLIES resource inventory

The original `7677` package contains 157 useful watchface resource files in the selected groups.

> Important: the filenames end in `.png`, but the file contents are TGA images. Tools must open them as TGA data rather than ordinary PNG files.

| Group | Files | Main original dimensions |
| --- | ---: | --- |
| `bg` | 4 | 192×490 background; 89×20, 44×14 and 34×101 elements |
| `time` | 13 | ten 44×67 digits; 32×18 separators; 17×51 element |
| `date` | 11 | ten 12×20 digits; 9×20 separator |
| `weather` | 34 | twenty-nine 40×40 icons plus small symbols |
| `battery` | 10 | ten 40×16 levels |
| `status` | 5 | four 14×14 icons and one 50×14 icon |
| `data` | 14 | ten 10×17 digits plus units and placeholders |
| `smdata` | 13 | ten 8×14 digits plus punctuation and percent |
| `week` | 7 | seven 38×20 weekday images |
| `level` | 16 | 40×22 and 72×22 level images |
| `moon` | 30 | thirty 27×27 moon phase images |

## Provisional scaling

The original canvas is `192 × 490`. The current Xiaomi Smart Band 10 scaffold uses `212 × 520`.

The helper script in `tools/prepare_assets.py` applies independent canvas ratios:

```text
x scale = 212 / 192
 y scale = 520 / 490
```

This creates a mechanically scaled first pass. It is not a final visual conversion: important digits and icons should be manually inspected for blur, palette conversion and pixel alignment.

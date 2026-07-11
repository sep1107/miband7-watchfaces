# iPhone transfer path for P67 watchfaces

## Current conclusion

An iPhone path is technically possible, but Xiaomi Smart Band 10 Pro has not yet been validated with the available iOS client.

The open-source My Band project is a native iOS/macOS application that implements Xiaomi authentication, watchface install commands, MD5/CRC32 upload framing and activation. Its published hardware validation currently covers Xiaomi Smart Band 10, not model M2551B1 / Smart Band 10 Pro.

## Important connection uncertainty

My Band uses CoreBluetooth and BLE services. Current Gadgetbridge metadata marks both Smart Band 10 and Smart Band 10 Pro as `BT_CLASSIC` devices while still using the Xiaomi support stack. That metadata may describe the preferred Android transport rather than proving that every command requires Classic Bluetooth, but ordinary iOS applications cannot open an arbitrary Classic Bluetooth SPP channel.

Therefore the first iPhone milestone is connection validation, not watchface upload.

## Safe validation order

1. Build and sideload My Band with Xcode on a physical iPhone.
2. Extend device-name matching and device metadata for Smart Band 10 Pro only where required.
3. Confirm that M2551B1 is discovered and authenticated.
4. Request battery/device state and the installed watchface list.
5. Stop if authentication, command transport or list retrieval fails.
6. Only after read-only operations succeed, test installation of a generated probe with a unique numeric ID.

## User requirements

- Physical iPhone running iOS 17 or newer.
- Mac with Xcode 16 or newer.
- Apple Developer account for sideloading; the client is not currently distributed through the App Store.
- Device AuthKey. Never commit, upload or paste the AuthKey into repository issues or logs.

## Recovery rules

- Keep Mi Fitness and at least one known-good stock face available.
- Do not delete the active stock face.
- Use a unique generated package ID.
- Perform the first write test only with adequate battery on both devices.
- Treat a disconnect, timeout or nonzero install status as a hard stop.

## Android fallback

Gadgetbridge already contains an experimental Smart Band 10 Pro coordinator and exposes Xiaomi watchface management. Android therefore remains the lower-friction fallback if the iPhone client cannot establish the required transport.

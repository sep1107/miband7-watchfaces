# P67 iPhone read-only probe

This folder contains a minimal, discovery-only iPhone app for Xiaomi Smart Band 10 Pro / M2551B1.

## Safety boundary

The app records:

- the advertised device name and service UUIDs;
- whether service `FE95` is present after connection;
- whether characteristics `005E` and `005F` are present;
- the CoreBluetooth properties exposed by each characteristic.

It deliberately does **not**:

- request or store the Xiaomi AuthKey;
- authenticate a session;
- enable notifications;
- write any characteristic;
- request the watchface list;
- upload, activate, replace or delete a watchface;
- request background Bluetooth execution.

CI scans every Swift file in this directory for write, notification, authentication and upload APIs. Introducing one of those APIs fails validation.

## Files

```text
P67ProbeApp.swift            SwiftUI app entry point
P67ReadOnlyProbe.swift       CoreBluetooth discovery logic
P67ReadOnlyProbeView.swift   Start, stop and JSON report screen
Info.plist                   Bluetooth permission text
project.yml                  XcodeGen project specification
generate_project.sh          Deterministic project generator
```

## Generate the Xcode project on a Mac

```sh
brew install xcodegen
cd source/miband10pro/ios-probe
./generate_project.sh
open P67ReadOnlyProbe.xcodeproj
```

In Xcode, select a personal development team and a physical iPhone. The first run should only tap **Start discovery** and export the JSON report. No AuthKey is required for this stage.

## Reading the first report

A useful positive result contains:

- a device name beginning with `Xiaomi Smart Band 10 Pro`;
- discovered service `FE95`;
- characteristics `005E` and `005F`;
- at least one writable characteristic and one notify-capable characteristic.

That result would prove that the Xiaomi command transport is visible through iOS CoreBluetooth. It would **not** yet prove that authentication or watchface upload works.

If `FE95` or the two characteristics are absent, the report still provides useful evidence that the P67 path may require another transport.

## Current status

The project scaffold and its read-only guard are statically validated. Physical-device execution on M2551B1 has not happened yet.

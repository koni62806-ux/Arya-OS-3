# Arya OS

Arya OS is a lightweight, Debian-based Linux distribution project designed first for the Dell Inspiron 1525 test machine.

## Current target hardware
- Intel Pentium Dual-Core T3200 (x86_64)
- 4 GiB RAM
- Intel GM965 graphics (PCI ID 8086:2A02; Linux i915 driver)
- Broadcom Dell Wireless 1395 (PCI ID 14e4:4315; exact firmware compatibility must be tested)
- Marvell Yukon 88E8040 Ethernet (Linux sky2 driver)
- Legacy BIOS boot is the first required boot target

## Build status
This repository contains the initial live-build configuration. A successful GitHub Actions run will produce a **test ISO**, not a finished or fully validated operating system.

## Build
The GitHub Actions workflow builds the ISO with Debian live-build. Download the artifact named `arya-os-iso` from a successful workflow run.

## Safety
1. Test the ISO in a virtual machine first.
2. Then test it from USB using the live session.
3. Do not install to the internal disk until display, keyboard, storage, Ethernet, Wi-Fi, audio and boot behavior have been checked.
4. Writing an ISO to a USB drive erases that USB drive.

## Important limitations
Arya OS does not promise compatibility with every Windows application or game. Wine/Proton compatibility depends on each application, GPU capabilities and anti-cheat support. The Intel GMA X3100 is an old GPU and cannot provide modern gaming performance.

## Planned work
- Arya visual theme, dock, launcher and sound design
- Hardware detection and first-boot diagnostics
- Arya Tool assistant with explicit permissions for device control
- Lightweight gaming profiles appropriate to supported hardware
- Installer and broader UEFI testing after the Legacy BIOS live image is validated

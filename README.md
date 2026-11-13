# Arya OS

Arya OS is a lightweight, Debian-based Linux distribution project designed first for the Dell Inspiron 1525 test machine.

## Target hardware

- Intel Pentium Dual-Core T3200 (x86_64)
- 4 GiB RAM
- Intel GM965 graphics (PCI ID 8086:2A02; Linux i915 driver)
- Broadcom Dell Wireless 1395 (PCI ID 14e4:4315; firmware package included, hardware behavior still requires testing)
- Marvell Yukon 88E8040 Ethernet (Linux sky2 driver)
- Legacy BIOS is the first required boot target

## Image type and installation

The build is configured to create a hybrid USB/DVD ISO containing:

- An XFCE live desktop for testing Arya OS without installing it.
- The official Debian Installer in **Live Installer** mode.
- A graphical installer entry and a desktop installer launcher.
- The Arya OS live filesystem, which the Live Installer copies to the selected hard disk; the installer then configures the bootloader and completes installation.

This is a real disk-installation path, not a live-only image. However, the resulting ISO must pass the automated build checks and then be tested in a virtual machine and on the target Dell before it can be called a validated release.

## Build

GitHub Actions builds the ISO. Download the artifact named `arya-os-installable-iso` from a successful workflow run. A SHA-256 checksum is uploaded alongside it.

## Safety before installation

1. Test the ISO in a virtual machine first.
2. Boot the USB and check the live desktop, display, keyboard, storage, Ethernet, Wi-Fi and audio.
3. Back up important files before changing disk partitions.
4. The installer asks you to choose a disk and partitioning method. Do not choose an option that uses the entire internal disk if you need to keep Windows or existing data.
5. Writing the ISO to a USB drive erases that USB drive.

## Current limitations

- The first image targets amd64 and Legacy BIOS compatibility; UEFI support is not yet a validated target.
- The Dell's Broadcom Wi-Fi firmware installer needs network access during image creation. Actual wireless operation still needs testing on the physical card.
- Arya OS does not promise compatibility with every Windows application or game. Wine/Proton compatibility depends on each application, GPU capabilities and anti-cheat support.
- The Intel GMA X3100 is an old GPU and cannot provide modern gaming performance.

## Remaining development

- Arya visual theme, dock, launcher and sound design
- Hardware detection and first-boot diagnostics
- Arya Tool assistant with explicit permissions for device control
- Lightweight gaming profiles appropriate to supported hardware
- Automated virtual-machine boot/install tests and physical-hardware validation

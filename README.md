# Arya OS

Arya OS is a lightweight Debian 13 (Trixie)-based Linux distribution project designed first for the Dell Inspiron 1525.

## Target hardware

- Intel Pentium Dual-Core T3200 (x86_64), approximately 4 GiB RAM
- Intel GM965 / GMA X3100 graphics (PCI ID 8086:2A02; Linux i915 driver)
- Broadcom Dell Wireless 1395 (PCI ID 14e4:4315; firmware package included, actual operation needs hardware validation)
- Marvell Yukon 88E8040 Ethernet (Linux sky2 driver)
- Legacy BIOS is the initial boot target

## Current development image components

- XFCE live desktop and Debian Live Installer-based installation path.
- Arya visual defaults: custom wallpaper, Arc theme, Papirus icons, top panel and Plank dock.
- Arya Center: searchable launcher for installed applications and a local HTML game library.
- Arya Tool: cloud/local OpenAI-compatible assistant, attachments, user-triggered X11 screenshots and confirmation for a small allowlist of app-launch actions.
- Arya Gaming: native Linux game launcher using GameMode when available.
- Arya Connect: user-controlled Tor/Snowflake service and dedicated Firefox profile using the local Tor SOCKS proxy.
- Arya Diagnostics: read-only hardware, storage, network and kernel-driver report.

These are implemented software components at source/package level. Their exact desktop behavior and hardware compatibility still require runtime validation; listing a feature does not mean every interaction has been tested on the Dell.

## Build and validation

A release candidate is build-validated only when GitHub Actions succeeds, ISO validation succeeds, and the ISO plus SHA-256 checksum are downloadable artifacts. CI success does not prove the ISO boots or installs correctly on physical hardware.

## Installation safety

1. Test in a virtual machine before installing.
2. Inspect display, keyboard, storage, Ethernet, Wi-Fi and audio in the live session.
3. Back up important files before changing partitions.
4. At the installer partitioning screen, inspect the selected disk and method carefully. Do not choose whole-disk erase if Windows or existing data must be preserved.
5. The development workflow never installs to or partitions the physical laptop.

## Known limitations

- Initial target is amd64 with Legacy BIOS; UEFI is not yet validated.
- Broadcom firmware and the exact Dell Wireless 1395 card revision need physical testing.
- Arya Tool does not execute arbitrary shell commands, install software, delete files, modify partitions or control arbitrary windows. Local AI inference may be too slow on a 4 GiB Pentium system.
- Arya Gaming launches native Linux games; it does not manage already-running processes, remove GPU limits or guarantee Windows game compatibility.
- Arya Connect is browser-scoped Tor proxy support, not a system-wide VPN. It cannot guarantee access if all international routes are unavailable.
- Arya Center is an application launcher, not yet a full replacement desktop shell.
- Physical hardware, suspend/resume, installer partition preservation and real network behavior remain unvalidated until tested on the target laptop.

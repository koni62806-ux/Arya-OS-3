# Dell Inspiron 1525 hardware notes

Detected from Windows device IDs supplied by the project owner.

| Component | Identification | Linux driver / notes |
|---|---|---|
| CPU | Intel Pentium Dual CPU T3200 @ 2.00 GHz | amd64 capable; confirm with live system |
| Graphics | Intel PCI 8086:2A02; GM965 family | i915 kernel driver; GMA X3100-class graphics |
| Wi-Fi | Broadcom PCI 14E4:4315, Dell Wireless 1395 | BCM4312 LP-PHY family; b43 firmware package is included, but verify firmware load and association on the actual card |
| Ethernet | Marvell PCI 11AB:4354, Yukon 88E8040 | sky2 kernel driver |
| RAM | 4,284,522,496 bytes reported by Windows | approximately 4 GiB |

## Live-session validation

- [ ] Boots in Legacy BIOS mode
- [ ] Internal disk is detected without modifying it
- [ ] Intel display works at native resolution
- [ ] Ethernet obtains network access
- [ ] Broadcom Wi-Fi firmware loads and connects
- [ ] Audio output works
- [ ] Suspend/resume is tested
- [ ] Live session remains usable with 4 GiB RAM

## Installer validation

- [ ] Debian Installer starts from the boot menu
- [ ] Graphical installer starts at a usable resolution
- [ ] Internal SATA disk is detected
- [ ] Manual partitioning can preserve existing Windows partitions
- [ ] GRUB installs in Legacy BIOS mode
- [ ] Installed system boots from the internal disk
- [ ] Installed XFCE session, network, audio and display work

Do not assume Wi-Fi works solely because a firmware package is included. Verify the exact card revision and firmware behavior on the target laptop.

Do not proceed with disk installation until backups exist and the partitioning screen has been checked carefully. The installer must not be treated as safe to erase the whole disk by default.

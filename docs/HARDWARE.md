# Dell Inspiron 1525 hardware notes

Detected from Windows device IDs supplied by the project owner.

| Component | Identification | Linux driver / notes |
|---|---|---|
| CPU | Intel Pentium Dual CPU T3200 @ 2.00 GHz | amd64 capable; confirm with live system |
| Graphics | Intel PCI 8086:2A02; GM965 family | i915 kernel driver; GMA X3100-class graphics |
| Wi-Fi | Broadcom PCI 14E4:4315, Dell Wireless 1395 | likely BCM4312; confirm LP-PHY/revision and firmware in live session |
| Ethernet | Marvell PCI 11AB:4354, Yukon 88E8040 | sky2 kernel driver |
| RAM | 4,284,522,496 bytes reported by Windows | approximately 4 GiB |

## Validation checklist
- [ ] Boots in Legacy BIOS mode
- [ ] Internal disk is detected without modifying it
- [ ] Intel display works at native resolution
- [ ] Ethernet obtains network access
- [ ] Broadcom Wi-Fi firmware loads and connects
- [ ] Audio output works
- [ ] Suspend/resume is tested
- [ ] Live session remains usable with 4 GiB RAM

Do not assume Wi-Fi works solely because the firmware package is included. Verify the exact card revision and firmware behavior on the target laptop.

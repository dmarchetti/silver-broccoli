#!/bin/bash
chroot /mnt
mount -t proc /proc /proc
mount -t sysfs /sys /sys
mount -B /dev
vgmknodes -v
mkinitrd -v /boot/initrd-$(uname -r)-lvm.img $(uname -r)
exit

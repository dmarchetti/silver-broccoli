#!/bin/bash
umount -v /mnt/tmpFs
lvremove /dev/vg00/*
vgremove vg00
pvremove /dev/sdb1
rm -vrf /mnt/tmpFs
rm -vrf /tmp/kill/00
rm /boot/initrd-3.10.0-514.6.1.el7.x86_64.img

#!/bin/bash

scsi_dir = "/sys/class/scsi_host/"

for i in $(ls $scsi_dir);
  do echo $scsi_dir,$i;
done

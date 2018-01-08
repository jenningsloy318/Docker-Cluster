1. create btrfs on /dev/sdb
```
#mkfs.btrfs /dev/sdb

btrfs-progs v4.4
See http://btrfs.wiki.kernel.org for more information.

Label:              (null)
UUID:               729840e5-d577-4003-aee7-501218b52602
Node size:          16384
Sector size:        4096
Filesystem size:    931.48GiB
Block group profiles:
  Data:             single            8.00MiB
  Metadata:         DUP               1.01GiB
  System:           DUP              12.00MiB
SSD detected:       no
Incompat features:  extref, skinny-metadata
Number of devices:  1
Devices:
   ID        SIZE  PATH
    1   931.48GiB  /dev/sdb
```

2. mount it to /data
```  
mount /dev/sdb /data/
```
3. add /dev/sdc to /data
```
btrfs device  add /dev/sdc /data
```

4. show the usage 
```
# btrfs fi usage /data
Overall:
    Device size:                   1.82TiB
    Device allocated:              2.02GiB
    Device unallocated:            1.82TiB
    Device missing:                  0.00B
    Used:                        512.00KiB
    Free (estimated):              1.82TiB      (min: 930.48GiB)
    Data ratio:                       1.00
    Metadata ratio:                   2.00
    Global reserve:               16.00MiB      (used: 0.00B)

Data,single: Size:8.00MiB, Used:256.00KiB
   /dev/sdb        8.00MiB

Metadata,DUP: Size:1.00GiB, Used:112.00KiB
   /dev/sdb        2.00GiB

System,DUP: Size:8.00MiB, Used:16.00KiB
   /dev/sdb       16.00MiB

Unallocated:
   /dev/sdb      929.46GiB
   /dev/sdc      931.48GiB
```

5. enable quota under /data
```
 btrfs  quota enable /data
```

6. create subvolume under /data

```
#cd /data
#btrfs subvolume create nfs-provisioner
Create subvolume './nfs-provisioner'
# btrfs subvolume create local-volume-provisioner
Create subvolume './local-volume-provisioner'
```

7. limit the size of the volumes
```
btrfs qgroup limit 100G /data/nfs-provisioner
btrfs qgroup limit 100G /data/local-volume-provisioner

```

# building #

## prerequisites ##
  * avr-gcc v4.7+
  * avr-libc v1.8+
  * git
  * make

**download source code:**
```
git clone https://code.google.com/p/avrprog/
cd avrprog
```

## bootloader ##

**build and compile using existing avrprog:**
```
cd avrboot
make BOARD=avrboot_mega88_rc PGPORT=/dev/tty.bt-module flash
```
  * if you don't chose BOARD, will be selected automatically board defined in Makedile (all boards are defined in ../boards/`*`.mk)
  * PGPORT is dev path for bluetooth serial device, default is defined in pg.mk

**if you have your own programmer:
```
make BOARD=avrboot_mega88_rc all
```
  * in build/avrboot you can found**bin**,**hex**and**srec**file to flash
  * fuses you can found in ../boards/`*`.mk**

## avrprog ##

**build and flash using previous installed bootloader
```
cd ../avrprog
make BOARD=avrboot_mega88_rc selfpg
```
  * will flash the avrprog to the CPU**

_enjoy it :-)_
## avrprog.py ##

single file python script for communicating with avrprog device or bootloader.

_this script need to have installed pyserial python library_

### commands list ###
```
  help
    print this help
  verbose:<loglevel>
    set loglevel (0 == no output, 4 = print everything)
  clear
    clear buffer
  load:<file>
    load file in to buffer
  buffer
    print content of buffer
  port:<serialport>
    connect to serial port
  bootloader[:<cpuid>]
    try to start bootloader (if cpuid is different, programmer exit with error)
  reboot
    reboot device
  sign
    sign content of buffer (use this for flashing from bootloader)
  cpu[:<cpuid>]
    connect to CPU, and detect it (if cpuid not match, programmer exit with error)
  erase
    chip erase, cause erase flash, eeprom and lockbits
  flash
    write buffer to flash
  download
    read flash to buffer
  verify
    verify flash with buffer
  fuse[:<fuseid>[:<value>]]
    read fuse(s) or write fuse. value is in hex
```

### examples ###
#### flash program.srec in to AVR via bootloader, where: ####
  * **port** select serial port
  * **bootloader** try to start bootloader if is avrprog running
  * **load** load binary.srec code in to buffer
  * **sign** calculate 16bit CRC and add it with size in to end of buffer (bootloader test this CRC before starting an application)
  * **flash** write content of buffer in to flash
  * **reboot** reboot AVR, which cause application start

```
avrprog.py port:/dev/tty.avrprog bootloader:atmega8 load:program.srec sign flash reboot
```

#### flash program.srec in to an slave AVR via avrprog programmer, where: ####
  * **cpu** select AVR CPU, this try to detect, and load signature from the CPU, if cpuId is selected, it will stop flashing if detected CPU is different
  * **erase** erase the flash memory in the slave AVR
  * **fuse** write fuses
  * **flash** when it is not in bootloader, but in 'CPU' mode this mean thats the content of buffer will be written in to slave CPU
  * **verify** verify content of buffer with content of flash in AVR

```
avrprog.py port:/dev/tty.avrprog load:program.srec cpu:atmega8 erase fuse:fusel:0x2f fuse:fuseh:0x91 flash verify
```

#### read and print all fuses: ####

```
avrprog.py port:/dev/tty.avrprog cpu fuse
```

#### read flash and display content of flash: ####
  * **download** download flash memory in to buffer
  * **buffer** this print content of buffer in to screen in hexmode

```
avrprog.py port:/dev/tty.avrprog cpu download buffer
```

#### print content of srec file (like hexdump): ####

```
avrprog.py load:program.srec buffer
```
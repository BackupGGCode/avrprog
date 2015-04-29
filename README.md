# avrprog
Automatically exported from code.google.com/p/avrprog
## Programmer and bootloader for Atmel AVR CPUs ##
### Features ###
  * communicating over serial terminal in text mode only and easy command interface
  * can connect to computer using UART serial port, USB (using FTDI,..), Bluetooth or Wifi module
  * programmer application is one python scrip
  * AVRprog includes BootLoader, which is usable for other applications and is compatible with programing utility

This programmer was developed as wireless bluetooth programmer.

more in wiki AvrProgrammer

### Programming examples ###
upload program using bootloader:
```
python avrprog.py port:/dev/tty.avrprog bootloader load:program.bin sign flash reboot
```

flashing program to an AVR connected to avrprog:
```
python avrprog.py port:/dev/tty.avrprog load:program.srec cpu erase flash verify
```

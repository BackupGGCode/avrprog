# AVR Boot Loader #

Is small program compatible with avrprog.py utility, for communication use UART

## Supported devices ##

  * **ATmega8**
  * **ATmega88**
  * **ATmega168**

  * _and is easy to add support for other processors_

bootloader is working with external XTAL or internal RC oscillator

## Starting bootloader ##

when CPU boot, avr boot loader start immediately and decide if run application or stay in boot-loader.
deciding consist of three steps:
  * check size and signature (checksum) of application (if application is wrong, stay in boot-loader)
  * check PUD bit in CPU register (if application want to restart in to bootloader)
  * check bit pin (PINB1) for stay in bootloader by an jumper

## Serial coomand line interface ##
> communication is over few text commands:
**hello** is command to activate communication with bootloader, return:
  * **hello**
  * **device `<`name`>` `<`version`>`** device name and version (for example: 'avrboot v1.0')
  * **cpu `<`cpu type`>`** is cpu type running bootloader ('atmega8')
  * **bootaddr `<`boot addr`>`** is address with bootloader, it is maximum program size in bytes
  * **pagesize `<`page size`>`** is size of one program page in bytes
  * **crc `<`ok|error`>`** indicate signature status of program ('ok' or 'error')
  * **ready** ready to receive other commands
> example:
```
hello
```
```
hello
device avrboot v1.0
cpu atmega168
bootaddr 14336
pagesize 128
crc ok
ready
```

**echo [`<`0|1`>`]** is command for control echo on serial line, return:
  * **echo `<`0|1`>`** echo status
  * **ready** ready to receive other commands
> example:
```
echo
```
```
echo 0
ready
```

**reboot** is command for control echo on serial line, return:
  * **rebooting..** cpu is rebooting, ready is not received.
> example:
```
reboot
```
```
rebooting..
```

**flash `<`addr`>` `<`magic`>` `<`data`>`** write **data** (with **page size**) to flash at **address** (**magic** is key 4321 for writing to flash), return:
  * **flash `<`ok|error`>`** flash status
  * **ready** ready to receive other commands
> example:
```
flash 0000 4321 0c94c4000c94e1000....
```
```
flash ok
ready
```
NAME = avrboot
MMCU = atmega8
SRC = avrboot.c drv/uart.c
BOOT_ADDRESS = 0x1800
F_CPU = 7372800
CCFLAGS = -Os -D BOOT_ADDRESS=$(BOOT_ADDRESS) -D CPU=\"${MMCU}\"
LNFLAGS = -Wl,--section-start=.progpg=0x1f80,--section-start=.text=${BOOT_ADDRESS}
OCFLAGS = -j .progpg
CROSS_COMPILE = avr-

F_CPU = 7372800

FUSEL = 0x2f
FUSEH = 0x91
#FUSEE = 0xff
#LOCK = 0xff

include avr.mk

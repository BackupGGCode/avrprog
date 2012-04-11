NAME = avrboot
MMCU = atmega8
SRC = avrboot.c drv/uart.c
BOOT_ADDRESS = 0x1800
PROGPG_ADDRESS = 0x1f80
F_CPU = 7372800
CCFLAGS = -Os -D BOOT_ADDRESS=$(BOOT_ADDRESS) -D PROGPG_ADDRESS=$(PROGPG_ADDRESS)
LNFLAGS = -Wl,--section-start=.text=$(BOOT_ADDRESS),--section-start=.progpg=$(PROGPG_ADDRESS)
OCFLAGS = -j .progpg
CROSS_COMPILE = avr-

FUSEL = 0x2f
FUSEH = 0x91
#FUSEE = 0xff
#LOCK = 0xff

include avr.mk

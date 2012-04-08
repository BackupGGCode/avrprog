NAME = avrprog
MMCU = atmega8
SRC = avrprog.c drv/uart.c drv/spiprog.c
BOOT_ADDRESS = 0x1800
F_CPU = 7372800
CCFLAGS = -Os -D BOOT_ADDRESS=$(BOOT_ADDRESS)
LNFLAGS = -Wl,--section-start=.progpg=0x1f80
OCFLAGS =
CROSS_COMPILE = avr-

F_CPU = 7372800

FUSEL = 0x2f
FUSEH = 0x91
#FUSEE = 0xff
#LOCK = 0xff

include avr.mk

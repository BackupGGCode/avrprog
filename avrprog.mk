NAME = avrprog
CPU ?= atmega8
SRC = avrprog.c drv/uart.c drv/spiprog.c drv/selfpg.c

ifeq ($(CPU), atmega8)
	MMCU = $(CPU)
	F_CPU = 7372800
	BOOT_ADDRESS = 0x1800
	PROGPG_ADDRESS = 0x1f80
	FUSEL = 0x2f
	FUSEH = 0x90
	#FUSEE = 0xff
	#LOCK = 0xff
endif

CCFLAGS = -Os -D BOOT_ADDRESS=$(BOOT_ADDRESS) -D PROGPG_ADDRESS=$(PROGPG_ADDRESS)
LNFLAGS = -Wl,--section-start=.progpg=$(PROGPG_ADDRESS)
OCFLAGS =
CROSS_COMPILE = avr-

include avr.mk

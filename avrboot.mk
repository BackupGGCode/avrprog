NAME = avrboot
BOARD ?= avrprog_mega8_xtal
SRC = avrboot.c drv/uart.c drv/selfpg.c

include boards/$(BOARD).mk

CCFLAGS = -Os -D BOOT_ADDRESS=$(BOOT_ADDRESS) -D PROGPG_ADDRESS=$(PROGPG_ADDRESS)
LNFLAGS = -Wl,--section-start=.text=$(BOOT_ADDRESS),--section-start=.progpg=$(PROGPG_ADDRESS)
OCFLAGS = -j .progpg
CROSS_COMPILE = avr-

include avr.mk

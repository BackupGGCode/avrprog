NAME = avrprog
BOARD ?= avrprog_mega8_xtal
SRC = avrprog.c drv/uart.c drv/spiprog.c drv/selfpg.c

include boards/$(BOARD).mk

CCFLAGS = -Os -D BOOT_ADDRESS=$(BOOT_ADDRESS) -D PROGPG_ADDRESS=$(PROGPG_ADDRESS)
LNFLAGS = -Wl,--section-start=.progpg=$(PROGPG_ADDRESS)
OCFLAGS =
CROSS_COMPILE = avr-

include avr.mk

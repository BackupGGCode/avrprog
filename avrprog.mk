# project name
NAME ?= avrprog

# board name (must board definitions)
BOARD ?= avrprog_mega8_xtal

# optimize (0, 1, 2, 3, s)
OPTIMIZE ?= s

# source files to compile
SRC += drv/selfpg.c

# source files to compile with link-time-optimalisations
SRC_LTO += $(NAME).c drv/uart.c drv/spiprog.c

# other compiler and linker options
CCFLAGS += -D BOOT_ADDRESS=$(BOOT_ADDRESS) -D PROGPG_ADDRESS=$(PROGPG_ADDRESS)
LNFLAGS += -Wl,--section-start=.progpg=$(PROGPG_ADDRESS)
OCFLAGS +=

include boards/$(BOARD).mk
include avr.mk

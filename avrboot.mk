# project name
NAME ?= avrboot

# board name (must board definitions)
BOARD ?= avrboot_mega8_xtal

# optimize (0, 1, 2, 3, s)
OPTIMIZE ?= s

# source files to compile
SRC += drv/selfpg.c

# source files to compile with link-time-optimalisations
SRC_LTO += $(NAME).c drv/uart.c

# other compiler and linker options
CCFLAGS += -D BOOT_ADDRESS=$(BOOT_ADDRESS) -D PROGPG_ADDRESS=$(PROGPG_ADDRESS)
LNFLAGS += -Wl,--section-start=.text=$(BOOT_ADDRESS),--section-start=.progpg=$(PROGPG_ADDRESS)
OCFLAGS += -j .progpg

include boards/$(BOARD).mk
include avr.mk

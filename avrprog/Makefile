# project name
NAME ?= avrprog

# board name (must board definitions)
BOARD ?= avrprog_mega8_xtal

# path to base direcory (where is avr.mk)
BASEDIR ?= ..

# optimize (0, 1, 2, 3, s)
OPTIMIZE ?= s

# source files to compile
SRC += $(NAME).c

# source files to compile with link-time-optimalisations
SRC_LTO +=

# modules to build with project
MODULES += drv/uart drv/spiprog drv/selfpg

# other compiler and linker options
CCFLAGS += -D BOOT_ADDRESS=$(BOOT_ADDRESS) -D PROGPG_ADDRESS=$(PROGPG_ADDRESS)
LNFLAGS += -Wl,--section-start=.progpg=$(PROGPG_ADDRESS)
OCFLAGS +=

# includes
include $(BASEDIR)/boards/$(BOARD).mk
include $(BASEDIR)/avr.mk

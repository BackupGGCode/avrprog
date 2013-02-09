# name:    makefile script
# desc:    makefile script for cross bulding AVR projects (UNIX version)
# author:  (c)2012-2013 Pavel Revak <pavel.revak@gmail.com>
# licence: GPL


### these definitions are project specific, put all in to your Makefile

# project name
NAME ?= project

# modules directory (path to this directory)
BASEDIR ?= .

# build directory
BUILDDIR ?= build/$(NAME)

# cpu type
MMCU ?= atmega8

# cpu clock
F_CPU ?= 8000000

# optimize (0, 1, 2, 3, s)
OPTIMIZE ?= s

# source files to compile
# SRC +=

# source files to compile with link-time-optimalisations
# SRC_LTO += $(NAME).c

# modules used in project
# MODULES +=

# other compiler and linker options
CCFLAGS +=
LNFLAGS +=
OCFLAGS +=

# don't forget to include this avr.mk from yout Makefile
# include avr.mk

###


# $(shell mkdir -p $(BUILDDIR) $(addprefix $(BUILDDIR)/,$(MODULES)))

# MODDIR := $(realpath $(MODDIR))

export CROSS_COMPILE ?= avr-

GCCFLAGS += -mmcu=$(MMCU)

ifdef OPTIMIZE
	GCCFLAGS += -O$(OPTIMIZE)
endif

ifdef DEBUG
	CCFLAGS += -DDEBUG
endif

ifneq ($(VERBOSE),1)
	export V := @
endif

export CCFLAGS += $(GCCFLAGS) -Wall -pedantic -std=c11 -c -D F_CPU=$(F_CPU) -D CPU=\"$(MMCU)\" -I$(realpath $(BASEDIR)) -fshort-enums
export LNFLAGS += $(GCCFLAGS) -Wl,--cref -flto
export OCFLAGS += -j .text -j .data
export ODFLAGS += -S -w -a -f -d
export SZFLAGS += -Bd

export CC := $(CROSS_COMPILE)gcc
export LN := $(CROSS_COMPILE)gcc
export AR := $(CROSS_COMPILE)ar
export OC := $(CROSS_COMPILE)objcopy
export OD := $(CROSS_COMPILE)objdump
export SZ := $(CROSS_COMPILE)size

ELF := $(BUILDDIR)/$(NAME).elf
HEX := $(BUILDDIR)/$(NAME).hex
BIN := $(BUILDDIR)/$(NAME).bin
SREC := $(BUILDDIR)/$(NAME).srec
DUMP := $(BUILDDIR)/$(NAME).dump
MAP := $(BUILDDIR)/$(NAME).map

.PHONY: hex bin srec dump dep meminfo

all:	modules srec bin hex dump
hex:	modules $(HEX)
bin:	modules $(BIN)
srec:	modules $(SREC)
dump:	modules $(DUMP)
help:	help_avr

$(HEX): $(ELF)
	@echo "  OC     $(@F) ($(<F))"
	$(V)$(OC) $(OCFLAGS) -O ihex $< $@

$(BIN): $(ELF)
	@echo "  OC     $(@F) ($(<F))"
	$(V)$(OC) $(OCFLAGS) -O binary $< $@
	@chmod a+w $@

$(SREC): $(ELF)
	@echo "  OC     $(@F) ($(<F))"
	$(V)$(OC) $(OCFLAGS) -O srec $< $@

$(DUMP): $(ELF)
	@echo "  OD     $(@F) ($(<F))"
	$(V)$(OD) $(ODFLAGS) $< > $@

meminfo: $(OBJ) $(OBJ_LTO) $(ELF)
	@echo "  SIZE   $(NAME) ..."
	$(V)$(SZ) $(SZFLAGS) $^

help_avr:
	@echo "AVR MAKE MODULE"
	@echo "default target:"
	@echo "  all:      build all (modules, srec, bin, hex and dump"
	@echo "other targets:"
	@echo "  srec:     create motorola hex file"
	@echo "  hex:      create intel hex file"
	@echo "  bin:      create binart file"
	@echo "  dump:     create $(DUMP) file with compiled assembler code"
	@echo

include $(BASEDIR)/build.mk
-include $(BASEDIR)/pg.mk

# name:    makefile script
# desc:    makefile script for cross bulding AVR projects (UNIX version)
# author:  (c)2012-2013 Pavel Revak <pavel.revak@gmail.com>
# licence: GPL


### these definitions are project specific, put all in to your Makefile

# project name
NAME ?= project

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

# other compiler and linker options
CCFLAGS +=
LNFLAGS +=
OCFLAGS +=

# don't forget to include this avr.mk from yout Makefile
# include avr.mk

###


BUILDDIR ?= build/$(NAME)
CROSS_COMPILE ?= avr-

GCCFLAGS += -mmcu=$(MMCU)

ifdef OPTIMIZE
	GCCFLAGS += -O$(OPTIMIZE)
endif

ifdef DEBUG
	CCFLAGS += -DDEBUG
endif

ifndef VERBOSE
	V = @
endif

CCFLAGS += $(GCCFLAGS) -Wall -std=c11 -c -D F_CPU=$(F_CPU) -D CPU=\"$(MMCU)\" -I. -fshort-enums
LNFLAGS += $(GCCFLAGS) -Wl,--cref -flto
OCFLAGS += -j .text -j .data
ODFLAGS += -S -w -a -f -d
SZFLAGS += -Bd

CC = $(CROSS_COMPILE)gcc
LN = $(CROSS_COMPILE)gcc
OC = $(CROSS_COMPILE)objcopy
OD = $(CROSS_COMPILE)objdump
SZ = $(CROSS_COMPILE)size

DEP = $(patsubst %.c,$(BUILDDIR)/%.d,$(SRC))
OBJ = $(patsubst %.c,$(BUILDDIR)/%.o,$(SRC))
DEP_LTO = $(patsubst %.c,$(BUILDDIR)/%.lto.d,$(SRC_LTO))
OBJ_LTO = $(patsubst %.c,$(BUILDDIR)/%.lto.o,$(SRC_LTO))

ELF = $(BUILDDIR)/$(NAME).elf
HEX = $(BUILDDIR)/$(NAME).hex
BIN = $(BUILDDIR)/$(NAME).bin
SREC = $(BUILDDIR)/$(NAME).srec
DUMP = $(BUILDDIR)/$(NAME).dump
MAP = $(BUILDDIR)/$(NAME).map

CLEANFILES = $(OBJ) $(OBJ_LTO) $(DEP) $(DEP_LTO) $(ELF) $(SREC) $(HEX) $(BIN) $(DUMP) $(MAP)

all:	dep srec bin hex dump

hex:	$(HEX)
bin:	$(BIN)
srec:	$(SREC)
dump:	$(DUMP)
dep:	$(DEP) $(DEP_LTO)

$(BUILDDIR)/%.d: %.c
	@echo "  DEP    $@ ($<)"
	$(V)$(CC) $(CCFLAGS) $< -MM -MT '$(patsubst %.d,%.o,$@)' -MF $@

$(BUILDDIR)/%.lto.d: %.c
	@echo "  DEP    $@ ($<) (LTO)"
	$(V)$(CC) $(CCFLAGS) $< -MM -MT '$(patsubst %.d,%.o,$@)' -MF $@

$(BUILDDIR)/%.o: %.c
	@echo "  CC     $@ ($<)"
	$(V)$(CC) $(CCFLAGS) $< -o $@

$(BUILDDIR)/%.lto.o: %.c
	@echo "  CC     $@ ($<) (LTO)"
	$(V)$(CC) $(CCFLAGS) -flto $< -o $@

$(ELF): $(OBJ) $(OBJ_LTO)
	@echo "  LN     $@ ($^)"
	$(V)$(LN) $(LNFLAGS) -o $@ $^ -Wl,-Map=$(MAP)

$(HEX): $(ELF)
	@echo "  OC     $@ ($<)"
	$(V)$(OC) $(OCFLAGS) -O ihex $< $@

$(BIN): $(ELF)
	@echo "  OC     $@ ($<)"
	$(V)$(OC) $(OCFLAGS) -O binary $< $@
	@chmod a+w $@

$(SREC): $(ELF)
	@echo "  OC     $@ ($<)"
	$(V)$(OC) $(OCFLAGS) -O srec $< $@

$(DUMP): $(ELF)
	@echo "  OD     $@ ($<)"
	$(V)$(OD) $(ODFLAGS) $< > $@

meminfo: $(OBJ) $(OBJ_LTO) $(ELF)
	@echo "  SIZE   $(NAME) ..."
	$(V)$(SZ) $(SZFLAGS) $^

clean:
	@echo "  CLEAN"
	$(V)rm -f $(CLEANFILES)

-include $(DEP) $(DEP_LTO)

.PHONY: all hex bin srec dump dep dump meminfo clean

$(shell mkdir -p $(dir $(OBJ) $(OBJ_LTO)))

# programer definitions
-include pg.mk

# name:    makefile script
# desc:    makefile script for cross bulding AVR/AVR32 projects (LINUX version)
# author:  (c)2012 Pavel Revak <pavel.revak@gmail.com>
# licence: GPL

###### general project settings (these settings are overwrited from config.mk file)
NAME ?= project
SRC ?= main.c
F_CPU ?= 8000000

# AVR
#MMCU ?= atmega8
#CROSS_COMPILE ?= avr-

# AVR32
#MPART ?= uc3a3256
#CROSS_COMPILE ?= avr32-

CCFLAGS ?= -Os
LNFLAGS ?=
OCFLAGS ?=
#####

BUILDDIR = build/$(NAME)

CC = $(CROSS_COMPILE)gcc
LN = $(CROSS_COMPILE)gcc
OC = $(CROSS_COMPILE)objcopy
OD = $(CROSS_COMPILE)objdump
SZ = $(CROSS_COMPILE)size

ifdef MMCU
	CPUFLAGS ?= -mmcu=$(MMCU)
endif

ifdef MPART
	CPUFLAGS ?= -mpart=$(MPART)
endif


CCFLAGS += $(CPUFLAGS) -std=c99 -gstabs -c -D F_CPU=$(F_CPU) -I. -fshort-enums
LNFLAGS += $(CPUFLAGS) -Wl,--cref
OCFLAGS += -j .text -j .data
ODFLAGS += -S -w -a -f -d
SZFLAGS += -Bd

ifdef DEBUG
	CCFLAGS += -DDEBUG
endif

ifndef VERBOSE
	V = @
endif

OBJ = $(patsubst %.c,$(BUILDDIR)/%.o,$(SRC))
DEP = $(patsubst %.c,$(BUILDDIR)/%.d,$(SRC))

ELF = $(BUILDDIR)/$(NAME).elf
HEX = $(BUILDDIR)/$(NAME).hex
BIN = $(BUILDDIR)/$(NAME).bin
SREC = $(BUILDDIR)/$(NAME).srec
DUMP = $(BUILDDIR)/$(NAME).dump
MAP = $(BUILDDIR)/$(NAME).map

CLEANFILES = $(OBJ) $(DEP) $(ELF) $(SREC) $(HEX) $(BIN) $(DUMP) $(MAP)

all:	dep srec bin hex dumpf

hex:	$(HEX)
bin:	$(BIN)
srec:	$(SREC)
dumpf:	$(DUMP)
dep:	$(DEP)

$(BUILDDIR)/%.d:	%.c
	$(V)$(CC) $(CCFLAGS) $< -MM -MT '$(patsubst %.d,%.o,$@)' -MF $@

$(BUILDDIR)/%.o:	%.c
	@echo "  CC    " $@ "("$<")"
	$(V)$(CC) $(CCFLAGS) $< -o $@

$(ELF): $(OBJ)
	@echo "  LN    " $@ "("$(OBJ)")"
	$(V)$(LN) $(LNFLAGS) -o $@ $(OBJ) -Wl,-Map=$(MAP)

$(HEX): $(ELF)
	@echo "  OC    " $@ "("$<")"
	$(V)$(OC) $(OCFLAGS) -O ihex $< $@

$(BIN): $(ELF)
	@echo "  OC    " $@ "("$<")"
	$(V)$(OC) $(OCFLAGS) -O binary $< $@
	@chmod a+w $@

$(SREC):	$(ELF)
	@echo "  OC    " $@ "("$<")"
	$(V)$(OC) $(OCFLAGS) -O srec $< $@

$(DUMP):	$(ELF)
	@echo "  ODF   " $(NAME) "..."
	$(V)$(OD) $(ODFLAGS) $< > $@

dump:	$(ELF)
	@echo "  OD    " $(NAME) "..."
	$(V)$(OD) $(ODFLAGS) $<

meminfo:	$(ELF)
	@echo "  SZ    " $(NAME) "..."
	$(V)$(SZ) $(SZFLAGS) $(OBJ) $<

clean:
	@echo "  CLEAN "
	$(V)rm -f $(CLEANFILES)

-include $(DEP)

.PHONY: all hex bin srec dumpf dep dump meminfo clean

$(shell mkdir -p $(dir $(OBJ)))

# programer definitions
-include pg.mk

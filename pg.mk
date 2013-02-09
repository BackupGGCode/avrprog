PG ?= python $(BASEDIR)/avrprog.py
PGPORT ?= /dev/tty.avrprog

#PGFLAGS =
PGPORTFLAG ?= port:$(PGPORT)

### define these fuses in your make file ###
# FUSEL = 0x9f
# FUSEH = 0x81
# FUSEE = 0xff
# LOCK = 0xff

FUSEFLAGS :=
ifdef FUSEL
	FUSEFLAGS += fuse:fusel:$(FUSEL)
endif
ifdef FUSEH
	FUSEFLAGS += fuse:fuseh:$(FUSEH)
endif
ifdef FUSEE
	FUSEFLAGS += fuse:fusee:$(FUSEE)
endif
ifdef LOCK
	FUSE_LOCK = fuse:lock:$(LOCK)
endif

.PHONY: selfpg flash reflash dump_flash dump_fuses dump_buffer help

help: help_pg

selfpg: $(SREC)
	@echo "  UPLOAD  $<"
	$(V)$(PG) $(PGFLAGS) load:$< $(PGPORTFLAG) bootloader:$(MMCU) sign flash reboot

flash: $(SREC)
	@echo "  FLASH   $<"
	$(V)$(PG) $(PGFLAGS) load:$< $(PGPORTFLAG) cpu:$(MMCU) erase $(FUSEFLAGS) flash verify $(FUSE_LOCK)

reflash: $(SREC)
	@echo "  FLASH   $<"
	$(V)$(PG) $(PGFLAGS) load:$< $(PGPORTFLAG) cpu:$(MMCU) erase flash

dump_flash:
	@echo "  DUMP FLASH"
	$(V)$(PG) $(PGFLAGS) $(PGPORTFLAG) cpu download buffer

dump_fuses:
	@echo "  FUSES"
	$(V)$(PG) $(PGFLAGS) $(PGPORTFLAG) cpu fuse

dump_buffer: $(SREC)
	@echo "  DUMP   $<"
	$(V)$(PG) $(PGFLAGS) load:$< buffer

help_pg:
	@echo "PROGRAMMER MODULE"
	@echo "bootloader targets:"
	@echo "  selfpg:      flash program"
	@echo "avrprog targets:"
	@echo "  flash:       erase - flash program - flash all fuses and lock bit"
	@echo "  reflash:     erase - flash program"
	@echo "  dump_flash:  download flash and print it in hexa"
	@echo "  dump_flash:  download fuses and print it"
	@echo "common targets:"
	@echo "  dump_buffer: print program (for flash) in hexa"
	@echo

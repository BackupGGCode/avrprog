PG ?= python $(BASEDIR)/avrprog.py
PORT ?= /dev/tty.avrprog

#PGFLAGS =
PORTFLAG ?= port:$(PORT)

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

.PHONY: upload flash fuses download_flash buffer

upload: $(SREC)
	@echo "  UPLOAD  $<"
	$(V)$(PG) $(PGFLAGS) load:$< $(PORTFLAG) bootloader sign flash reboot

flash: $(SREC)
	@echo "  FLASH   $<"
	$(V)$(PG) $(PGFLAGS) load:$< $(PORTFLAG) cpu:$(MMCU) erase $(FUSEFLAGS) flash verify $(FUSE_LOCK)

print_flash: $(SREC)
	@echo "  FLASH   $<"
	$(V)$(PG) $(PGFLAGS) load:$< buffer

fuses:
	@echo "  FUSES"
	$(V)$(PG) $(PGFLAGS) $(PORTFLAG) cpu fuse

download_flash:
	@echo "  DUMP"
	$(V)$(PG) $(PGFLAGS) $(PORTFLAG) cpu download buffer

buffer: $(SREC)
	@echo "  BUFFER  $<"
	$(V)$(PG) $(PGFLAGS) load:$< buffer

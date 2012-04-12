PG ?= python avrprog.py
PORT ?= /dev/tty.avrprog

PGFLAGS = port:$(PORT)

#FUSEL = 0x9f
#FUSEH = 0x81
#FUSEE = 0xff
#LOCK = 0xff

FUSES =
ifdef FUSEL
	FUSES += fuse:fusel:$(FUSEL)
endif
ifdef FUSEH
	FUSES += fuse:fuseh:$(FUSEH)
endif
ifdef FUSEE
	FUSES += fuse:fuseh:$(FUSEE)
endif
FUSE_LOCK =
ifdef LOCK
	FUSE_LOCK = fuse:lock:$(LOCK)
endif

upload: $(SREC)
	@echo "  UPLOAD "$<
	@$(PG) $(PGFLAGS) bootloader load:$< sign flash reboot

flash: $(SREC)
	@echo "  FLASH  "$<
	$(PG) $(PGFLAGS) cpu load:$< erase $(FUSES) flash verify $(FUSE_LOCK)

fuses:
	@echo "  FUSES"
	$(PG) $(PGFLAGS) cpu fuse

dump_flash:
	@echo "  DUMP"
	$(PG) $(PGFLAGS) cpu dump buffer

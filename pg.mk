PG ?= python avrprog.py
PORT ?= /dev/tty.avrprog

#PGFLAGS =
PORTFLAG ?= port:$(PORT)

### define these fuses in your make file ###
# FUSEL = 0x9f
# FUSEH = 0x81
# FUSEE = 0xff
# LOCK = 0xff

ifdef FUSEL
	FUSES += fuse:fusel:$(FUSEL)
endif
ifdef FUSEH
	FUSES += fuse:fuseh:$(FUSEH)
endif
ifdef FUSEE
	FUSES += fuse:fusee:$(FUSEE)
endif
ifdef LOCK
	FUSE_LOCK = fuse:lock:$(LOCK)
endif

.PHONY: upload flash fuses dump_flash buffer

upload: $(SREC)
	@echo "  UPLOAD  $<"
	$(V)$(PG) $(PGFLAGS) load:$< $(PORTFLAG) bootloader sign flash reboot

flash: $(SREC)
	@echo "  FLASH   $<"
	$(V)$(PG) $(PGFLAGS) load:$< $(PORTFLAG) cpu:$(MMCU) erase $(FUSES) flash verify $(FUSE_LOCK)

fuses:
	@echo "  FUSES"
	$(V)$(PG) $(PGFLAGS) $(PORTFLAG) cpu fuse

dump_flash:
	@echo "  DUMP"
	$(V)$(PG) $(PGFLAGS) $(PORTFLAG) cpu dump buffer

buffer: $(SREC)
	@echo "  BUFFER  $<"
	$(V)$(PG) $(PGFLAGS) load:$< buffer

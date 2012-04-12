FUSEL ?= 0x9f
FUSEH ?= 0x81
FUSEE ?= 0xff
LOCK ?= 0xff

PG = python avrprog.py
PORT = /dev/tty.avrprog
PGFLAGS += port:$(PORT)

FUSES =

upload: $(SREC)
	@echo "  PG    " $(SREC) "..."
	@$(PG) $(PGFLAGS) bootloader load:$(SREC) sign flash reboot

flash: $(SREC)
	@echo "  PG    " $(SREC) "..."
	@$(PG) $(PGFLAGS) cpu load:$(SREC) erase fuse:fusel:$(FUSEL) fuse:fuseh:$(FUSEH) flash verify

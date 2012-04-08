FUSEL ?= 0x9f
FUSEH ?= 0x81
FUSEE ?= 0xff
LOCK ?= 0xff

PG = python avrprog.py
PORT = /dev/tty.avrprog
PGFLAGS += port:$(PORT)

upload: $(BIN)
	@echo "  PG    " $(BIN) "..."
	@$(PG) $(PGFLAGS) bootloader load:$(BIN) sign flash reboot

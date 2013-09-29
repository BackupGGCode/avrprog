# cpu type
MMCU ?= atmega8

# cpu clock
F_CPU ?= 7372800

# bootloader addresses
BOOT_ADDRESS ?= 0x1800
PROGPG_ADDRESS ?= 0x1f80

# fuses
FUSEL ?= 0x2f
FUSEH ?= 0x90
# FUSEE ?= 0xff
# LOCK ?= 0xff

CCFLAGS += -include $(realpath ../boards/$(BOARD).h)

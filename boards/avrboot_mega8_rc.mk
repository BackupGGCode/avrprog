# cpu type
MMCU ?= atmega8

# cpu clock
F_CPU ?= 8000000

# bootloader addresses
BOOT_ADDRESS ?= 0x1800
PROGPG_ADDRESS ?= 0x1f80

# fuses
FUSEL ?= 0x24
FUSEH ?= 0x90
# FUSEE ?= 0xff
# LOCK ?= 0xff

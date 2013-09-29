# cpu type
MMCU ?= atmega162

# cpu clock
F_CPU ?= 8000000

# bootloader addresses
BOOT_ADDRESS ?= 0x3800
PROGPG_ADDRESS ?= 0x3f80

# fuses
FUSEL ?= 0xa2
FUSEH ?= 0xd0
FUSEE ?= 0xfb
# LOCK ?= 0xff

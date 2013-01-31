# cpu type
MMCU ?= atmega168

# cpu clock
F_CPU ?= 8000000

# bootloader addresses
BOOT_ADDRESS ?= 0x3800
PROGPG_ADDRESS ?= 0x3f80

# fuses
FUSEL ?= 0xe2
FUSEH ?= 0xdf
FUSEE ?= 0xf8
# LOCK ?= 0xff

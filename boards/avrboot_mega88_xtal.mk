# cpu type
MMCU ?= atmega88

# cpu clock
F_CPU ?= 7372800

# bootloader addresses
BOOT_ADDRESS ?= 0x1800
PROGPG_ADDRESS ?= 0x1f80

# fuses
FUSEL ?= 0xe7
FUSEH ?= 0xdf
FUSEE ?= 0xf8
# LOCK ?= 0xff

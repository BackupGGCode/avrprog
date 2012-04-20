# usage:
#   make BUILD=avrboot [target]

BUILD ?= avrboot avrprog

all clean hex bin srec meminfo dump dumpf:
	@for i in $(BUILD); do echo "  MAKE   "$$i $@; make -f $$i.mk $@; done

avrboot_flash:
	@echo "  MAKE   "$@
	@make -f avrboot.mk flash

avrprog_upload:
	@echo "  MAKE   "$@
	@make -f avrprog.mk upload

fuses:
	@echo "  MAKE   "$@
	@make -f pg.mk fuses

dump_flash:
	@echo "  MAKE   "$@
	@make -f pg.mk dump_flash

all: avrboot avrprog

avrboot:
	@echo "  MAKE   "$@
	@make -f avrboot.mk all

avrprog:
	@echo "  MAKE   "$@
	@make -f avrprog.mk all

clean:
	@echo "  MAKE   "$@
	@make -f avrboot.mk $@
	@make -f avrprog.mk $@

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

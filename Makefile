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

avrprog_upload:
	@echo "  MAKE   "$@
	@make -f avrprog.mk upload

avrboot_flash:
	@echo "  MAKE   "$@
	@make -f avrboot.mk flash

fuses:
	@echo "  MAKE   "$@
	@make -f pg.mk fuses

dump:
	@echo "  MAKE   "$@
	@make -f pg.mk dump

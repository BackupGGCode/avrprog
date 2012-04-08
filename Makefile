all: avrboot avrprog

avrboot:
	make -f avrboot.mk all

avrprog:
	make -f avrprog.mk all

clean:
	make -f avrboot.mk $@
	make -f avrprog.mk $@

avrprog_upload:
	make -f avrprog.mk upload

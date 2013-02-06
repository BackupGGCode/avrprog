#include <avr/boot.h>

#include "selfpg.h"

char programPage(uint16_t page, uint16_t *buf, uint16_t magic) __attribute__ ((section (".progpg")));

char programPage(uint16_t page, uint16_t *buf, uint16_t magic) {
	if (magic != PG_MAGIC) return 1;
	if (page >= PROGPG_ADDRESS) return 1;
	boot_spm_interrupt_disable();
	eeprom_busy_wait();
	boot_page_erase(page);
	boot_spm_busy_wait();
	uint16_t i;
	for (i = 0; i < SPM_PAGESIZE; i += 2) {
		boot_page_fill(page + i, *buf++);
	}
	boot_page_write(page);
	boot_spm_busy_wait();
	boot_rww_enable();
	return 0;
}


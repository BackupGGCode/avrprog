/* name:    AVR programmer
 * desc:    SPI programmer for Atmel AVR CPU
 * arch:    AVR CPU, optimized for ATmega8
 * author:  (c)2012 Pavel Revak <pavel.revak@gmail.com>
 * licence: GPL
 */

/* TODO:
 * - eeprom write
 * - eeprom read
 * - extended adresses support (mega256)
 */

#include <util/delay.h>
#include <avr/io.h>
#include <avr/sleep.h>
#include <avr/interrupt.h>
#include <avr/eeprom.h>
#include <avr/wdt.h>
#include <avr/boot.h>
#include <avr/pgmspace.h>

#include "drv/uart.h"
#include "drv/spiprog.h"

/*
** bluetooth module send this after init and never answer on this!!!:
!!! THIS IS BETA RELEASE AND MAY BE USED FOR EVALUATION PURPOSES ONLY !!!

WRAP THOR AI (2.1.0 build 15)
Copyright (c) 2003-2005 Bluegiga Technologies Inc.
READY.

** after connected device (comupter):
RING 0 5c:59:48:cc:73:a0 1 RFCOMM

** after disconnected device:
NO CARRIER 0 ERROR 0
*/

#define NAME "avrprog"
#define VERSION "v1.0"
#define CPU "atmega8"
#define COPYRIGHT "(c)2012 pavel.revak@gmail.com"

#define PG_MAGIC 0x4321

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

static unsigned char avrCmd(unsigned char data1, unsigned char data2, unsigned char data3, unsigned char data4) {
	spiprogSend(data1);
	spiprogSend(data2);
	spiprogSend(data3);
	return spiprogSend(data4);
}

//void printString(const char *str) {
//	while(*str) {
//		uartPutChar(*str++);
//	}
//}

void printStringP(PGM_P str) {
	char ch;
	while(ch = pgm_read_byte(str++)) {
		uartPutChar(ch);
	}
}

void printNum(unsigned long n) {
	if (n > 9) {
		printNum(n / 10);
	}
	uartPutChar('0' + n % 10);
}

void printHex4(unsigned char n) {
	n &= 0x0f;
	uartPutChar((n < 10) ? n + '0' : n + 'a' - 10);
}

void printHex8(uint8_t n) {
	printHex4(n >> 4);
	printHex4(n);
}

void printHex16(uint16_t n) {
	printHex8((uint8_t)(n >> 8));
	printHex8((uint8_t)n);
}

void printHex24(uint32_t n) {
	printHex8((uint8_t)(n >> 16));
	printHex8((uint8_t)(n >> 8));
	printHex8((uint8_t)n);
}

char compareString(PGM_P str1, char *str2) {
	while (pgm_read_byte(str1++) == *str2++) {
		if (pgm_read_byte(str1) == 0 && *str2 == 0) return 1;
	}
	return 0;
}

char readHex4(char ch) {
	char h = -1;
	if (ch >= '0' && ch <= '9') h = ch -'0';
	if (ch >= 'a' && ch <= 'f') h = ch -'a' + 10;
	return h;
}

char readHexNum(char *str, unsigned char *out, char bytes) {
	while (bytes-- > 0) {
		unsigned char h = readHex4(*str++) << 4;
		if (h == -1) return 1;
		h |= readHex4(*str++);
		if (h == -1) return 1;
		out[bytes] = h;
	}
	return 0;
}

char readHexString(const char *str, unsigned char *buffer, unsigned char size) {
	char count = 0;
	char crc8 = 0x00;
	while (count++ < size && *str) {
		unsigned char h = readHex4(*str++) << 4;
		if (h == -1) return -1;
		h |= readHex4(*str++);
		if (h == -1) return -1;
		*buffer++ = h;
		crc8 ^= h;
	}
	buffer--;
	count--;
	while (count++ <= size) *buffer++ = 0xff;
	if (crc8) return -1;
	return count;
}

char readHexStringToSpi(const char *str, unsigned int blockSize) {
	unsigned char count = 0;
	char crc8 = 0x00;
	char h1;
	char h2;
	blockSize >>= 1;
	while (*str) {
		h1 = readHex4(*str++);
		if (h1 == -1) return 1;
		h2 = readHex4(*str++);
		if (h2 == -1) return 2;
		h2 |= (h1 << 4);
		crc8 ^= h2;
		if (*str == 0) {
			if (crc8 ) return 3;
			while (count < blockSize) {
				avrCmd(0x40, 0x00, count, 0xff);
				avrCmd(0x48, 0x00, count, 0xff);
				count++;
			}
			return 0;
		}
		if (count >= blockSize) return 3;
		avrCmd(0x40, 0x00, count, h2);
		h1 = readHex4(*str++);
		if (h1 == -1) return 4;
		h2 = readHex4(*str++);
		if (h2 == -1) return 5;
		h2 |= (h1 << 4);
		crc8 ^= h2;
		avrCmd(0x48, 0x00, count, h2);
		count++;
	}
	return 6;
}

void printState(char state) {
	if (state) {
		printStringP(PSTR("enabled\n"));
	} else {
		printStringP(PSTR("disabled\n"));
	}
}

static char ready = 0;
static char echo = 0;
static char spiprogEnabled = 0;
void readCommand(char **cmd, char count) {
	if (compareString(PSTR("hello"), cmd[0])) {
		ready = 1;
		printStringP(PSTR("\nhello\ndevice " NAME " " VERSION "\n"));
	} else if (ready && compareString(PSTR("spi"), cmd[0])) {
		if (count > 1) {
			if (compareString(PSTR("enable"), cmd[1])) {
				/* clear reset */
				PORTB &= ~ _BV(PORTB2);
				/* enable spi */
				spiprogEnable();
				_delay_ms(5);
				/* set reset */
				PORTB |= _BV(PORTB2);
				_delay_ms(5);
				/* clear reset */
				PORTB &= ~ _BV(PORTB2);
				_delay_ms(5);
				/* avrprog start sequence */
				spiprogSend(0xac);
				spiprogSend(0x53);
				unsigned char tmp = spiprogSend(0x00);
				spiprogSend(0x00);
				if (tmp == 0x53) {
					spiprogEnabled = 1;
					printStringP(PSTR("spi enable ok\nsignature "));
					printHex8(avrCmd(0x30, 0x00, 0x00, 0x00));
					uartPutChar(' ');
					printHex8(avrCmd(0x30, 0x00, 0x01, 0x00));
					uartPutChar(' ');
					printHex8(avrCmd(0x30, 0x00, 0x02, 0x00));
					uartPutChar('\n');
				} else {
					spiprogEnabled = 0;
					/* disable spi */
					spiprogDisable();
					/* set reset */
					PORTB |= _BV(PORTB2);
					printStringP(PSTR("spi enable error\n"));
				}
			} else if (spiprogEnabled) {
				unsigned char tmp;
				if (compareString(PSTR("disable"), cmd[1])) {
					spiprogEnabled = 0;
					/* disable spi */
					spiprogDisable();
					/* set reset */
					PORTB |= _BV(PORTB2);
					printStringP(PSTR("spi disable ok\n"));
				} else if (compareString(PSTR("lock"), cmd[1])) {
					if (count > 2 && !readHexNum(cmd[2], &tmp, 1)) {
						/* write lock */
						avrCmd(0xac, 0xe0, 0x00, tmp);
						_delay_ms(10);
					}
					/* read lock */
					printStringP(PSTR("lock "));
					printHex8(avrCmd(0x58, 0x00, 0x00, 0x00));	/// LOCK
					uartPutChar('\n');
				} else if (compareString(PSTR("fusel"), cmd[1])) {
					if (count > 2 && !readHexNum(cmd[2], &tmp, 1)) {
						/* write fuse low */
						avrCmd(0xac, 0xa0, 0x00, tmp);
						_delay_ms(10);
					}
					/* read fuse low */
					printStringP(PSTR("fusel "));
					printHex8(avrCmd(0x50, 0x00, 0x00, 0x00));	/// LOW
					uartPutChar('\n');
				} else if (compareString(PSTR("fuseh"), cmd[1])) {
					if (count > 2 && !readHexNum(cmd[2], &tmp, 1)) {
						/* write fuse low */
						avrCmd(0xac, 0xa8, 0x00, tmp);
						_delay_ms(10);
					}
					/* read fuse high */
					printStringP(PSTR("fuseh "));
					printHex8(avrCmd(0x58, 0x08, 0x00, 0x00));	/// HIGH
					uartPutChar('\n');
				} else if (compareString(PSTR("fusee"), cmd[1])) {
					if (count > 2 && !readHexNum(cmd[2], &tmp, 1)) {
						/* write fuse low */
						avrCmd(0xac, 0xa4, 0x00, tmp);
						_delay_ms(10);
					}
					/* read fuse ext */
					printStringP(PSTR("fusee "));
					printHex8(avrCmd(0x50, 0x08, 0x00, 0x00));	/// EXT
					uartPutChar('\n');
				} else if (compareString(PSTR("cal"), cmd[1])) {
					/* read calibration byte */
					printStringP(PSTR("cal "));
					printHex8(avrCmd(0x38, 0x00, 0x00, 0x00));	/// CALIB
					uartPutChar('\n');
				} else if (compareString(PSTR("flash"), cmd[1])) {
					if (count > 2) {
						if (compareString(PSTR("read"), cmd[2])) {
							unsigned int addrFrom;
							unsigned int addrTo;
							if (count != 5 || readHexNum(cmd[3], (unsigned char *)&addrFrom, 3) || readHexNum(cmd[4], (unsigned char *)&addrTo, 3) || (addrFrom > addrTo)) {
								printStringP(PSTR("bad parameters\n"));
							} else {
								addrFrom >>= 1;
								addrTo >>= 1;
								printStringP(PSTR("data "));
								printHex24(addrFrom << 1);
								uartPutChar(' ');
								char crc8 = 0;
								while (1) {
									char tmp = avrCmd(0x20, (unsigned char)(addrFrom >> 8), (unsigned char)addrFrom, 0x00);
									crc8 ^= tmp;
									printHex8(tmp);
									tmp = avrCmd(0x28, (unsigned char)(addrFrom >> 8), (unsigned char)addrFrom, 0x00);
									crc8 ^= tmp;
									printHex8(tmp);
									if (addrFrom++ == addrTo) {
										printHex8(crc8);
										uartPutChar('\n');
										break;
									}
									if ((addrFrom % 16) == 0) {
										printHex8(crc8);
										crc8 = 0;
										printStringP(PSTR("\ndata "));
										printHex24(addrFrom << 1);
										uartPutChar(' ');
										wdt_reset();
									}
								}
							}
						} else if (compareString(PSTR("write"), cmd[2])) {
							unsigned long addr;
							unsigned int blockSize;
							char errorCode;
							if (count != 6 || readHexNum(cmd[3], (unsigned char *)&blockSize, 2) || readHexNum(cmd[4], (unsigned char *)&addr, 3)) {
								printStringP(PSTR("parameters error\n"));
							} else if (addr % (unsigned long)blockSize) {
								printStringP(PSTR("address error\n"));
							} else if (errorCode = readHexStringToSpi(cmd[5], blockSize)) {
								printStringP(PSTR("data error: "));
								printNum(errorCode);
								uartPutChar('\n');
							} else {
								addr >>= 1;
								avrCmd(0x4c, (unsigned char)(addr >> 8), (unsigned char)addr, 0);
								_delay_ms(10);
								printStringP(PSTR("flash ok\n"));
							}
						} else {
							printStringP(PSTR("spi flash\nunknown command\n"));
						}
					}
				} else if (compareString(PSTR("eeprom"), cmd[1])) {
					printStringP(PSTR("not implemented\n"));
					// TODO
				} else if (compareString(PSTR("erase"), cmd[1])) {
					/* chip erase */
					avrCmd(0xac, 0x80, 0x00, 0x00);
					_delay_ms(20);
					printStringP(PSTR("erase ok\n"));
				} else {
					printStringP(PSTR("spi\nunknow command\n"));
				}
			} else {
				printStringP(PSTR("spi not connected\n"));
			}
		}
	} else if (ready && compareString(PSTR("echo"), cmd[0])) {
		if (count == 2) {
			echo = (*cmd[1] != '0');
		}
		printStringP(PSTR("echo "));
		uartPutChar(echo + '0');
		uartPutChar('\n');
	} else if (ready && compareString(PSTR("reboot"), cmd[0])) {
		printStringP(PSTR("rebooting..\n"));
		wdt_enable(WDTO_250MS);
		while(1);
	} else if (ready && compareString(PSTR("flashboot"), cmd[0])) {
		/* flash <addr_16bit> <PG_MAGIC> <data_SPM_PAGESIZE> */
		static uint16_t addr;
		static uint16_t pgMagic;
		static char buff[SPM_PAGESIZE + 1];
		if (count != 4 || readHexNum(cmd[1], (unsigned char *)&addr, 2) || readHexNum(cmd[2], (unsigned char *)&pgMagic, 2)) {
			printStringP(PSTR("bad parameters\n"));
		} else if (readHexString(cmd[3], buff, SPM_PAGESIZE) == -1) {
			printStringP(PSTR("data error\n"));
		} else if (programPage(addr, (uint16_t *)buff, pgMagic)) {
			printStringP(PSTR("flash error\n"));
		} else {
			printStringP(PSTR("flash ok\n"));
		}
	} else if (ready && compareString(PSTR("bootloader"), cmd[0])) {
		cli();
		// DISABLE TWI
		TWAR = 0x00;
		TWCR = 0x00;
		// DISABLE COUNTER
		TCCR0 = 0x00;
		TCCR1A = 0x00;
		TCCR1B = 0x00;
		TCCR2 = 0x00;
		TIMSK = 0x00;
		// DISABLE SERIAL
		UBRRH = 0x00;
		UBRRL = 0x00;
		UCSRA = 0x00;
		UCSRB = 0x00;
		UCSRC = 0x00;
		// SET PUD (to stay in bootloader)
		SFIOR = _BV(PUD);

		wdt_enable(WDTO_2S);
		wdt_reset();

		__asm__("ldi r30, 0x00");
		__asm__("ldi r31, 0x0c");
		__asm__("ijmp");
	} else if (compareString(PSTR("NO"), cmd[0])) {
		/* COMMAND FROM BLUETOOTH MODULE BLUEGIGA WT12 - client disconnected */
		if (spiprogEnabled) {
			spiprogEnabled = 0;
			/* disable spi */
			spiprogDisable();
			/* set reset */
			PORTB |= _BV(PORTB2);
		}
		ready = 0;
		return;
	} else if (ready) {
		printStringP(PSTR("unknown command\n"));
	} else if (!ready) return;
	printStringP(PSTR("ready\n"));
}

char split(char *str, char **out, char max) {
	char count = 0;
	char inWord = 0;
	while (*str != 0) {
		if (*str == ' ') {
			if (inWord) {
				*str = 0;
				inWord = 0;
			}
		} else if (!inWord) {
			out[count++] = str;
			if (count == max) break;
			inWord = 1;
		}
		str++;
	}
	return count;
}

#define BUFFER_SIZE 640
#define MAX_CMD_SPLIT 10

int main( void ) {
	// enable watchdog..
	wdt_enable(WDTO_2S);
	wdt_reset();

	DDRB |= _BV(DDB2);
	PORTB |= _BV(PORTB2);

	uartOpen(115200UL);
	spiprogInit();

	SFIOR &= ~ _BV(PUD);

	sei();

	static char buffer[BUFFER_SIZE];
	unsigned int index = 0;

	while(1) {
		wdt_reset();
		char ch = uartGetChar();
		if (ch == 0) continue;
		if (ready && echo) uartPutChar(ch);
		if (ch != '\n' && ch != '\r') {
			buffer[index++] = (char)ch;
			if (index >= BUFFER_SIZE) index = 0;
			buffer[index] = 0;
			continue;
		};
		if (index == 0 || ch != '\n') continue;
		static char *cmd[MAX_CMD_SPLIT];
		char count = split(buffer, cmd, MAX_CMD_SPLIT);
		if (count > 0) readCommand(cmd, count);
		index = 0;
		buffer[index] = 0;
	}

	return(0);
}

/* name:    AVR bootloader
 * desc:    bootloader for Atmel AVR CPU
 * arch:    AVR CPU
 * author:  (c)2012 Pavel Revak <pavel.revak@gmail.com>
 * licence: GPL
 */

#include <avr/io.h>
#include <avr/sleep.h>
#include <avr/interrupt.h>
#include <avr/wdt.h>
#include <avr/boot.h>
#include <avr/pgmspace.h>
#include <util/delay.h>

#include "lib/cpudefs.h"
#include "drv/uart.h"
#include "drv/selfpg.h"

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

#define NAME "avrboot"
#define VERSION "v1.0"
#define COPYRIGHT "2012 pavel.revak@gmail.com"

static uint16_t crc16_update(uint16_t crc, uint8_t a) {
	uint8_t i;
	crc ^= a;
	for (i = 0; i < 8; i++) {
		if (crc & 1)
			crc = (crc >> 1) ^ 0xA001;
		else
			crc = (crc >> 1);
	}
	return crc;
}

static uint8_t checkCrc() {
	uint16_t i;
	uint16_t size = pgm_read_word(BOOT_ADDRESS - 4);
	uint16_t crc16 = 0;
	if (size < 0x0020) return 0;
	if (size > BOOT_ADDRESS - 4) return 0;
	for (i = 0; i < size; i++) {
		crc16 = crc16_update (crc16, pgm_read_byte(i));
		wdt_reset();
	}
	return (crc16) == pgm_read_word(BOOT_ADDRESS - 2);
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

void printNum(unsigned int n) {
	if (n > 9) {
		printNum(n / 10);
	}
	uartPutChar('0' + n % 10);
}

//void printHex4(unsigned char n) {
//	n &= 0x0f;
//	uartPutChar((n < 10) ? n + '0' : n + 'a' - 10);
//}
//
//void printHex8(uint8_t n) {
//	printHex4(n >> 4);
//	printHex4(n);
//}
//
//void printHex16(uint16_t n) {
//	printHex8((uint8_t)(n >> 8));
//	printHex8((uint8_t)n);
//}

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
	while (count++ <= size && *str) {
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

static char ready = 0;
static uint8_t crcOk;
#ifdef USE_ECHO
static char echo = 0;
#endif

void readCommand(char **cmd, char count) {
	if (compareString(PSTR("hello"), cmd[0])) {
		ready = 1;
		printStringP(PSTR("\nhello\ndevice " NAME " " VERSION "\ncpu " CPU "\nbootaddr "));
		printNum(BOOT_ADDRESS);
		printStringP(PSTR("\npagesize "));
		printNum(SPM_PAGESIZE);
		printStringP(PSTR("\ncrc "));
		printStringP(crcOk ? PSTR("ok\n") : PSTR("error\n"));
#ifdef USE_ECHO
	} else if (ready && compareString(PSTR("echo"), cmd[0])) {
		if (count == 2) {
			echo = (*cmd[1] != '0');
		}
		printStringP(PSTR("echo "));
		uartPutChar(echo + '0');
		uartPutChar('\n');
#endif
	} else if (ready && compareString(PSTR("reboot"), cmd[0])) {
		printStringP(PSTR("rebooting..\n"));
		wdt_enable(WDTO_250MS);
		while(1);
	} else if (ready && compareString(PSTR("flash"), cmd[0])) {
		/* flash <addr_16bit> <PG_MAGIC> <data_SPM_PAGESIZE> */
		static uint16_t addr;
		static uint16_t pgMagic;
		static char buff[SPM_PAGESIZE + 1];
		if (count != 4 || readHexNum(cmd[1], (unsigned char *)&addr, 2) || readHexNum(cmd[2], (unsigned char *)&pgMagic, 2)) {
			printStringP(PSTR("parameters error\n"));
		} else if ((addr % SPM_PAGESIZE) || (addr >= BOOT_ADDRESS)) {
			printStringP(PSTR("address error\n"));
		} else if (readHexString(cmd[3], buff, SPM_PAGESIZE) == -1) {
			printStringP(PSTR("data error\n"));
		} else if (programPage(addr, (uint16_t *)buff, pgMagic)) {
			printStringP(PSTR("flash error\n"));
		} else {
			printStringP(PSTR("flash ok\n"));
		}
	//} else if (compareString(PSTR("RING"), cmd[0])) {
	//	/* COMMAND FROM BLUETOOTH MODULE BLUEGIGA WT12 - client connected */
	//	_delay_ms(100);
	//	uartPutChar('\n');
	//	printStringP(PSTR(NAME"\n"));
	} else if (compareString(PSTR("NO"), cmd[0])) {
		/* COMMAND FROM BLUETOOTH MODULE BLUEGIGA WT12 - client disconnected */
		ready = 0;
		return;
	} else if (ready) {
		printStringP(PSTR("command error\n"));
	} else if (!ready) return;
	printStringP(PSTR("ready\n"));
}

#define BUFFER_SIZE 256
#define MAX_CMD_SPLIT 5

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

int main() {
	crcOk = checkCrc();
	/* if CRC is OK, then we can start application */
	while (crcOk) {
		/* if PUD is cleared */
		/* (reset default PUD is set, but application can clear this bit) */
		/* .. then we stay in bootloader */
		if (getPUD()) break;
		/* test PINB2 (jumper - stay in bootloader) */
		/* turn on PULL UP on this pin */
		clrPUD();
		PORTB |= _BV(PORTB1);
		_delay_ms(10);
		/* if PINB1 is cleared (jumper is detected) */
		/* .. then we stay in bootloader */
		if (!((PINB >> PINB1) & 1)) break;
		/* start app */
		__asm__("ldi r30, 0x00");
		__asm__("ldi r31, 0x00");
		__asm__("ijmp");
	}
	/* enable watchdog.. */
	wdt_enable(WDTO_2S);
	wdt_reset();

	setIVCE();
	setIVSEL();

	uartOpen(115200UL);

	clrPUD();

	sei();

	static char buffer[BUFFER_SIZE];
	unsigned char index = 0;

	while(1) {
		wdt_reset();
		char ch = uartGetChar();
		if (ch == 0) continue;
#ifdef USE_ECHO
		if (ready && echo) uartPutChar(ch);
#endif
		if (ch != '\n' && ch != '\r') {
			buffer[index++] = (char)ch;
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

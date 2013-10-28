/* name:    AVR programmer
 * desc:    SPI programmer for Atmel AVR CPU
 * arch:    AVR CPU
 * author:  (c)2012 Pavel Revak <pavel.revak@gmail.com>
 * licence: GPL
 */

/* TODO:
 * - eeprom write
 * - eeprom read
 * - extended adresses support (mega256)
 * - configurable spi speed
 * - rewrite this for stdio
 */

#include <avr/io.h>
#include <avr/sleep.h>
#include <avr/interrupt.h>
#include <avr/eeprom.h>
#include <avr/wdt.h>
#include <avr/boot.h>
#include <avr/pgmspace.h>
#include <util/delay.h>

#include "lib/cpudefs.h"
#include "drv/uart/uart.h"
#include "drv/spiprog/spiprog.h"
#include "drv/selfpg/selfpg.h"

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
#define VERSION "v2.0"
#define COPYRIGHT "(c)2012-2013 pavel.revak@gmail.com"

static char ready = 0;
static char echo = 0;
static char avrIspConnected = 0;


void printString(const char *str) {
	while(*str) {
		uartPutChar(*str++);
	}
}

void printStringP(PGM_P str) {
	char ch;
	while((ch = pgm_read_byte(str++))) {
		uartPutChar(ch);
	}
}

void printBoolP(char state, PGM_P off, PGM_P on) {
	if (state) {
		printStringP(on);
	} else {
		printStringP(off);
	}
}

void printNum(unsigned long n) {
	if (n > 9) {
		printNum(n / 10);
	}
	uartPutChar('0' + n % 10);
}

void printBcd(unsigned char n) {
	n &= 0x0f;
	uartPutChar((n < 10) ? n + '0' : n + 'a' - 10);
}

void printHex8(uint8_t n) {
	printBcd(n >> 4);
	printBcd(n);
}

void printHex16(uint16_t n) {
	printHex8((uint8_t)(n >> 8));
	printHex8((uint8_t)n);
}

void printHex24(unsigned long n) {
	printHex8((uint8_t)(n >> 16));
	printHex8((uint8_t)(n >> 8));
	printHex8((uint8_t)n);
}

char parseBcd(char ch) {
	if (ch >= '0' && ch <= '9') return ch - '0';
	if (ch >= 'a' && ch <= 'f') return ch - 'a' + 10;
	if (ch >= 'A' && ch <= 'F') return ch - 'A' + 10;
	return -1;
}

char parseHexNum(char *str, unsigned char *out, unsigned char bytes) {
	while (bytes-- > 0) {
		unsigned char h = parseBcd(*str++) << 4;
		if (h == -1) return -1;
		h |= parseBcd(*str++);
		if (h == -1) return -1;
		out[bytes] = h;
	}
	return 0;
}

char compareStringP(const char *str1, PGM_P str2) {
	while (*str1 == pgm_read_byte(str2)) {
		if (*str1 == 0) return 1;
		str1++;
		str2++;
	}
	return 0;
}

char uartReadChar() {
	char ch;
	do {
		wdt_reset();
		ch = uartGetChar();
	} while (ch == 0x00 || ch == '\r');
	if (ready && echo) uartPutChar(ch);
	return ch;
}

/** read string from uart
- remove spaces on begin
- end on space or EOL
@param out      output to store string
@param len      buffer length
@return         - ' ' if string ends with space
                - '\n' if ends with EOL
                - 0 if string is longer than len */
char uartReadString(char *out, char len) {
	char empty = 1;
	while(len--) {
		char ch = uartReadChar();
		if (empty && ch == ' ') continue;
		if (ch == '\n' || ch == ' ') {
			*out = 0x00;
			return ch;
		}
		empty = 0;
		*out++ = ch;
	}
	return 0;
}

/** wait for end of line
@param ch       last readed character */
void uartWaitForEol(char ch) {
	while (ch != '\n') {
		ch = uartReadChar();
	}
}

static unsigned char avrCmd(unsigned char data1, unsigned char data2, unsigned char data3, unsigned char data4) {
	spiprogSend(data1);
	spiprogSend(data2);
	spiprogSend(data3);
	return spiprogSend(data4);
}

void avrDisconnectCommand() {
	avrIspConnected = 0;
	/* disable spi */
	spiprogDisable();
	/* set reset */
	PORTB |= _BV(PORTB2);
}

void clientDisconnectCommand(char ch) {
	ready = 0;
	echo = 0;
	uartWaitForEol(ch);
	if (avrIspConnected) avrDisconnectCommand();
}

void tooLongCommand() {
	uartWaitForEol(0);
	printStringP(PSTR("error: command is too long\n"));
}

void badParam(char ch) {
	uartWaitForEol(ch);
	printStringP(PSTR("error: bad param\n"));
}

void unknownCommand(char ch, char *command) {
	uartWaitForEol(ch);
	printStringP(PSTR("error: unknown command "));
	printString(command);
	uartPutChar('\n');
}

void helloCommand() {
	ready = 1;
	printStringP(PSTR("\nhello\ndevice " NAME " " VERSION "\n"));
}

void rebootCommand(char ch) {
	uartWaitForEol(ch);
	printStringP(PSTR("rebooting..\n"));
	wdt_enable(WDTO_250MS);
	while(1);
}

void bootloaderCommand(char ch) {
	uartWaitForEol(ch);
	printStringP(PSTR("starting bootloader..\n"));
	_delay_ms(10);
	cli();
	// spiprogClose();
	uartClose();
	/* SET PUD to stay in bootloader */
	setPUD();

	wdt_enable(WDTO_2S);
	wdt_reset();

	__asm__("ldi r30, 0x00");
	__asm__("ldi r31, 0x0c");
	__asm__("ijmp");
}

void echoCommand(char ch) {
	if (ch != '\n') {
		char param[2];
		ch = uartReadString(param, 2);
		if (ch == '\n' && (*param == '0' || *param == '1')) {
			echo = *param - '0';
		} else {
			badParam(ch);
			return;
		}
	}
	printStringP(PSTR("echo "));
	printBoolP(echo, PSTR("disabled\n"), PSTR("enabled\n"));
}

void avrStatus() {
	printStringP(PSTR("avr "));
	printBoolP(avrIspConnected, PSTR("disconnected\n"), PSTR("connected\n"));
}

void avrConnectCommand() {
	/* clear reset */
	PORTB &= ~ _BV(PORTB2);
	/* enable spi */
	spiprogEnable();
	_delay_ms(20);
	/* set reset */
	PORTB |= _BV(PORTB2);
	_delay_ms(20);
	/* clear reset */
	PORTB &= ~ _BV(PORTB2);
	_delay_ms(20);
	/* avrprog start sequence */
	spiprogSend(0xac);
	spiprogSend(0x53);
	unsigned char tmp = spiprogSend(0x12);
	spiprogSend(0x00);
	_delay_ms(20);
	if (tmp == 0x53) {
		avrIspConnected = 1;
		printStringP(PSTR("signature "));
		printHex8(avrCmd(0x30, 0x00, 0x00, 0x00));
		uartPutChar(' ');
		printHex8(avrCmd(0x30, 0x00, 0x01, 0x00));
		uartPutChar(' ');
		printHex8(avrCmd(0x30, 0x00, 0x02, 0x00));
		uartPutChar('\n');
	} else {
		avrDisconnectCommand();
		printStringP(PSTR("error: connecting to avr "));
		printHex8(tmp);
		uartPutChar('\n');
	}
}

void avrFlashEraseCommand() {
	/* chip erase */
	avrCmd(0xac, 0x80, 0x00, 0x00);
	_delay_ms(20);
	printStringP(PSTR("avr flash erase done\n"));
}

void avrFlashReadCommand(char ch) {
	if (ch == '\n') return;
	char param[8];
	ch = uartReadString(param, 8);
	if (ch == 0 || ch == '\n') {
		badParam(ch);
		return;
	}
	unsigned long addrFrom = 0;
	if (parseHexNum(param, (unsigned char *)&addrFrom, 3)) {
		badParam(ch);
		return;
	}
	ch = uartReadString(param, 8);
	if (ch != '\n') {
		badParam(ch);
		return;
	}
	unsigned long addrTo = 0;
	if (parseHexNum(param, (unsigned char *)&addrTo, 3)) {
		badParam(ch);
		return;
	}
	while (addrFrom <= addrTo) {
		wdt_reset();
		printStringP(PSTR("data "));
		printHex24(addrFrom);
		uartPutChar(' ');
		char crc8 = 0;
		while (addrFrom <= addrTo) {
			char tmp = avrCmd(
				(addrFrom & 1) ? 0x28 : 0x20,
				(unsigned char)(addrFrom >> 9),
				(unsigned char)(addrFrom >> 1),
				0x00
			);
			crc8 ^= tmp;
			printHex8(tmp);
			addrFrom++;
			if (addrFrom % 32 == 0) break;
		}
		printHex8(crc8);
		uartPutChar('\n');
	}
	printStringP(PSTR("avr flash read done\n"));
}

char avrFlashWriteBuffer(unsigned char bufferSize) {
	unsigned char bufferAddress = 0;
	char crc8 = 0x00;
	while (1) {
		char param[3];
		char ch = uartReadString(param, 2);
		if (ch != 0) {
			uartWaitForEol(ch);
			printStringP(PSTR("unexpected end of data\n"));
			return -1;
		}
		unsigned char data = 0xff;
		if (parseHexNum(param, (unsigned char *)&data, 1)) {
			uartWaitForEol(ch);
			printStringP(PSTR("wrong data 0\n"));
			return -1;
		}
		crc8 ^= data;
		ch = uartReadString(param, 2);
		if (ch != 0) {
			if (crc8) {
				uartWaitForEol(ch);
				printStringP(PSTR("wrong checksum: "));
				printHex8(crc8);
				uartPutChar('\n');
				return -1;
			}
			while (bufferAddress < bufferSize) {
				avrCmd(0x40, 0x00, bufferAddress, 0xff);
				avrCmd(0x48, 0x00, bufferAddress, 0xff);
				bufferAddress++;
			}
			return 0;
		}
		if (bufferAddress >= bufferSize) {
			uartWaitForEol(ch);
			printStringP(PSTR("too long data\n"));
			return -1;
		}
		avrCmd(0x40, 0x00, bufferAddress, data);
		if (parseHexNum(param, (unsigned char *)&data, 1)) {
			uartWaitForEol(ch);
			printStringP(PSTR("wrong data 1\n"));
			return -1;
		}
		crc8 ^= data;
		avrCmd(0x48, 0x00, bufferAddress, data);
		bufferAddress++;
	}
	return 6;
}

void avrFlashWriteCommand(char ch) {
	if (ch == '\n') return;
	char param[8];
	ch = uartReadString(param, 8);
	if (ch == 0 || ch == '\n') {
		badParam(ch);
		return;
	}
	unsigned char bufferSize = 0;
	if (parseHexNum(param, (unsigned char *)&bufferSize, 1)) {
		badParam(ch);
		return;
	}
	ch = uartReadString(param, 8);
	if (ch == 0 || ch == '\n') {
		badParam(ch);
		return;
	}
	unsigned long addr = 0;
	if (parseHexNum(param, (unsigned char *)&addr, 3)) {
		badParam(ch);
		return;
	}
	if (addr % (unsigned long)bufferSize) {
		uartWaitForEol(ch);
		printStringP(PSTR("address error\n"));
		return;
	}
	if ((avrFlashWriteBuffer(bufferSize))) {
		return;
	}
	addr >>= 1;
	avrCmd(0x4c, (unsigned char)(addr >> 8), (unsigned char)addr, 0);
	_delay_ms(5);
	printStringP(PSTR("avr flash write done\n"));
}

void avrFlashCommand(char ch) {
	if (ch == '\n') return;
	char param[8];
	ch = uartReadString(param, 8);
	if (ch == 0) {
		badParam(ch);
		return;
	}
	if (compareStringP(param, PSTR("erase"))) {
		avrFlashEraseCommand(ch);
	} else if (compareStringP(param, PSTR("read"))) {
		avrFlashReadCommand(ch);
	} else if (compareStringP(param, PSTR("write"))) {
		avrFlashWriteCommand(ch);
	} else {
		badParam(ch);
		return;
	}
}

void avrFuseWriteReadCommand(char ch, unsigned char wrByte2, unsigned char rdByte1, unsigned char rdByte2, char* fuseId) {
	unsigned char fuseValue;
	if (ch == ' ') {
		if (wrByte2 == 0x00) {
			badParam(ch);
			return;
		}
		char param[4];
		ch = uartReadString(param, 4);
		if (ch != '\n') {
			badParam(ch);
			return;
		}
		if (parseHexNum(param, (unsigned char *)&fuseValue, 1)) {
			badParam(ch);
			return;
		}
		avrCmd(0xac, wrByte2, 0x00, fuseValue);
		_delay_ms(10);
	}
	fuseValue = avrCmd(rdByte1, rdByte2, 0x00, 0x00);
	printStringP(PSTR("fuse "));
	printString(fuseId);
	uartPutChar(' ');
	printHex8(fuseValue);
	uartPutChar('\n');
}

void avrFuseCommand(char ch) {
	if (ch == '\n') return;
	char param[8];
	ch = uartReadString(param, 8);
	if (ch == 0) {
		badParam(ch);
		return;
	}
	if (compareStringP(param, PSTR("low"))) {
		avrFuseWriteReadCommand(ch, 0xa0, 0x50, 0x00, param);	/* LOW */
	} else if (compareStringP(param, PSTR("high"))) {
		avrFuseWriteReadCommand(ch, 0xa8, 0x58, 0x08, param);	/* LOW */
	} else if (compareStringP(param, PSTR("extend"))) {
		avrFuseWriteReadCommand(ch, 0xa4, 0x50, 0x08, param);	/* LOW */
	} else if (compareStringP(param, PSTR("lock"))) {
		avrFuseWriteReadCommand(ch, 0xe0, 0x58, 0x00, param);	/* LOW */
	} else if (compareStringP(param, PSTR("calib"))) {
		avrFuseWriteReadCommand(ch, 0x00, 0x38, 0x00, param);	/* LOW */
	} else {
		badParam(ch);
		return;
	}
}

void avrCommand(char ch) {
	if (ch == '\n') {
		avrStatus();
		return;
	}
	char param[12];
	ch = uartReadString(param, 12);
	if (ch == 0) {
		badParam(ch);
	} else if (ch == '\n' && compareStringP(param, PSTR("connect"))) {
		avrConnectCommand();
		avrStatus();
	} else if (ch == '\n' && compareStringP(param, PSTR("disconnect"))) {
		avrDisconnectCommand();
		avrStatus();
	} else if (!avrIspConnected) {
		uartWaitForEol(ch);
		printStringP(PSTR("error: not connected to avr\n"));
	} else if (compareStringP(param, PSTR("fuse"))) {
		avrFuseCommand(ch);
	} else if (compareStringP(param, PSTR("flash"))) {
		avrFlashCommand(ch);
	} else {
		badParam(ch);
	}
}

void proccessCommand(char ch) {
	char command[12];
	ch = uartReadString(command, 12);
	if (ch == '\n' && compareStringP(command, PSTR("hello"))) {
		helloCommand();
	} else if (!ready) {
		return;
	} else if (ch == 0) {
		tooLongCommand();
	} else if (!*command) {
		return;
	} else if (compareStringP(command, PSTR("bye")) || compareStringP(command, PSTR("NO"))) {
		/* command from bluetooth module bluegiga wt12 - client disconnected or lost connection: */
		/* NO CARRIER 0 ERROR 0 */
		clientDisconnectCommand(ch);
		return;
	} else if (compareStringP(command, PSTR("reboot"))) {
		rebootCommand(ch);
	} else if (compareStringP(command, PSTR("bootloader"))) {
		bootloaderCommand(ch);
	} else if (compareStringP(command, PSTR("echo"))) {
		echoCommand(ch);
	} else if (compareStringP(command, PSTR("avr"))) {
		avrCommand(ch);
	// } else if (compareStringP(command, PSTR("flashboot"))) {
	// 	flashbootCommand(cmd, count);
	} else {
		unknownCommand(ch, command);
	}
	printStringP(PSTR("ready\n"));
}

int main() {
	/* enable watchdog.. */
	wdt_enable(WDTO_2S);
	wdt_reset();

	DDRB |= _BV(DDB2);
	PORTB |= _BV(PORTB2);

	uartOpen(115200UL);
	spiprogInit();

	clrPUD();

	sei();

	while(1) {
		proccessCommand(0);
	}

	return(0);
}

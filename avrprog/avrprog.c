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
#define VERSION "v1.1"
#define COPYRIGHT "(c)2012 pavel.revak@gmail.com"

static unsigned char avrCmd(unsigned char data1, unsigned char data2, unsigned char data3, unsigned char data4) {
	spiprogSend(data1);
	spiprogSend(data2);
	spiprogSend(data3);
	return spiprogSend(data4);
}

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
	if (ch >= '0' && ch <= '9') return ch - '0';
	if (ch >= 'a' && ch <= 'f') return ch - 'a' + 10;
	return -1;
}

char readHexNum(char *str, unsigned char *out, unsigned char bytes) {
	while (bytes-- > 0) {
		unsigned char h = readHex4(*str++) << 4;
		if (h == -1) return 1;
		h |= readHex4(*str++);
		if (h == -1) return 1;
		out[bytes] = h;
	}
	return 0;
}

char readHexString(const char *str, unsigned char *buffer, unsigned int size) {
	unsigned int count = 0;
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
	blockSize >>= 1;
	while (*str) {
		char h1 = readHex4(*str++);
		if (h1 == -1) return 1;
		char h2 = readHex4(*str++);
		if (h2 == -1) return 2;
		h2 |= (h1 << 4);
		crc8 ^= h2;
		if (*str == 0) {
			if (crc8) return 3;
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

void helloCommand() {
	ready = 1;
	printStringP(PSTR("\nhello\ndevice " NAME " " VERSION "\n"));
}

void echoCommand(char **cmd, char count) {
	if (count == 1) {
		echo = (*cmd[0] != '0');
	}
	printStringP(PSTR("echo "));
	printState(echo);
}

void rebootCommand() {
	printStringP(PSTR("rebooting..\n"));
	wdt_enable(WDTO_250MS);
	while(1);
}

void bootloaderCommand() {
	printStringP(PSTR("starting bootloader..\n"));
	_delay_ms(10);
	cli();
	spiprogClose();
	uartClose();
	/* SET PUD to stay in bootloader */
	setPUD();

	wdt_enable(WDTO_2S);
	wdt_reset();

	__asm__("ldi r30, 0x00");
	__asm__("ldi r31, 0x0c");
	__asm__("ijmp");
}

void spiEnableCommand() {
	/* clear reset */
	PORTB &= ~ _BV(PORTB2);
	/* enable spi */
	spiprogEnable();
	_delay_ms(200);
	/* set reset */
	PORTB |= _BV(PORTB2);
	_delay_ms(200);
	/* clear reset */
	PORTB &= ~ _BV(PORTB2);
	_delay_ms(200);
	/* avrprog start sequence */
	spiprogSend(0xac);
	spiprogSend(0x53);
	unsigned char tmp = spiprogSend(0x12);
	spiprogSend(0x00);
	_delay_ms(200);
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
		printStringP(PSTR("spi enable error: "));
		printHex8(tmp);
		uartPutChar('\n');
	}
}

void spiDisableCommand() {
	spiprogEnabled = 0;
	/* disable spi */
	spiprogDisable();
	/* set reset */
	PORTB |= _BV(PORTB2);
	printStringP(PSTR("spi disable ok\n"));
}

void spiLockCommand(char **cmd, char count) {
	unsigned char tmp;
	if (count > 2 && !readHexNum(*cmd, &tmp, 1)) {
		/* write lock */
		avrCmd(0xac, 0xe0, 0x00, tmp);
		_delay_ms(10);
	}
	/* read lock */
	printStringP(PSTR("lock "));
	printHex8(avrCmd(0x58, 0x00, 0x00, 0x00));	/* LOCK */
	uartPutChar('\n');
}

void spiFuselCommand(char **cmd, char count) {
	unsigned char tmp;
	if (count > 2 && !readHexNum(*cmd, &tmp, 1)) {
		/* write fuse low */
		avrCmd(0xac, 0xa0, 0x00, tmp);
		_delay_ms(10);
	}
	/* read fuse low */
	printStringP(PSTR("fusel "));
	printHex8(avrCmd(0x50, 0x00, 0x00, 0x00));	/* LOW */
	uartPutChar('\n');
}

void spiFusehCommand(char **cmd, char count) {
	unsigned char tmp;
	if (count > 2 && !readHexNum(*cmd, &tmp, 1)) {
		/* write fuse high */
		avrCmd(0xac, 0xa8, 0x00, tmp);
		_delay_ms(10);
	}
	/* read fuse high */
	printStringP(PSTR("fuseh "));
	printHex8(avrCmd(0x58, 0x08, 0x00, 0x00));	/* HIGH */
	uartPutChar('\n');
}

void spiFuseeCommand(char **cmd, char count) {
	unsigned char tmp;
	if (count > 2 && !readHexNum(*cmd, &tmp, 1)) {
		/* write fuse ext */
		avrCmd(0xac, 0xa4, 0x00, tmp);
		_delay_ms(10);
	}
	/* read fuse ext */
	printStringP(PSTR("fusee "));
	printHex8(avrCmd(0x50, 0x08, 0x00, 0x00));	/* EXT */
	uartPutChar('\n');
}

void spiCalibrationByte() {
	/* read calibration byte */
	printStringP(PSTR("cal "));
	printHex8(avrCmd(0x38, 0x00, 0x00, 0x00));	/* CALIB */
	uartPutChar('\n');
}

void spiFlashReadCommand(char **cmd, char count) {
	uint32_t addrFrom = 0;
	uint32_t addrTo = 0;
	if (
		count != 2
		|| readHexNum(cmd[0], (unsigned char *)&addrFrom, 3)
		|| readHexNum(cmd[1], (unsigned char *)&addrTo, 3)
		|| (addrFrom > addrTo)
	) {
		printStringP(PSTR("bad parameters\n"));
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
}

void spiFlashWriteCommand(char **cmd, char count) {
	unsigned long addr;
	unsigned int blockSize;
	char errorCode;
	if (count != 3 || readHexNum(cmd[0], (unsigned char *)&blockSize, 2) || readHexNum(cmd[1], (unsigned char *)&addr, 3)) {
		printStringP(PSTR("parameters error\n"));
		return;
	}
	if (addr % (unsigned long)blockSize) {
		printStringP(PSTR("address error\n"));
		return;
	}
	if ((errorCode = readHexStringToSpi(cmd[2], blockSize))) {
		printStringP(PSTR("data error: "));
		printNum(errorCode);
		uartPutChar('\n');
		return;
	}
	addr >>= 1;
	avrCmd(0x4c, (unsigned char)(addr >> 8), (unsigned char)addr, 0);
	_delay_ms(5);
	printStringP(PSTR("flash ok\n"));
}

void spiFlashCommand(char **cmd, char count) {
	if (count == 0) {
		printStringP(PSTR("spi flash ready\n"));
		return;
	}
	char *command = *cmd;
	cmd++;
	count--;
	if (compareString(PSTR("read"), command)) {
		spiFlashReadCommand(cmd, count);
	} else if (compareString(PSTR("write"), command)) {
		spiFlashWriteCommand(cmd, count);
	} else {
		printStringP(PSTR("spi flash\nunknown command\n"));
	}
}

void spiEraseCommand() {
	/* chip erase */
	avrCmd(0xac, 0x80, 0x00, 0x00);
	_delay_ms(20);
	printStringP(PSTR("erase ok\n"));
}

void spiCommand(char **cmd, char count) {
	if (count == 0) {
		printStringP(PSTR("spi "));
		printState(spiprogEnabled);
		return;
	}
	char *command = *cmd;
	cmd++;
	count--;
	if (compareString(PSTR("enable"), command)) {
		spiEnableCommand();
	} else if (spiprogEnabled) {
		if (compareString(PSTR("disable"), command)) {
			spiDisableCommand();
		} else if (compareString(PSTR("lock"), command)) {
			spiLockCommand(cmd, count);
		} else if (compareString(PSTR("fusel"), command)) {
			spiFuselCommand(cmd, count);
		} else if (compareString(PSTR("fuseh"), command)) {
			spiFusehCommand(cmd, count);
		} else if (compareString(PSTR("fusee"), command)) {
			spiFuseeCommand(cmd, count);
		} else if (compareString(PSTR("cal"), command)) {
			spiCalibrationByte();
		} else if (compareString(PSTR("flash"), command)) {
			spiFlashCommand(cmd, count);
		} else if (compareString(PSTR("eeprom"), command)) {
			printStringP(PSTR("not implemented\n"));
			// TODO
		} else if (compareString(PSTR("erase"), command)) {
			spiEraseCommand();
		} else {
			printStringP(PSTR("spi\nunknow command\n"));
		}
	} else {
		printStringP(PSTR("spi not connected\n"));
	}
}

void flashbootCommand(char **cmd, char count) {
	/* flashboot <addr_16bit> <PG_MAGIC> <data_SPM_PAGESIZE> */
	static uint16_t addr;
	static uint16_t pgMagic;
	static unsigned char buff[SPM_PAGESIZE + 1];
	if (count != 3 || readHexNum(cmd[0], (unsigned char *)&addr, 2) || readHexNum(cmd[1], (unsigned char *)&pgMagic, 2)) {
		printStringP(PSTR("bad parameters\n"));
		return;
	}
	if (readHexString(cmd[3], buff, SPM_PAGESIZE) == -1) {
		printStringP(PSTR("data error\n"));
		return;
	}
	if (programPage(addr, (uint16_t *)buff, pgMagic)) {
		printStringP(PSTR("flash error\n"));
		return;
	}
	printStringP(PSTR("flash ok\n"));
}

void readCommand(char **cmd, char count) {
	char *command = *cmd;
	cmd++;
	count--;
	if (compareString(PSTR("hello"), command)) {
		helloCommand();
	} else if (ready && compareString(PSTR("spi"), command)) {
		spiCommand(cmd, count);
	} else if (ready && compareString(PSTR("echo"), command)) {
		echoCommand(cmd, count);
	} else if (ready && compareString(PSTR("reboot"), command)) {
		rebootCommand();
	} else if (ready && compareString(PSTR("flashboot"), command)) {
		flashbootCommand(cmd, count);
	} else if (ready && compareString(PSTR("bootloader"), command)) {
		bootloaderCommand();
	} else if (compareString(PSTR("NO"), command)) {
		/* command from bluetooth module bluegiga wt12 - client disconnected or lost connection */
		/* NO CARRIER 0 ERROR 0 */
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
	unsigned char count = 0;
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

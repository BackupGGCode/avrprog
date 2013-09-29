/* name:    serial driver
 * desc:    simple serial driver
 * arch:    AVR CPU, optimized for ATmega8
 * author:  (c)2012 Pavel Revak <pavel.revak@gmail.com>
 * licence: GPL
 */

#include <avr/io.h>
#include <avr/interrupt.h>

#include "spiprog.h"

#define DDR_SPI DDRB
#define DD_MOSI DDB3
#define DD_SCK DDB5

void spiprogInit() {
	SPCR = _BV(MSTR) | _BV(SPR1);
	SPSR = 0;
	// spiprogSpeed(7);
}

void spiprogEnable() {
	DDR_SPI |= _BV(DD_MOSI) | _BV(DD_SCK);
	SPCR |= _BV(SPE);
}

void spiprogDisable() {
	DDR_SPI &= ~ (_BV(DD_MOSI) | _BV(DD_SCK));
	SPCR &= ~ _BV(SPE);
}

void spiprogSpeed(unsigned char speed) {
	/*
	0 - fsck / 2
	1 - fsck / 4
	2 - fsck / 8
	3 - fsck / 16
	4 - fsck / 32
	5 - fsck / 64
	6 - fsck / 64
	7 - fsck / 128
	*/
	if (speed & 1) SPSR &= ~ _BV(SPI2X); else SPSR |= _BV(SPI2X);
	if (speed & 2) SPCR |= _BV(SPR0); else SPCR &= ~ _BV(SPR0);
	if (speed & 4) SPCR |= _BV(SPR1); else SPCR &= ~ _BV(SPR1);
}

unsigned char spiprogSend(unsigned char data) {
	SPDR = data;
	while (!(SPSR & _BV(SPIF)));
	return SPDR;
}

void spiprogClose() {
	SPCR = 0;
	SPSR = 0;
}


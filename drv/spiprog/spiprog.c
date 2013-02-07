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
	SPCR &= ~ (_BV(SPR1) | _BV(SPR0)); SPSR &= ~ _BV(SPI2X);
	switch (speed) {
		case 2 : SPSR |= _BV(SPI2X); break;
		case 4 : break;
		case 8 : SPCR |= _BV(SPR0); SPSR |= _BV(SPI2X); break;
		case 16 : SPCR |= _BV(SPR0); break;
		case 32 : SPCR |= _BV(SPR1); SPSR |= _BV(SPI2X); break;
		case 64 : SPCR |= _BV(SPR1); break;
		case 128 : SPCR |= _BV(SPR1) | _BV(SPR0); break;
	}
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


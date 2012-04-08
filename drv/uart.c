/* name:    serial driver
 * desc:    simple serial driver
 * arch:    AVR CPU, optimized for ATmega8
 * author:  (c)2012 Pavel Revak <pavel.revak@gmail.com>
 * licence: GPL
 */

#include <avr/io.h>
#include <avr/interrupt.h>

#include "uart.h"

#define ASCII_MODE

/* alloved values 2, 4, 8, 16, 32, 64, 128, 256 */
#define BUFFER_SIZE	(64)

#define BUFFER_MASK	(BUFFER_SIZE - 1)
#if (BUFFER_SIZE > 256)
#error BUFFER_SIZE exceed max size (256Bytes)
#endif
#if (BUFFER_SIZE & BUFFER_MASK)
#error BUFFER_SIZE is not a power of 2
#endif

static uint8_t rx_buffer[BUFFER_SIZE];
static uint8_t rx_tail;
static volatile uint8_t rx_head;

#ifdef UDR
#define UDR0 UDR
#endif

#ifdef UCSRA
#define UCSR0A UCSRA
#define UCSR0B UCSRB
#define UCSR0C UCSRC
#define UCSZ00 UCSZ0
#define UCSZ01 UCSZ1
#define UCSZ02 UCSZ2
#define TXEN0 TXEN
#define RXEN0 RXEN
#define RXCIE0 RXCIE
#define U2X0 U2X
#define UDRIE0 UDRIE
#endif

#ifdef UBRRL
#define UBRR0L UBRRL
#define UBRR0H UBRRH
#endif

#ifdef USART_RXC_vect
#define USART0_RXC_vect USART_RXC_vect
#endif

#ifdef USART_RX_vect
#define USART0_RXC_vect USART_RX_vect
#endif

#ifdef USART0_RX_vect
#define USART0_RXC_vect USART0_RX_vect
#endif

void uartPutChar(char c) {
#ifdef ASCII_MODE
	if (c == '\n') uartPutChar('\r');
#endif
	while (!(UCSRA & (1<<UDRE)));
	UDR0 = c;
}

ISR(USART0_RXC_vect) {
	uint8_t ch = UDR0;
	if (((rx_head + 1) & BUFFER_MASK) == rx_tail) return;
	rx_buffer[rx_head++] = ch;
	rx_head &= BUFFER_MASK;
}

char uartIsChar() {
	return (rx_head != rx_tail);
}

char uartGetChar() {
	if (rx_head != rx_tail) {
		uint8_t ch = rx_buffer[rx_tail++]; rx_tail &= BUFFER_MASK;
		return ch;
	}
	return 0;
}

void uartOpen(uint32_t baud) {
	uint16_t br = ((F_CPU + baud * 4UL) / (baud * 8UL) - 1);
	rx_head = 0;
	rx_tail = 0;
	UCSR0B = 0x00;
	UBRR0H = (uint8_t)(br >> 8);
	UBRR0L = (uint8_t)(br & 0x00ff);
	UCSR0A = _BV(U2X0);
#ifdef URSEL
	UCSR0C = _BV(UCSZ01) | _BV(UCSZ00) | _BV(URSEL);
#else
	UCSR0C = _BV(UCSZ01) | _BV(UCSZ00);
#endif
	UCSR0B = _BV(TXEN0) | _BV(RXEN0) | _BV(RXCIE0);
}

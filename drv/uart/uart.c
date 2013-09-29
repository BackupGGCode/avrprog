/* name:    serial driver
 * desc:    simple serial driver
 * arch:    AVR CPU, optimized for ATmega8
 * author:  (c)2012 Pavel Revak <pavel.revak@gmail.com>
 * licence: GPL
 */

#include <avr/io.h>
#include <avr/interrupt.h>

#include "lib/cpudefs.h"
#include "uart.h"

#if defined(__AVR_ATmega8__)

#define UDR0 UDR
#define UBRR0L UBRRL
#define UBRR0H UBRRH
#define UCSR0A UCSRA
#define UCSR0B UCSRB
#define UCSR0C UCSRC
#define UDRE0 UDRE
#define U2X0 U2X
#define UCSZ00 UCSZ0
#define UCSZ01 UCSZ1
#define UCSZ02 UCSZ2
#define TXEN0 TXEN
#define RXEN0 RXEN
#define RXCIE0 RXCIE
#define USART0_RXC_vect USART_RXC_vect

#elif defined(__AVR_ATmega48__) \
 || defined(__AVR_ATmega48P__) \
 || defined(__AVR_ATmega88__) \
 || defined(__AVR_ATmega88P__) \
 || defined(__AVR_ATmega168__) \
 || defined(__AVR_ATmega168P__) \
 || defined(__AVR_ATmega328__) \
 || defined(__AVR_ATmega328P__)

#define USART0_RXC_vect USART_RX_vect

#elif defined(__AVR_ATmega162__)

#else
#error "Unsupported CPU selected for cpudefs.h"
#endif


#if (UART0_RX_BUFFER_SIZE > 0)

#define UART0_RX_BUFFER_MASK	(UART0_RX_BUFFER_SIZE - 1)
#if (UART0_RX_BUFFER_SIZE > 256)
#error UART0_RX_BUFFER_SIZE exceed max size (256Bytes)
#endif
#if (UART0_RX_BUFFER_SIZE & UART0_RX_BUFFER_MASK)
#error UART0_RX_BUFFER_SIZE is not a power of 2
#endif

static uint8_t uart0RxBuffer[UART0_RX_BUFFER_SIZE];
static uint8_t uart0RxTail;
static volatile uint8_t uart0RxHead;

ISR(USART0_RXC_vect) {
	uint8_t ch = UDR0;
	if (((uart0RxHead + 1) & UART0_RX_BUFFER_MASK) == uart0RxTail) return;
	uart0RxBuffer[uart0RxHead++] = ch;
	uart0RxHead &= UART0_RX_BUFFER_MASK;
}

char uart0IsChar() {
	return (uart0RxHead != uart0RxTail);
}

char uart0GetChar() {
	if (uart0RxHead != uart0RxTail) {
		uint8_t ch = uart0RxBuffer[uart0RxTail++]; uart0RxTail &= UART0_RX_BUFFER_MASK;
		return ch;
	}
	return 0;
}

#else

#error UART0_RX_BUFFER_SIZE must by larger tahan 0
char uart0IsChar() {
	return 0;
}

char uart0GetChar() {
	return 0;
}

#endif


void uart0PutCharBinary(char c) {
	while (!getBit(UCSR0A, UDRE0));
	UDR0 = c;
}

void uart0PutChar(char c) {
	if (c == '\n') uart0PutCharBinary('\r');
	uart0PutCharBinary(c);
}

static int uart0PutCharBinaryStd(char c, FILE *stream) {
	uart0PutChar(c);
	return 0;
}

static int uart0PutCharStd(char c, FILE *stream) {
	uart0PutChar(c);
	return 0;
}

static int uart0GetCharStd(FILE *stream) {
	if (uart0IsChar()) return uart0GetChar();
	return EOF;
}

void uart0Close() {
	UBRR0H = 0x00;
	UBRR0L = 0x00;
	UCSR0A = 0x00;
	UCSR0B = 0x00;
	#ifndef URSEL
	UCSR0C = 0x00;
	#else
	UCSR0C = 0x00 | _BV(URSEL);
	#endif
}

void uart0Open(uint32_t baud) {
	uint16_t br = ((F_CPU + baud * 4UL) / (baud * 8UL) - 1);
	#if (UART0_RX_BUFFER_SIZE > 0)
	uart0RxHead = 0;
	uart0RxTail = 0;
	#endif
	UBRR0H = (uint8_t)(br >> 8);
	UBRR0L = (uint8_t)(br & 0x00ff);
	UCSR0A = _BV(U2X0);
	UCSR0B = _BV(TXEN0) | _BV(RXEN0) | _BV(RXCIE0);
	#ifndef URSEL
	UCSR0C = _BV(UCSZ01) | _BV(UCSZ00);
	#else
	UCSR0C = _BV(UCSZ01) | _BV(UCSZ00) | _BV(URSEL);
	#endif
}

static FILE ttyUART0;

FILE *uart0FOpenBinary(uint32_t baud) {
	uart0Open(baud);
	fdev_setup_stream(&ttyUART0, uart0PutCharBinaryStd, uart0GetCharStd, _FDEV_SETUP_RW);
	return &ttyUART0;
}

FILE *uart0FOpen(uint32_t baud) {
	uart0Open(baud);
	fdev_setup_stream(&ttyUART0, uart0PutCharStd, uart0GetCharStd, _FDEV_SETUP_RW);
	return &ttyUART0;
}


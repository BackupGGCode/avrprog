#ifndef UART_H
#define UART_H 1

#include <stdio.h>

extern void uart0PutCharBinary(char c);
extern void uart0PutChar(char c);
extern char uart0IsChar();
extern char uart0GetChar();
extern void uart0Close();
extern void uart0Open(uint32_t baud);
extern FILE *uart0FOpenBinary(uint32_t baud);
extern FILE *uart0FOpen(uint32_t baud);

#ifdef UDR1
extern void uart1PutCharBinary(char c);
extern void uart1PutChar(char c);
extern char uart1IsChar();
extern char uart1GetChar();
extern void uart1Close();
extern void uart1Open(uint32_t baud);
extern FILE *uart1FOpenBinary(uint32_t baud);
extern FILE *uart1FOpen(uint32_t baud);
#endif

#if defined(DEFAULT_UART1) && defined(UDR1)
	#define uartPutCharBinary uart1PutCharBinary
	#define uartPutChar uart1PutChar
	#define uartGetChar uart1GetChar
	#define uartIsChar uart1IsChar
	#define uartOpen uart1Open
	#define uartClose uart1Close
	#define uartFOpenBinary uart1FOpenBinary
	#define uartFOpen uart1FOpen
#else
	#define uartPutCharBinary uart0PutCharBinary
	#define uartPutChar uart0PutChar
	#define uartGetChar uart0GetChar
	#define uartIsChar uart0IsChar
	#define uartOpen uart0Open
	#define uartClose uart0Close
	#define uartFOpenBinary uart0FOpenBinary
	#define uartFOpen uart0FOpen
#endif

#endif  /* UART_H */

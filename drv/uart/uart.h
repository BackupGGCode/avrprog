#ifndef UART_H
#define UART_H 1

#include <stdio.h>

extern void uartPutCharBinary(char c);
extern void uartPutChar(char c);
extern char uartIsChar();
extern char uartGetChar();
extern void uartClose();
extern void uartOpen(uint32_t baud);
extern FILE *uartFOpenBinary(uint32_t baud);
extern FILE *uartFOpen(uint32_t baud);

#endif  /* UART_H */

#ifndef UART_H
#define UART_H 1

extern void uartSync();
extern void uartPutChar(char c);
extern char uartIsChar();
extern char uartGetChar();
extern void uartOpen(uint32_t baud);

#endif  /* UART_H */

#ifndef CPUDEFS_H
#define CPUDEFS_H 1

/* control an bit in an register
 * clrBit - clear bit to 0
 * setBit - set bit to 1
 * cplBit - negate bit
 * getBit - read bit and return 0 or 1 */
#define clrBit(reg, bit) {(reg) &= ~ _BV((bit));}
#define setBit(reg, bit) {(reg) |= _BV((bit));}
#define cplBit(reg, bit) {(reg) ^= _BV((bit));}
#define getBit(reg, bit) (((reg) >> (bit)) & 1)


/* control bits on CPU IO pins
 * you can define it by example:
 * #define LED B, 4
 * an use it as example:
 * outPin(LED)
 * cplPin(LED)
 */
#define outPin_(port,pin) setBit(DDR##port, DD##port##pin)
#define outPin(p) outPin_(p)
#define inpPin_(port,pin) clrBit(DDR##port, DD##port##pin)
#define inpPin(p) inpPin_(p)
#define clrPin_(port,pin) clrBit(PORT##port, PORT##port##pin)
#define clrPin(p) clrPin_(p)
#define setPin_(port,pin) setBit(PORT##port, PORT##port##pin)
#define setPin(p) setPin_(p)
#define cplPin_(port,pin) cplBit(PORT##port, PORT##port##pin)
#define cplPin(p) cplPin_(p)
#define getPin_(port,pin) getBit(PIN##port, PIN##port##pin)
#define getPin(p) getPin_(p)

#if defined(__AVR_ATmega8__)

	#define getPUD() getBit(SFIOR, PUD)
	#define clrPUD() clrBit(SFIOR, PUD)
	#define setPUD() setBit(SFIOR, PUD)
	#define setIVCE() {GICR = _BV(IVCE);}
	#define setIVSEL() {GICR = _BV(IVSEL);}

	#define getUDR() (UDR)
	#define setUDR(val) {UDR = (val);}
	#define setUBRRL(val) {UBRRL = (val);}
	#define setUBRRH(val) {UBRRH = (val);}
	#define setUCSRA(val) {UCSRA = (val);}
	#define setUCSRB(val) {UCSRB = (val);}
	#ifdef URSEL
		#define setUCSRC(val) {UCSRC = (val) | _BV(URSEL);}
	#else
		#define setUCSRC(val) {UCSRC = (val);}
	#endif
	#define BV_U2X _BV(U2X)
	#define BV_UCSZ0 _BV(UCSZ0)
	#define BV_UCSZ1 _BV(UCSZ1)
	#define BV_UCSZ2 _BV(UCSZ2)
	#define BV_TXEN _BV(TXEN)
	#define BV_RXEN _BV(RXEN)
	#define BV_RXCIE _BV(RXCIE)
	#define USART_RX_vect USART_RXC_vect
	#define waitUDRE() {while (!getBit(UCSRA, UDRE));};

#elif defined(__AVR_ATmega48__) \
 || defined(__AVR_ATmega48P__) \
 || defined(__AVR_ATmega88__) \
 || defined(__AVR_ATmega88P__) \
 || defined(__AVR_ATmega168__) \
 || defined(__AVR_ATmega168P__) \
 || defined(__AVR_ATmega328__) \
 || defined(__AVR_ATmega328P__)

	#define getPUD() getBit(MCUCR, PUD)
	#define clrPUD() clrBit(MCUCR, PUD)
	#define setPUD() setBit(MCUCR, PUD)
	#define setIVCE() {MCUCR = _BV(IVCE);}
	#define setIVSEL() {MCUCR = _BV(IVSEL);}

	#define getUDR() (UDR0)
	#define setUDR(val) {UDR0 = (val);}
	#define setUBRRL(val) {UBRR0L = (val);}
	#define setUBRRH(val) {UBRR0H = (val);}
	#define setUCSRA(val) {UCSR0A = (val);}
	#define setUCSRB(val) {UCSR0B = (val);}
	#define setUCSRC(val) {UCSR0C = (val);}
	#define BV_U2X _BV(U2X0)
	#define BV_UCSZ0 _BV(UCSZ00)
	#define BV_UCSZ1 _BV(UCSZ01)
	#define BV_UCSZ2 _BV(UCSZ02)
	#define BV_TXEN _BV(TXEN0)
	#define BV_RXEN _BV(RXEN0)
	#define BV_RXCIE _BV(RXCIE0)
	#define waitUDRE() {while (!getBit(UCSR0A, UDRE0));};

#else
	#error "Wrong CPU selected"
#endif

#endif  /* CPUDEFS_H */

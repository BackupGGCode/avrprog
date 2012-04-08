#ifndef SPIPROG_H
#define SPIPROG_H 1

extern void spiprogInit(void);
extern void spiprogSpeed(unsigned char speed);
extern unsigned char spiprogSend(unsigned char data);
extern void spiprogEnable(void);
extern void spiprogDisable(void);

#endif  /* SPIPROG_H */

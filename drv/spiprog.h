#ifndef SPIPROG_H
#define SPIPROG_H 1

extern void spiprogInit();
extern void spiprogSpeed(unsigned char speed);
extern unsigned char spiprogSend(unsigned char data);
extern void spiprogEnable();
extern void spiprogDisable();
extern void spiprogClose();

#endif  /* SPIPROG_H */

#ifndef SELFPG_H
#define SELFPG_H 1

#define PG_MAGIC 0x4321

extern char programPage(uint16_t page, uint16_t *buf, uint16_t magic);

#endif  /* SELFPG_H */

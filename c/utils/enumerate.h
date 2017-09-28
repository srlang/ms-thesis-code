#ifndef _ENUMERATE_H
#define _ENUMERATE_H

#include "cribbage.h"
#include "score.h"

#define THREAD_COUNT	10

void thread_work_method(Hand * hand);
void output(Hand * hand, Score score);
Hand * next_hand();
uint8_t valid_next(Hand * hand);
Hand * inc_hand();

uint8_t valid(Hand * hand);

void * threader(void * args);

#endif /*_ENUMERATE_H*/

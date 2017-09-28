#ifndef _ENUMERATE_H
#define _ENUMERATE_H

#include <pthread.h>
#include <sqlite3.h>

#include "cribbage.h"
#include "score.h"

#define THREAD_COUNT	10

void kt_thread_work_method(KeepToss * kt);

void kt_output(KeepToss * kt);

void * kt_threader(void * args);

uint8_t kt_valid(KeepToss * kt);

KeepToss * kt_next();

uint8_t kt_valid_next_kt(KeepToss * kt);

int kt_db_add(KeepToss * kt, sqlite3 * db, pthread_mutex_t * mutex);

#endif /*_ENUMERATE_H*/

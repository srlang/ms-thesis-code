#ifndef _ENUMERATE_H
#define _ENUMERATE_H

#include <pthread.h>
#include <sqlite3.h>

#include "cribbage.h"
#include "score.h"

#define CRIBBAGE_MEMCPY					1
#define KEEP_SORT(x)					qsort(x)
#define TOSS_SORT(x)					qsort(x)

#define THREAD_COUNT					10
#define CARDS_IN_KEEP_TOSS_MODIFIABLE	(4+2+2)
#define CARDS_IN_KEEP_TOSS_INCREMENT	(4+2)

typedef struct keep_toss_s {
	Card keep[4];
	Card toss[2];
	Card tosd[2];
	Card cut;
} KeepToss;
#define KT_LAST_FIRST_CARD				(51-2-4)

typedef struct KeepTossInformation_s {
	Score kmin;
	Score kmax;
	Score kmed;
	float kavg;
	float kmod;
	Score tmin;
	Score tmax;
	Score tmed;
	float tavg;
	float tmod;
} KeepTossInfo;

typedef struct kt_threader_args {
	char * db_filename;
} kt_threader_args_t;

void free_keep_toss(KeepToss * kt);

void kt_thread_work_method(KeepToss * kt);

void kt_output(KeepToss * kt);

void * kt_threader(void * args);

uint8_t kt_valid(KeepToss * kt);

KeepToss * kt_next(KeepToss * kt);

uint8_t kt_valid_next_kt(KeepToss * kt);

int kt_db_add(KeepToss * kt, sqlite3 * db, pthread_mutex_t * mutex);

#endif /*_ENUMERATE_H*/

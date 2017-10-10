#ifndef _DB_POPULATE_H
#define _DB_POPULATE_H

#include <pthread.h>
#include <sqlite3.h>

#include "cribbage.h"
#include "score.h"

#define DB_FILENAME						"file:///tmp_db_c.db"

#define CRIBBAGE_MEMCPY					1
#define KEEP_SORT(w,x,y,z)				qsort(w,x,y,z)
#define TOSS_SORT(w,x,y,z)				qsort(w,x,y,z)

#ifdef DEBUG
	#define DB_THREAD_COUNT				1
#else
	#define DB_THREAD_COUNT				10
#endif
#define CARDS_IN_KEEP_TOSS_MODIFIABLE	(4+2+2)
#define CARDS_IN_KEEP_TOSS_INCREMENT	(4+2)

//#define TOSS_POSS_VALS					15180
//explanation of below:
// I don't know, i just let the program run and print out the last index
#define TOSS_POSS_VALS					47610

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
	float kmed;
	float kavg;
	Score kmod;
	Score tmin;
	Score tmax;
	float tmed;
	float tavg;
	Score tmod;
} KeepTossInfo;

typedef struct kt_threader_args {
	char * db_filename;
} kt_threader_args_t;

void free_keep_toss(KeepToss * kt);

void kt_thread_work_method(KeepToss * kt, sqlite3 * db);

void eval_keep_vals(KeepToss * kt, KeepTossInfo * kti);

void eval_toss_vals(KeepToss * kt, KeepTossInfo * kti);

void kt_output(KeepToss * kt);

void * kt_threader(void * args);

uint8_t kt_valid(KeepToss * kt);

KeepToss * kt_next(KeepToss * kt);

uint8_t kt_valid_next_kt(KeepToss * kt);

uint8_t kt_db_add(sqlite3 * db, KeepToss * kt, KeepTossInfo * kti);

static int kt_sqlite_callback(void * _x, int argc, char ** argv, char ** _y);

#endif /*_DB_POPULATE_H*/

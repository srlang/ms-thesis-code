#ifndef _DB_POPULATE_H
#define _DB_POPULATE_H

#include <stdlib.h>
#include <pthread.h>
#include <sqlite3.h>

#include "cribbage.h"
#include "score.h"
#include "utils.h"

#define DB_MULTI_FILE	1

#define DB_FILENAME						"/tmp/srlang_ind/tmp_db_c.db"
#define DB_FILENAME_FORMAT				"/tmp/srlang_ind/tmp_db_c_%d.db"
//#define DB_FILENAME	":memory:"
//#define DB_FILENAME_FORMAT	":memory:"
#define DB_OPEN_FLAGS					(SQLITE_OPEN_READWRITE |\
										SQLITE_OPEN_CREATE |\
										SQLITE_OPEN_FULLMUTEX)

#define CRIBBAGE_MEMCPY					1
#define KEEP_SORT(w,x,y,z)				qsort(w,x,y,z)
#define TOSS_SORT(w,x,y,z)				qsort(w,x,y,z)

#ifdef DEBUG
	#define DB_THREAD_COUNT				64 //should probably be 32
#else
	#define DB_THREAD_COUNT				56
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
#ifdef DEBUG
	#define KT_LAST_FIRST_CARD				1
#else
	#define KT_LAST_FIRST_CARD				46
#endif

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
	//char * db_filename;
	char db_filename[100];
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

void /*inline*/ _kt_mode(Score * mode, Score * vals, int vals_len);

int all_increasing(KeepToss * kt);

//long int id(int k0, int k1, int k2, int k3, int t0, int t1);
long int id(KeepToss * kt);

#endif /*_DB_POPULATE_H*/

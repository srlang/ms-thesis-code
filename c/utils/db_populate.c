#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

#include "enumerate.h"
#include "cribbage.h"
#include "score.h"
#include "utils.h"


/*
 * Free the memory taken up by the KeepToss object.
 */
void free_keep_toss(KeepToss * kt) {
	free(kt->keep);
	free(kt->toss);
	free(kt->tosd);
	free(kt);
}

/*
 * Input: hand that is not complete (i.e. is missing a crib card (is 0) and tosd)
 * 	This hand is also not a proper keep/toss combination, but an ordered set of
 * 	6 cards that can then be rearranged into keep/tos possiblities.
 * This method will find each of these 24 keep/toss possibilities,
 * evaluate each kept hand with a toss card and
 */
void kt_thread_work_method(KeepToss * kt, sqlite3 * db) {
	Card ordered[6];
	KeepTossInfo kti;

	// keep an ordered copy for the sake of using something
	// due to implementation, given hand is in order
	// even if it wasn't, AN order is all we need
	memcpy(ordered, kt->hand, 6*sizeof(Card));

	for (int f_i = 0; f_i < 5; f_i++) {
		for (int s_i = f_i+1; s_i < 6; s_i++) {
			// copy the hand to the right location for evaluating possibilities
			// f_i is index of first card in throw
			// s_i is index of second card in throw
			// i index of card in orderd hand
			// j index location of where to put the card
			for (int i = 0, j = 0; i < 6; i++) {
				if (i == f_i) {
					kt->hand[4] = ordered[i];
				} else if (i == s_i) {
					kt->hand[5] = ordered[i];
				} else {
					kt->hand[j] = ordered[i];
					j++;
				}
			}

			// evaluate keep values
			// TODO

			// evaluate toss hands
			// TODO

			// add to database
			kt_db_add(db, kt, kti);
		}
	}
}

/*
 * Print the output of a keep/toss combination in a nice format.
 */
void kt_output(KeepToss * kt) {
	// TODO
}

#define DB_FLAGS			SQLITE_OPEN_NOMUTEX
/*
 * Method called for each thread start.
 * Repeatedly finds the next valid hand and calls the scorer method on it.
 */
void * kt_threader(void * args) {
	KeepToss * kt;
	sqlite3 * db;
	kt_threader_args_t * targs = (kt_threader_args_t *) args;

	PD("entering threader\n");

	PD("\topening database connection\n");
	sqlite3_open_v2(targs->db_filename, &db, DB_FLAGS, NULL);

	while ((kt = kt_next(kt))) {
		PD("\thave a non-NULL hand\n");
		if (valid_keep_toss(kt)) {
			PD("\t\thand is valid\n");
			kt_thread_work_method(kt, db);
		}
		// don't free because we don't want to waste time reallocating memory,
		// so there's no freeing/reallocating
	}

	PD("\tfreeing keep/toss memory before exit\n");
	//honestlly can't remember how safely this is non-null, so double check
	if (kt) 
		free_keep_toss(kt);

	PD("\tclosing database connection\n");
	sqlite3_close(db);

	PD("exiting from thread\n");
	return NULL;
}

/*
 * Determine if the keep-toss struct is valid (i.e. each card is unique).
 */
uint8_t kt_valid(KeepToss * kt) {
	uint8_t ret = 1;

	for (uint8_t i = 0; i < CARDS_IN_KEEP_TOSS_MODIFIABLE-1; i++) {
		for (uint8_t j = i+1; j < CARDS_IN_KEEP_TOSS_MODIFIABLE; j++) {
			ret &= hand->hand[i] != hand->hand[j];
		}
	}

	return ret;
}

/*
 * Retrieve the next KeepToss combination that needs to be computed for
 * each combination, etc.
 *
 * Params:
 * 	kt: the location of a KeepToss struct to be overwritten to avoid repetitive
 * 		memory allocation
 * 		if kt is NULL, memory will be allocated
 * Returns:
 * 	the address of the new hand
 * 	This is usually just kt
 */
#define CRIBBAGE_HAND_INCREMENT_BASE	52
KeepToss * _kt_next_object;
pthread_mutex_t * _kt_next_object_lock;
uint8_t _kt_next_object_done;
KeepToss * kt_next(KeepToss * kt) {
	if (!kt) {
		// allocate memory
		kt = (KeepToss *) calloc(1, sizeof(KeepToss));
		if (!kt)
			// exit quick if still not valid (NULL)
			// better to let single thread die than segfault proc
			return NULL;
	}

	// lock mutex to avoid race conditions
	pthread_mutex_lock(_kt_next_object_lock);

	if (_kt_next_object_done) {
		// exit with NULL if we've gone through all the possibilities so threads
		// can exit
		// make sure to unlock the mutex and free memory as appropriate
		pthread_mutex_unlock(_kt_next_object_lock);
		free_keep_toss(kt);
		kt = NULL;
		return kt;
	}

	// implement integer increment base 52 on KeepToss->keep,toss as a dealt
	// hand
	// take advantage of the fact that C treats memory like a single tape
	uint8_t carry = 1;
	for (uint8_t i = CARDS_IN_KEEP_TOSS_INCREMENT; i >= 0 && carry; i--) {
		_kt_next_object->keep[i] += carry;
		carry = _kt_next_object->keep[i] >= 52;
		_kt_next_object->keep[i] %= CRIBBAGE_HAND_INCREMENT_BASE;
	}
	// zero out the KeepToss->tosd,cut fields
	// (this can be handled by increment later and a validity check after a few
	// steps)
	// not necessary since this increment is on the global next object that
	// won't ever be touched in those fields

	// quit the "next"-ing when we've gone through all combinations once
	_kt_next_object_done = (_kt_next_object->keep[0] >= KT_LAST_FIRST_CARD);

	// copy the incremented global hand to the destination memory location
	memcpy(kt, _kt_next_object, sizeof(KeepToss));

	// unlock mutex to allow next thread access
	pthread_mutex_unlock(_kt_next_object_lock);

	return kt;
}


/*
 * Execute the SQL statement required to insert a single database row into
 * the table.
 * Params:
 * 	db: sqlite3 database pointer for operations
 * 	kt: KeepToss object for which cards are kept and tossed
 * 	kti: All the statistics computed for keep/toss combo
 */
#define SQL_FORMAT	\
	"INSERT INTO keep_throw_stats "\
	"(kcard0, kcard1, kcard2, kcard3, "\
		"tcard0, tcard1, "\
		"kmin, kmax, kmed, kavg, kmod, "\
		"tmin, tmax, tmed, tavg, tmod) "\
	"VALUES (%d, %d, %d, %d, "\
		"%d, %d, "\
		"%d, %d, %f, %f, %d, "\
		"%d, %d, %f, %f, %d);-- "
uint8_t kt_db_add(sqlite3 * db, KeepToss * kt, KeepTossInfo * kti) {
	int rc;
	
	// generate sql statement
	char sql[2048];
	sprintf(sql, SQL_FORMAT, kt->keep[0], kt->keep[1], kt->keep[2], kt->keep[3],
			kt->toss[0], kt->toss[1],
			kti->kmin, kti->kmax, kti->kmed, kti->kavg, kti->kmod,
			kti->tmin, kti->tmax, kti->tmed, kti->tavg, kti->tmod);

	// run sql statement in db
	rc = sqlite3_exec(db, sql, kt_sqlite_callback, 0, &err_msg);

	return (uint8_t) rc;
}


static int kt_sqlite_callback(void * _x, int argc, char ** argv, char ** _y) {
	return 0;
}

int main(void) {
	PD("initializations\n");
	pthread_t threads[THREAD_COUNT];

	// initialize shared objects
	_kt_next_object_done = 0;
	_kt_next_object_lock = (pthread_mutex_t *) malloc(sizeof(pthread_mutex_t));
	_kt_next_object = (KeepToss *) malloc(sizeof(KeepToss));

	// initialize mutex lock
	pthread_mutex_init(_kt_next_object_lock, NULL);

	// create pthreads
	PD("creating threads\n");
	for (int i = 0; i < THREAD_COUNT; i++) {
		if(pthread_create(&threads[i], NULL, threader, NULL)) {
			PD("\terror occurred in creation\n");
		}
	}

	// join threads
	PD("joining threads\n");
	for (int i = 0; i < THREAD_COUNT; i++) {
		pthread_join(threads[i], NULL);
	}

	// destroy objects/free memory
	PD("destroying\n");
	free_keep_toss(_kt_next_object);
	pthread_mutex_destroy(_kt_next_object_lock);

	return 0;
}

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <sqlite3.h>

#include "enumerate.h"
#include "cribbage.h"
#include "score.h"
#include "utils.h"
#include "db_populate.h"


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
#ifdef CRIBBAGE_MEMCPY
	memcpy(ordered, kt->keep, 6*sizeof(Card));
#else
	ordered[0] = kt->keep[0];
	ordered[1] = kt->keep[1];
	ordered[2] = kt->keep[2];
	ordered[3] = kt->keep[3];
	ordered[4] = kt->keep[4];
	ordered[5] = kt->keep[5];
#endif

	for (int f_i = 0; f_i < 5; f_i++) {
		for (int s_i = f_i+1; s_i < 6; s_i++) {
			// copy the hand to the right location for evaluating possibilities
			// f_i is index of first card in throw
			// s_i is index of second card in throw
			// i index of card in orderd hand
			// j index location of where to put the card
			for (int i = 0, j = 0; i < 6; i++) {
				if (i == f_i) {
					kt->keep[4] = ordered[i];
				} else if (i == s_i) {
					kt->keep[5] = ordered[i];
				} else {
					kt->keep[j] = ordered[i];
					j++;
				}
			}

			// evaluate keep values
			eval_keep_vals(kt, &kti);

			// evaluate toss hands
			eval_toss_vals(kt, &kti);

			// add to database
			kt_db_add(db, kt, &kti);
		}
	}
}

/*
 * N.B.: This method assumes that vals are SORTED. Without that, functionality
 * won't really happen.
 *
 * Basically, this will move forward in the array, then keep a count as long
 * as the values do not change, keeping a count of that.
 * Kind of similar to the buckets strategy of counting runs.
 *
 * In the case of a multi-modal distribution, the lowest mode will be returned.
 */
void inline _kt_mode(Score * mode, Score * vals, int vals_len) {
	uint8_t local_counter = 1;
	uint8_t local_counter_max = 0;
	for (int i = 1; i < vals_len; i++) {
		if (vals[i] == vals[i-1]) {
			// if we're on the same number, increase counter
			local_counter++;
		} else {
			// if we change number, check
			if (local_counter > local_counter_max) {
				local_counter_max = local_counter;
				*mode = vals[i-1];
			}
			local_counter = 0;
		}
	}
	// one last check
	if (local_counter > local_counter_max) {
		local_counter_max = local_counter;
		*mode = vals[vals_len-1];
	}
}

int compare_doubles(const void * a, const void * b) {
	return (int) ( *((double *)a) - *((double *)b) );
}

/*
 * Evaluate all values possible from the kept cards.
 * kti:
 * 	kmax
 * 	kmin
 * 	kavg
 * 	kmod
 * 	kmed
 */
void eval_keep_vals(KeepToss * kt, KeepTossInfo * kti) {
	Hand hand;
	// ensure that the min is set over the course of the loops
	// otherwise, min will always be 0
	// 29 is the max possible hand, no need for higher
	kti->kmin = 29;
	// need to keep track of values for mode/median
	Score vals[46];
	uint8_t v_indx = 0;

	// copy cards to hand
	// (questions: would it be faster to simply copy values over by myself?)
	// according to Topi: this will likely get optimized by gcc anyways
#ifdef CRIBBAGE_MEMCPY
	memcpy(hand.hand, kt->keep, 4*sizeof(Card));
#else
	// but, i'm not going to leave it to chance and code both ways for the
	// heck of 'quick' switching
	for (int i = 0; i < 4; i++) {
		hand.hand[i] = kt->keep[i];
	}
#endif

	// run through possible cribs
	for (uint8_t crib = 0; crib < NUM_CARDS; crib++) {
		uint8_t valid = 1;
		// 6 cards to include both keep and toss
		for (uint8_t i = 0; i < 6; i++) {
			valid &= (hand.hand[i] != crib);
		}
		if (valid) {
			Score s = score(&hand);

			// med, mode: just record for later
			vals[v_indx++] = s;

			// avg
			kti->kavg += (float) s;
		}
	}

	// cleanup
	kti->kavg /= 46.0; //46 possible cribs, this is constant

	KEEP_SORT(vals, 46, sizeof(Score), compare_doubles);

	// min/max
	kti->kmin = vals[0];
	kti->kmax = vals[45];

	// median
	kti->kmed = (vals[22] + vals[23]) / 2.0;

	// mode
	_kt_mode(&kti->kmod, vals, 46);
}


/*
 * Evaluate all possible values for the toss and crib.
 */
void eval_toss_vals(KeepToss * kt, KeepTossInfo * kti) {
	Hand hand;
	kti->tmin = 29;
	Score vals[TOSS_POSS_VALS];
	uint8_t v_indx = 0;

	// copy over hand for adjustment later.
	hand.hand[0] = kt->toss[0];
	hand.hand[1] = kt->toss[1];


	// Loop over possible values for keep/toss
	// loop through each crib possibility (yet again, integer addition, base 52)
	for (Card i = 0; i < 51; i++) {
		uint8_t any_same_i = 0;
		for (int x = 0; x < 6; x++) {
			any_same_i |= (i == kt->keep[x]);
		}
		// don't continue searching with this number if any are the same
		if (any_same_i)
			continue;

		hand.hand[2] = i;
		for (Card j = i+1; j < 52; j++) {
			uint8_t any_same_j = 0;
			for (int y = 0; y < 6; y++) {
				any_same_j |= (j == kt->keep[y]);
			}
			// don't continue searching with this number if any are the same
			if (any_same_j)
				continue;

			hand.hand[3] = j;
			for (Card crib = 0; crib < 52; crib++) {
				uint8_t any_same_crib = 0;
				for (int z = 0; z < 6; z++) {
					any_same_crib |= (crib == kt->keep[z]);
				}

				// don't continue searching with this number if any are the same
				if (any_same_crib)
					continue;

				hand.hand[4] = crib;
				Score s= score(&hand);

				// med, mode: just record for later
				vals[v_indx++] = s;

				// avg
				kti->tavg += (float) s;
			}
		}
	}


	// cleanup
	kti->tavg /= (float) TOSS_POSS_VALS;

	KEEP_SORT(vals, TOSS_POSS_VALS, sizeof(Score), compare_doubles);

	// min/max (have to sort anyways, why waste computation time sorting
	kti->tmin = vals[0];
	kti->tmax = vals[TOSS_POSS_VALS-1];

	// median
	kti->tmed = (vals[(TOSS_POSS_VALS/2)-1] + vals[TOSS_POSS_VALS/2]) / 2.0;

	// mode
	_kt_mode(&kti->tmod, vals, TOSS_POSS_VALS);
}

/*
 * Print the output of a keep/toss combination in a nice format.
 */
void kt_output(KeepToss * kt) {
	// TODO
}

uint8_t valid_keep_toss(KeepToss * kt) {
	uint8_t any_same = 0;
	for (int i = 0; i < 5; i++) {
		for (int j = i+1; j < 6; j++) {
			any_same |= kt->keep[i] == kt->keep[j];
		}
	}
	return !any_same;
}

#define DB_FLAGS			SQLITE_OPEN_NOMUTEX
/*
 * Method called for each thread start.
 * Repeatedly finds the next valid hand and calls the scorer method on it.
 */
void * kt_threader(void * args) {
	KeepToss * kt = NULL;
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
			ret &= kt->keep[i] != kt->keep[j];
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
	char * err_msg;
	
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
		if(pthread_create(&threads[i], NULL, kt_threader, NULL)) {
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

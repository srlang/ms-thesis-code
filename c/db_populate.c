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
	//free(kt->keep);
	//free(kt->toss);
	//free(kt->tosd);
	if (kt)
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
	PD("\t\t\tentering kt_thread_work_method\n");
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
					//kt->keep[4] = ordered[i];
					kt->toss[0] = ordered[i];
				} else if (i == s_i) {
					//kt->keep[5] = ordered[i];
					kt->toss[1] = ordered[i];
				} else {
					kt->keep[j] = ordered[i];
					j++;
				}
			}

			PD("\t\t\t\tevaluating keep values\n");
			// evaluate keep values
			eval_keep_vals(kt, &kti);

			PD("\t\t\t\tevaluating toss values\n");
			// evaluate toss hands
			eval_toss_vals(kt, &kti);

			PD("\t\t\t\tadding hand to the database\n");
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
void /*inline*/ _kt_mode(Score * mode, Score * vals, int vals_len) {
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

int compare_scores(const void * a, const void * b) {
	//return (int) ( *((Score *)a) - *((Score *)b) );
	//PD("\t\t\t\t\t\t\t\tcompare_scores: a:%p, b%p\n", a, b);
	//PD("\t\t\t\t\t\t\t\tcompare_scores: a:%p-->%d, b:%p-->%d\n",
		//a, *((Score *)a), b, *((Score *) b));
	if (!a || !b) {
		PD("compare_scores: a or b is NULL: a=%p, b=%p\n", a, b);
	}
	return (*((Score *)a)) - (*((Score *)b));
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
	//PD("\t\t\t\t\tentering eval_keep_vals\n");
	Hand hand;
	// ensure that the min is set over the course of the loops
	// otherwise, min will always be 0
	// 29 is the max possible hand, no need for higher
	kti->kmin = 29;
	// need to keep track of values for mode/median
#define KT_POSS_KEEP_VAL_CT		46
	Score vals[KT_POSS_KEEP_VAL_CT];
	uint8_t v_indx = 0;

	//PD("\t\t\t\t\tcopying cards to hand...\n");
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
	//PD("\t\t\t\t\tdone\n");

	//PD("\t\t\t\t\tRunning through possible cribs\n");
	// run through possible cribs
	for (uint8_t crib = 0; crib < NUM_CARDS; crib++) {
		uint8_t valid = 1;
		// 6 cards to include both keep and toss
		for (uint8_t i = 0; i < 6; i++) {
			valid &= (kt->keep[i] != crib);
		}
		if (valid) {
			//PD("\t\t\t\t\tValid crib(%d) found\n", crib);
			hand.hand[4] = crib;
			Score s = score(&hand);
			//PD("\t\t\t\t\t\tscore = %d\n", s);

			//PD("\t\t\t\t\t\tadding to record of values\n");
			// med, mode: just record for later
			vals[v_indx++] = s;

			// avg
			kti->kavg += s;// + 0.0;//(float) s;
		}
	}

	// because there's a single case of min=max=12, but avg=12.667, double check
	// that this is not due to incorrect count
	//PD("keep_vals.size = %d\n", v_indx);
	// cleanup
	kti->kavg /= (float) KT_POSS_KEEP_VAL_CT; //46 possible cribs, this is constant

	KEEP_SORT(vals, 46, sizeof(Score), compare_scores);

	// min/max
	kti->kmin = vals[0];
	kti->kmax = vals[45];

	// median
	kti->kmed = (vals[22] + vals[23]) / 2.0;

	// mode
	_kt_mode(&kti->kmod, vals, 46);

	//PD("\t\t\t\t\texiting eval_keep_vals with: "
	//		"kmin=%d, kmax=%d, kavg=%f, kmed=%f, kmod=%d\n",
	//		kti->kmin, kti->kmax, kti->kavg, kti->kmed, kti->kmod);
}


/*
 * Evaluate all possible values for the toss and crib.
 */
void eval_toss_vals(KeepToss * kt, KeepTossInfo * kti) {
	PD("\t\t\t\t\tentering eval_toss_vals\n");
	Hand hand;
	// set the bitmask to be the crib's hand because it is the crib and the
	// crib is score just __slightly__ differently enough that it actually
	// matters
	// kinda drives one crazy
	hand.bitmask = _HAND_CRIB;
	kti->tmin = 29;
	Score vals[TOSS_POSS_VALS];
	int v_indx = 0;

	//PD("\t\t\t\t\t\tHello,\n");
	// copy over hand for adjustment later.
	hand.hand[0] = kt->toss[0];
	hand.hand[1] = kt->toss[1];


	//PD("\t\t\t\t\t\tIs\n");
	// Loop over possible values for keep/toss
	// loop through each crib possibility (yet again, integer addition, base 52)
	for (Card i = 0; i < 51; i++) {
		//PD("\t\t\t\t\t\tEntering I loop\n");
		uint8_t any_same_i = 0;
		//PD("\t\t\t\t\t\tIt\n");
		for (int x = 0; x < 6; x++) {
			any_same_i |= (i == kt->keep[x]);
		}
		//PD("\t\t\t\t\t\tIt\n");
		// don't continue searching with this number if any are the same
		if (any_same_i)
			continue;

		//PD("\t\t\t\t\t\tMe\n");
		hand.hand[2] = i;
		for (Card j = i+1; j < 52; j++) {
			//PD("\t\t\t\t\t\tEntering J loop\n");
			uint8_t any_same_j = 0;
			for (int y = 0; y < 6; y++) {
				any_same_j |= (j == kt->keep[y]);
			}
			//PD("\t\t\t\t\t\tYou're\n");
			// don't continue searching with this number if any are the same
			if (any_same_j)
				continue;

			//PD("\t\t\t\t\t\tLooking\n");
			hand.hand[3] = j;
			for (Card crib = 0; crib < 52; crib++) {
				//PD("\t\t\t\t\t\t\t\tEntering Crib loop\n");
				uint8_t any_same_crib = 0;
				for (int z = 0; z < 6; z++) {
					any_same_crib |= (crib == kt->keep[z]);
				}
				//PD("\t\t\t\t\t\tFor\n");

				// don't continue searching with this number if any are the same
				if (any_same_crib)
					continue;

				//PD("\t\t\t\t\t\t?\n");
				hand.hand[4] = crib;
				Score s = score(&hand);

				//PD("\t\t\t\t\t\tPotential culprit?\n");
				// med, mode: just record for later
				vals[v_indx++] = s;
				//PD("\t\t\t\t\t\tNope\n");

				// avg
				kti->tavg += (float) s;
				//PD("\t\t\t\t\t\tSomething else\n");
				
				//PD("\t\t\t\t\t\t\t\tExiting Crib loop\n");
			}
			//PD("\t\t\t\t\t\tExiting J loop\n");
		}
		//PD("\t\t\t\t\t\tExiting I loop\n");
	}


	// cleanup
	//PD("toss_vals.size = %d\n", v_indx);
	PD("\t\t\t\t\t\tHello,\n");
	kti->tavg /= (float) TOSS_POSS_VALS;

	PD("\t\t\t\t\t\tIs it me\n");
	PD("\t\t\t\t\t\t\tWhat is throwing the segfault? Let's find out!\n");
	PD("\t\t\t\t\t\t\t\tvals\n");
	//PD("\t\t\t\t\t\t\t\t\tLet's verify!\n");
	//PD("[");
	// More news: fails here as well, so vals has stopped being accessible(?)
	//for (int _i_ = 0; _i_ < v_indx-1; _i_++) {
		//PD("%d, ", vals[_i_]);
	//}
	PD("%d]\n", vals[v_indx-1]);
	// The "answer" is vals
	// the next question is WHY?????
	// It's stack allocated memory for this location. There is no access
	// error in this method
	// You could argue that it's highly localized and printf should fail
	// because of that, but it still succeeds about 200 times before this.
	// Also, I'm only printing the pointer address itself, not the content.
	//PD("\t\t\t\t\t\t\t\t&vals=%p\n", &vals);
	PD("\t\t\t\t\t\t\t\tvals=%p\n", vals);
	PD("\t\t\t\t\t\t\t\tsize\n");
	PD("\t\t\t\t\t\t\t\tsize=%d\n", sizeof(vals[0]));
	PD("\t\t\t\t\t\t\t\tcompare_score\n");
	PD("\t\t\t\t\t\t\t\tcompare_score=%p\n", compare_scores);
	PD("\t\t\t\t\t\t\t: vals: %p, TOSS_POSS_VALS=%d, size=%d, compare_scores=%p\n",
		vals, TOSS_POSS_VALS, sizeof(vals[0]), compare_scores);
	TOSS_SORT(vals, TOSS_POSS_VALS, sizeof(vals[0]), compare_scores); //sizeof(Score), compare_scores);

	PD("\t\t\t\t\t\tYou're looking for?\n");
	// min/max (have to sort anyways, why waste computation time sorting
	kti->tmin = vals[0];
	kti->tmax = vals[TOSS_POSS_VALS-1];

	PD("\t\t\t\t\t\tHow about now?\n");
	// median
	kti->tmed = (vals[(TOSS_POSS_VALS/2)-1] + vals[TOSS_POSS_VALS/2]) / 2.0;

	PD("\t\t\t\t\t\tA terrifying...\n");
	// mode
	_kt_mode(&kti->tmod, vals, TOSS_POSS_VALS);

	PD("\t\t\t\t\t\t...Terrorist.\n");
	PD("\t\t\t\t\texiting eval_toss_vals with: "
			"tmin=%u, tmax=%u, tavg=%.5f, tmed=%.2f, tmod=%u\n",
			kti->tmin, kti->tmax, kti->tavg, kti->tmed, kti->tmod);
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

/*
 * Method called for each thread start.
 * Repeatedly finds the next valid hand and calls the scorer method on it.
 */
void * kt_threader(void * args) {
/*
#ifdef DEBUG
	PD("\tentering\n");
	if (1)
		return NULL;
#endif
*/
	KeepToss * kt = NULL;
	sqlite3 * db;
	kt_threader_args_t * targs = (kt_threader_args_t *) args;

	PD("entering threader\n");

	PD("\topening database connection\n");
	sqlite3_open_v2(targs->db_filename, &db, DB_OPEN_FLAGS, NULL);
	// as of 2017-10-10 18:12
	// 	this does not open the db, i guess because db==null afterwards
	// fixed as of 2017-10-10 18:23
	// 	new error: 5: SQLITE_BUSY (too many concurrent writes, by appearances)
	PD("\t\tdatabase opened\n");

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
	PD("\t\tentering kt_next()\n");
	if (!kt) {
		PD("\t\t\tkt is NULL, allocating\n");
		// allocate memory
		kt = (KeepToss *) calloc(1, sizeof(KeepToss));
		if (!kt) {
			PD("\t\t\t\tkt still NULL after calloc, exiting.\n");
			// exit quick if still not valid (NULL)
			// better to let single thread die than segfault proc
			return NULL;
		}
	}

	PD("\t\tLocking mutex to avoid race conditions.\n");
	// lock mutex to avoid race conditions
	pthread_mutex_lock(_kt_next_object_lock);
	{

		if (_kt_next_object_done) {
			PD("\t\tWe're done, so free memory and exit\n");
			// exit with NULL if we've gone through all the possibilities so threads
			// can exit
			// make sure to unlock the mutex and free memory as appropriate
			pthread_mutex_unlock(_kt_next_object_lock);
			free_keep_toss(kt);
			kt = NULL;
			return kt;
		}

		PD("\t\tincrementing the keep-toss to the next state\n");
		// implement integer increment base 52 on KeepToss->keep,toss as a dealt
		// hand
		// take advantage of the fact that C treats memory like a single tape
		do {	
			uint8_t carry = 1;
			for (uint8_t i = CARDS_IN_KEEP_TOSS_INCREMENT-1; i >= 0 && carry; i--) {
				_kt_next_object->keep[i] += carry;
				carry = _kt_next_object->keep[i] >= 52;
				_kt_next_object->keep[i] %= CRIBBAGE_HAND_INCREMENT_BASE;
			}
		} while (!all_increasing(_kt_next_object));
		// hand integer increment not necessary.
		// later on down the line, these cards are shuffled around anyways,
		// so order doesn't matter
		// therefore, we can keep the cards in numerical order and simply
		// walk through all possibilities where hand[0] < hand[1] < hand[2]...
		// however, we will re-use the increment code an
		// TODO
		// zero out the KeepToss->tosd,cut fields
		// (this can be handled by increment later and a validity check after a few
		// steps)
		// not necessary since this increment is on the global next object that
		// won't ever be touched in those fields

		PD("\t\tfinding out if we're done next step:\n");
		// quit the "next"-ing when we've gone through all combinations once
#ifdef DEBUG
		// initial keep...: {0, 1, 2, 3} ... {4, 4}
		// exit after XX * YY possibilities to keep it short and test time taken
		//_kt_next_object_done = (_kt_next_object->toss[0] >= 5);
		_kt_next_object_done = (_kt_next_object->keep[3] >= 4);
#else
		_kt_next_object_done = (_kt_next_object->keep[0] >= KT_LAST_FIRST_CARD);
#endif
		PD("\t\t\t%d\n", _kt_next_object_done);

		PD("\t\tCopying over incremented global hand to dst mem loc\n");
		// copy the incremented global hand to the destination memory location
		memcpy(kt, _kt_next_object, sizeof(KeepToss));

		PD("\t\tUnlocking mutex to avoid race conditions.\n");
		// unlock mutex to allow next thread access
	}
	pthread_mutex_unlock(_kt_next_object_lock);

	PD("\t\texiting\n");
	return kt;
}

int all_increasing(KeepToss * kt) {
	// rewrite explicitly instead of through loop to avoid:
	// 	1. compiler warning (annoying)
	// 	2. making compiler have to optimize
	// 	3. allow explicit fast-circuiting
	return kt->keep[0] < kt->keep[1] &&
		kt->keep[1] < kt->keep[2] &&
		kt->keep[2] < kt->keep[3] &&
		kt->keep[3] < kt->toss[0] &&
		kt->toss[0] < kt->toss[1];
}


//long int id(int k0, int k1, int k2, int k3, int t0, int t1) {
long int id(KeepToss * kt) {
	return 	kt->keep[0]	* 10000000000L
		+ kt->keep[1]	* 100000000L
		+ kt->keep[2]	* 1000000L
		+ kt->keep[3]	* 10000L
		+ kt->toss[0]	* 100L
		+ kt->toss[1]	* 1L;
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
	"(id, "\
		"kcard0, kcard1, kcard2, kcard3, "\
		"tcard0, tcard1, "\
		"kmin, kmax, kmed, kavg, kmod, "\
		"tmin, tmax, tmed, tavg, tmod) "\
	"VALUES (%ld, "\
		"%d, %d, %d, %d, "\
		"%d, %d, "\
		"%d, %d, %f, %f, %d, "\
		"%d, %d, %f, %f, %d);-- "
pthread_mutex_t * _kt_db_mutex;
uint8_t kt_db_add(sqlite3 * db, KeepToss * kt, KeepTossInfo * kti) {
	int rc;
	//char * err_msg;
	char err_msg[1024];
	
	// generate sql statement
	char sql[2048];
	sprintf(sql, SQL_FORMAT,
			id(kt),
			kt->keep[0], kt->keep[1], kt->keep[2], kt->keep[3],
			kt->toss[0], kt->toss[1],
			kti->kmin, kti->kmax, kti->kmed, kti->kavg, kti->kmod,
			kti->tmin, kti->tmax, kti->tmed, kti->tavg, kti->tmod);

#ifdef DEBUG
	PD("soon-to-be-executed sql: %s\n", sql);
	if (!db)
		PD("Database is null!!!!\n");
#endif

	// run sql statement in db
	// loop over until it's no longer locked
	// 	will this cause a lot of locking? IDK, but worth trying
	// 	yes, yes it does
	//while ((rc = sqlite3_exec(db, sql, kt_sqlite_callback, NULL, &err_msg)) == 5);
#ifndef DB_MULTI_FILE
	pthread_mutex_lock(_kt_db_mutex);
	{
#endif
	rc = sqlite3_exec(db, sql, kt_sqlite_callback, NULL, NULL); //&err_msg);
#ifndef DB_MULTI_FILE
	}
	pthread_mutex_unlock(_kt_db_mutex);
#endif
	PD("kt_db_add: returned %d\n", rc);
#ifdef DEBUG
	if (rc) {
		PD("SQL ERROR: %s\n", err_msg);
	}
#endif

	return (uint8_t) rc;
}


static int kt_sqlite_callback(void * _x, int argc, char ** argv, char ** _y) {
	for (int i = 0; i < argc; i++) {
		printf("%s = %s\n", _y[i], argv[i] ? argv[i] : "NULL");
	}
	printf("\n");
	return 0;
}

int main(void) {
	PD("initializations\n");
	pthread_t threads[DB_THREAD_COUNT];
#ifndef DB_MULTI_FILE
	kt_threader_args_t thread_args = {
		.db_filename = DB_FILENAME
	};
#endif

	// initialize shared objects
	_kt_next_object_done = 0;
	_kt_next_object_lock = (pthread_mutex_t *) malloc(sizeof(pthread_mutex_t));
	_kt_next_object = (KeepToss *) malloc(sizeof(KeepToss));
	// initialize to a sane start to avoid a few million invalid object fails
	//repeat 4 to allow the increment to succeed and not miss 0,1,2,3,4,5
	//_kt_next_object->keep = (Card[]) {0, 1, 2, 3};
	//_kt_next_object->toss = (Card[]) {4, 4};
//#ifdef CRIBBAGE_MEMCPY
//	memcpy(_kt_next_object->keep, (Card[])({0, 1, 2, 3, 4, 4};), 6*sizeof(Card));
//#else
	_kt_next_object->keep[0] = 0;
	_kt_next_object->keep[1] = 1;
	_kt_next_object->keep[2] = 2;
	_kt_next_object->keep[3] = 3;
	_kt_next_object->toss[0] = 4;
	_kt_next_object->toss[1] = 4;
//#endif
	_kt_db_mutex = (pthread_mutex_t *) malloc(sizeof(pthread_mutex_t));

	// initialize mutex lock
	pthread_mutex_init(_kt_next_object_lock, NULL);
	pthread_mutex_init(_kt_db_mutex, NULL);

	// create pthreads
	PD("creating threads\n");
	for (int i = 0; i < DB_THREAD_COUNT; i++) {
#ifdef DB_MULTI_FILE
		PD("creating thread arguments for thread %d\n", i);
		kt_threader_args_t * thread_args =
			(kt_threader_args_t *) malloc(sizeof(kt_threader_args_t));
		sprintf(thread_args->db_filename, DB_FILENAME_FORMAT, i);
		PD("creating thread %d\n", i);
		if(pthread_create(&threads[i], NULL, kt_threader, thread_args)) {
			PD("\terror occurred in creation\n");
		}
#else
		PD("creating thread %d\n", i);
		if(pthread_create(&threads[i], NULL, kt_threader, &thread_args)) {
			PD("\terror occurred in creation\n");
		}
#endif
	}

	// join threads
	PD("joining threads\n");
	for (int i = 0; i < DB_THREAD_COUNT; i++) {
		pthread_join(threads[i], NULL);
	}

	// destroy objects/free memory
	PD("destroying\n");
	if (_kt_next_object)
		free_keep_toss(_kt_next_object);
	if (_kt_next_object_lock)
		pthread_mutex_destroy(_kt_next_object_lock);
	if (_kt_db_mutex)
		pthread_mutex_destroy(_kt_db_mutex);

	return 0;
}

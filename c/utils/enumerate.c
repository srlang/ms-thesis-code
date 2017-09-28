#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

#include "enumerate.h"
#include "cribbage.h"
#include "score.h"
#include "utils.h"

/* globals */
Hand * global_hand;
pthread_mutex_t * global_hand_lock;


/*
 * Input: hand that is not complete (i.e. is missing a crib card (is 0))
 */
void thread_work_method(Hand * hand) {
	PD("\tthread_work_method: entering: %d %d %d %d | %d\n",
			hand->hand[0],
			hand->hand[1],
			hand->hand[2],
			hand->hand[3],
			hand->hand[4]
			);
	for (uint8_t i = 0; i < NUM_CARDS; i++) {
		uint8_t valid = 1;
		PD("\tthread_work_method: trying crib: %d\n", i);
		for (uint8_t j = 0; j < CARDS_IN_HAND && valid; j++) {
			valid &= i != hand->hand[j];
		}
		if (valid) {
			PD("\tthread_work_method: valid\n");
			hand->hand[CRIB_LOC] = i;
			output(hand, score(hand));
		} else {
			PD("\tthread_work_method: invalid\n");
		}
	}
	PD("\texiting thread_work_method\n");
	// we are done with all of these combinations, free the memory
	// don't actually, because calling method will do this for us
	//free_hand(hand); // drawing
}

void output(Hand * hand, Score score) {
	printf("%u, %u, %u, %u; %u: %u\n",
			hand->hand[0],
			hand->hand[1],
			hand->hand[2],
			hand->hand[3],
			hand->hand[4],
			score);
}

/*
 * Method called for each thread start.
 * Repeatedly finds the next valid hand and calls the scorer method on it.
 */
void * threader(void * args) {
	PD("entering threader\n");
	Hand * hand;
	while ((hand = next_hand()) != NULL) {
		PD("\thave a non-NULL hand\n");
		if (valid(hand)) {
			PD("\thand is valid\n");
			thread_work_method(hand);
		}
		PD("\tfreeing hand\n");
		free_hand(hand);
	}
	PD("exiting from thread\n");
	return NULL;
}

/*
 * Is a hand valid? Are all of the cards unique?
 */
uint8_t valid(Hand * hand) {
	uint8_t ret = 1;

	for (uint8_t i = 0; i < CARDS_IN_COUNT-1; i++) {
		for (uint8_t j = i+1; j < CARDS_IN_COUNT; j++) {
			ret &= hand->hand[i] != hand->hand[j];
		}
	}

	return ret;
}

/*
 * Returns a copy of the next hand that needs to be evaluated for all
 * possible cribs.
 * This is a _COPY_ of the hand, therefore, it must be destroyed after
 * use by the calling function.
 */
Hand * next_hand() {
	PD("next_hand: entering\n");
	Hand * ret;
	while(!valid_next(ret = inc_hand())) {
		PD("next_hand:\t%p is not valid hand, freeing\n", ret);
		PD("next_hand:\t%d %d %d %d | %d\n",
				ret->hand[0], ret->hand[1], ret->hand[2], ret->hand[3], ret->hand[4]);
		free_hand(ret);
	}
	PD("next_hand: exiting with %p\n", ret);
	return ret;
}
uint8_t valid_next(Hand * hand) {
	uint8_t valid = 1;
	for (uint8_t i = 0; i < CARDS_IN_HAND-1 && valid; i++) {
		for (uint8_t j = i+1; j < CARDS_IN_HAND && valid; j++) {
			PD("valid_next: %d ?!=? %d: %d\n", i, j, (hand->hand[i] != hand->hand[j]));
			valid &= hand->hand[i] < hand->hand[j];
		}
	}
	return valid;
}
Hand * inc_hand() {
	// basically, we have to rewrite integer increment/carrying base 52
	//PD("inc_hand: entering\n");
	
	// begin lock
	//PD("inc_hand: getting lock...\n");
	pthread_mutex_lock(global_hand_lock);
	//PD("inc_hand: ...lock acquired\n");

	// hand[0, 1, 2, 3, crib]
	//PD("inc_hand: going through addition logic\n");
	uint8_t base = 52;
	uint8_t carry = 1;
	for (int8_t i = 3; i >= 0 && carry; i--) {
		//PD("inc_hand:\tentering loop\n");
		//PD("inc_hand:\t0:%d 1:%d 2:%d 3:%d | 4:%d\n",
				//global_hand->hand[0], global_hand->hand[1], global_hand->hand[2], global_hand->hand[3],
				//global_hand->hand[4]);
		//PD("inc_hand:\tadding carry:%d to position %d\n", carry, i);
		global_hand->hand[i] += carry;
		carry = global_hand->hand[i] >= 52;
		global_hand->hand[i] %= base;
	}

	//PD("inc_hand: calling malloc for ret\n");
	Hand * ret = new_hand(); //(Hand *) malloc(sizeof(Hand));
	if (ret) {
		//PD("inc_hand: ret malloc'd\n");
		memcpy(ret->hand, global_hand->hand, CARDS_IN_COUNT*sizeof(Card));
		//PD("inc_hand: ret memcpy'd\n");
	}

	// end lock
	//PD("inc_hand: unlocking...\n");
	pthread_mutex_unlock(global_hand_lock);
	//PD("inc_hand: lock relinquished\n");

	//PD("inc_hand: exiting with %p\n", ret);
	return ret;
}

void * DBthreader(void * args) {
	int i = 0;
	while (++i < 1000)
		;
	return NULL;
}

int main(void) {
	PD("initializations\n");
	pthread_t threads[THREAD_COUNT];
	global_hand_lock = (pthread_mutex_t *) malloc(sizeof(pthread_mutex_t));
	//global_hand = (Hand *) calloc(1, sizeof(Hand));
	global_hand = new_hand();

	// initialize mutex lock
	//PD("creating mutexes\n");
	pthread_mutexattr_t mutex_attr;
	//PD("\tattr_init...\n");
	//pthread_mutexattr_init(&mutex_attr);
	//PD("\tmutex_init...");
	pthread_mutex_init(global_hand_lock, NULL); //&mutex_attr);
	//PD("done.\n");

	PD("creating threads\n");
	for (int i = 0; i < THREAD_COUNT; i++) {
		if(pthread_create(&threads[i], NULL, threader, NULL)) {
			PD("\terror occurred in creation\n");
		}
	}

	PD("joining threads\n");
	int retval;
	for (int i = 0; i < THREAD_COUNT; i++) {
		pthread_join(threads[i], NULL);
	}

	PD("destroying\n");
	// destroy mutex lock
	pthread_mutex_destroy(global_hand_lock);
}

#include <stdlib.h>

#include "utils.h"
#include "cribbage.h"
#include "score.h"

extern Score score(Hand * hand) {
	return fifteens(hand)
		+ pairs(hand)
		+ runs(hand)
		+ right_jack(hand)
		+ flush(hand);
}

Score fifteens(Hand * hand) {
//	PD("fifteens: input: %u %u %u %u %u\n",
//			hand->hand[0],
//			hand->hand[1],
//			hand->hand[2],
//			hand->hand[3],
//			hand->hand[4]);
	uint8_t arr[16];
	arr[0] = 1;
	for (uint8_t i = 1 ; i < 16; i++) {
		// force initialization to all 0s in case memory allocator didn't
		arr[i] = 0;
	}

	for (uint8_t i = 0; i < 5; i++) {
		uint8_t shift = value(hand->hand[i]);
		for (uint8_t j = 15; j >= shift; j--) {
			arr[j] += arr[j-shift];
		}
	}

	//PD("fifteens: count: %u\n", arr[15]);
	return SCORE_FIFTEENS * arr[15];
}

Score pairs(Hand * hand) {
	uint8_t pairs = 0;
	for (int i = 0; i < 4; i++) {
		Type a = type(hand->hand[i]);
		for (int j = i+1; j <= 4; j++) {
			if (type(hand->hand[j]) == a)
				pairs++;
		}
	}
	//PD("pairs: count: %u\n", pairs);
	return (Score) (pairs * SCORE_PAIRS);
}

Score runs(Hand * hand) {
	uint8_t buckets[NUM_TYPES];

	Score runs_score = 0;

	// clear buckets array for safety
	for (uint8_t i = 0; i < NUM_TYPES; i++) {
		buckets[i] = 0;
	}

	// populate types buckets
	for (uint8_t i = 0; i < 5; i++) {
		buckets[type(hand->hand[i])]++;
	}
	#ifdef DEBUG
	//PD("score: buckets = [");
	for (int i = 0; i < NUM_TYPES-1; i++) {
		//PD("%u, ", buckets[i]);
	}
	//PD("%u]\n", buckets[NUM_TYPES-1]);
	#endif

	for (uint8_t i = 0; i < NUM_TYPES; i++) {
		if (!buckets[i])
			continue;

		uint8_t local_run = 0;
		uint8_t prod = 1;
		for (; buckets[i] != 0 && i < NUM_TYPES; i++) {
			local_run++;
			prod *= buckets[i];
		}

		if (local_run >= 3)
			runs_score += local_run * prod;
	}

	//PD("runs: score: %u\n", runs_score);
	return runs_score;
}

Score right_jack(Hand * hand) {
	Card crib = hand->hand[4];
	Score ret = 0;
	for (int i = 0; i < 4; i++) {
		Card card = hand->hand[i];
		if (type(card) == Jack && suit(card) == suit(crib)) {
			ret = 1;
			break;
		}
	}
	//PD("right_jack: %u\n", ret);
	return ret;
}

Score flush(Hand * hand) {
	Score of_same_suit = 0;
	for (uint8_t i = 3; i >= 0; i--) {
		if (suit(hand->hand[i]) == suit(hand->hand[i+1]))
			of_same_suit++;
		else
			break;
	}

	if (is_dealers_hand(hand) && of_same_suit == 5) {
		//PD("flush: returning %u\n", of_same_suit);
		return of_same_suit;
	} else if (of_same_suit >= 4) {
		//PD("flush: returning %u\n", of_same_suit);
		return of_same_suit;
	} else {
		//PD("flush: returning %u\n", 0);
		return 0;
	}
}

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
	// see python code for algorithm and explanation.
	// earler did not work, according to test cases. this is copied from python
	uint8_t A[5] = {0, 0, 0, 0, 0};
	for (int i = 1; i < 5; i++) {
		A[i] = A[i-1] + ( (suit(hand->hand[i]) == suit(hand->hand[i-1])) ? 1 : 0 );
	}
	if (is_crib_hand(hand)) {
		return A[4] == 4 ? 5 : 0;
	} else if (A[3] == 3) {
		// should be able to just return A[4], but python uses this and I'm not
		// taking any chances right now.
		// highly doubt that this one comparison will cause too much cpu usage
		// difference and affect the computation time greatly.
		return 1 + MAX(A[3], A[4]);
	} else {
		return 0;
	}
}

#ifdef MAIN_SCORE
int main(void) {
	// suits
	ASSERT_EQ(0, suit(16), "suits issue 0\n");
	ASSERT_EQ(1, suit(21), "suits issue 1\n");
	ASSERT_EQ(2, suit(38), "suits issue 2\n");
	ASSERT_EQ(3, suit(43), "suits issue 3\n");

	// class
	ASSERT_EQ(0, type(1), "type issue 0\n");
	ASSERT_EQ(1, type(5), "type issue 1\n");
	ASSERT_EQ(2, type(8), "type issue 2\n");
	ASSERT_EQ(3, type(15), "type issue 3\n");
	ASSERT_EQ(4, type(16), "type issue 4\n");
	ASSERT_EQ(5, type(20), "type issue 5\n");
	ASSERT_EQ(6, type(26), "type issue 6\n");
	ASSERT_EQ(7, type(28), "type issue 7\n");
	ASSERT_EQ(8, type(33), "type issue 8\n");
	ASSERT_EQ(9, type(38), "type issue 9\n");
	ASSERT_EQ(10, type(40), "type issue 10\n");
	ASSERT_EQ(11, type(45), "type issue 11\n");
	ASSERT_EQ(12, type(50), "type issue 12\n");

	// value
	ASSERT_EQ(1, value(1), "value issue 0\n");
	ASSERT_EQ(2, value(5), "value issue 1\n");
	ASSERT_EQ(3, value(8), "value issue 2\n");
	ASSERT_EQ(4, value(15), "value issue 3\n");
	ASSERT_EQ(5, value(16), "value issue 4\n");
	ASSERT_EQ(6, value(20), "value issue 5\n");
	ASSERT_EQ(7, value(26), "value issue 6\n");
	ASSERT_EQ(8, value(28), "value issue 7\n");
	ASSERT_EQ(9, value(33), "value issue 8\n");
	ASSERT_EQ(10, value(38), "value issue 9\n");
	ASSERT_EQ(10, value(40), "value issue 10\n");
	ASSERT_EQ(10, value(45), "value issue 11\n");
	ASSERT_EQ(10, value(50), "value issue 12\n");

	// fifteens
	Hand hand;
	//hand.hand = {0, 5, 10, 15, 20};
	hand.hand[0] = 0;
	hand.hand[1] = 1;
	hand.hand[2] = 2;
	hand.hand[3] = 3;
	hand.hand[4] = 4;
	ASSERT_EQ(0, fifteens(&hand), "fifteens issue 0\n");
	hand.hand[0] = 16;
	hand.hand[1] = 38;
	hand.hand[2] = 0;
	hand.hand[3] = 1;
	hand.hand[4] = 2;
	ASSERT_EQ(2, fifteens(&hand), "fifteens issue 1\n");
	hand.hand[0] = 16;
	hand.hand[1] = 38;
	hand.hand[2] = 39;
	hand.hand[3] = 0;
	hand.hand[4] = 1;
	ASSERT_EQ(4, fifteens(&hand), "fifteens issue 2\n");
	hand.hand[0] = 16;
	hand.hand[1] = 17;
	hand.hand[2] = 18;
	hand.hand[3] = 40;
	hand.hand[4] = 41;
	ASSERT_EQ(14, fifteens(&hand), "fifteens issue 3\n");
	hand.hand[0] = 16;
	hand.hand[1] = 17;
	hand.hand[2] = 18;
	hand.hand[3] = 40;
	hand.hand[4] = 16;
	ASSERT_EQ(16, fifteens(&hand), "fifteens issue 4\n");

	// pairs
	hand.hand[0] = 0;
	hand.hand[1] = 5;
	hand.hand[2] = 10;
	hand.hand[3] = 15;
	hand.hand[4] = 20;
	ASSERT_EQ(0, pairs(&hand), "pairs issue 0\n");
	hand.hand[0] = 0;
	hand.hand[1] = 1;
	hand.hand[2] = 10;
	hand.hand[3] = 15;
	hand.hand[4] = 20;
	ASSERT_EQ(2, pairs(&hand), "pairs issue 1\n");
	hand.hand[0] = 0;
	hand.hand[1] = 1;
	hand.hand[2] = 4;
	hand.hand[3] = 5;
	hand.hand[4] = 10;
	ASSERT_EQ(4, pairs(&hand), "pairs issue 2\n");
	hand.hand[0] = 0;
	hand.hand[1] = 1;
	hand.hand[2] = 2;
	hand.hand[3] = 5;
	hand.hand[4] = 10;
	ASSERT_EQ(6, pairs(&hand), "pairs issue 3\n");
	hand.hand[0] = 0;
	hand.hand[1] = 1;
	hand.hand[2] = 2;
	hand.hand[3] = 4;
	hand.hand[4] = 5;
	ASSERT_EQ(8, pairs(&hand), "pairs issue 4\n");
	hand.hand[0] = 0;
	hand.hand[1] = 1;
	hand.hand[2] = 2;
	hand.hand[3] = 3;
	hand.hand[4] = 4;
	ASSERT_EQ(12, pairs(&hand), "pairs issue 5\n");

	// runs
	hand.hand[0] = 0;
	hand.hand[1] = 10;
	hand.hand[2] = 20;
	hand.hand[3] = 30;
	hand.hand[4] = 40;
	ASSERT_EQ(0, runs(&hand), "runs issue 0\n");
	hand.hand[0] = 0;
	hand.hand[1] = 4;
	hand.hand[2] = 15;
	hand.hand[3] = 20;
	hand.hand[4] = 30;
	ASSERT_EQ(0, runs(&hand), "runs issue 1\n");
	hand.hand[0] = 0;
	hand.hand[1] = 4;
	hand.hand[2] = 8;
	hand.hand[3] = 20;
	hand.hand[4] = 24;
	ASSERT_EQ(3, runs(&hand), "runs issue 2\n");
	hand.hand[0] = 0;
	hand.hand[1] = 4;
	hand.hand[2] = 8;
	hand.hand[3] = 12;
	hand.hand[4] = 20;
	ASSERT_EQ(4, runs(&hand), "runs issue 3\n");
	hand.hand[0] = 0;
	hand.hand[1] = 4;
	hand.hand[2] = 8;
	hand.hand[3] = 12;
	hand.hand[4] = 16;
	ASSERT_EQ(5, runs(&hand), "runs issue 4\n");
	hand.hand[0] = 0;
	hand.hand[1] = 1;
	hand.hand[2] = 4;
	hand.hand[3] = 8;
	hand.hand[4] = 25;
	ASSERT_EQ(6, runs(&hand), "runs issue 5\n");
	hand.hand[0] = 0;
	hand.hand[1] = 1;
	hand.hand[2] = 4;
	hand.hand[3] = 8;
	hand.hand[4] = 12;
	ASSERT_EQ(8, runs(&hand), "runs issue 6\n");
	hand.hand[0] = 0;
	hand.hand[1] = 1;
	hand.hand[2] = 4;
	hand.hand[3] = 8;
	hand.hand[4] = 9;
	ASSERT_EQ(12, runs(&hand), "runs issue 7\n");

	// nobs/right-jack
	hand.hand[0] = 17;
	hand.hand[1] = 18;
	hand.hand[2] = 19;
	hand.hand[3] = 41;
	hand.hand[4] = 16;
	ASSERT_EQ(0, right_jack(&hand), "nobs issue 0\n");
	hand.hand[0] = 17;
	hand.hand[1] = 18;
	hand.hand[2] = 19;
	hand.hand[3] = 40;
	hand.hand[4] = 16;
	ASSERT_EQ(1, right_jack(&hand), "nobs issue 1\n");
	hand.hand[0] = 17;
	hand.hand[1] = 18;
	hand.hand[2] = 40;
	hand.hand[3] = 19;
	hand.hand[4] = 16;
	ASSERT_EQ(1, right_jack(&hand), "nobs issue 2\n");

	// flush
	hand.hand[0] = 1;
	hand.hand[1] = 2;
	hand.hand[2] = 3;
	hand.hand[3] = 4;
	hand.hand[4] = 5;
	hand.bitmask &= 0;
	ASSERT_EQ(0, flush(&hand), "flush issue 0 hand\n"); // own hand
	hand.bitmask ^= _HAND_CRIB;
	ASSERT_EQ(0, flush(&hand), "flush issue 0 crib\n"); // crib
	hand.hand[0] = 1;
	hand.hand[1] = 5;
	hand.hand[2] = 9;
	hand.hand[3] = 13;
	hand.hand[4] = 14;
	hand.bitmask ^= _HAND_CRIB;
	ASSERT_EQ(4, flush(&hand), "flush issue 1 hand\n"); // own hand
	hand.bitmask ^= _HAND_CRIB;
	ASSERT_EQ(0, flush(&hand), "flush issue 1 crib\n"); // crib
	hand.hand[0] = 1;
	hand.hand[1] = 5;
	hand.hand[2] = 9;
	hand.hand[3] = 13;
	hand.hand[4] = 17;
	hand.bitmask ^= _HAND_CRIB;
	ASSERT_EQ(5, flush(&hand), "flush issue 2 hand\n"); // hand
	hand.bitmask ^= _HAND_CRIB;
	ASSERT_EQ(5, flush(&hand), "flush issue 2 crib\n"); // crib

	// all together, now
	// whole hand scoring
	hand.hand[0] = 17;
	hand.hand[1] = 18;
	hand.hand[2] = 19;
	hand.hand[3] = 40;
	hand.hand[4] = 16;
	ASSERT_EQ(29, score(&hand), "whole-hand scoring issue 0\n");
	hand.hand[0] = 20;
	hand.hand[1] = 21;
	hand.hand[2] = 24;
	hand.hand[3] = 28;
	hand.hand[4] = 29;
	ASSERT_EQ(20, score(&hand), "whole-hand scoring issue 1\n");
	hand.hand[0] = 12;
	hand.hand[1] = 13;
	hand.hand[2] = 16;
	hand.hand[3] = 20;
	hand.hand[4] = 21;
	ASSERT_EQ(24, score(&hand), "whole-hand scoring issue 2\n");
	hand.hand[0] = 0;
	hand.hand[1] = 5;
	hand.hand[2] = 36;
	hand.hand[3] = 47;
	hand.hand[4] = 49;
	ASSERT_EQ(0, score(&hand), "whole-hand scoring issue 3\n");
	hand.hand[0] = 36;
	hand.hand[1] = 47;
	hand.hand[2] = 0;
	hand.hand[3] = 5;
	hand.hand[4] = 49;
	ASSERT_EQ(0, score(&hand), "whole-hand scoring issue 4\n");
	hand.hand[0] = 12;
	hand.hand[1] = 20;
	hand.hand[2] = 16;
	hand.hand[3] = 13;
	hand.hand[4] = 21;
	ASSERT_EQ(24, score(&hand), "whole-hand scoring issue 5\n");
	hand.hand[0] = 17;
	hand.hand[1] = 40;
	hand.hand[2] = 19;
	hand.hand[3] = 18;
	hand.hand[4] = 16;
	ASSERT_EQ(29, score(&hand), "whole-hand scoring issue 6\n");
	hand.hand[0] = 17;
	hand.hand[1] = 18;
	hand.hand[2] = 40;
	hand.hand[3] = 19;
	hand.hand[4] = 16;
	ASSERT_EQ(29, score(&hand), "whole-hand scoring issue 7\n");
}
#endif

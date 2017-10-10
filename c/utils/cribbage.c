#include "cribbage.h"

extern uint8_t is_dealers_hand(Hand * hand) {
	return _HAND_DEALER & hand->bitmask;
}
extern uint8_t is_crib_hand(Hand * hand) {
	return _HAND_CRIB & hand->bitmask;
}

/*
 * Allocate a new hand (including the actual card slot) to avoid segfaults.
 */
extern Hand * new_hand() {
	Hand * ret = (Hand *) calloc(1, sizeof(Hand));

	//Card * hand = (Card *) calloc(CARDS_IN_COUNT, sizeof(Card));
	//ret->hand = hand;
	//ret.hand = hand;

	return ret;
}

extern void free_hand(Hand * hand) {
	//free(hand->hand);
	free(hand);
}

extern Suit suit(Card card) {
	return (Suit) card % 4;
}

extern Type type(Card card) {
	return (Type) card / 4;
}

#define MIN(x,y)	(x < y ? x : y)
extern uint8_t value(Card card) {
	return MIN(MAX_VALUE, 1+(card/4));
}


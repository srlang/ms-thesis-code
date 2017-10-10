#ifndef _CRIBBAGE_H_
#define _CRIBBAGE_H_

#include <stdint.h>
#include <stdlib.h>

#define MAX_SCORE		29
#define ERROR_SCORE		-1

#define NUM_CARDS		52
#define CARDS_IN_HAND	4
#define CARDS_IN_COUNT	5
#define CRIB_LOC		4

#define NUM_TYPES		13
#define MAX_VALUE		10

typedef int8_t Card;
typedef struct hand_s {
	//Card * hand; // original
	Card hand[5];
	uint8_t bitmask;
} Hand;
#define _HAND_DEALER	0x02
#define _HAND_CRIB		0x01
extern uint8_t is_dealers_hand(Hand * hand);
extern uint8_t is_crib_hand(Hand * hand);
extern Hand * new_hand();
extern void free_hand(Hand * hand);

typedef uint8_t Score;
//typedef int Score;

typedef enum {
	Clubs = 0,
	Diamonds = 1,
	Hearts = 2,
	Spades = 3
} Suit;

typedef enum {
	Ace = 0,
	Two,
	Three,
	Four,
	Five,
	Six,
	Seven,
	Eight,
	Nine,
	Ten,
	Jack,
	Queen,
	King
} Type;

extern Suit suit(Card card);
extern Type type(Card card);
extern uint8_t value(Card card);


#endif /* _CRIBBAGE_H_ */

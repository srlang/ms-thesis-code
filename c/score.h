#ifndef _CRIBBAGE_SCORE_H
#define _CRIBBAGE_SCORE_H

#define SCORE_FIFTEENS	2
#define SCORE_PAIRS		2

extern Score score(Hand * hand);
Score fifteens(Hand * hand);
Score pairs(Hand * hand);
Score runs(Hand * hand);
Score right_jack(Hand * hand);
Score flush(Hand * hand);

#endif /* _CRIBBAGE_SCORE_H */

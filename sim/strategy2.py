# Sean R. Lang <sean.lang@cs.helsinki.fi>

from cribbage import score_hand

from utils import PD

###
# N.B.:
#   1. all methods in this module will assume that the cards passed to it are
#       in sorted order.
#       This is crucial to the search method for the database.
#   2. Each of these methods will return a LIST of possible items.
#       There may be cases in which multiple hands deal have the same property:
#       (out of 25 possible scores, and 46 possible cribs, pigeon-hole principle).
###

KEEP_NUMBER = 4

def _possible_keep_toss_tuple_list(cards):
    # return a list of the tuples of all possible combinations of keep/toss of
    # the given cards
    combos = combinations(cards, KEEP_NUMBER)
    ret = []
    for combo in combos:
        cards_not_in_combo = [x for x in cards if x not in combo]
        ret.append((tuple(combo), tuple(cards_not_in_combo)))
    return ret

def _retrieve_hand_statistics(kt_tuple):
    k,t = kt_tuple
    # TODO
    pass

def hand_max_min(card):
    # Choose the hand(s) with the maximum minimum.
    # i.e. most guaranteed points
    # TODO
    pass

def hand_max_avg(cards):
    # Choose the hand(s) with the maximum average score
    # TODO
    pass

def hand_max_med(cards):
    # Choose the hand(s) with the maximum median score
    # TODO
    pass

def hand_max_poss(cards):
    # Choose the hand(s) with the maximum possible score (gambler's strategy)
    # TODO
    pass

def hand_min_avg_crib(cards):
    # Choose the hand(s) with the minimum average crib
    # TODO
    pass

def _stanley(cards):
    return hand_min_avg(cards)

def hand_max_avg_both(cards):
    # Choose the hand(s) with the maximum sum of average crib + average hand
    # TODO
    pass

def pegging_max_avg(cards):
    # Choose the hand which has the maximum average pegging points scored
    # TODO
    pass

def pegging_max_med(cards):
    # Choose the hand which has the maximum median pegging points scored
    # TODO
    pass


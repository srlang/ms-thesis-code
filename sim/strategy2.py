# Sean R. Lang <sean.lang@cs.helsinki.fi>

from itertools  import      combinations

from cribbage   import      score_hand

from records    import      engine,\
                            session,\
                            PlayedHandRecord,\
                            KeepThrowStatistics
                    

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

def _retrieve_hand_statistics(kt_tuple, session=session):
    k,t = kt_tuple
    q = session.query(KeepThrowStatistics).filter_by(\
            kcard0=k[0],\
            kcard1=k[1],\
            kcard2=k[2],\
            kcard3=k[3],\
            tcard0=t[0],\
            tcard1=t[1])
    return q.first() #one_or_none()

def possible_KeepThrowStatistics(cards):
    ret = [_retrieve_hand_statistics(kt_t)\
            for kt_t in _possible_keep_toss_tuple_list(cards)]
    return [x for x in ret if x is not None]

def _retrieve_property_list(list_kts, prop_name):
    return [kts.__dict__[prop_name] for kts in list_kts]

def _get_all_indices(list_vals, spec_val):
    return [i for i,x in enumerate(list_vals) if x == spec_val]

def _get_by_multiple_indices(list_vals, indices):
    return [list_vals[i] for i in indices]

def _to_keep_toss_tuple(kts):
    return ((kts.kcard0, kts.kcard1, kts.kcard2, kts.kcard3), (kts.tcard0, kts.tcard1))

def hand_picker(cards, hand_property, eval_fn):
    # From a given set of cards, pick the keep/toss combination(s) that have
    # the desired eval_fn(combo.hand_property)
    kts = possible_KeepThrowStatistics(cards)
    props = _retrieve_property_list(kts, hand_property)
    _prop = eval_fn(props)
    p_indices = _get_all_indices(props, _prop)
    kts_ret = _get_by_multiple_indices(kts, p_indices)
    return [_to_keep_toss_tuple(x) for x in kts_ret]

def hand_max_min(cards):
    # Choose the hand(s) with the maximum minimum.
    # i.e. most guaranteed points
    return hand_picker(cards, 'kmin', max)

def hand_max_avg(cards):
    # Choose the hand(s) with the maximum average score
    return hand_picker(cards, 'kavg', max)

def hand_max_med(cards):
    # Choose the hand(s) with the maximum median score
    return hand_picker(cards, 'kmed', max)

def hand_max_poss(cards):
    # Choose the hand(s) with the maximum possible score (gambler's strategy)
    return hand_picker(cards, 'kmin', max)

def hand_min_avg_crib(cards):
    # Choose the hand(s) with the minimum average crib
    return hand_picker(cards, 'tavg', min)

#def hand_max_avg_both(cards):
#    # Choose the hand(s) with the maximum sum of average crib + average hand
#    kts = possible_KeepThrowStatistics(cards)
#    kavgs = _retrieve_property_list(kts, 'kavg')
#    tavgs = _retrieve_property_list(kts, 'tavg')
#    avgs = [kavgs[i] + tavgs[i] for i in xrange(len(kavgs))]
#    max_avg = max(avgs)
#    p_indcs = _get_all_indices(avgs, max_avg)
#    kts_ret = _get_by_multiple_indices(kts, p_indcs)
#    return [_to_keep_toss_tuple(x) for x in kts_ret]

def pegging_max_avg_gained(cards):
    # Choose the hand which has gained the maximum average of points for the
    # player. This would typically be useful as a Hail Mary for the dealer in
    # a very close game at the last hand.
    # TODO
    pass

def pegging_max_med_gained(cards):
    # Choose the hand which has the maximum median pegging points scored
    # TODO
    pass

def pegging_min_avg_given(cards):
    # Choose the hand which has given the least points up, on average
    # TODO
    pass



from itertools import combinations

KEEP_NUMBER = 4

def _strategy_interface(cards):
    return cards[:KEEP_NUMBER]

def _get_strategy_interface(module, strategy_str):
    # return the method object to call corresponding to the strategy named
    # in the given string
    return getattr(module, strategy_str)

def possible_keep_throw_choices(cards):
    # possible choices to keep and throw so that we know what
    # visual inspection: good
    combos = combinations(cards, KEEP_NUMBER)
    ret = []
    for combo in combos:
        cards_not_in_combo = [x for x in cards if x not in combo]
        ret.append((list(combo), cards_not_in_combo))
    return ret

def _enumerate_possible_hand_values(keep, toss):
    possible_cut_cards = [x for x in range(52)
            if x not in toss and x not in keep]
    possible_hand_values = []
    for cut_card in possible_cut_cards:
        possible_hand_values.append(score_hand(hand, cut_card))
    return possible_hand_values

def hand_compute_value(cards, list_func):
    values = {}
    for kt in possible_keep_throw_choices(cards):
        k,t = kt
        hv = _enumerate_possible_hand_values(k,t)
        values[kt] = list_func(hv)
    return values

def select_min_valued_hand(possible_hands_values_dict):
    return _select_valued_hand(possible_hands_values_dict, min)

def select_max_valued_hand(possible_hands_values_dict):
    # select the key corresponding to the maximum value
    return _select_valued_hand(possible_hands_values_dict, max)

def _select_valued_hand(possible_hands_values_dict, find_fn):
    # reference: https://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
    # make them lists to be able to index later
    values = list(possible_hand_values_dict.values())
    keys = list(possible_hand_values_dict.keys())
    return keys[values.index(find_fn(values))]


def list_min(values):
    return min(values)

def list_max(values):
    return max(values)

def list_avg(values):
    return sum(values) / len(values)

# TODO: in the future, find a way to use pre-computed/stored values
def hand_max_min(cards):
    # Safe strategy, pick the hand that has the most guaranteed points
    return select_max_valued_hand(hand_compute_values(cards, list_min))

def hand_max_avg(cards):
    # Choose the hand that has the maximum average points when accounting for
    # cut card possibilities
    return select_max_valued_hand(hand_compute_values(cards, list_avg))

def hand_max_med(cards):
    # Choose the hand that has the maximum median points when accounting for
    # cut card possibilities
    return select_max_valued_hand(hand_compute_values(cards, list_med))

def hand_max_poss(cards):
    # Hail Mary strategy, pick the hand that has the chance of the largest value.
    return select_max_valued_hand(hand_compute_values(cards, list_max))


def pegging_max_avg(cards):
    # TODO
    # Pick the hand that has the maximum average points scored over time.
    pass

def pegging_max_med(cards):
    # TODO
    # Pick the hand that has the maximum median for points scored over time.
    pass

def disjoint(a, b):
    for x in a:
        if x in b:
            return False
    return True

def possible_cribs(keep, throw):
    # enumerate possible cribs knowing the kept and thrown cards
    possibilities = []
    for candidate in combinations(range(52), 2):
        cand = list(candidate)
        if disjoint(cand, keep) and disjoint(cand, throw):
            possibilities.append(throw + cand)
    return possibilities

def _stanley(cards):
    # TODO
    # Otherwise known as an extremely defensive strategy.
    # Avoid giving points to the dealer at all costs.
    # A stupid homage to a man I've never met: my great-grandfather who was
    # supposedly so defensive that he would throw away the chance ot a 
    # 29-hand to avoid giving the opposing player a pair in the crib.
    crib_avg_possibilities = {}
    for keep,throw in possible_keep_throw_combinations(cards):
        poss_cribs = possible_cribs(keep,throw)
        summa = 0
        #numma = 0
        for crib in poss_cribs:
            for cut_card in range(52):
                # throw is subset of crib
                if cut_card not in crib and cut_card not in keep:
                    summa += score_hand(throw, crib)
            #numba += 1
        #crib_avg_possibilities.append(summa / numba)
        crib_avg_possibilities[(keep,throw)] = summa #/ numba
    return select_min_valued_hand(crib_avg_possibilities)

def hand_min_avg_crib(cards):
    # Minimize the average expected point value of the crib if the cards
    # are thrown.
    return _stanley(cards)

def hand_max_avg_both(cards):
    # TODO
    # Find the combination of keep and throw that returns the maximum
    # expected return from both combined.
    # Can be thought of as a combination of hand_max_*_hand & hand_max_avg_crib
    pass

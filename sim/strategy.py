from itertools  import combinations
from statistics import median

from cribbage   import score_hand
from records    import Session,\
                        PlayedHandRecord,\
                        HandStatistics,\
                        ThrowStatistics
from utils      import PD

KEEP_NUMBER = 4

session = Session()

######
# remnant of a time in which I thought of keeping each strategy in a separate
# file and import dynamically
# As these will likely not get used, their tests are just as useless
def _strategy_interface(cards):
    return cards[:KEEP_NUMBER]

def _get_strategy_interface(module, strategy_str):
    # return the method object to call corresponding to the strategy named
    # in the given string
    return getattr(module, strategy_str)
######

def possible_keep_throw_choices(cards):
    # possible choices to keep and throw so that we know what
    # Returns: list of tuples ([cards_in_hand], [cards_thrown_to_crib])
    # visual inspection: good
    # tested for basic properties
    combos = combinations(cards, KEEP_NUMBER)
    ret = []
    for combo in combos:
        cards_not_in_combo = [x for x in cards if x not in combo]
        ret.append((list(combo), cards_not_in_combo))
    return ret

def _enumerate_possible_hand_values(keep, toss):
    # Enumerate possible hand values knowing which cards are kept and tossed
    # Returns: list [int] of hand scores
    #   It is important to the implementation of this project that none of
    #   the cause for each of the individual values is not needed.
    #   i.e. we only care about the aggregate list of scores, not the card
    #   combinations that caused each individual score.
    # tested
    possible_cut_cards = [x for x in range(52)
            if x not in toss and x not in keep]
    possible_hand_values = []
    for cut_card in possible_cut_cards:
        possible_hand_values.append(score_hand(keep, cut_card))
    return possible_hand_values

def hand_compute_value(cards, list_func):
    # Compute a function over the list of possible scores available to each
    #   keep,toss combination
    # Return dict{tuple(tuple(keep),tuple(toss))
    #               --> list_func(possible_hand_values(keep,toss))}
    # tested
    PD('entering', 'hand_compute_value')
    values = {}
    for kt in possible_keep_throw_choices(cards):
        PD('>> loop: kt=%s' % str(kt))
        k,t = kt
        hv = _enumerate_possible_hand_values(k,t)
        values[(tuple(k),tuple(t))] = list_func(hv)
    PD('exiting', 'hand_compute_value')
    return values

def select_min_valued_hand(possible_hands_values_dict):
    # Find the hand combination that returns the minimum associated score
    return _select_valued_hand(possible_hands_values_dict, min)

def select_max_valued_hand(possible_hands_values_dict):
    # Find the hand combination that returns the maximum associated score
    # select the key corresponding to the maximum value
    return _select_valued_hand(possible_hands_values_dict, max)

def _select_valued_hand(possible_hands_values_dict, find_fn):
    # Find the hand that returns the value determined through find_fn
    # Returns: FIRST (keep,toss) that gives the value returned by find_fn
    #           applied to the values of the input dict
    # reference: https://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
    # make them lists to be able to index later
    values = list(possible_hands_values_dict.values())
    keys = list(possible_hands_values_dict.keys())
    return keys[values.index(find_fn(values))]


def list_min(values):
    return min(values)

def list_max(values):
    return max(values)

def list_avg(values):
    return sum(values) / len(values)

def list_med(values):
    return median(values)

# TODO: in the future, find a way to use pre-computed/stored values
def hand_max_min(cards):
    # Safe strategy, pick the hand that has the most guaranteed points
    #data = retrieve_statistics(Table, Property, cards)
    return select_max_valued_hand(hand_compute_value(cards, list_min))

def hand_max_avg(cards):
    # Choose the hand that has the maximum average points when accounting for
    # cut card possibilities
    return select_max_valued_hand(hand_compute_value(cards, list_avg))

def hand_max_med(cards):
    # Choose the hand that has the maximum median points when accounting for
    # cut card possibilities
    return select_max_valued_hand(hand_compute_value(cards, list_med))

def hand_max_poss(cards):
    # Hail Mary strategy, pick the hand that has the chance of the largest value.
    return select_max_valued_hand(hand_compute_value(cards, list_max))


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
    # TODO: rewrite
    #   This is impractically slow. One hand takes 25s locally to make a decision
    #   ((obviously) because of the bruteforcing,
    #    using dictionaries don't turn out to be that noticeably bad)
    # Otherwise known as an extremely defensive strategy.
    # Avoid giving points to the dealer at all costs.
    # A stupid homage to a man I've never met: my great-grandfather who was
    # supposedly so defensive that he would throw away the chance ot a 
    # 29-hand to avoid giving the opposing player a pair in the crib.
    PD('entering with hand=%s' % str(cards), '_stanley')
    crib_avg_possibilities = {}
    for keep,throw in possible_keep_throw_choices(cards):
        PD('>> analyzing keeping(%s) and throwing(%s)' % (keep,throw), '_stanley')
        poss_cribs = possible_cribs(keep,throw)
        summa = 0
        #numma = 0
#        ###
#        for crib in poss_cribs:
#            #PD('>>>> possible crib(%s)' % str(crib), '_stanley')
#            for cut_card in range(52):
#                # throw is subset of crib
#                if cut_card not in crib and cut_card not in keep:
#                    #summa += score_hand(throw, crib)
#                    summa += score_hand(crib, cut_card)
#            #numba += 1
#        #crib_avg_possibilities.append(summa / numba)
#        ###
        PD('>> crib_avg_possibilities[k,t] = %d' % summa, '_stanley')
        crib_avg_possibilities[(tuple(keep),tuple(throw))] = summa #/ numba
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


#################################
def retrieve_statistics(table, prop, cards):
    # Retreive statistics from the database for easier/quicker use
    # Returns desired property from the first found instance of the card
    #   combination found in the database
    found = retrieve_all_statistics(table, cards)# .first()
    if found is not None:
        try:
            return found.first().__dict__[prop]
        except:
            #raise Exception()
            return None
    else:
        return None

def retrieve_all_statistics(table, cards):
    global session
    found = None
    try:
        found = session.query(table).filter_by(card0=cards[0]).\
                filter_by(card1=cards[1]).\
                filter_by(card2=cards[2]).\
                filter_by(card3=cards[3])
    except:
        pass
    return found

###
# Statistics returns:
#   {
#       'max': <maximum>,
#       'min': <minimum>,
#       'avg': <average>, (adjusted to exclude impossible hands)
#       'med': <median>
#   }
#   max is not adjusted because there are potentially other combinations that
#       give the same result
#   min is not adjusted because it will likely only be used as a guarantee,
#       and it can't be worsened through more knowledge
#   med is not adjusted because there isn't necessarily a formulaic way to do so
###
#def keep_stastics(keep, throw):
#    pass
#
#def throw_statistics(keep, throw):
#    pass
#
#def keep_throw_statistics(keep, throw):
#    pass

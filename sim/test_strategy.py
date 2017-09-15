# Sean R. Lang <sean.lang@cs.helsinki.fi>

#import cribbage.strategy as strategy
from strategy import *
from strategy import _enumerate_possible_hand_values

def test_possible_keep_throw_choices():
    cards = [1,2,3,4,5,6]
    poss = possible_keep_throw_choices(cards)
    for keep, throw in poss:
        for t in throw:
            assert t not in keep
            assert t in cards
        for k in keep:
            assert k not in throw
            assert k in cards

def test__enumerate_possible_hand_values():
    # All aces do not get improved by any possible cut card
    keep = [0,1,2,3]
    toss = [5,6]
    assert _enumerate_possible_hand_values(keep,toss) == 46 * [12]
    pass

def test_hand_compute_values():
    assert False
    pass

def test_select_min_valued_hand():
    assert False
    pass

def test_select_min_valued_hand():
    assert False
    pass

def test__select_valued_hand():
    assert False
    pass

def test_possible_cribs():
    assert False

def test_disjoint():
    assert False

def test_list_min():
    assert False

def test_list_max():
    assert False

def test_list_avg():
    assert False

################

def test_hand_max_min():
    assert False
    pass

def test_hand_max_avg():
    assert False
    pass

def test_hand_max_med():
    assert False
    pass

def test_hand_max_poss():
    assert False
    pass

def test_pegging_max_avg():
    assert False
    pass

def test_pegging_max_med():
    assert False
    pass

def test_hand_min_avg_crib():
    #test__stanley()
    assert False
    pass

def test__stanley():
    assert False
    pass

def test_hand_max_avg_both():
    assert False
    pass


################
def test__strategy_interface():
    assert False

def test__get_strategy_interface():
    assert False

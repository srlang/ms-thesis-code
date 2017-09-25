# Sean R. Lang <sean.lang@cs.helsinki.fi>

#import cribbage.strategy as strategy
from strategy   import      *
from strategy   import      _enumerate_possible_hand_values, \
                            _enumerate_possible_toss_values, \
                            _stanley, \
                            _select_valued_hand
from utils import PD

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

def test__enumerate_possible_toss_values():
    keep = [1,2,3,4]
    toss = [5,6]
    poss = _enumerate_possible_toss_values(keep,toss)
    assert len(poss) == 15180 # 46 choose 3


def test__enumerate_possible_hand_values():
    # All aces do not get improved by any possible cut card
    keep = [0,1,2,3]
    toss = [5,6]
    assert _enumerate_possible_hand_values(keep,toss) == 46 * [12]

    keep = [16, 17, 18, 43] # 5, 5, 5, J
    toss = [0, 1]           # A, A
    expected = \
            [14, 15]         + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [29]             + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [20, 20, 20, 21] + \
            [22, 22, 22]     + \
            [20, 20, 20, 21] + \
            [20, 20, 20, 21]
    assert _enumerate_possible_hand_values(keep,toss) == expected

def test_hand_compute_values():
    cards = [16, 17, 18, 43, 0, 1]
    keep = [16, 17, 18, 43] # 5, 5, 5, J
    toss = [0, 1]           # A, A
    expected = \
            [14, 15]         + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [29]             + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [20, 20, 20, 21] + \
            [22, 22, 22]     + \
            [20, 20, 20, 21] + \
            [20, 20, 20, 21]
    ret_d = hand_compute_value(cards, list_max)
    assert ret_d[(tuple(keep),tuple(toss))] == 29
    ret_d = hand_compute_value(cards, list_min)
    assert ret_d[(tuple(keep),tuple(toss))] == 14
    ret_d = hand_compute_value(cards, list_avg)
    assert ret_d[(tuple(keep),tuple(toss))] == (sum(expected) / len(expected))
    pass


def test_select_min_valued_hand():
    cards = [16, 17, 18, 43, 0, 1]
    keep = [16, 17, 18, 43] # 5, 5, 5, J
    toss = [0, 1]           # A, A
    expected = \
            [14, 15]         + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [29]             + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [20, 20, 20, 21] + \
            [22, 22, 22]     + \
            [20, 20, 20, 21] + \
            [20, 20, 20, 21]
    poss_d = hand_compute_value(cards, list_min)
    ret_t = select_min_valued_hand(poss_d)
    PD('ret_t: %s' % str(ret_t), 'test_select_max_valued_hand')
    #assert ret_d[(tuple(keep),tuple(toss))] == 29
    assert poss_d[ret_t] == 4
    pass

def test_select_max_valued_hand():
    cards = [16, 17, 18, 43, 0, 1]
    keep = [16, 17, 18, 43] # 5, 5, 5, J
    toss = [0, 1]           # A, A
    expected = \
            [14, 15]         + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [29]             + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [14, 14, 14, 15] + \
            [20, 20, 20, 21] + \
            [22, 22, 22]     + \
            [20, 20, 20, 21] + \
            [20, 20, 20, 21]
    poss_d = hand_compute_value(cards, list_max)
    ret_t = select_max_valued_hand(poss_d)
    PD('ret_t: %s' % str(ret_t), 'test_select_max_valued_hand')
    #assert ret_d[(tuple(keep),tuple(toss))] == 29
    assert poss_d[ret_t] == 29
    pass

def test__select_valued_hand():
    d = {'a': 100, 'b': 50, 'c': 1}
    assert _select_valued_hand(d, list_max) == 'a'
    assert _select_valued_hand(d, list_min) == 'c'
    pass

def test_possible_cribs():
    keep = [0, 1, 2, 3]
    toss = [4, 5]
    poss = possible_cribs(keep,toss)
    for pc in poss:
        #PD('pc: %s' % str(pc), 'test_possible_cribs')
        for k in keep:
            assert k not in pc
        for t in toss:
            assert t in pc
        for c in pc:
            assert c not in keep

def test_disjoint():
    assert disjoint([1,2,3], [4,5,6])
    assert disjoint([1,5,6], [2,3,4])
    assert not disjoint([1,2,3], [3,4,5])

def test_list_min():
    assert list_min([1,2,3,4,5]) == 1
    assert list_min([5,4,1,2,3]) == 1

def test_list_max():
    assert list_max([1,2,3,4,5]) == 5
    assert list_max([5,4,1,2,3]) == 5

def test_list_avg():
    assert list_avg([1,2,3,4,5]) == 3
    assert list_avg([5,4,1,2,3]) == 3

################

def test_hand_max_min():
    dealt = [0, 1, 2, 3, 4, 5]
    assert hand_max_min(dealt) == ((0,1,2,3),(4,5))
    
    #         4, 5, 6, 8, 9, J      --> 4, 5, 6, 8 (interestingly enough)
    dealt = [12, 16, 20, 28, 32, 41]
    assert hand_max_min(dealt) == ((12, 16, 20, 28), (32, 41))
    pass

def test_hand_max_avg():
    #        A, A, 4, 4, 5, 6   --> 4, 4, 5, 6
    dealt = [0, 1, 12, 13, 16, 20]
    assert hand_max_avg(dealt) == ((12, 13, 16, 20), (0, 1))
    pass

def test_hand_max_med():
    #        A, A, 4, 4, 5, 6   --> 4, 4, 5, 6
    dealt = [0, 1, 12, 13, 16, 20]
    assert hand_max_med(dealt) == ((12, 13, 16, 20), (0, 1))
    pass

def test_hand_max_poss():
    #        5   5   5   J   J   J      --> 5 5 5 J
    dealt = [16, 17, 18, 40, 41, 43]
    assert hand_max_poss(dealt) == ((16, 17, 18, 43), (40,41))

    #        4   4   5   6   7   8      --> 4 4 5 6
    dealt = [12, 13, 16, 20, 24, 28]
    assert hand_max_poss(dealt) == ((12, 13, 16, 20), (24, 28))

    # mixed up this time for safety in testing
    dealt = [12, 13, 24, 16, 28, 20]
    assert hand_max_poss(dealt) == ((12, 13, 16, 20), (24, 28))
    pass

def test_hand_min_avg_crib():
    dealt = [0, 1, 12, 24, 36, 50]
    assert hand_min_avg_crib(dealt) == ((0, 1, 12, 24), (36, 50))
    pass

def test__stanley():
    #       A,  A, 4, 7, 10, K
    dealt = [0, 1, 12, 24, 36, 50]
    assert _stanley(dealt) == ((0, 1, 12, 24), (36, 50))
    pass

def test_hand_max_avg_both():
    assert False
    pass

def test_pegging_max_avg():
    assert False
    pass

def test_pegging_max_med():
    assert False
    pass

################
def test__strategy_interface():
    assert True
    pass

def test__get_strategy_interface():
    assert True
    pass
################

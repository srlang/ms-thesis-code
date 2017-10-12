# Sean R. Lang <sean.lang@cs.helsinki.fi>

from cribbage import *
from cribbage import _trim_zeros, _reset_pegging
#import cribbage

def test_card_suit():
    assert card_suit(16) == 0
    assert card_suit(21) == 1
    assert card_suit(38) == 2
    assert card_suit(43) == 3

def test_hand_suits():
    assert hand_suits([16, 21, 38, 43]) == [0, 1, 2, 3]

def test_card_class():
    assert card_class(1) == 0
    assert card_class(5) == 1
    assert card_class(8) == 2
    assert card_class(15) == 3
    assert card_class(16) == 4
    assert card_class(20) == card_class(21) == 5
    assert card_class(26) == card_class(27) == 6
    assert card_class(28) == 7
    assert card_class(33) == 8
    assert card_class(38) == 9
    assert card_class(40) == 10
    assert card_class(45) == 11
    assert card_class(50) == 12

def test_hand_classes():
    assert hand_classes([40, 44, 45, 50]) == [10, 11, 11, 12]

def test_card_value():
    assert card_value(1) == 1
    assert card_value(5) == 2
    assert card_value(8) == 3
    assert card_value(15) == 4
    assert card_value(16) == 5
    assert card_value(20) == card_value(21) == 6
    assert card_value(26) == card_value(27) == 7
    assert card_value(28) == 8
    assert card_value(33) == 9
    assert card_value(38) == 10
    assert card_value(40) == 10 # jack
    assert card_value(45) == 10 # queen
    assert card_value(50) == 10 # king

def test_hand_values():
    assert hand_values([40, 41, 16, 17]) == [10, 10, 5, 5]

def test_score_fifteens():
    assert score_fifteens([0, 1, 2, 3, 4, 5]) == 0      # 0 combos
    assert score_fifteens([16, 38, 0, 1, 2]) == 2       # 1 combo
    assert score_fifteens([16, 38, 39, 0, 1]) == 4      # 2 combos
    assert score_fifteens([16, 17, 18, 40, 41]) == 14   # 7 combos
    #J(1)-5(1,2,3), J(2)-5(1,2,3), 5(1)-5(2)-5(3)
    assert score_fifteens([17, 18, 19, 40, 16]) == 16    # 8 combos

def test_score_pairs():
    assert score_pairs([0, 5, 10, 15, 20]) == 0 # no pairs
    assert score_pairs([0, 1, 10, 15, 20]) == 2 # one pair
    assert score_pairs([0, 1, 4, 5, 10]) == 4   # two pair
    assert score_pairs([0, 1, 2, 5, 10]) == 6   # 3-of-a-kind (3 pairs)
    assert score_pairs([0, 1, 2, 4, 5]) == 8    # full house
    assert score_pairs([0, 1, 2, 3, 4]) == 12   # 4-of-a-kind (6 pairs)

def test_score_runs():
    assert score_runs([0, 10, 20, 30, 40]) == 0 # no in a row
    assert score_runs([0, 4, 15, 20, 30]) == 0 # 2 in a row
    assert score_runs([0, 4, 8, 20, 24]) == 3 # 3 in a row
    assert score_runs([0, 4, 8, 12, 20]) == 4 # 4 in a row
    assert score_runs([0, 4, 8, 12, 16]) == 5 # 5 in a row
    assert score_runs([0, 1, 4, 8, 25]) == 6 # 2 runs of 3
    assert score_runs([0, 1, 4, 8, 12]) == 8 # 2 runs of 4
    assert score_runs([0, 1, 4, 8, 9]) == 12 # 4 runs of 3

def test_score_nobs():
    assert score_nobs([17, 18, 19, 41, 16]) == 0 # no right jack
    assert score_nobs([17, 18, 19, 40, 16]) == 1 # right jack, as we say
    assert score_nobs([17, 18, 40, 19, 16]) == 1 # right jack, different order

def test_score_flush():
    # re-test suits
    assert hand_suits([1,5,9,13,14]) == [1,1,1,1,2]
    # non-crib hands
    assert score_flush([1, 2, 3, 4, 5], is_crib=False) == 0 # not a flush
    assert score_flush([1, 5, 9, 13, 14], is_crib=False) == 4 # flush without the cut card
    assert score_flush([1, 5, 9, 13, 17], is_crib=False) == 5 # flush with cut card

    # crib conditions
    assert score_flush([1, 2, 3, 4, 5], is_crib=True) == 0 # no flush
    assert score_flush([1, 5, 9, 13, 14], is_crib=True) == 0 # would-be, but needed cut
    assert score_flush([1, 5, 9, 13, 17], is_crib=True) == 5 # full flush

def test_score_hand():
    # 29-hand 5 5 5 J 5
    assert score_hand([17, 18, 19, 40, 16]) == 29    # highest poss hand
    # 6 6 7 8 8 ==> 20
    assert score_hand([20, 21, 24, 28, 29]) == 20
    # 4 4 5 6 6 ==> 24
    assert score_hand([12, 13, 16, 20, 21]) == 24
    # A 2 10 Q K ==> 0
    assert score_hand([0, 5, 36, 47, 49]) == 0
    # Including the cut_card separately
    assert score_hand([0, 5, 36, 47], cut_card=49) == 0
    assert score_hand([12, 13, 16, 20], 21) == 24
    assert score_hand([17, 18, 40, 19], cut_card=16) == 29 # right jack, declared
    assert score_hand([17, 18, 40, 19], 16) == 29 # right jack, positional

def test__trim_zeros():
    assert _trim_zeros([0, 1, 2, 3, 0]) == [1, 2, 3]
    assert _trim_zeros([1, 2, 3, 0]) == [1, 2, 3]
    assert _trim_zeros([0, 1, 0, 1, 0]) == [1, 0, 1]

def test__reset_pegging():
    cards_played = []
    assert not _reset_pegging(cards_played)

    cards_played = [0, 1, 2]
    assert not _reset_pegging(cards_played)

    cards_played = [40, 41, 42]
    assert not _reset_pegging(cards_played)

    cards_played = [40, 41, 42, 1]
    assert _reset_pegging(cards_played)

def test_score_peg():
    # 15
    #                 10, 5
    assert score_peg([40, 16]) == 2

    # 31
    #                 10, 5, 10, 5, A
    assert score_peg([40, 16, 41, 17, 0]) == 2 #(2, 2, 0, 0)

    # pairs
    #                A, A
    #assert score_peg([0, 1]) == 2
    assert score_peg([0, 1, 2]) == 6
    assert score_peg([0, 1, 2, 3]) == 12
    assert score_peg([0, 1, 2, 4, 3]) == 0
    # 

    # pair and 15
    #                 10, 3, A, A
    assert score_peg([40, 10, 0, 1]) == 4
    # pair and 31
    #                 10, 10, 7, 2, 2
    assert score_peg([40, 41, 24, 4, 5]) == 4

    # runs
    #                A, 2, 3
    assert score_peg([0, 4, 8]) == 3
    #                A, 2, 3, 4
    assert score_peg([0, 4, 8, 12]) == 4
    #                A, 2, 4, 3 (out of order, still should count)
    assert score_peg([0, 4, 12, 8]) == 4
    #                A, 2, 4 
    assert score_peg([0, 4,12]) == 0

    # run and 15
    #               9, 2, 3, A
    assert score_peg([32, 4, 8, 0]) == (3+2)

    # run and 31
    #               10, 5, 10, 3, 2, 1
    assert score_peg([40, 16, 41, 8, 4, 0]) == (3+2)

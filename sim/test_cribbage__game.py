# Sean R. Lang <sean.lang@cs.helsinki.fi>

from agent import CribbageAgent
from cribbage import CribbageGame

def basic_setup():
    agent1 = CribbageAgent()
    agent2 = CribbageAgent()
    game = CribbageGame(agent1, agent2)

    return agent1, agent2, game

def test_nothing():
    assert True

def test_play_full_game():
    a1,a2,g = basic_setup()
    g.play_full_game()

    assert g.game_finished
    if a1.is_winner:
        assert not a2.is_winner
    else:
        assert a2.is_winner

def test___init__():
    agent1, agent2, game = basic_setup()
    assert game.player1 == agent1
    assert game.player2 == agent2

def test_count_points():
    # run-of-the-mill counting in the middle of the game
    _,_,g = basic_setup()
    g.assign_dealer()
    g.deal_cards()
    g.dealer.score = 56
    g.pone.score = 49
    g.cut_card = 51
    g.dealer.hand = [4, 5, 6, 7]
    g.dealer.crib = [8, 9, 10, 11]
    g.pone.hand = [0, 1, 2, 3]
    g.count_points()
    assert g.pone.score == 49 + 12
    assert g.dealer.score == 56 + 12 + 12

    # both players close, pone beats dealer to win
    _,_,g = basic_setup()
    g.assign_dealer()
    g.deal_cards()
    g.dealer.score = 110
    g.pone.score = 118
    g.cut_card = 51
    g.dealer.hand = [4, 5, 6, 7]
    g.dealer.crib = [8, 9, 10, 11]
    g.pone.hand = [0, 1, 2, 3]
    g.count_points()
    assert g.pone.score == 118 + 12
    assert g.dealer.score == 110
    assert g.pone.is_winner
    assert not g.dealer.is_winner

    # dealer wins
    _,_,g = basic_setup()
    g.assign_dealer()
    g.deal_cards()
    g.dealer.score = 118
    g.pone.score = 100
    g.cut_card = 51
    g.dealer.hand = [4, 5, 6, 7]
    g.dealer.crib = [8, 9, 10, 11]
    g.pone.hand = [0, 1, 2, 3]
    g.count_points()
    assert g.dealer.score == 118 + 12 + 12
    assert g.pone.score == 100 + 12
    assert not g.pone.is_winner
    assert g.dealer.is_winner

def test_peg():
    # This will actually be a decent amount of work.
    # I need to test the following:
    #   1. GO's are given at the correct time.
    #   2. No cards are played twice (not sure if code makes this even possible,
    #       but check in case)
    # take that back, strategy is not included, so it's not that bad
    a,b,g = basic_setup()
    g.assign_dealer()
    g.deal_cards()
    p,d = g.pone, g.dealer
    p._name = 'pone'
    d._name = 'deal'

    # basic flow: both peg to 31, repeat: 0 complications
    #                    SJ,    J,     SK,      K(6)
    p._peg_cards_left = [40,    41,     49,     51]
    #                   5(2),  E6(2),   K(2),  EA(2)
    d._peg_cards_left = [16,    20,     50,     0]
    p.score = 40
    d.score = 40
    g.peg()
    assert p.score == 40 + 6
    assert d.score == 40 + 2 + 2 + 2 + 2

    # both peg, introduce a go and last-card into the mix
    #                    S10,    E10(7) J      SJ
    p._peg_cards_left = [36,    38,     40,     42]
    #                    10(2)  S10     EJ(3)  EJ(3)
    d._peg_cards_left = [37,    39,     41,     43]
    p.score = 40
    d.score = 40
    g.peg()
    assert p.score == 40 + 7
    assert d.score == 40 + 2 + 3 + 3

    # early exit because pone wins
    p._peg_cards_left = [15, 37, 51, 50]
    d._peg_cards_left = [38, 39, 40, 41]
    p.score = 119
    d.score = 40
    g.peg()
    assert p.score == 121
    assert d.score == 40
    assert p._peg_cards_left == [51, 50]
    assert d._peg_cards_left == [39, 40, 41]

    # early exit because dealer wins
    p._peg_cards_left = [0, 1, 4, 5]
    d._peg_cards_left = [2, 3, 6, 7]
    p.score = 40
    d.score = 120
    g.peg()
    assert p.score == 40
    assert d.score == 120 + 2
    assert p._peg_cards_left == [1, 4, 5]
    assert d._peg_cards_left == [3, 6, 7]

    # early exit because pone wins very close game
    p._peg_cards_left = [10, 2, 4, 6]
    d._peg_cards_left = [1, 3, 5, 7]
    p.score = 120
    d.score = 120
    g.peg()
    assert p.score == 120 + 2
    assert d.score == 120
    assert p._peg_cards_left == [4, 6]
    assert d._peg_cards_left == [3, 5, 7]

def test_deal_cards():
    a, b, g = basic_setup()

    g.assign_dealer()
    g.deal_cards()
    
    for card in g.pone.hand:
        assert 0 <= card <= 51
    for card in g.dealer.hand:
        assert 0 <= card <= 51
        assert card not in g.pone.hand
    assert g.cut_card not in g.dealer.hand
    assert g.cut_card not in g.pone.hand

def test_cut_random_card():
    a, b, g = basic_setup()

    g.assign_dealer()
    g.deal_cards()

    g.cut_random_card()
    
    #for card in g.dealer.hand:
    #    assert card not in g.pone.hand
    assert g.cut_card not in g.dealer.hand
    assert g.cut_card not in g.pone.hand

def test_game_finished():
    a1, a2, g = basic_setup()
    g.assign_dealer()

    g.dealer.score = 120
    g.pone.score = 120

    assert not g.game_finished

    g.dealer.score = 121
    assert g.game_finished

    g.dealer.score = 120
    g.pone.score = 121
    assert g.game_finished

    g.dealer.score = 10
    g.pone.score = 134
    assert g.game_finished

def test__assign_winner():
    a1, a2, g = basic_setup()
    g.assign_dealer()
    g.dealer.score = 125
    g.pone.score = 40
    g._assign_winner()
    assert g.dealer.is_winner
    assert not g.pone.is_winner

    g.dealer.score = 50
    g.pone.score = 121
    g._assign_winner()
    assert g.pone.is_winner
    assert not g.dealer.is_winner

def test_assign_dealer():
    a1, a2, game = basic_setup()

    game.assign_dealer()
    if game.dealer == a1:
        assert game.pone == a2
    else: #dealer == a2
        assert game.pone == a1

def test_rotate_dealer():
    agent1, agent2, game = basic_setup()

    game.assign_dealer()
    dealer,pone = game.dealer,game.pone
    game.rotate_dealer()
    assert game.dealer == pone
    assert game.pone == dealer

def test__cards_to_be_played():
    a,b,g = basic_setup()
    g.assign_dealer()
    d,p = g.dealer, g.pone

    d._peg_cards_left = [1,2]
    p._peg_cards_left = [3,4]
    assert g._cards_to_be_played

    d._peg_cards_left = [1]
    p._peg_cards_left = [2,3]
    assert g._cards_to_be_played

    d._peg_cards_left = [1]
    p._peg_cards_left = []
    assert g._cards_to_be_played

    p._peg_cards_left = [1]
    d._peg_cards_left = []
    assert g._cards_to_be_played

from agent import CribbageAgent
from cribbage import CribbageGame

def basic_setup():
    agent1 = CribbageAgent()
    agent2 = CribbageAgent()
    game = CribbageGame(agent1, agent2)

    return agent1, agent2, game

def test_nothing():
    assert True

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
    assert False

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

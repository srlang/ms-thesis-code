# Sean R. Lang <sean.lang@cs.helsinki.fi>

from agent import CribbageAgent, GoException

def test_initialization():
    agent = CribbageAgent()
    assert agent.score == 0

def test_choose_cards():
    agent = CribbageAgent()
    agent.hand = [1, 2, 3, 4, 5, 6]
    keep, toss = agent.choose_cards()
    assert len(keep) == 4 and len(toss) == 2

def test_can_peg_more():
    agent = CribbageAgent()
    # have plenty of room
    agent._peg_cards_left = [45, 50, 51, 22]
    cards_played = [1, 2, 3, 4]
    assert agent.can_peg_more(cards_played)

    # Face cards have been played, total=30, only have 10s left
    agent._peg_cards_left = [45, 46, 47, 48]
    cards_played = [41, 42, 43]
    assert not agent.can_peg_more(cards_played)

    # 2 left, 2 in the hand
    agent._peg_cards_left = [5, 10, 15, 20]
    cards_played = [41, 42, 33] # J, J, 9
    assert agent.can_peg_more(cards_played)

    # 2 left, 3 minimum in hand
    agent._peg_cards_left = [9, 10, 13, 20]
    cards_played = [41, 42, 33] # J, J, 9
    assert not agent.can_peg_more(cards_played)

    # no cards left, can't peg
    agent._peg_cards_left = []
    assert not agent.can_peg_more(cards_played)

def test_has_peg_cards_left():
    agent = CribbageAgent()

    # null peg cards
    agent._peg_cards_left = None
    assert not agent.has_peg_cards_left()

    # empty list
    agent._peg_cards_left = []
    assert not agent.has_peg_cards_left()

    # has cards left
    agent._peg_cards_left = [1,2,3]
    assert agent.has_peg_cards_left()

def test_next_peg_card():
    agent = CribbageAgent()

    # can't peg anymore, raise exception
    try:
        agent._peg_cards_left = [40, 41]
        agent._peg_cards_gone = [42, 43]
        cards_played = [40, 39, 41]
        card = agent.next_peg_card(cards_played)
        assert False
    except GoException:
        assert True

    # can peg, make sure the correct things are updated
    agent._peg_cards_left = [1, 2]
    agent._peg_cards_gone = [5, 6]
    cards_played = [5, 7, 6]
    card = agent.next_peg_card(cards_played)
    assert (card in agent._peg_cards_gone) and \
            (card not in agent._peg_cards_left)

    # test that invalid cards are "skipped"
    agent._peg_cards_left = [40, 41, 1]
    agent._peg_cards_gone = [3]
    cards_played = [37, 38, 39]
    card = agent.next_peg_card(cards_played)
    assert card == 1

def test_count_points():
    agent = CribbageAgent()

    cut_card = 16 # 5
    #             A  2  3  4
    agent.hand = [1, 4, 8, 12] # score = 7: 5(run) + 2(fifteen)
    agent.is_dealer = False
    agent.crib = [1, 4, 8, 12] # score = 7 (again)
    agent.score = 30
    score = agent.count_points(cut_card)
    assert score == 7 and agent.score == 37

    # same, but dealer this time
    agent.is_dealer = True
    score = agent.count_points(cut_card)
    assert score == 14 and agent.score == 51


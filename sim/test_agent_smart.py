# Sean R. Lang <sean.lang@cs.helsinki.fi>

from copy       import  deepcopy
from itertools  import  combinations

from agent      import  SmartCribbageAgent
from cribbage   import  htoc_str, htoc, GoException
from strategy3  import  hand_max_avg, hand_max_poss
from records    import  create_tables,\
                        _populate_keep_throw_statistics,\
                        session as records_session,\
                        KeepThrowStatistics,\
                        AggregatePlayedHandRecord
from train      import  create_agent
from utils      import  PD

_db_setup_run = False
_db_setup_suc = False
def db_setup():
    global _db_setup_run
    global _db_setup_suc
    if (not _db_setup_run) and (not _db_setup_suc):
        create_tables()
        # populate with basic stuff for the first few cards
        PD('need to run')
        l_succ = True 
        cards_l = [
                    [0, 1, 2, 3, 4, 5]#,
                    #[60, 61, 62, 63, 64, 65]
                    # cards out of possible range not allowed by some method
                    #   further in (don't even remember anymore)
                    #   But, doesn't matter, not possible
                    ]
        for cards in cards_l:
            for keep in combinations(cards, 4):
                k = list(keep)
                t = [card for card in cards if card not in k]
                PD('populating keep=%s, toss=%s' % (k,t))
                try:
                    #l_succ = l_succ and
                    _populate_keep_throw_statistics(k,t, records_session)
                    records_session.commit()
                except Exception as e:
                    PD('error: %s' % str(e))
                    l_succ = False

        # populate with non-existant cards so that it can be consistent when
        # dealing with pegging choices
        pcards_l = [
                    ([60, 61, 62, 63], [2, 14, 4.3, 5.1, 4]),
                    ([61, 62, 63, 64], [2, 14, 4.3, 5.1, 4]),
                    ([62, 63, 64, 65], [2, 14, 4.3, 5.1, 4])
                    ]

        for pcards,stats in pcards_l:
            aggrec = AggregatePlayedHandRecord(\
                        card0=pcards[0],
                        card1=pcards[1],
                        card2=pcards[2],
                        card3=pcards[3],
                        gained_min=stats[0],
                        gained_max=stats[1],
                        gained_avg=stats[2],
                        gained_med=stats[3],
                        gained_mod=stats[4],
                        given_min=stats[0],
                        given_max=stats[1],
                        given_avg=stats[2],
                        given_med=stats[3],
                        given_mod=stats[4],
                        records_refresh_counter=1)
            try:
                records_session.add(aggrec)
                records_session.commit()
            except Exception as e:
                PD('error: %s' % str(e))

        _db_setup_run = True
        l_succ = l_succ and records_session.query(KeepThrowStatistics).filter_by(\
                            kcard0=cards_l[0][0],
                            kcard1=cards_l[0][1],
                            kcard2=cards_l[0][2],
                            kcard3=cards_l[0][3],
                            tcard0=cards_l[0][4],
                            tcard1=cards_l[0][5]).first() is not None
        l_succ = l_succ and records_session.query(AggregatePlayedHandRecord).filter_by(\
                            card0=pcards_l[0][0][0],
                            card1=pcards_l[0][0][1],
                            card2=pcards_l[0][0][2],
                            card3=pcards_l[0][0][3]).first() is not None
        _db_setup_suc = l_succ



def test__constructor():
    agent = SmartCribbageAgent()
    assert agent._tmp_S is None
    assert agent._tmp_p is None

def test__choose_cards():
    global _db_setup_run
    global _db_setup_suc
    db_setup()
    assert _db_setup_run and _db_setup_suc
    # single strategy
    input_file = './checkpoints/test_input.csv'
    agent = create_agent(input_file, 'NimiTällä')
    assert agent is not None
    agent.hand = [0, 4, 3, 5, 2, 1]
    agent.score = 10
    agent.is_dealer = True
    agent._choose_cards(opponent_score=11)
    #exp_S = [[1.0, 0.15, 0.15, 0.15, 0.15, 0.0, 0.15, 0.15, 0.0, 0.0, 0.15, 0.15, 0.0, 0.0, 0.0], [0.0, 0.75, 0.75, 0.75, 0.75, 1.0, 0.75, 0.75, 1.0, 1.0, 0.75, 0.75, 1.0, 1.0, 1.0]]
    #exp_p = [0.32,0.558, 0.558, 0.558, 0.558, 0.68, 0.558, 0.558, 0.68, 0.68, 0.558, 0.558, 0.68, 0.68, 0.68] 
    exp_p = [1.0, 0.183, 0.183, 0.183, 0.183, 0.0, 0.183, 0.183, 0.0, 0.0, 0.183, 0.183,  0.0,0.0, 0.0]
    exp_S = [[1.0, 0.25, 0.25, 0.25, 0.25, 0.0, 0.25, 0.25, 0.0, 0.0, 0.25, 0.25, 0.0, 0.0, 0.0], [1.0, 0.15, 0.15, 0.15, 0.15, 0.0, 0.15, 0.15, 0.0, 0.0, 0.15, 0.15, 0.0, 0.0, 0.0]]
    assert exp_S == list(agent._tmp_S)
    assert exp_p == list(agent._tmp_p)
    # TODO: what should the choice made be?
    #assert True

def test_retrieve_weights():
    input_file = './checkpoints/test_input.csv'
    agent = create_agent(input_file, 'NimiTällä')
    assert agent is not None

    agent.score = 10
    agent.is_dealer = True
    weights = agent.retrieve_weights(opponent_score=11)
    assert weights == [0.33, 0.67]

def test_reward():
    assert True

def test_punish():
    assert True

def test_modify_weights():
    input_file = './checkpoints/random_start.txt'
    agent = create_agent(input_file, 'NimiTällä')
    path = [
                    (0,0,0, 0),
                    (10, 14, 1, 1),
                    (20, 19, 0, 2),
                    (55, 40, 1, 3),
                    (70, 66, 0, 4),
                    (90, 77, 1, 5),
                    (110, 108, 0, 6)
                    ]
    original_weights_ref = [agent.weights[m][o][d] for m,o,d,a in path]
    original_weights = deepcopy(original_weights_ref)
    agent.game_weights_path = path
    agent.modify_weights(0.175)

    # check that weights "increased"
    for i in range(len(path)):
        m,o,d,a = path[i]
        ow = original_weights[i]

        # make sure the non-taken actions are scaled down
        for j in range(len(ow)):
            if j == a:
                # make sure the action is rewarded
                assert agent.weights[m][o][d][j] > ow[j]
            else:
                # make sure the action is less weighted
                assert agent.weights[m][o][d][j] < ow[j]

    # re-save weights
    original_weights_ref = [agent.weights[m][o][d] for m,o,d,e in path]
    original_weights = deepcopy(original_weights_ref)
    agent.modify_weights(-0.134)

    # check that weights "decreased"
    for i in range(len(path)):
        m,o,d,a = path[i]
        ow = original_weights[i]

        # make sure the non-taken actions are scaled up
        for j in range(len(ow)):
            if j == a:
                # make sure the action is punished
                assert agent.weights[m][o][d][j] < ow[j]
            else:
                # make sure the action is more weighted
                assert agent.weights[m][o][d][j] > ow[j]

def test__weights_modifier():
    agent = SmartCribbageAgent()
    agent.score = 1345 #truncated down to 121
    opponent_score = 100
    exp_out = 21.0 / 121.0
    assert exp_out == agent._weights_modifier(opponent_score)

    agent.score = 98
    opponent_score = 125
    exp_out = -23.0 / 121.0
    assert exp_out == agent._weights_modifier(opponent_score)

def test_save_weights_str():
    #db_setup()
    input_file = './checkpoints/test_input.csv'
    agent = create_agent(input_file, 'NimiTällä')
    assert agent is not None

    exp_str = '''my_score opp_score dealer hand_max_min hand_max_avg
10 11 1 0.33 0.67
12 13 1 0.4 0.6'''
    assert exp_str == agent.save_weights_str()

def test__assign_strategies():
    from strategy3 import hand_max_min as hmm, hand_max_avg as hma
    strat_names_input = ['hand_max_min', 'hand_max_avg']
    exp_strat_names = ['hand_max_min', 'hand_max_avg']
    exp_strats = [hmm, hma]

    #input_file = './checkpoints/test_input.csv'
    #agent = create_agent(input_file, 'NimiTällä')
    #assert agent is not None
    agent = SmartCribbageAgent()

    agent._assign_strategies(strat_names_input)
    assert agent._strat_names == exp_strat_names
    assert agent.strategies == exp_strats

def test__select_next_valid_peg_card():
    agent = SmartCribbageAgent()

    cards_played = htoc_str('10S')
    valid_cards = htoc_str('5C 4H 3S 10C')
    exp = htoc('5C')
    assert agent._select_next_valid_peg_card(cards_played, valid_cards) == exp

    # order matters
    cards_played = htoc_str('10S')
    valid_cards = htoc_str('10C 5C 4H 3S')
    exp = htoc('10C')
    assert agent._select_next_valid_peg_card(cards_played, valid_cards) == exp

    # select to get a run instead of a fifteen
    cards_played = htoc_str('6C 7S')
    valid_cards = htoc_str('2S 5H')
    exp = htoc('5H')
    assert agent._select_next_valid_peg_card(cards_played, valid_cards) == exp

    # select a triple instead of a fifteen
    cards_played = htoc_str('6C 6S')
    valid_cards = htoc_str('3S 6H')
    exp = htoc('6H')
    assert agent._select_next_valid_peg_card(cards_played, valid_cards) == exp

def test_load_checkpoint():
    input_file = './checkpoints/test_input.csv'
    #agent = create_agent(input_file, 'NimiTällä')
    #assert agent is not None

    agent = SmartCribbageAgent()
    agent.load_checkpoint(input_file)
    assert agent.weights[10][11][1] == [0.33, 0.67]
    assert agent.weights[12][13][1] == [0.40, 0.60]

def test_can_peg_more():
    agent = SmartCribbageAgent()
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
    agent = SmartCribbageAgent()

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
    agent = SmartCribbageAgent()

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

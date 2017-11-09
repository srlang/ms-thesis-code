# Sean R. Lang <sean.lang@cs.helsinki.fi>

from itertools  import  combinations

from agent      import  SmartCribbageAgent

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
    assert exp_p == list(agent._tmp_p)
    assert exp_S == list(agent._tmp_S)
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
    assert False

def test_punish():
    assert False

def test__modify_weights():
    assert False

def test__weights_modifier():
    assert False

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
    assert False

def test_load_checkpoint():
    input_file = './checkpoints/test_input.csv'
    #agent = create_agent(input_file, 'NimiTällä')
    #assert agent is not None

    agent = SmartCribbageAgent()
    agent.load_checkpoint(input_file)
    assert agent.weights[10][11][1] == [0.33, 0.67]
    assert agent.weights[12][13][1] == [0.40, 0.60]


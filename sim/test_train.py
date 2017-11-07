# Sean R. Lang <sean.lang@cs.helsinki.fi>

from os             import  access,\
                            W_OK as dir_permissions,\
                            F_OK as file_permissions
from sqlalchemy     import  create_engine
from sqlalchemy.orm import  sessionmaker

from agent          import  SmartCribbageAgent
from train          import  *
from weights        import  WeightCoordinate, create_weight_tables

def create_session():
    engine = create_engine('sqlite:///:memory:')
    create_weight_tables(engine)
    Session = sessionmaker(engine)
    return Session()
    # all methods using this work, "test" passed

def test_play_training_game():
    try:
        input_file = './checkpoints/test_input.csv'
        suc1, suc2, a1, a2 = create_agents(input_file, input_file)
        
        assert suc1
        assert suc2

        game = play_training_game(a1, a2)
        assert game.game_finished
        if a1.is_winner:
            assert not a2.is_winner
        else:
            assert a2.is_winner
    except Exception as e:
        print(str(e))
        assert False

def test_create_agent():
    input_file = './checkpoints/test_input.csv'
    agent_name = 'TestAgent'

    succ, agent = create_agent(input_file, agent_name)

    assert succ
    assert agent.name == agent_name
    assert agent._strat_names == ['hand_max_min', 'hand_max_avg']
    assert agent.weights_db_session is not None
    first_weight = agent.weights_db_session.query(WeightCoordinate).first()
    assert first_weight.dealer
    assert first_weight.my_score == 10
    assert first_weight.opp_score == 11
    assert first_weight.w0 == 0.33
    assert first_weight.w1 == 0.67

def test_create_agents():
    input_file = './checkpoints/test_input.csv'

    suc1, suc2, a1, a2 = create_agents(input_file, input_file)

    assert suc1
    assert suc2
    assert a1.name == 'agent1'
    assert a2.name == 'agent2'
    assert a1._strat_names == ['hand_max_min', 'hand_max_avg']
    assert a1.weights_db_session is not None
    first_weight = a1.weights_db_session.query(WeightCoordinate).first()
    assert first_weight.dealer
    assert first_weight.my_score == 10
    assert first_weight.opp_score == 11
    assert first_weight.w0 == 0.33
    assert first_weight.w1 == 0.67

def test_save_checkpoint():
    #global dir_permissions
    #global file_permissions
    # create agent
    agent = SmartCribbageAgent()
    agent.name = 'TestAgent'
    agent.weights_db_session = create_session()
    weights = [
                WeightCoordinate(my_score=12, opp_score=12, dealer=True, w0=2, w1=3),
                WeightCoordinate(my_score=13, opp_score=11, dealer=True, w0=1, w1=5),
                WeightCoordinate(my_score=14, opp_score=10, dealer=True, w0=4, w1=0)
                ]
    for w in weights:
        agent.weights_db_session.add(w)
    agent.weights_db_session.commit()
    agent._strat_names = ['test_strat1', 'test_strat2']

    # checkpoints dir exists
    checkpts_dir = './checkpoints'
    exp_filename = 'checkpoint_TestAgent_TestStartTime_100.txt'
    assert access(checkpts_dir, dir_permissions)
    assert not access(checkpts_dir + '/' + exp_filename, file_permissions)
    save_checkpoint(agent, 100,  'TestStartTime', checkpts_dir)
    assert access(checkpts_dir+'/'+exp_filename, file_permissions)
    # manually verify to see that values are correct
    #   (at least for the first few times)
    # testing this would require either using other methods or basically
    # re-writing load_checkpoint

    # checkpoints dir does not exist
    checkpts_dir = './checkpoints_dne'
    exp_filename = 'checkpoint_TestAgent_TestStartTime_100.txt'
    assert not access(checkpts_dir, dir_permissions)
    assert not access(checkpts_dir + '/' + exp_filename, file_permissions)
    save_checkpoint(agent, 100,  'TestStartTime', checkpts_dir)
    assert access(checkpts_dir, dir_permissions)
    assert access(checkpts_dir+'/'+exp_filename, file_permissions)
    # again, manually verify first couple of times
    #assert False # output does not include actual weights

def test_load_checkpoint():
    # create agent
    agent = SmartCribbageAgent()
    agent.name = 'TestAgent'
    agent.weights_db_session = create_session()

    assert agent.weights_db_session.query(WeightCoordinate).first() is None

    #checkpts_dir = './checkpoints'
    checkpts_file = './checkpoints/test_input.csv'
    status, strats = load_checkpoint(checkpts_file, agent.weights_db_session)
    assert status # heh
    assert strats == ['hand_max_min', 'hand_max_avg']
    first = agent.weights_db_session.query(WeightCoordinate).first() 
    assert first is not None and \
            first.my_score == 10 and\
            first.opp_score == 11 and\
            first.dealer and\
            first.w0 == 0.33 and\
            first.w1 == 0.67

def test_train():
    assert False


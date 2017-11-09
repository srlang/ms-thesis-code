# Sean R. Lang <sean.lang@cs.helsinki.fi>

from os             import  access,\
                            W_OK as dir_permissions,\
                            F_OK as file_permissions
from sqlalchemy     import  create_engine
from sqlalchemy.orm import  sessionmaker

from agent          import  SmartCribbageAgent
from train          import  *
from weights        import  WeightCoordinate, create_weight_tables

def test_play_training_game():
    try:
        input_file = './checkpoints/test_input.csv'
        a1, a2 = create_agents(input_file, input_file)
        
        assert a1 is not None
        assert a2 is not None

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

    agent = create_agent(input_file, agent_name)

    assert agent.name == agent_name
    assert agent._strat_names == ['hand_max_min', 'hand_max_avg']
    assert agent.weights[10][11][1] == [0.33, 0.67]
    assert agent.weights[12][13][1] == [0.40, 0.60]

def test_create_agents():
    input_file = './checkpoints/test_input.csv'

    a1,a2 = create_agents(input_file, input_file)

    assert a1.name == 'agent1'
    assert a2.name == 'agent2'
    assert a1._strat_names == ['hand_max_min', 'hand_max_avg']
    first_weights = a1.weights[10][11][1]
    second_weights = a1.weights[12][13][1]
    assert first_weights == [0.33, 0.67]
    assert second_weights == [0.40, 0.60]
    first_weights = a2.weights[10][11][1]
    second_weights = a2.weights[12][13][1]
    assert first_weights == [0.33, 0.67]
    assert second_weights == [0.40, 0.60]

def test_save_checkpoint():
    #global dir_permissions
    #global file_permissions
    # create agent
    agent = SmartCribbageAgent()
    agent.name = 'TestAgent'
    agent.weights[10][12][1] = [0.23, 0.77]
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
    #assert False # Rewrite without weights DB

def test_train():
    assert False # Rewrite without weights DB
    assert False


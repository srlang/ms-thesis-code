# Sean R. Lang <sean.lang@cs.helsinki.fi>

from os             import  access, mkdir, W_OK
from pandas         import  read_csv
from sqlalchemy     import  create_engine
from sqlalchemy.exc import  SQLAlchemyError
from sqlalchemy.orm import  sessionmaker

from agent          import  SmartCribbageAgent
from cribbage       import  CribbageGame
from weights        import  WeightCoordinate, create_weight_tables
from utils          import  PD

CHECKPOINT_FILENAME_FORMAT = 'checkpoint_%s_%s_%d.txt'

def play_training_game(agent1, agent2):
    '''
    Create and play a single game for training purposes.
    Reward and punish the correct 
    '''
    game = CribbageGame(agent1, agent2)
    game.play_full_game()

    if agent1.is_winner:
        agent1.reward(agent2.score)
    else:
        agent1.punish(agent2.score)

    if agent2.is_winner:
        agent2.reward(agent1.score)
    else:
        agent2.punish(agent1.score)

    return game

def create_agent(start_weights_file, name):
    _METHOD = 'create_agent'
    PD('entering', _METHOD)
    PD('creating agent', _METHOD)
    agent = SmartCribbageAgent()
    agent.name = name

    PD('loading checkpoint...', _METHOD)
    strat_names = agent.load_checkpoint(start_weights_file)
    #agent.assign_strategies(strat_names)
    PD('...done', _METHOD)

    PD('exiting with agent=%s' % str(agent), _METHOD)
    return agent

def create_agents(a1sf, a2sf):
    # params: start file, output_format
    agent1 = create_agent(a1sf, 'agent1')
    agent2 = create_agent(a2sf, 'agent2')
    return agent1, agent2

def _write_checkpoint(output, filename, directory='./checkpoints'):
    if not access(directory, W_OK):
        mkdir(directory)
    with open(directory + '/' + filename, 'w') as f:
        f.write(output)

def save_checkpoint(agent, epoch, start_time_str, checkpoints_dir='./checkpoints'):
    filename = checkpoints_dir + '/' + \
            CHECKPOINT_FILENAME_FORMAT % (agent.name, start_time_str, epoch)
    output = agent.save_weights_str()
    _write_checkpoint(output, filename, checkpoints_dir)

def train(agent1stratfile, agent2stratfile, epochs=1000, epoch_checkpoint=None):
    if epoch_checkpoint is None:
        epoch_checkpoint = max(int(epochs / 100), 1)
    agent1, agent2 = create_agents(agent1stratfile, agent2stratfile)

    for epoch in range(epochs):
        PD('Epoch %d' % epoch)
        play_training_game(agent1, agent2)

        if (epoch % epoch_checkpoint) == 0:
            save_checkpoint(agent1, epoch, start_time)
            save_checkpoint(agent2, epoch, start_time)

        agent1.reset()
        agent2.reset()


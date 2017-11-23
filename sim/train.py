# Sean R. Lang <sean.lang@cs.helsinki.fi>

from os             import  access, mkdir, W_OK
from pandas         import  read_csv
from sqlalchemy     import  create_engine
from sqlalchemy.exc import  SQLAlchemyError
from sqlalchemy.orm import  sessionmaker
from time           import  gmtime, strftime

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

    # modify weights
    #   (no need for punish/reward specifically because generic modify_weights)
    agent1.modify_weights(agent2.score)
    agent2.modify_weights(agent1.score)

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
    #PD('entering', '_write_checkpoint')
    if not access(directory, W_OK):
        #PD('no access to dir(%s), creating' % directory)
        mkdir(directory)
    #PD('writing to file: %s/%s' % (directory,filename), '_write_checkpoint')
    with open(directory + '/' + filename, 'w') as f:
        f.write(output)

def save_checkpoint(agent, epoch, start_time_str, checkpoints_dir='./checkpoints'):
    #PD('entering agent=%s, epoch=%s, start_time_str=%s, cehckpoints_fir=%s' % \
    #        (agent,epoch,start_time_str,checkpoints_dir), 'save_checkpoint')
    #filename = checkpoints_dir + '/' + \
    filename = CHECKPOINT_FILENAME_FORMAT % (agent.name, start_time_str, epoch)
    #PD('filename=%s' % filename, 'save_checkpoint')
    output = agent.save_weights_str()
    _write_checkpoint(output, filename, checkpoints_dir)

def train(agent1stratfile, agent2stratfile, epochs=1000, epoch_checkpoint=None):
    if epoch_checkpoint is None:
        epoch_checkpoint = max(int(epochs / 100), 1)
    start_time = strftime('%Y%m%d-%H%M%S', gmtime())
    agent1, agent2 = create_agents(agent1stratfile, agent2stratfile)

    for epoch in range(epochs):
        PD('Epoch %d' % epoch)
        play_training_game(agent1, agent2)

        if (epoch % epoch_checkpoint) == 0:
            save_checkpoint(agent1, epoch, start_time)
            save_checkpoint(agent2, epoch, start_time)

        agent1.reset()
        agent2.reset()

    # save final output, no sense in running last epoch_checkpoint times if not
    # ever saved
    save_checkpoint(agent1, epoch, start_time)
    save_checkpoint(agent2, epoch, start_time)

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('agent1_file', help="filename for agent1's weights")
    parser.add_argument('agent2_file', help="filename for agent2's weights")
    parser.add_argument('-v', '--verbose', help='verbose mode?', action='store_true')
    parser.add_argument('-e', '--epochs', help='number of epochs(games) to play for training',
            type=int, default=1000)
    parser.add_argument('-c', '--checkpoint', help='number of epochs to checkpoint at',
            type=int, default=None)
    # ...
    args = parser.parse_args()

    PD('training (%s) against (%s) for (%d) epochs and checkpointint after every (%s)' %\
            (args.agent1_file, args.agent2_file, args.epochs, str(args.checkpoint)))
    train(args.agent1_file, args.agent2_file, args.epochs, args.checkpoint)

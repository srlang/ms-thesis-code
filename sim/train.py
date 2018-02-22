#!/usr/bin/env python3
# Sean R. Lang <sean.lang@cs.helsinki.fi>

from copy           import  deepcopy
from os             import  access, mkdir, W_OK
from pandas         import  read_csv
from random         import  sample, randint
from sqlalchemy     import  create_engine
from sqlalchemy.exc import  SQLAlchemyError
from sqlalchemy.orm import  sessionmaker
from time           import  gmtime, strftime

from agent          import  SmartCribbageAgent
from cribbage       import  CribbageGame, ctoh_str
from weights        import  WeightCoordinate, create_weight_tables
from utils          import  PD

CHECKPOINT_FILENAME_FORMAT = 'checkpoint_%s_%s_%012d.txt'

def play_training_game(agent1, agent2):
    '''
    Create and play a single game for training purposes.
    Reward and punish the correct 
    '''
    # create the game
    game = CribbageGame(agent1, agent2)

    # randomize the starting position
    # keep the scores within 60 points:
    #   1. unlikely to go beyond that difference
    #   2. philosophically, if losing by that much, maybe not really your fault
    pt_spread = 60
    score1 = randint(0, 120)
    score2 = randint(max(0, score1-pt_spread), min(120, score1+pt_spread))
    if score1 % 2 == 0:
        agent1.score = score1
        agent2.score = score2
    else:
        agent1.score = score2
        agent2.score = score1


    # play the actual game
    game.play_full_game()

    # modify weights
    #   (no need for punish/reward specifically because generic modify_weights)
    agent1.reward_punish(agent2.score)
    agent2.reward_punish(agent1.score)

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

def train_multi(agent1stratfile, agent2stratfile,
        epochs=1000, epoch_checkpoint=None,
        procs=8):
    _METHOD = 'train_multi'
    from multiprocessing import Pool
    args = []
    for i in range(procs):
        args.append(\
                        (agent1stratfile, agent2stratfile,
                            epochs, epoch_checkpoint,
                            ('agent%03d'%(2*i), 'agent%03d'%((2*i)+1)))
                    )

    PD('calling starmap on args=%s' % str(args), _METHOD)
    with Pool(processes=procs) as pool:
        pool.starmap(train, args)
        pass

def train(agent1stratfile, agent2stratfile,
            epochs=1000,  epoch_checkpoint=None,
            agent_names=('agent1', 'agent2')):
    PD('entering with(a1sf=%s, a2sf=%s, ep=%d, chkpt=%s, anames=%s' %\
                        (agent1stratfile, agent2stratfile, epochs, epoch_checkpoint, agent_names),
                        'train')
    if epoch_checkpoint is None:
        epoch_checkpoint = max(int(epochs / 100), 1)
    start_time = strftime('%Y%m%d-%H%M%S', gmtime())
    agent1, agent2 = create_agents(agent1stratfile, agent2stratfile)
    agent1.name = agent_names[0]
    agent2.name = agent_names[1]

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

def train_pegging(rounds=1000, agent_names=('agent1', 'agent2')):
    _METHOD = 'train_pegging'
    PD('entering', _METHOD)
    agent1 = SmartCribbageAgent()
    agent1.name = agent_names[0]
    agent2 = SmartCribbageAgent()
    agent2.name = agent_names[1]
    game = CribbageGame(agent1, agent2)
    game.pone, game.dealer = agent1, agent2
    # randomly assign pone and dealer
    for i in range(rounds):
        PD('\tRound %d' % (i+1), _METHOD)
        # set scores to 0 so there isn't ever a early stopping winning condition
        PD('\t\tScores reset', _METHOD)
        game.pone.score = 0
        game.dealer.score = 0

        # manually deal out cards (randomly)
        PD('\t\tDealing out cards', _METHOD)
        all_cards = sample(range(52), 8)
        game.pone.hand = all_cards[:4]
        game.pone._peg_cards_left = deepcopy(game.pone.hand)
        PD('\t\t\tPone hand: %s' % ctoh_str(game.pone.hand))
        game.dealer.hand = all_cards[4:]
        game.dealer._peg_cards_left = deepcopy(game.dealer.hand)
        PD('\t\t\tDealer hand: %s' % ctoh_str(game.dealer.hand))

        # play the pegging round
        PD('\t\tPlaying the actual pegging round', _METHOD)
        game.peg()

        PD('\t\tScores after: Dealer(%d) - Pone(%d)' % (game.dealer.score, game.pone.score),
                _METHOD)

        # randomly assign agents as pone or dealer;
        # really just cycle to keep even distribution
        PD('\t\tSwapping dealer/pone', _METHOD)
        game.pone, game.dealer = game.dealer, game.pone
        pass
    PD('exiting', _METHOD)

OPERATIONS = ['game', 'peg']
if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('operation', help='what we are training', choices=OPERATIONS)
    parser.add_argument('-a', '--agent1file', help="filename for agent1's weights", default='')
    parser.add_argument('-b', '--agent2file', help="filename for agent2's weights", default='')
    parser.add_argument('-v', '--verbose', help='verbose mode?', action='store_true')
    parser.add_argument('-e', '--epochs', help='number of epochs(games) to play for training',
            type=int, default=1000)
    parser.add_argument('-c', '--checkpoint', help='number of epochs to checkpoint at',
            type=int, default=None)
    parser.add_argument('-p', '--processes', help='number of processes to use',
            type=int, default=None)
    # ...
    args = parser.parse_args()

    if args.processes is not None:
        PD('have multiple processes', '__main__')
        if args.operation == 'game':
            train_multi(args.agent1file, args.agent2file,
                        args.epochs, args.checkpoint,
                        args.processes)
        elif args.operation == 'peg':
            pass
    else:
        if args.operation == 'game':
            PD('training (%s) against (%s) for (%d) epochs and checkpointint after every (%s)' %\
                    (args.agent1file, args.agent2file, args.epochs, str(args.checkpoint)))
            train(args.agent1file, args.agent2file, args.epochs, args.checkpoint)
        elif args.operation == 'peg':
            train_pegging(args.epochs)

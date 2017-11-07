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


    PD('creating engine and session', _METHOD)
    engine = create_engine('sqlite:///:memory:')
    create_weight_tables(engine)
    Session = sessionmaker(engine)
    agent.weights_db_session = Session()

    PD('loading checkpoint...', _METHOD)
    succ, strat_names = load_checkpoint(start_weights_file, agent.weights_db_session)
    agent.assign_strategies(strat_names)
    PD('...done', _METHOD)
    PD('succ=%s' % str(succ), _METHOD)

    PD('exiting', _METHOD)
    return succ, agent

def create_agents(a1sf, a2sf):
    # params: start file, output_format
    suc1, agent1 = create_agent(a1sf, 'agent1')
    suc2, agent2 = create_agent(a2sf, 'agent2')
    return suc1, suc2, agent1, agent2

def save_checkpoint(agent, epoch, start_time_str, checkpoints_dir='./checkpoints'):
    if not access(checkpoints_dir, W_OK):
        mkdir(checkpoints_dir)
    filename = checkpoints_dir + '/' + \
            CHECKPOINT_FILENAME_FORMAT % (agent.name, start_time_str, epoch)
    with open(filename, 'w') as f:
        f.write(agent.save_weights_str())
        #print(agent.save_weight_str(), file=f)
    pass

def load_checkpoint(filename, db_sess):
    _METHOD = 'load_checkpoint'
    PD('entering', _METHOD)
    PD('reading input file...', _METHOD)
    csv_table = read_csv(filename, sep=' ') #, header=True)
    PD('...done', _METHOD)
    ret = True

#    PD('ensuring database tables exist...', _METHOD)
#    create_weight_tables(
#    PD('...done', _METHOD)

    for _,row in csv_table.iterrows():
        wc = WeightCoordinate(my_score=row.iloc[0], opp_score=row.iloc[1], dealer=row.iloc[2])
        for i in range(3, len(row)):
            wc.__dict__['w%d'%(i-3)] = float(row.iloc[i])
        try:
            db_sess.add(wc)
        except SQLAlchemyError as s:
            PD('sql error: %s' % str(s), _METHOD)
            ret = False
    try:
        db_sess.commit()
    except SQLAlchemyError as s:
        PD('sql error: %s' % str(s), _METHOD)
        ret = False

    headers = [header for header in csv_table][3:] # cut out already known
    PD('exiting with ret=%s, headers=%s' % (str(ret), str(headers)), _METHOD)
    return ret, headers

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
            pass

        agent1.reset()
        agent2.reset()
        pass


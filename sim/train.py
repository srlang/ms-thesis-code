# Sean R. Lang <sean.lang@cs.helsinki.fi>

from cribbage   import  CribbageGame

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

def create_agents(a1sf, a1of, a2sf, a2of):
    agent1 = CribbageAgent()
    # TODO
    pass

def checkpoint(agent, epoch, start_time_str):
    # TODO
    pass

def train(agent1stratfile, agent1outfile, agent2stratfile, agent1outfile, epochs=1000, epoch_checkpoint=None):
    if epoch_checkpoint is None:
        epoch_checkpoint = max(int(epochs / 100), 1)
    agent1, agent2 = create_agents(agent1stratfile,
                        agent1outfile,
                        agent2stratfile,
                        agent2outfile)

    for epoch in range(epochs):
        PD('Epoch %d' % epoch)
        play_training_game(agent1, agent2)

        if (epoch % epoch_checkpoint) == 0:
            checkpoint(agent1, epoch)
            checkpoint(agent2, epoch)
            pass

        agent1.reset()
        agent2.reset()
        pass


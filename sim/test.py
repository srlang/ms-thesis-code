# Sean R. Lang <sean.lang@cs.helsinki.fi>

from cribbage   import CribbageGame
from train      import create_agent
from ui         import InteractiveCribbageAgent
from utils      import PD

def play_test_game(agent, player):
    game = CribbageGame(agent, player)
    game.play_full_game()
    return game


def test(agent_strat_file, games=9):
    agent = create_agent(agent_strat_file, 'opponent')
    player = InteractiveCribbageAgent()
    player.name = 'player'

    for game_ct in range(games):
        game = play_test_game(agent, player)
        
        print()
        print('Final Score: %d - %d.' % (player.score, agent.score)) 
        print('You Win!' if player.is_winner else 'You Lose.')
        agent.reset()
        player.reset()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('agent_file', help='filename for agent checkpoint to load')
    parser.add_argument('-v', '--verbose', help='verbose mode?', action='store_true')
    parser.add_argument('-g', '--games', help='number of games to play', type=int,
            default=9)
    # ...
    args = parser.parse_args()
    if args.verbose:
        pass
    print('Testing with (%d) games against agent(%s)' % (args.games, args.agent_file))
    test(args.agent_file, args.games)


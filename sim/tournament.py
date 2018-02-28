#!/usr/bin/env python3

# Sean R. Lang <sean.lang@cs.helsinki.fi>

from cribbage   import  CribbageGame
from train      import  create_agent

def clean_score(score):
    return min(121, score)

def play_tournament_game(agent1, agent2):
    '''
    Create and play a game between the two agents in a tournament format.
    Won't necessarily follow tournament rules.
    1. Any number of games allowed
    2. Crib will be assigned randomly at the start of each game.
    '''
    # niceties: reset agents to remove scores and whatnot from any previous game
    agent1.reset()
    agent2.reset()

    # create Game object
    game = CribbageGame(agent1, agent2)

    # allow the game to be played
    game.play_full_game()

    # return the scores of each agent so that any logic is done outside of this method
    return (clean_score(agent1.score), clean_score(agent2.score))

def play_tournament(agent1_file, agent2_file, num_games=100):
    '''
    Play `num_game` games between agents defined by given files.
    What is returned is a summary of statistics for each player

    ret = (agent1 wins, agent2 wins, point-spread for agent1)
    '''
    # create the agents which will be competing
    agent1 = create_agent(agent1_file, 'agent1')
    agent2 = create_agent(agent2_file, 'agent2')
    
    scores = []

    wins = 0
    losses = 0
    spread = 0
    tourny_a = 0
    tourny_b = 0
    for i in range(num_games):
        score = play_tournament_game(agent1, agent2)
        scores.append(score)
        a,b = score

        print('Game %d: %3d - %3d' % (i, a, b))

        if a > b:
            wins += 1
            tourny_a += 2 if a - b < 31 else 3
        else:
            losses += 1
            tourny_b += 2 if b - a < 31 else 3

        spread += a - b
    
    return (tourny_a, tourny_b, spread, (wins, losses))

def play_official_tournament_match(agent1, agent2):
    '''
    Create and play an official tournament match.
    TODO later
    '''
    pass

def declare_winner(name, infile):
    print('%s is the winner, "%s" passes on to next round' % (name, infile))

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-a', '--agent1file', help="filename for agent1's weights", default=None, type=str)
    parser.add_argument('-b', '--agent2file', help="filename for agent2's weights", default=None, type=str)
    parser.add_argument('-g', '--games', help="Number of games to run", default=100, type=int)
    parser.add_argument('-t', '--tournament-scoring', help='Do we care about tournament scoring or just pure win/loss', action='store_true')

    args = parser.parse_args()
    print('args')
    print(args)

    if (args.agent1file is None) or (args.agent2file is None):
        print("please supply both agents' files")

    else:
        a,b,s,wl = play_tournament(args.agent1file, args.agent2file, num_games=args.games)
        print()
        print('Final Results:')
        print('Score(A): %d' % a)
        print('Score(B): %d' % b)
        print('Spread: %d' % s)
        print('Wins: %d - %d' % wl)

        if args.tournament_scoring:
            # TODO: check actual rules for this
            # care about points first, then spread
            if a > b:
                # clear a winner
                declare_winner('A', args.agent1file)
            elif b > a:
                # clear b winner
                declare_winner('B', args.agent2file)
            else:
                # go to points spread
                if s > 0:
                    declare_winner('A', args.agent1file)
                elif s < 0:
                    declare_winner('B', args.agent2file)
                else:
                    print('Tie, break it how you will.')
        else:
            # win-loss only
            w,l = wl
            if w > l:
                # clear a winner
                declare_winner('A', args.agent1file)
            elif l > w:
                # clear b winner
                declare_winner('B', args.agent2file)
            else:
                print('Tie, break it how you will')
            pass


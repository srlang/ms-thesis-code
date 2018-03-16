#!/usr/bin/env python3

# Sean R. Lang <sean.lang@cs.helsinki.fi>

import matplotlib.pyplot as plt

from cribbage   import  CribbageGame
from train      import  create_agent
from tournament import  play_tournament, play_tournament_game

#from analyze    import  read_

METRIC_OPTIONS = ['points', 'wins', 'spread']

if __name__ == '__main__':
    from argparse import ArgumentParser
    '''
    want:
        1. agent master file
        2. previous agent files
        3. points numbers for x axis
        4. labels for axes
    '''
    parser = ArgumentParser()
    parser.add_argument('metric', help='what are we plotting?', choices=METRIC_OPTIONS)
    parser.add_argument('-a', '--master-agent', help='agent file to use for comparison against all others')
    parser.add_argument('-p', '--previous-agents', help='previous agent files to play against')

    parser.add_argument('-o', '--output', help='file to output')

    parser.add_argument('-x', '--x-label', help='x axis label', default='')
    parser.add_argument('-y', '--y-label', help='y axis label', default='')

    parser.add_argument('-u', '--x-range', help='range of values for the x-axis')
    parser.add_argument('-v', '--x-step', help='step for x', type=int, default=1)

    parser.add_argument('-g', '--games', help='number of games to play', type=int, default=100)

    parser.add_argument('-t', '--times', help='number of "times" or lines to draw on graph', type=int, default=20)

    args = parser.parse_args()
    print('args')
    print(args)

    xr = [int(s) for s in args.x_range.split(',')]

    for t in range(args.times):
        print('Time=%d' % t)
        results = []
        for p in args.previous_agents.split(','):
            print('playing game between %s and %s' % (args.master_agent, p))
            results.append(play_tournament(args.master_agent, p, num_games=args.games))
        

        if args.metric == 'spread':
            ys = spreads = [s for a,b,s,(w,l) in results]
        elif args.metric == 'points':
            ys = points = [a for a,b,s,(w,l) in results]
        elif args.metric == 'wins':
            ys = wins = [w for a,b,s,(w,l) in results]
        else:
            raise NotImplementedError('not yet available (if ever)')
        
        xs = range(xr[0], xr[1]+1, args.x_step)

        print('plotting %s along %s' % (ys,xs))
        plt.plot(xs, ys)
        pass

    plt.xlabel(args.x_label)
    plt.ylabel(args.y_label)
    plt.savefig(args.output)

    pass


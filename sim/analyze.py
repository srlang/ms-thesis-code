# Sean R. Lang <sean.lang@cs.helsinki.fi>

from os                     import  listdir
from re                     import  match

import numpy                as      np
import matplotlib.pyplot    as      plt
from pandas                 import  read_csv

from train                  import  CHECKPOINT_FILENAME_FORMAT
from utils                  import  PD

'''
Script to be used after a bunch of runs have been made,
making some plots that could be useful for the thesis.

Ideas:
    plot a matrix of a single strategy in heatmap/grayscale with strength
        - actually 2: 1 for the dealer, 1 for the pone
    plot a time-stretch of matrices of a single strategy in grayscale/heatmap
        as time progresses for

This can be left for later
'''

def read_weights_file(filename, directory='./checkpoints'):
    csv_table = read_csv(directory + '/' + filename, sep=' ')

    dealer = csv_table[csv_table['dealer'] == 0]
    pone = csv_table[csv_table['dealer'] == 1]

    return dealer,pone

def weights_tabled(table, num_weights, dimensions=(121,121)):
    dims = tuple([num_weights] + list(dimensions))
    ret = np.zeros(dims)

    for _i,row in table.iterrows():
        m = int(row.iloc[0])
        o = int(row.iloc[1])
        #d = int(row.iloc[2])
        for weight in range(num_weights):
            ret[weight,m,o] = row.iloc[weight+3]

    return ret

def all_files(file_format, agent_name, date_str, directory='./checkpoints'):
    regex_base = file_format % (agent_name, date_str, 999)
    #print('regex_base')
    #print(regex_base)
    regex = regex_base.replace('999', '.*')
    #print('regex')
    #print(regex)
    af = sorted(listdir(directory))
    #print('ls')
    #print(af)
    #print('types')
    #print([type(f) for f in af])
    ret = [f for f in af if match(regex, f)]
    return ret

def plot_single_strategy(file_names, strat_name,
                            pone=False, color_map='Greys', out_dir='./images/'):
    for fn in file_names:
        d,p = read_weights_file(fn)
        w = p if pone else d
        strat = w[['my_score', 'opp_score', 'dealer'] + [strat_name]]
        t = weights_tabled(strat, 1)[0] # grab first index (of 1)

        # plot as image
        #plt.imshow(t, cmap=color_map)
        #plt.savefig(out_dir + '/' +  fn + '_genimg_' + strat_name + '.png')
        out_file = out_dir + '/' +\
                fn.replace('.txt', '') +\
                '_genimg_' +\
                ('_%s_' % ('pone' if pone else 'dealer')) +\
                strat_name + '.png'

        plt.imsave(out_file, t, cmap=color_map)

    pass

def plot_all_strategies(file_name):
    # TODO
    pass

def plot_strategy_over_time(file_format, strat_name):
    # TODO
    pass

OPERATIONS = ['single']

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('operation', help='what are we running', choices=OPERATIONS)
    parser.add_argument('-a', '--agent', help='agent name')
    parser.add_argument('-D', '--date-str', help='date string for start time')
    parser.add_argument('-p', '--pone', help='are we looking at pone?', action='store_true')
    parser.add_argument('-d', '--directory', help='directory to look for checkpoints', default='./checkpoints')
    parser.add_argument('-c', '--color', help='color map to use', default='Greys')
    parser.add_argument('-o', '--output-dir', help='directory to plot images to', default='./images')
    parser.add_argument('-s', '--strategy', help='strategy name(s(?)) to use')
    # do stuff
    # [[None]*121]*121 --> does not work: all rows same pointer
    args = parser.parse_args()
    if args.operation == 'single':
        files = all_files(CHECKPOINT_FILENAME_FORMAT, args.agent, args.date_str)
        #print('files:')
        #print(files)
        plot_single_strategy(\
                files,\
                args.strategy,
                pone=args.pone,
                color_map=args.color,
                out_dir=args.output_dir)

    else:
        print('other operation gotten')
    pass

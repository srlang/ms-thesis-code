#!/usr/bin/env python3
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
    regex_base = file_format % (agent_name, date_str, 999999999999)
    #print('regex_base')
    #print(regex_base)
    regex = regex_base.replace('999999999999', '.*')
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
                            pone=False, color_map='Greys', out_dir='./images/', in_dir='./checkpoints'):
    for fn in file_names:
        d,p = read_weights_file(fn, directory=in_dir)
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

        print(strat_name + ': weights[0:3,0:3]: ' + str(t[0:3,0:3]))
        # set vmin/vmax to ensure that colors stay consistent across multiple
        # runs. we know that this can only be 0-1 because of normalization
        plt.imsave(out_file, t, cmap=color_map, vmin=0.0, vmax=1.0)

    pass

def dealer_pone_difference(file_name, out_dir='./hot', color_map='Greys'):
    from train import _write_checkpoint
    from generate_checkpoints import blank_weights
    STRATEGIES = ['hand_max_min', 'hand_max_avg', 'hand_max_med', 'hand_max_poss', 'crib_min_avg', 'pegging_max_avg_gained', 'pegging_max_med_gained', 'pegging_min_avg_given']

    # bug in code (which I'm keeping for nostalgia/to point out later)
    # means that these are switched.
    # "fixing" here by reversing to keep things straight
    #p,d = read_weights_file(file_name, directory='.') #, directory=in_dir)
    #print(d)

    table = read_csv(file_name, sep=' ') #, directory=in_dir)
    dealer = np.zeros((121,121,len(STRATEGIES)))
    pone = np.zeros((121,121,len(STRATEGIES)))
    #print(pone)
    #print(pone.shape)
    for _,row in table.iterrows():
        m = int(row.iloc[0])
        o = int(row.iloc[1])
        d = int(row.iloc[2])
        weights = [row.iloc[i+3] for i in range(len(STRATEGIES))]
        if d:
            dealer[m][o] = np.array(weights)
            pass
        else:
            # pone
            pone[m][o] = np.array(weights)
            pass
#        for i in range(len(STRATEGIES)):
#            diff[i,m,o] = table[(table['my_score'] == m) & (table['opp_score'] == o) & (table['dealer'] == 1)] - table[(table['my_score'] == m) & (table['opp_score'] == o) & (table['dealer'] == 0)]

    diff = np.transpose(np.subtract(dealer, pone))
    print(diff.shape)

    for i in range(len(STRATEGIES)):
        strat = STRATEGIES[i]
        out_file = out_dir + '/' + strat + '.png'
        plt.imsave(out_file, np.transpose(diff[i]), cmap=color_map, vmin=-1.0, vmax=1.0)
    #print(diff)
    #print(diff.shape)
    #diff = blank_weights()
    #dealer_tabled = weights_tabled(d, len(STRATEGIES))
    #pone_tabled = weights_tabled(p, len(STRATEGIES))
    #print(dealer_tabled)

    #for _,row in d.iterrows():

#    for i in range(121):
#        for j in range(121):
#            # make pone and dealer the same, who cares?
#            # we're just hacking together a difference for a single image
#            _diff = d[i][j] - p[i][j]
#            print(_diff)
#            #diff[i][j][0] = d[i][j] - p[i][j]
#            #diff[i][j][1] = d[i][j] - p[i][j]

#    all_strats = weights_tabled(diff, len(STRATEGIES))
#    for i in range(len(all_strats)):
#        #strat = STRATEGIES[i]
#        strategy = STRATEGIES[i]
#        out_file = out_dir + '/' + strategy + '.png'
#        plt.imsave(out_file, all_strats[i], cmap=color_map) # allow self-scaling
#    #wstr = weights_string(diff, strat_names)

    #_write_checkpoint(wstr, file_name+'.diff', directory=out_dir)


def weights_string(weights, strat_names):
    from re import sub # overall, wrong way to do this, but whatever
    header_ln = 'my_score opp_score dealer ' + ' '.join(strat_names) + '\n'
    ret = '\n'.join(
            [
                    (
                        (('%d %d %d ' % (m,o,d)) + \
                             ' '.join(
                                    [str(w) for w in weights[m][o][d]]
                                    )
                             ) if weights[m][o][d] is not None
                                    else ''
                    )
                    for m in range(len(weights))
                for o in range(len(weights[m]))
            for d in [0,1]
            ]
        ).strip()
    #ret = filter(lambda line: not re.match(r'^\s*$', line), ret)
    ret = sub(r'(\n){2,}', '\n', ret)
    return header_ln + ret

def plot_all_strategies(file_name):
    # TODO
    pass

def plot_strategy_over_time(file_format, strat_name):
    # TODO
    pass

OPERATIONS = ['single', 'diff']

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
    parser.add_argument('-i', '--input', help='idk')
    #parser.add_argument('-p', '--png', help='idk')
    # do stuff
    # [[None]*121]*121 --> does not work: all rows same pointer
    args = parser.parse_args()
    if args.operation == 'single':
        files = all_files(CHECKPOINT_FILENAME_FORMAT, args.agent, args.date_str, directory=args.directory)
        #print('files:')
        #print(files)
        print('Running with parameters:')
        #print('\tfiles=%s' % files)
        print('\tstrategy=%s' % args.strategy)
        print('\tpone?=%s' % str(args.pone))
        print('\tcolor_map=%s' % args.color)
        print('\tout_dir=%s' % args.output_dir)

        plot_single_strategy(\
                files,\
                args.strategy,
                pone=args.pone,
                color_map=args.color,
                out_dir=args.output_dir,
                in_dir=args.directory)

    elif args.operation == 'diff':
        dealer_pone_difference(args.input, args.output_dir, color_map=args.color)

    else:
        print('other operation gotten')
    pass

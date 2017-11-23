# Sean R. Lang <sean.lang@cs.helsinki.fi>

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

def read_weights_file(filename):
    csv_table = read_csv(filename, sep=' ')

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

def plot_single_strategy(file_name, strat_name):
    # TODO
    pass

def plot_all_strategies(file_name):
    # TODO
    pass

def plot_strategy_over_time(file_format, strat_name):
    # TODO
    pass


if __name__ == '__main__':
    # do stuff
    # [[None]*121]*121 --> does not work: all rows same pointer
    pass

# Sean R. Lang <sean.lang@cs.helsinki.fi>

from random import random as rand
from sklearn.preprocessing  import normalize as sknorm

from agent import blank_weights, normalize, SmartCribbageAgent
from train import _write_checkpoint

#def blank_weights():
#    return [ [ [ None for d in [0,1] ] for o in range(121) ] for m in range(121) ] 
#    
def normalize(vector):
    return list(sknorm([vector], norm='l1')[0])

def write_checkpoint(filename, weights, strats):
    agent = SmartCribbageAgent()
    agent.weights = weights
    agent._strat_names = strats
    output = agent.save_weights_str()
    _write_checkpoint(output, filename, './checkpoints')

def random_weights(strats):
    nstrats = len(strats)
    weights = blank_weights()
    for m in range(len(weights)):
        for o in  range(len(weights[m])):
            for d in [0,1]:
                weights[m][o][d] = normalize([rand() for x in range(nstrats)])
    return weights

def sensible_weights(**kwargs):
    # ignore strats in this scenario
    #nstarts = len(strats)
    # TODO
    weights = blank_weights()
    return weights

def uniform_weights(strats):
    nstrats = len(strats)
    weights = blank_weights()
    for m in range(len(weights)):
        for o in  range(len(weights[m])):
            for d in [0,1]:
                weights[m][o][d] = normalize([1.0 for x in range(nstrats)])
    return weights

def verify_weights_full(weights):
    ret = True
    for m in range(121):
        for o in range(121):
            for d in [0,1]:
                try:
                    if weights[m][o][d] is None or weights[m][o][d] == []:
                        print('weights empty at index (%d,%d,%d)' % (m,o,d))
                        return False
                except Exception as e:
                    print(e)
                    return False
    return ret

def main(filename, weight_gen, strats):
    weights = weight_gen(strats)
    if verify_weights_full(weights):
        write_checkpoint(filename, weight_gen(strats), strats)

if __name__ == '__main__':
    from strategy3 import ALL_STRATEGY_NAMES
    main('random_start.txt', random_weights, ALL_STRATEGY_NAMES)
    main('uniform_start.txt', uniform_weights, ALL_STRATEGY_NAMES)
    #main('sensible_start.txt', random_weights, ALL_STRATEGY_NAMES)


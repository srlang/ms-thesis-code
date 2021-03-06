# Sean R. Lang <sean.lang@cs.helsinki.fi>

#from numpy      import  matmul

from itertools  import  combinations

from cribbage   import  score_hand

from records    import  session as records_session,\
                        AggregatePlayedHandRecord,\
                        KeepThrowStatistics

from strategy2  import  _possible_keep_toss_tuple_list,\
                        _retrieve_hand_statistics,\
                        _get_all_indices,\
                        _get_by_multiple_indices,\
                        _to_keep_toss_tuple
                        #possible_KeepThrowStatistics,\
                        #_retrieve_property_list,\

from utils      import  PD


###
# N.B.:
#   1. all methods in this module will assume that the cards passed to it are
#       in sorted order.
#       This is crucial to the search method for the database.
#   2. Each of these methods will return a "weight vector" in which the best
#       hands are given "full" points of 1.0, the worst hand 0.0, and all else
#       somewhere on that scale.
#
#   These can all be combined as such:
#   1. Think of the strategy as returning a 24x1 matrix
#   2. Think of the weight vector at any (M,O,D) position as a 1xS matrix,
#       where S is the number of strategies
###

def _retrieve_property_list(objs, prop):
    ''' Retrieve a given property name from a list of objects '''
    return [obj.__dict__[prop] if (obj is not None and prop in obj.__dict__) else None\
            for obj in objs]

def kts_evaluator(kts, hand_property, min_):
    '''
    Evaluate a list of KeepThrowStatistics (and AggregatePlayedHandRecords)
    for a given set of scores and scale them.
    '''
    # retrieve relevant info
    # don't do database stuff here, so that access errors don't cause offset issues
    #kts = possible_KeepThrowStatistics(cards)
    scores = _retrieve_property_list(kts, hand_property)
    scores_num = [score for score in scores if score is not None]
    scores_num = [0, 1] if scores_num == [] else scores_num
    
    # scale scores to 0.0---1.0
    max_score = max(scores_num)
    min_score = min(scores_num)
    diff = max_score - min_score
    scores = [
                ((score - min_score) / diff)
                    if ((score is not None) and (diff != 0)) else 0.5\
                # 0.5 is necessary to basically ignore for either max or min
                # TODO: ^^^better this
                for score in scores]

    # flip around if minimum is desired
    if min_:
        scores = [1.0 - x for x in scores]

    return scores

def pegging_evaluator(aphrs, prop, min_):
    # as of now, the other method works for both
    return kts_evaluator(aphrs, prop, min_)

def possible_AggregatePlayedHandRecords(ktts):
    global records_session
    ret = []

    for k,t in ktts:
        #k,t = ktt
        retrieved = records_session.query(AggregatePlayedHandRecord).filter_by(\
                        id=AggregatePlayedHandRecord.generate_id(k)).first()
                        #card0=k[0],
                        #card1=k[1],
                        #card2=k[2],
                        #card3=k[3]).first()
        ret.append(retrieved)

    return ret

def possible_KeepThrowStatistics(ktts):
    global records_session
    ret = []

    for k,t in ktts:
        retrieved = records_session.query(KeepThrowStatistics).filter_by(\
                        id=KeepThrowStatistics.generate_id(k,t)).first()
                        #kcard0=k[0],
                        #kcard1=k[1],
                        #kcard2=k[2],
                        #kcard3=k[3],
                        #tcard0=t[0],
                        #tcard1=t[1]).first()
        ret.append(retrieved)

    return ret

def hand_evaluator(cards, strategies): #, strategy_weights):
    '''
    Evaluate a hand to produce the P vector of probabilities.

    P = w * S
        where
            w is the weight vector for all strategies (1 x m)
            S is the (m x n) matrix of each strategy
        So,
            P is a (1 x n) matrix

    Return only the S matrix as w is dependent upon the calling agent and is
    only needed for the final matrix multiplication.
    '''
    _METHOD = 'hand_evaluator'
    PD('entering', _METHOD)
    keep_toss_tuples = _possible_keep_toss_tuple_list(cards)
    PD('keep_toss_tuples=%s' % str(keep_toss_tuples), _METHOD)
    kts = possible_KeepThrowStatistics(keep_toss_tuples) #TODO: rewrite method to allow Nones
    PD('kts=%s' % str(kts), _METHOD)
    pinfo = possible_AggregatePlayedHandRecords(keep_toss_tuples)
    PD('pinfo=%s' % str(pinfo), _METHOD)

    S = []
    for strategy in strategies:
        S.append(strategy(kts, pinfo))

    PD('exiting with S=%s' % str(S), _METHOD)
    return S

def hand_max_min(kts, pinfo=None):
    # Choose the hand(s) with the maximum minimum.
    # i.e. most guaranteed points
    return kts_evaluator(kts, 'kmin', False)

def hand_max_avg(kts, pinfo=None):
    # Choose the hand(s) with the maximum average score
    return kts_evaluator(kts, 'kavg', False)

def hand_max_med(kts, pinfo=None):
    # Choose the hand(s) with the maximum median score
    return kts_evaluator(kts, 'kmed', False)

def hand_max_poss(kts, pinfo=None):
    # Choose the hand(s) with the maximum possible score (gambler's strategy)
    return kts_evaluator(kts, 'kmax', False)

def crib_min_avg(kts, pinfo=None):
    # Choose the hand(s) with the minimum average crib
    return kts_evaluator(kts, 'tavg', True)

def pegging_max_avg_gained(kts, pinfo):
    # Choose the hand which has gained the maximum average of points for the
    # player. This would typically be useful as a Hail Mary for the dealer in
    # a very close game at the last hand.
    return pegging_evaluator(pinfo, 'gained_avg', False)

def pegging_max_med_gained(kts, pinfo):
    # Choose the hand which has the maximum median pegging points scored
    return pegging_evaluator(pinfo, 'gained_med', False)

def pegging_min_avg_given(kts, pinfo):
    # Choose the hand which has given the least points up, on average
    return pegging_evaluator(pinfo, 'given_avg', True)

ALL_STRATEGY_NAMES = [
                        'hand_max_min',
                        'hand_max_avg',
                        'hand_max_med',
                        'hand_max_poss',
                        'crib_min_avg',
                        'pegging_max_avg_gained',
                        'pegging_max_med_gained',
                        'pegging_min_avg_given'
                    ]
ALL_STRATEGIES = [
                    hand_max_min,
                    hand_max_avg,
                    hand_max_med,
                    hand_max_poss,
                    crib_min_avg,
                    pegging_max_avg_gained,
                    pegging_max_med_gained,
                    pegging_min_avg_given
                ]

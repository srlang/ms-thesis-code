#!/usr/bin/env python3

# Sean R. Lang <sean.lang@cs.helsinki.fi>

'''
Use the dailycribbagehand.org data to see how our agent stacks against
human enthusiast play.
Can't necessarily say anyone is an expert, but someone who looks this stuff up
is likely to have some experience.
'''

from collections                import  Counter

from itertools                  import  combinations

from sqlalchemy                 import  Boolean, Column, Float, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy                 import  create_engine
from sqlalchemy.ext.declarative import  declarative_base
from sqlalchemy.orm             import  sessionmaker

from statistics                 import  mean, median, mode

from agent                      import  normalize
from train                      import  create_agent
from strategy2                  import  _get_all_indices

ch_engine = create_engine("mysql://root@localhost/cribbage", echo=False)
ch_Base = declarative_base()
ch_Session = sessionmaker(bind=ch_engine)
ch_session = ch_Session()

def create_tables():
    global ch_Base
    global ch_engine
    ch_Base.metadata.create_all(ch_engine)

SUITS = ['s', 'c', 'h', 'd']
CARDS = ['a', '2', '3', '4', '5', '6', '7', '8', '9', 't', 'j', 'q', 'k']

class Hands(ch_Base):

    __tablename__ = 'hands'

    id = Column(Integer, primary_key=True)
    
    date = Column(Date)

    one = Column(String)
    two = Column(String)
    three = Column(String)
    four = Column(String)
    five = Column(String)
    six = Column(String)

    upcard = Column(String)

    dealer = Column(String)
    position = Column(String)

    def cards_nums(self):
        cards = [self.one, self.two, self.three, self.four, self.five, self.six]
        return sorted(cards_str_to_num(cards))

    def location(self):
        my,opp = self.position.split('-')
        dealer = int('*' in my)
        mys = my.replace('*','')
        opps = opp.replace('*','')
        my = int(mys if mys is not '' else '0')
        opp = int(opps if opps is not '' else '0')
        return (my,opp,dealer)


def card_str_to_num(card):
    #print('>>>>>card_str_to_num('+card+')')
    return (4 * CARDS.index(card[0]))  + (SUITS.index(card[1]))

def cards_str_to_num(cards):
    return [card_str_to_num(card) for card in cards]


class Results(ch_Base):

    __tablename__ = 'results'

    id = Column(Integer, primary_key=True)

    handid = Column(Integer, ForeignKey('hands.id')) # foreign key

    one = Column(String)
    two = Column(String)
    three = Column(String)
    four = Column(String)

    date = Column(Date)

    def is_empty(self):
        return (self.one is '') or (self.two is '') or (self.three is '') or (self.four is '')

    def card_nums(self):
        cards = [self.one, self.two, self.three, self.four]
        #print('>>>card_nums.cards:' + str(cards))
        return sorted(cards_str_to_num(cards))


def most_common(arr):
    counter = Counter(arr)
    most = 0
    melm = None
    for elem,count in counter.items():
        if count > most:
            most = count
            melm = elem
    return melm

def most_common_key(d):
    max = 0
    val = None
    for k,v in d.items():
        if v > max:
            max = v
            val = k
    return k

def unique_id(cards):
    sum = 0
    pow = 0
    for c in reversed(cards):
        sum += c * (10 ** pow)
        pow += 2
    return sum

def main_comparison(agent_file, max_num=100):
    global ch_session
    agent = create_agent(agent_file, 'agent_name')
    hands = ch_session.query(Hands).all()
    index = 0
    same = []
    diff = []
    print('total hands: ' + str(len(hands)))
    for hand in hands:
        responses = [x for x in ch_session.query(Results).filter_by(handid=hand.id).all() if not x.is_empty()]
        try:
            m,o,d = hand.location()
        except:
            continue
        print(str(hand.id) +':'+str(hand.location()) + ':' + str(hand.cards_nums()))
        try:
            responses_nums = [r.card_nums() for r in responses if not r.is_empty()]
        except Exception as e:
            print(e)
            print('responses: ' + str(responses))
            continue
        if not responses_nums:
            continue

        unique_responses = {unique_id(r) : r for r in responses_nums}
        #print('\tUniqueResponses: %s' % str(unique_responses))

        # rcount_d: {response.uid --> occurrence count}
        rcount_d = {}
        for resp in responses_nums:
            uid = unique_id(resp)
            if uid not in rcount_d:
                rcount_d[uid] = 0
            rcount_d[uid] += 1

        #print('\trcount_d: %s' % str(rcount_d))

        # find the most common key, assuming values as a counter
        mocom = most_common_key(rcount_d)
        print('\tMost Common: ' + str(unique_responses[mocom]))

        # let agent choose from the cards
        # setup score location and whatnot
        agent.hand = hand.cards_nums()
        agent.score = m
        agent.is_dealer = bool(d)
        try:
            agents_choice,toss = agent.choose_cards(opponent_score=o)
        except:
            continue
        if list(agents_choice) == unique_responses[mocom]:
            same.append(hand.id)
        else:
            diff.append(hand.id)
        print('\tAgent Chose: ' + str(agents_choice))

        index += 1
        if index > max_num:
            break

    total = len(same) + len(diff)
    print('Agent made the human choice: %d/%d' % (len(same),total))
    print('IDs of hands that were chosen differently for comparison: ' + str(diff))
    '''
        if responses_nums:
            cmap = {unique_id(rn) : rn for rn in responses_nums}
            print('\tcmap: %s' % str(cmap))
#            print('\tAll: ')
#            for r in responses_nums:
#                print('\t\t' + str(r))
            mc = most_common(cmap.keys())
            print('\tMost Common: ' + str(cmap[mc]))

            # let agent choose from the cards
            # setup score location and whatnot
            agent.hand = hand.cards_nums()
            agent.score = m
            agent.is_dealer = bool(d)
            agents_choice,toss = agent.choose_cards(opponent_score=o)
            if list(agents_choice) == cmap[mc]:
                same.append(hand.id)
            else:
                diff.append(hand.id)
            print('\tAgent Chose: ' + str(agents_choice))
    '''


def main_distance(agent_file, max_num=100):
    global ch_session
    agent = create_agent(agent_file, 'AgentName')
    hands = ch_session.query(Hands).all()
    index = 0

    all_squared_sum_diffs = []

    print('len(hands)=' + str(len(hands)))

    for hand in hands:
        responses = [x for x in
                        ch_session.query(Results).filter_by(handid=hand.id).all()
                        if not x.is_empty()]
        try:
            m,o,d = hand.location()
            responses_nums = [r.card_nums() for r in responses
                                if not r.is_empty()]
        except:
            continue

        if not responses_nums:
            continue

        unique_responses = {unique_id(r) for r in responses_nums}

        # keep count of how many of each response garnered
        rcount_d = {}
        for resp in responses_nums:
            uid = unique_id(resp)
            if uid not in rcount_d:
                rcount_d[uid] = 0
            rcount_d[uid] += 1

        # each response as a fraction now (match with L1 norm)
        total_responses = sum(rcount_d.values())
        rcount_frac_d = {uid : val / total_responses for uid,val in rcount_d.items()}

        # let agent choose its hand
        agent.hand = sorted(hand.cards_nums())
        agent.score = m
        agent.is_dealer = bool(d)
        try:
            agents_choice,toss = agent.choose_cards(opponent_score=o)
        except IndexError as ie:
            # in the event of an exception, just skip
            continue

        # retreive p vector for comparison (normalized to L1)
        p = normalize(agent._tmp_p)
        keeps = combinations(sorted(hand.cards_nums()), 4)

        # map agent's p to a dict for comparison
        p_d = {}
        for i,k in enumerate(keeps):
            indx = unique_id(list(k))
            p_d[indx] = p[i]

        # retrieve differences between rcount_frac_d and p_d
        diffs = []
        for uid in p_d.keys():
            a = p_d[uid]
            b = rcount_frac_d[uid] if uid in rcount_frac_d else 0
            diffs.append(a-b)
        
        # squared difference
        squared_diffs = [x*x for x in diffs]
        
        sum_squared_diffs = sum(squared_diffs)

        all_squared_sum_diffs.append(sum_squared_diffs)

        print(hand.location(), end=' : ')
        print(hand.cards_nums())
        print('\tHuman.d: ', end='')
        print(rcount_frac_d)
        print('\tAgent.p: ', end='')
        print(p_d)
        print('\tDifference: ', end='')
        print(diffs)
        print('\tSquaredDifference: ', end='')
        print(squared_diffs)
        print('\t\tSum: ', end='')
        print(sum_squared_diffs)

        index += 1
        if index >= max_num:
            break
    
    print('MeanSquaredError: %f' % mean(all_squared_sum_diffs))
    print('MaxError: %f' % max(all_squared_sum_diffs))
    print('MinError: %f' % min(all_squared_sum_diffs))

def main_top_x(agent_file, x=3, max_num=100):
    global ch_session
    agent = create_agent(agent_file, 'agent_name')
    hands = ch_session.query(Hands).all()
    index = 0
    top = [0] * x
    ntop = 0
    right = 0

    for hand in hands:
        responses = [x for x in ch_session.query(Results).filter_by(handid=hand.id).all()
                        if not x.is_empty()]
        try:
            m,o,d = hand.location()
            responses_nums = [r.card_nums() for r in responses if not r.is_empty()]
            if not responses_nums:
                continue
        except:
            continue

        unique_responses = {unique_id(r) : r for r in responses_nums}

        rcount_d = {}
        for resp in responses_nums:
            uid = unique_id(resp)
            if uid not in rcount_d:
                rcount_d[uid] = 0
            rcount_d[uid] += 1

        ranked_responses = rank_responses(rcount_d)

        agent.hand = hand.cards_nums()
        agent.score = m
        agent.is_dealer = bool(d)
        try:
            agents_choice,toss = agent.choose_cards(opponent_score=o)
            agents_choice_l = list(agents_choice)
            agents_choice_uid = unique_id(agents_choice_l)
        except:
            continue

        found_ind = 999
        for i in range(len(ranked_responses)):
            if agents_choice_uid == ranked_responses[i]:
                found_ind = i
                break

        if found_ind < min(len(ranked_responses), x):
            # found within top X and need to update top[] accordingly
            # used ranked_responses.length to ensure that all
            print("\tAgent's response in top %d" % (found_ind+1))
            top[found_ind:] = [x+1 for x in top[found_ind:]]
            right += 1
        else:
            # not found within top X or there were too few responses to say
            # that conclusively, so not counting as success
            print("\tAgent's choice not in top %d" % x)
            ntop += 1
        
        index += 1
        if max_num is not None and index >= max_num:
            break

    #right = sum(top)
    total = right + ntop
    print('Times "correct" = %d/%d' % (right,total))
    print('Total Percent "correct" = %f' % (100.0 * right / total))
    print('Top=' + str(top))

def rank_responses(counts_d):
    sorted_responses = reversed(sorted(counts_d.items(), key=lambda x: x[1]))
    return [k for k,v in sorted_responses]


def main_percent_agreed(agent_file, max_num=100):
    global ch_session
    agent = create_agent(agent_file, 'agentin_nimi')
    hands = ch_session.query(Hands).all()
    index = 0
    stats = [] # list of (raw_agree, raw_total, raw_max_responses, percent)

    for hand in hands:
        responses = [x for x in ch_session.query(Results).filter_by(handid=hand.id).all()
                        if not x.is_empty()]
        try:
            m,o,d = hand.location()
            responses_nums = [r.card_nums() for r in responses if not r.is_empty()]
            if not responses_nums:
                continue
        except:
            continue

        unique_responses = {unique_id(r) : r for r in responses_nums}

        rcount_d = {}
        for resp in responses_nums:
            uid = unique_id(resp)
            if uid not in rcount_d:
                rcount_d[uid] = 0
            rcount_d[uid] += 1

        ranked_responses = rank_responses(rcount_d)

        agent.hand = hand.cards_nums()
        agent.score = m
        agent.is_dealer = bool(d)
        try:
            agents_choice,toss = agent.choose_cards(opponent_score=o)
            agents_choice_l = list(agents_choice)
            agents_choice_uid = unique_id(agents_choice_l)
        except:
            continue

        raw_agree = rcount_d[agents_choice_uid] if agents_choice_uid in rcount_d else 0
        raw_total = sum(rcount_d.values())
        raw_max_responses = max(rcount_d.values())
        percent = raw_agree / raw_total
        
        print('\t%s --> %s' % \
                (hand.cards_nums() , str((raw_agree, raw_total, raw_max_responses, percent)) )
            )
        stats.append( (raw_agree, raw_total, raw_max_responses, percent) )

        index += 1
        if max_num is not None and index >= max_num:
            break

    percents = [p for (_,_,_,p) in stats]
    top_percents = [mx / tot for (_,tot,mx,_) in stats]
    print('Average agreed percent: %f' % mean(percents) )
    print('Median agreed percent: %f' % median(percents) )
    print('Min agreed percent: %f' % min(percents))
    print('Max agreed percent: %f' % max(percents))
    print('Average top response percent: %f' % mean(top_percents))

def main_dists(agent_file, one_hot=False, max_num=100):
    global ch_session
    agent = create_agent(agent_file, 'agent_name')
    hands = ch_session.query(Hands).all()
    index = 0
    tvds = []
    #top = [0] * x
    #ntop = 0
    #right = 0

    for hand in hands:
        responses = [x for x in ch_session.query(Results).filter_by(handid=hand.id).all()
                        if not x.is_empty()]
        try:
            m,o,d = hand.location()
            responses_nums = [r.card_nums() for r in responses if not r.is_empty()]
            if not responses_nums:
                continue
        except:
            continue

        unique_responses = {unique_id(r) : r for r in responses_nums}

        rcount_d = {}
        for resp in responses_nums:
            uid = unique_id(resp)
            if uid not in rcount_d:
                rcount_d[uid] = 0
            rcount_d[uid] += 1

        ranked_responses = rank_responses(rcount_d)

        agent.hand = hand.cards_nums()
        agent.score = m
        agent.is_dealer = bool(d)
        try:
            agents_choice,toss = agent.choose_cards(opponent_score=o)
            agents_choice_l = list(agents_choice)
            agents_choice_uid = unique_id(agents_choice_l)
        except:
            continue

        # A is just normalized p vector
        if one_hot:
            p = agent._tmp_p
            max_ind = _get_all_indices(p, max(p))[0]
            A = [0] * 15
            A[max_ind] = 1
            pass
        else:
            A = normalize(agent._tmp_p)

        # H must be constructed from the same order as the agent's choices
        H = []
        combos = combinations(hand.cards_nums(), 4)
        total_responses = sum(rcount_d.values())
        for combo in combos:
            uid = unique_id(list(combo))
            H.append(rcount_d[uid]/total_responses if uid in rcount_d else 0)

        tvd = dot(A,H) / dot(H,H)
        print('TVD(%22s): %f' % (str(hand.cards_nums()), tvd))
        tvds.append(tvd)

        index += 1
        if max_num is not None and index >= max_num:
            break

    print('Average TVD: %f' % mean(tvds))


def dot(A,B):
    return sum([ A[i] * B[i] for i in range(len(A)) ])

def main_tvd(agent_file, max_num=None):
    global ch_session
    agent = create_agent(agent_file, 'agent-name')
    hands = ch_session.query(Hands).all()
    index = 0
    tvds = []

    for hand in hands:
        responses = [x for x in ch_session.query(Results).filter_by(handid=hand.id).all()
                        if not x.is_empty()]
        try:
            m,o,d = hand.location()
            responses_nums = [r.card_nums() for r in responses if not r.is_empty()]
            if not responses_nums:
                continue
        except:
            continue

        unique_responses = {unique_id(r) : r for r in responses_nums}

        rcount_d = {}
        for resp in responses_nums:
            uid = unique_id(resp)
            if uid not in rcount_d:
                rcount_d[uid] = 0
            rcount_d[uid] += 1

        ranked_responses = rank_responses(rcount_d)

        agent.hand = hand.cards_nums()
        agent.score = m
        agent.is_dealer = bool(d)
        try:
            agents_choice,toss = agent.choose_cards(opponent_score=o)
            agents_choice_l = list(agents_choice)
            agents_choice_uid = unique_id(agents_choice_l)
        except:
            continue

###        if one_hot:
###            p = agent._tmp_p
###            max_ind = _get_all_indices(p, max(p))[0]
###            A = [0] * 15
###            A[max_ind] = 1
###        else:
        A = normalize(agent._tmp_p)

        H = []
        combos = combinations(hand.cards_nums(), 4)
        total_responses = sum(rcount_d.values())
        for combo in combos:
            uid = unique_id(list(combo))
            H.append(rcount_d[uid]/total_responses if uid in rcount_d else 0)

        tvd = 0
        for i in range(len(A)):
            tvd += abs(A[i] - H[i])
        tvd /= 2.0

        print('TVD(%25s): %f' % (str(hand.cards_nums()), tvd))

        tvds.append(tvd)

        index += 1
        if max_num is not None and index >= max_num:
            break

    print('Average TVD: %f' % mean(tvds))
    print('Minimum TVD: %f' % min(tvds))
    print('Maximum TVD: %f' % max(tvds))
    print('Median TVD: %f' % median(tvds))

    bucketed = [int(x*10) / 10 for x in tvds]
    print('Mode TVD(0.1): %f' % mode(bucketed))

if __name__ == '__main__':
    from argparse import ArgumentParser
    '''
    Args:
        <op> = comparison | distance | top

        common args:
            -n : number of hands to look at. default depends on op
            -a : agent file to use for comparison

        <top> args:
            -x : x parameter = top X to look at for success
    '''
    OPS = ['comparison', 'distance', 'top', 'percent', 'dists', 'tvd']

    parser = ArgumentParser()
    parser.add_argument('op', help='which method to run, basically', choices=OPS)

    parser.add_argument('-n', '--num', help='number of hands to look at', type=int, default=5000)
    parser.add_argument('-a', '--agent', help='agent file to use for picking cards', default='')
    parser.add_argument('-x', '--top-x', help='number of top choices to use for comparison', type=int, default=3)
    parser.add_argument('-1', '--one-hot', help='is tvd one-hot vector(true) or l1 diff(false)', action='store_true')
    #main_comparison('data/round2/g0/checkpoint_agent1_20180306-161355_000000999999.txt', max_num=4000)
    #main_distance('data/round2/g0/checkpoint_agent1_20180306-161355_000000999999.txt', max_num=100)
    #main_top_x('data/round2/g0/checkpoint_agent1_20180306-161355_000000999999.txt', x=3, max_num=None)
    args = parser.parse_args()

    if args.op == 'comparison':
        pass
    elif args.op == 'distance':
        pass
    elif args.op == 'top':
        main_top_x(args.agent, x=args.top_x, max_num=args.num)
    elif args.op == 'percent':
        main_percent_agreed(args.agent, max_num=args.num)
    elif args.op == 'dists':
        main_dists(args.agent, one_not=args.one_hot, max_num=args.num)
    elif args.op == 'tvd':
        main_tvd(args.agent, max_num=args.num)
    else:
        print("unrecognized operation")


#!/usr/bin/env python3

# Sean R. Lang <sean.lang@cs.helsinki.fi>

'''
Use the dailycribbagehand.org data to see how our agent stacks against
human enthusiast play.
Can't necessarily say anyone is an expert, but someone who looks this stuff up
is likely to have some experience.
'''

from collections                import  Counter

from sqlalchemy                 import  Boolean, Column, Float, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy                 import  create_engine
from sqlalchemy.ext.declarative import  declarative_base
from sqlalchemy.orm             import  sessionmaker

from train                      import  create_agent

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
        m,o,d = hand.location()
        print(str(hand.id) +':'+str(hand.location()) + ':' + str(hand.cards_nums()))
        responses_nums = [r.card_nums() for r in responses if not r.is_empty()]
        if responses_nums:
            cmap = {unique_id(rn) : rn for rn in responses_nums}
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
        index += 1
        if index > max_num:
            break

    total = len(same) + len(diff)
    print('Agent made the human choice: %d/%d' % (len(same),total))
    print('IDs of hands that were chosen differently for comparison: ' + str(diff))


if __name__ == '__main__':
    main_comparison('data/round2/g0/checkpoint_agent1_20180306-161355_000000999999.txt', max_num=4000)

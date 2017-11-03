#!/usr/bin/env python

# Sean R. Lang <sean.lang@cs.helsinki.fi>

from sqlachemy.exc  import SQLAlchemyError

from copy       import deepcopy

from numpy      import matmul


#from config     import STRATEGIES, STRATEGY_WEIGHTS

from cribbage   import score_hand, hand_values, card_value, GoException

from strategy3  import hand_evaluator
STRATEGIES = []
STRATEGY_WEIGHTS = []

from utils      import PD

class CribbageAgent(object):

    '''
    Fields:
        - score: integer score
        - cards: 6 cards dealt to the player
        - hand: 4 cards kept
        - crib: 4 cards crib
        - is_dealer: is this agent the dealer of this hand
        - is_winner: did this agent win the game?
        - _peg_cards_left: cards that have yet to be played
        - _peg_cards_gone: cards that have been played (for later retrieval)
    '''

    def __init__(self):
        # tested
        self.score = 0
        self.crib = None
        self._peg_cards_gone = []
        self._peg_cards_left = []
        # force initialization for _name field for debugging purposes
        self._name = ''

    def reset(self):
        self.score = 0
        self.crib = None
        self._peg_cards_gone = []
        self._peg_cards_left = []
        self.hand = []
        self.is_dealer = False
        self.is_winner = False
        #self._name = ''

    def choose_cards(self):
        # tested
        keep, toss = self._choose_cards()
        self.hand = keep
        #self.game.add_to_crib(toss)
        self._peg_cards_left = deepcopy(self.hand)
        self._peg_cards_gone = []
        return keep, toss

    def _choose_cards(self):
        # default behavior: return (essentially) random 2 cards
        # TODO: incorporate some percentage-based decision making
        #   this will go in SmartCribbageAgent
        return deepcopy(self.cards[:4]), deepcopy(self.cards[-2:])

    def next_peg_card(self, cards_played, go=False):
        # tested
        if self.can_peg_more(cards_played):
            to_play = self._select_next_peg_card(cards_played, go=go)
            self._peg_cards_left.remove(to_play)
            self._peg_cards_gone.append(to_play)
            return to_play
        else:
            raise GoException

    def has_peg_cards_left(self):
        # tested
        return self._peg_cards_left is not None and \
                len(self._peg_cards_left) > 0

    def can_peg_more(self, cards_played):
        # tested
        return self.has_peg_cards_left() and \
                (min(hand_values(self._peg_cards_left)) <=
                 31 - sum([card_value(card) for card in cards_played]))

    def _select_next_peg_card(self, cards_played, go=False):
        try:
            # default behavior: play "random" card
            #   keep it predictable for testing purposes
            # ensure that only valid cards are used
            valid_cards = [card for card in self._peg_cards_left
                            if card_value(card) <= 31 - sum(hand_values(cards_played))]
            return valid_cards[0]
        except:
            raise GoException

    def count_points(self, cut_card):
        # tested
        # Find old "streamlined" code and reference it here
        hand = deepcopy(self.hand)
        hand.append(cut_card)
        score = score_hand(hand, is_crib=False)
        if self.is_dealer:
            score += self._count_crib(cut_card)
        self.score += score
        return score

    def _count_crib(self, cut_card):
        if self.crib:
            hand = deepcopy(self.crib)
            hand.append(cut_card)
            score = score_hand(hand, is_crib=True)
            #self.score += score
            return score
        else:
            return 0

    # TODO

'''
2 possible solutions for how to handle weighting

1. single database row
    M,O,D, strat1name, strat1weight, strat2name, strat2weight ...
    can load all fn's into a dict at load,
    then reference dict lookup later

2. Diff DB tables
    T1: number and names of strategies, in order
    T2: M,O,D, strat1weight, strat2weight, ....
    Can keep a single array of strategies at start time

I like choice 2 better 

'''

class SmartCribbageAgent(CribbageAgent):

    def __init__(self): #, strategies, strat_weights):
        super(CribbageAgent, self).__init__()
        #self.strategies = strategies
        #self.strategy_weights = strat_weights
        self._tmp_p = None
        self._tmp_S = None
        self.game_weights_path = []
        self.weights_db_session = None

    def _choose_cards(self):
        # Return keep,toss tuple. Do nothing else.
        _METHOD = 'SmartCribbageAgent._choose_cards'
        # using self.cards[0:5]
        # TODO
        self.cards = sorted(self.cards)
        PD('sorted cards: %s' % str(self.cards), _METHOD)
        #w,
        S = hand_evaluator(self.cards, self.strategies) #, self.strategy_weights)
        self._tmp_S = S
        #PD('w=%s' % str(w), _METHOD)
        PD('S=%s' % str(S), _METHOD)
        num_strategies = len(self._strat_names)
        # retrieve weights_record from database
        weights_record = read_weights(self.weights_db_session,
                                self.score,
                                self.opponent.score,
                                num_strategies)
        if weights_record is None:
            # insert record for later consideration
            # initialize to "blank" so each option considered valid
            # basically, this shouldn't ever be triggered
            wc = WeightCoordinate(my_score=self.score,
                    opp_score=self.opponent.score,
                    dealer=self.is_dealer)
            for i in range(num_strategies):
                wc.__dict__['wd%d'%i] = 1.0 / num_strategies
            try:
                self.weights_db_session.add(wc)
                self.weights_db_session.commit()
            except SQLAlchemyError as sql:
                pass
            except Exception as e:
                pass
            weights_record = wc

        # keep a record of where we tread
        self.game_weights_path.append(weights_record)

        weights = weights_record.weights(num_strategies)
        p = matmul(weights,S)
        self._tmp_p = p
        PD('P=%s' % str(p), _METHOD)
        # v TODO: HOW DO WE DECIDE?????
        pass

    '''
    N.B.
        How are we going to punish/reward?
        I think we should scale this on score differential
        Would simply squashing/extending existing differences work?
            i.e. make the smaller stuff smaller, bigger stuff bigger when
            things work, opposite when not?
            potential issue: could easily oscillate on one/few strategy(ies)
                and never see other strategies
                Could be okay if simulated annealing or using enough parallel
                to be able to see different strategies
                Problem is we're not going to work sim annealing into the
                training framework (likely)
                Check back into this after we've read the book a bit more
    '''
    def reward(self, other_agent_score):
        # using self.weight_db_session, self.game_weights_path
        # TODO
        pass

    def punish(self, other_agent_score):
        # using self.weight_db_session, self.game_weights_path
        # TODO
        pass

    def save_weights_str(self):
        header = 'my_score opp_score dealer ' + ' '.join(self._strat_names)
        weights = self._retrieve_all_weights()
        return header + '\n'.join([weight.to_str(len(self._strat_names))
                                    for weight in weights])

    def _retrieve_all_weights(self):
        all_weights = self._weight_db_session.query(WeightCoordinate)
        return all_weights


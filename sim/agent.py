#!/usr/bin/env python

# Sean R. Lang <sean.lang@cs.helsinki.fi>

from copy                   import deepcopy
from itertools              import combinations
from numpy                  import matmul
from numpy.random           import choice
from pandas                 import read_csv
from random                 import random
from re                     import sub
from statistics             import variance
from sqlalchemy.exc         import SQLAlchemyError
from sklearn.preprocessing  import normalize as sknorm


from cribbage               import score_hand,\
                                    score_peg,\
                                    hand_values,\
                                    card_value,\
                                    GoException
from config                 import WEIGHTS_MODIFIER_STEP_DECAY,\
                                    WEIGHTS_MODIFIER_SCALING_FACTOR
from records                import input_PlayedHandRecord
from strategy2              import _get_all_indices
import strategy3 as strategy_module
from strategy3              import hand_evaluator
from weights                import WeightCoordinate, read_weights

from utils                  import PD

KEEP_AMOUNT = 4
REALLY_SMALL_FLOAT = 1e-300

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
        self.name = ''
        self.is_dealer = False
        self.is_winner = False
        self.hand = []

    def reset(self):
        self.score = 0
        self.crib = None
        self._peg_cards_gone = []
        self._peg_cards_left = []
        self.hand = []
        self.is_dealer = False
        self.is_winner = False
        #self._name = ''

    def choose_cards(self, **kwargs):
        # tested
        keep, toss = self._choose_cards(**kwargs)
        self.hand = list(keep)
        #self.game.add_to_crib(toss)
        self._peg_cards_left = deepcopy(self.hand)
        self._peg_cards_gone = []
        return keep, toss

    def _choose_cards(self, **kwargs):
        # default behavior: return (essentially) random 2 cards
        return deepcopy(self.hand[:4]), deepcopy(self.hand[-2:])

    def next_peg_card(self, cards_played, go=False):
        # tested
        _METHOD = 'Agent.next_peg_card'
        PD('entering', _METHOD)
        if self.can_peg_more(cards_played):
            PD('can peg more', _METHOD)
            to_play = self._select_next_peg_card(cards_played, go=go)
            self._peg_cards_left.remove(to_play)
            self._peg_cards_gone.append(to_play)
            PD('exiting with to_play=%d' % to_play, _METHOD)
            return to_play
        else:
            PD('cannot peg more, raising GoException', _METHOD)
            raise GoException

    def has_peg_cards_left(self):
        # tested
        return self._peg_cards_left is not None and \
                len(self._peg_cards_left) > 0

    def can_peg_more(self, cards_played):
        # tested
        _METHOD = 'Agent.can_peg_more'
        PD('has_peg_cards_left = %s' % self.has_peg_cards_left(), _METHOD)
        #min_card_value = min(hand_values(self._peg_cards_left))
        #remaining = 31 - sum([card_value(card) for card in cards_played])
        #PD('min card value (%d) <= remaining(%d) : %s' % (min_card_value, remaining, min_card_value <= remaining), _METHOD)
        #PD('returning: %s' % (self.has_peg_cards_left() and min_card_value <= remaining), _METHOD)
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
            return self._select_next_valid_peg_card(cards_played, valid_cards) #valid_cards[0]
        except:
            raise GoException

    def _select_next_valid_peg_card(self, cards_played, valid_cards):
        return valid_cards[0]

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

    def record_pegging_round(self, gained, given):
        pass
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

def blank_weights():
    return [
            [
                [ 
                    None for d in [0,1]
                ]
                for o in range(121) ] 
            for m in range(121) ]

class SmartCribbageAgent(CribbageAgent):

    def __init__(self): #, strategies, strat_weights):
        CribbageAgent.__init__(self)
        #super(CribbageAgent, self).__init__()
        #self.strategies = strategies
        #self.strategy_weights = strat_weights
        self._tmp_p = None
        self._tmp_S = None
        self.game_weights_path = []
        #self.weights_db_session = None
        self._strat_names = []
        #self.opponent = None
        # self.weights is a 4-d array:
        #   my-score -> opp_score -> dealer -> weights_list
        self.weights = blank_weights()

    def reset(self):
        CribbageAgent.reset(self)
        self._tmp_p = None
        self._tmp_S = None
        self.game_weights_path = []
        # Don't reset weights or strategy names. Those need to stay.
        #self._strat_names = []
        #self.weights = blank_weights()

    def _assign_strategies(self, strats_str_list):
        self._strat_names = strats_str_list
        self.strategies = [getattr(strategy_module, strat_name) \
                                for strat_name in self._strat_names]

    def _select_next_valid_peg_card(self, cards_played, valid_cards):
        # TODO: run through some heuristics:
        # Basic idea for this: greedy choose next card that maximizes next
        #   possible score
        # Tie goes to the first card to be found with that maximum
        # TODO: make tie go to the last (highest value)
        #   highest value helps avoid a potential go later
        max_score = 0
        ret_card = valid_cards[0]
        for card in valid_cards:
            score = score_peg(cards_played + [card])
            if score > max_score:
                max_score = score
                ret_card = card
        return ret_card

    def _choose_cards(self, opponent_score): #**kwargs):
        # Return keep,toss tuple. Do nothing else.
        _METHOD = 'SmartCribbageAgent._choose_cards'
        # using self.hand[0:5]
        self.hand = sorted(self.hand)
        PD('sorted cards: %s' % str(self.hand), _METHOD)
        S = hand_evaluator(self.hand, self.strategies)
        self._tmp_S = S
        weights = self.retrieve_weights(opponent_score)
        #self.add_to_visited_path(opponent_score)
        PD('weights: %s' % str(weights), _METHOD)
        p = matmul(weights,S)
        self._tmp_p = p
        PD('P=%s' % str(p), _METHOD)
        # TODO: need to decide to be able to test this method and to test training
        # temporary decision:
        #   EXPLORE_RATE% chance of picking randomly according to existing weights
        #       this should be (obviously) configurable
        explore_rand = random()
        PD('explore_rand=%f' % explore_rand, _METHOD)
        # N.B.: need to have explore_rate be dependant upon how varying the weights
        #   already are (more accurately inversely correlated)
        #   variance is the word you're looking for
        PD('variance=%f' % variance(p), _METHOD)
        explore_rate = 0.3 - variance(p) # EXPLORE_RATE
        PD('explore_rate=%f' % explore_rate, _METHOD)
        explore = explore_rand < explore_rate
        action = None
        if explore:
            PD("explore_rand < explore_rate, exploring",_METHOD)
            # explore step, choose randomly according to weights
            # numpy.random.choice(stuff, p=probabilities)
            p_choice = choice(len(p), p=normalize(p)) # fix params
            index = p_choice
            action = index
            PD("exploring to use index=%d" % index, _METHOD)
        else:
            PD('exploration not in the cards this time, using largest possible probability', _METHOD)
            # choose the largest possible percentage
            # in multi-modal weights produced, a random choice will be made
            #   between these strategies with uniform probability
            # random.choice --> uniform choice
            # random.choices --> weighted choice, but that's used for
            # numpy choice also allows uniform choice
            indices = _get_all_indices(p, max(p))
            index = choice(indices)
            action = index
            PD('Using %d of available %s' % (index, str(indices)), _METHOD)

        # path is (state, action), where state is (MyScore,OppScore,Dealer?)
        self.add_to_visited_path(opponent_score, action)
        keep = list(combinations(self.hand, KEEP_AMOUNT))[index]
        toss = [card for card in self.hand if card not in keep]
        PD('exiting with keep=%s, toss=%s' % (keep,toss), _METHOD)
        return keep,toss

    def load_checkpoint(self, start_weights_file):
        csv_table = read_csv(start_weights_file, sep=' ')

        for _,row in csv_table.iterrows():
            #m,o,d = row.iloc[:3]
            m = int(row.iloc[0])
            o = int(row.iloc[1])
            d = int(row.iloc[2])
            self.weights[m][o][d] = list(row.iloc[3:])

        strats = [header for header in csv_table][3:]
        self._assign_strategies(strats)
        return strats

    def retrieve_weights(self, opponent_score):
        m = self.score
        o = opponent_score
        d = int(self.is_dealer)
        num_strats = max(len(self._strat_names),1)
        weights = self.weights[m][o][d]
        if weights is None or weights == []:
            weights = [1/num_strats] * num_strats
            self.weights[m][o][d] = weights
        return weights

    def add_to_visited_path(self, opponent_score, action):
        self.game_weights_path.append((self.score, opponent_score, self.is_dealer, action))
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
        self.modify_weights(self._weights_modifier(other_agent_score))

    def punish(self, other_agent_score):
        self.modify_weights(self._weights_modifier(other_agent_score))

    def modify_weights(self, weights_mod):
        _METHOD = 'SmartCribbageAgent._modify_weights'
        PD('entering with weights_mod=%f, path=%s'\
                % (weights_mod, self.game_weights_path),
                _METHOD)
        #decay = 0.10 # "percent" to decay adjustments at each step back
        decay = WEIGHTS_MODIFIER_STEP_DECAY
        # my_score, opp_score, dealer, explore
        for m,o,d,a in reversed(self.game_weights_path):
            PD('> entering loop with weights_mod=%f' % weights_mod, _METHOD)
            start = self.weights[m][o][d]
            PD('> starting weights = %s' % start, _METHOD)
            # N.B.: topic for part of thesis background: regularization
            # (of the weights, not the decay of the modifier)

            # adjust the action weight by the modifier
            # 1 + weights_mod will scale weight down if wm is negative,
            #   and up if wm is positive
            start[a] *= (1.0 + weights_mod)

            # normalize vector
            end = normalize(start)
            self.weights[m][o][d] = end
            PD('> ending weights = %s' % end, _METHOD)

            weights_mod *= (1.0 - decay) # allow for decaying return values
            # because early points should be punished less severely since more
            # possible outcomes from that position
        pass

    def _weights_modifier(self, other_agent_score):
        MAX_SCORE = 121
        wm_scaling_factor = WEIGHTS_MODIFIER_SCALING_FACTOR
        diff = min(self.score, MAX_SCORE) - min(other_agent_score, MAX_SCORE)
        return diff / MAX_SCORE # scale to percentage of points in a game
        #question for later: 120 or 121?

    def save_weights_str(self):
        header_ln = 'my_score opp_score dealer ' + ' '.join(self._strat_names) + '\n'
        ret = '\n'.join(
                [
                        (
                            (('%d %d %d ' % (m,o,d)) + \
                                 ' '.join(
                                        [str(w) for w in self.weights[m][o][d]]
                                        )
                                 ) if self.weights[m][o][d] is not None
                                        else ''
                        )
                        for m in range(len(self.weights))
                    for o in range(len(self.weights[m]))
                for d in [0,1]
                ]
            ).strip()
        #ret = filter(lambda line: not re.match(r'^\s*$', line), ret)
        ret = sub(r'(\n){2,}', '\n', ret)
        return header_ln + ret

    def record_pegging_round(self, gained, given):
        PD('entering', 'SmartCribbageAgent.record_pegging_round')
        input_PlayedHandRecord(self.hand, gained, given)
        PD('exiting', 'SmartCribbageAgent.record_pegging_round')

def normalize(vector):
    return list(sknorm([vector], norm='l1')[0])

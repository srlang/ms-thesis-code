#!/usr/bin/env python

# Sean R. Lang <sean.lang@cs.helsinki.fi>

from copy       import deepcopy


#from config     import STRATEGIES, STRATEGY_WEIGHTS

from cribbage   import score_hand, hand_values, card_value, GoException

from strategy3  import hand_evaluator
STRATEGIES = []
STRATEGY_WEIGHTS = []

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

class SmartCribbageAgent(CribbageAgent):

    def __init__(self, strategies, strat_weights):
        self.strategies = strategies
        self.strategy_weights = strat_weights

    def _choose_cards(self):
        _METHOD = 'SmartCribbageAgent._choose_cards'
        # using self.cards[0:5]
        # TODO
        self.cards = sorted(self.cards)
        PD('sorted cards: %s' % str(self.cards), _METHOD)
        w,S = hand_evaluator(self.cards, self.strategies, self.strategy_weights)
        PD('w=%s' % str(w), _METHOD)
        PD('S=%s' % str(S), _METHOD)
        p = matmul(w,S)
        PD('P=%s' % str(p), _METHOD)
        # TODO
        pass


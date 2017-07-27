#!/usr/bin/env python

from copy import deepcopy

from cribbage import score_hand, hand_values, card_value

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

    def choose_cards(self):
        # tested
        keep, toss = self._choose_cards()
        self.hand = keep
        #self.game.add_to_crib(toss)
        self._peg_cards_left = deepcopy(self.hand)
        return keep, toss

    def _choose_cards(self):
        # default behavior: return (essentially) random 2 cards
        return deepcopy(self.cards[:4]), deepcopy(self.cards[-2:])

    def next_peg_card(self, cards_played):
        # tested
        if self.can_peg_more(cards_played):
            to_play = self._select_next_peg_card(cards_played)
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

    def _select_next_peg_card(self, cards_played):
        # default behavior: play random card
        return self._peg_cards_left[0]

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


class GoException(Exception):
    pass

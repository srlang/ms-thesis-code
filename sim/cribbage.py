#!/usr/bin/env python

from copy import deepcopy
from random import randint, sample

from utils import PD


def _list_comp(arr, func):
    ''' apply a function across a set of items '''
    return [func(x) for x in arr]

# scoring methods
#       Spades, Clubs, Hearts, Diamonds
SUITS = ['S', 'C', 'H', 'D']
NUMBER_SUITS = len(SUITS)
def card_suit(card):
    return card % NUMBER_SUITS

def hand_suits(hand):
    return _list_comp(hand, card_suit)

#           0    1    2    3    4    5    6    7    8    9     10   11   12
CLASSES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
JACK = 10
NUMBER_CLASSES = len(CLASSES)
def card_class(card):
    return card // NUMBER_SUITS

def hand_classes(hand):
    return _list_comp(hand, card_class)

def card_value(card):
    return min(1 + card_class(card), 10)

def hand_values(hand):
    return _list_comp(hand, card_value)

def score_hand(hand, cut_card=None, **kwargs):
    PD('entering: hand(%s), cut_card(%s)' % (hand,cut_card), 'score_hand')
    if cut_card is not None:
        hand = hand + [cut_card]
    PD('>> hand: %s' % str(hand), 'score_hand')
    return score_pairs(hand, **kwargs) + \
            score_runs(hand, **kwargs) + \
            score_fifteens(hand, **kwargs) + \
            score_nobs(hand, **kwargs) + \
            score_flush(hand, **kwargs)

def score_pairs(hand, **kwargs):
    ''' each unique pair of cards are awarded 2 points '''
    t_hand = hand_classes(hand)
    buckets = [0] * NUMBER_CLASSES
    total_pts = 0
    for t in t_hand:
        buckets[t] += 1
    for b in buckets:
        # 0 of a kind --> 0 pts  = 0*0
        # 1 of a kind --> 0 pts  = 1*0
        # 2 of a kind --> 2 pts  = 2*1
        # 3 of a kind --> 6 pts  = 3*2
        # 4 of a kind --> 12 pts = 4*3
        # 5 of a kind --> impossible, you cheater
        #total_pts += max(0, b-1) * b
        total_pts += (b-1) * b
    return total_pts

def score_runs(hand, **kwargs):
    '''
    each card in a run of 3 or more consecutive cards is awarded 1 point
    each
    '''
    t_hand = hand_classes(hand)
    buckets = [0] * NUMBER_CLASSES
    for t in t_hand:
        buckets[t] += 1

    total = 0
    i = 0
    while i < NUMBER_CLASSES - 2:
        if buckets[i] == 0:
            i += 1
            continue

        l = 0
        prod = 1
        # source of error #3: no index bounds on this loop
        while buckets[i] != 0:
            l += 1
            prod *= buckets[i]
            i += 1

        if l >= 3:
            total += l * prod

    return total

FIFTEENS_VALUE = 2
def score_fifteens(hand, **kwargs):
    '''
    determine how many combinations exist that add up to 15
    An algorithm worked out with a friend a few years ago the last time I
    wrote a cribbage scorer for a different project.
    Basic premise of the algorithm is similar to the matrix-creation algo
    that was discussed in the Design and Analysis of Algorithms course,
    except, since we don't care about how we got there, we keep it all in
    one list.
    Basically, we deal with an array A[0...15] in which A[i] can be
    interpreted as "the number of ways in which we can reach value i"
    Initially A = [1, 0, 0, 0,..., 0]. Then, for each card, we rotate the
    array right by the value of that card (filling the left side with 0s)
    and add to A.
    At the end A[15] will have the correct number of possible combinations
    in which a value of 15 can be found in the current hand.
    '''
    n = hand_values(hand)
    vals = [1] + [0] * 15   # for whatever bug exists, the last element
                            # never actually gets updated
                            # "cheat" and make 15 not the last element
                            # until I overcome my own stupidity and see
                            # what I did
    for v in n:
        #print('Shift: ' + str(v))
        #print('Vals Before: ' + str(vals))
        vals = _add_shift(vals, v)
        #print('Vals After:  ' + str(vals))
    return vals[15] * FIFTEENS_VALUE

def _add_shift(arr, shift):
    ''' rotate an array <arr> by <shift>, filling with 0s then add to <arr> '''
    for i in reversed(range(shift, len(arr))):
        arr[i] += arr[i-shift]
    return arr

def score_nobs(hand, **kwargs):
    '''
    Otherwise known as the right jack:
    determine if there is a jack in the player's hand that is the same suit
    as the cut card.
    '''
    typs = hand_classes(hand)
    i = 0
    ret = 0
    while i < 4 and ret == 0:
        ret = 1 if card_suit(hand[i]) == card_suit(hand[4]) \
                    and typs[i] == JACK\
                else 0
        i += 1
    return ret

def score_flush(hand, is_crib=False, **kwargs):
    '''
    A rule I didn't know until last semester.
    Like in poker, a flush is when all cards share the same suit.
    However, this needs not include the cut card, except when counting the
    crib.
    If all 4 cards of the hand are the same, 4 points are earned.
    If the cut card is additionally of the same suit, 5 points are earned.
    The only possible flush in the crib is the 5-card flush.
    '''
    suits = hand_suits(hand)
    A = [0] * len(suits)
    last_suit = suits[0]
    for i in range(1,len(A)):
        A[i] = A[i-1] + (1 if suits[i-1] == suits[i] else 0)
    if is_crib:
        return 5 if A[4] == 4 else 0
    else:
        return 1 + max(A[3],A[4]) if A[3] == 3 else 0

def score_peg(cards_played):
    score = 0
    summa = sum(hand_values(cards_played))
    sscore = 2 if summa == 15 or summa == 31 else 0
    score += sscore


    # pairs
    classes = hand_classes(reversed(cards_played))
    first_class = classes[0]
    pscore = 1
    for card in classes[1:]:
        if card == first_class:
            pscore += 1
        else:
            break
    pscore = pscore * (pscore - 1)
    score += pscore


    # runs
    # find longest sequence of run in the last cards played,
    # without repeating cards
    rscore = 0
    if len(cards_played) >= 3:
        buckets = [0] * NUMBER_CLASSES
        classes = hand_classes(reversed(cards_played))
        for card in classes:
            buckets[card] += 1
            if 2 in buckets:
                # double run possible to detect; not valid in rules
                break
            #tz = trim_zeros(buckets)
            if 0 not in _trim_zeros(buckets):
                # if we can remove leading and trailing zeros and have none left,
                #   we have a run
                bsum = sum(buckets)
                rscore = bsum if bsum >= 3 else 0
    score += rscore

    return score #, sscore, pscore, rscore

def _trim_zeros(arr):
    s = 0
    for i in arr:
        if i == 0:
            s += 1
        else:
            break

    e = 0
    for i in reversed(arr):
        if i == 0:
            e += 1
        else:
            break

    #ret = deepcopy(arr[s:len(arr)-e])
    ret = arr[s:len(arr)-e]
    return ret
    
def random_card():
    return randint(0, 51)

def _reset_pegging(cards_played):
    return 31 == sum(hand_values(cards_played))

class CribbageGame(object):

    def __init__(self, agent1, agent2=None):
        self.player1 = agent1
        if agent2:
            self.player2 = agent2
        else:
            self.player2 = None # TODO
        pass

    def play_full_game(self):
        # 'cut the deck' : determine who will start as dealer
        self.assign_dealer()
        # this condition check for backup safety
        while not self.game_finished:
            # deal each player cards
            self.deal_cards()

            # choose cards
            _,crib1 = self.dealer.choose_cards()
            _,crib2 = self.pone.choose_cards()
            crib = []
            crib.append(crib1)
            crib.append(crib2)
            self.dealer.crib = crib

            if card_class(self.cut_card) == JACK:
                self.dealer.score += 2
                if self.game_finished:
                    self._assign_winner()
                    break

            # go through the pegging phase
            self.peg()
            if self.game_finished:
                self._assign_winner()
                break

            # count final card values
            self.count_points()
            if self.game_finished:
                self._assign_winner()
                break

            # rotate positions
            self.rotate_dealer()

    def peg(self):
        # rule?: do you /have/ to go until 31 if given a go
        #   doesn't seem to be the case, it may be beneficial to keep
        # IS the case, see Rule 1.5 (e)

        player, observer = self.pone, self.dealer
        go = False
        cards_played = []
        cards_played_this_round = []
        last_31 = False

        PD("begin", "peg()")

        while self._cards_to_be_played and not self.game_finished:
            PD('begin loop with agent(%s)' % player._name, 'peg()')
            last_31 = False

            # let the player play his card
            try:
                # notable "issue": there is no checking for validity of card
                #   played here. agents are expected to determine valid cards
                #   themselves. technically, they can cheat if they don't check
                played_card = player.next_peg_card(cards_played_this_round, go=go)
                cards_played_this_round.append(played_card)
                cards_played.append(played_card)
                PD('>> Playing card [%d] for [%d] points' % (played_card, score_peg(cards_played_this_round)), 'peg()')
                player.score += score_peg(cards_played_this_round)
            except GoException:
                # dumby, how could you forget this after all these years?
                # Rule 1.5 (e) (2): player that calls "go" goes first next round
                if go:
                    PD('>> second go achieved, awarding points [%d]' % \
                            1 if not _reset_pegging(cards_played_this_round) else 0,\
                            'peg()')
                    player.score += 1 if not _reset_pegging(cards_played_this_round) else 0
                    # reset because we have reached the end of the round
                    cards_played_this_round = []
                    go = False
                else:
                    PD('>> first go achieved, passing play to other player', 'peg()')
                    PD('>> forcefully swapping here to ensure correct path', 'peg()')
                    player, observer = observer, player
                    go = True

            # swap who has the play, iff there is not a go
            if not go:
                PD('>> go == False, swapping players', 'peg()')
                player, observer = observer, player
            if _reset_pegging(cards_played_this_round):
                PD('>> reached end of peg round (31 pts)', 'peg()')
                cards_played_this_round = []
                last_31 = True
                pass

            PD('end loop', 'peg()')

        if not self.game_finished and not last_31:
            # Give the last card point to the final player
            # (which is at this point, thanks to the swap earlier, the observer)
            PD('game has finished, awarding last card point', 'peg()')
            observer.score += 1 # last card point

        PD('end', 'peg()')
        pass

    @property
    def _cards_to_be_played(self):
        return self.dealer.has_peg_cards_left() or self.pone.has_peg_cards_left()

    def count_points(self):
        self.pone.count_points(self.cut_card)
        if self.game_finished:
#            self.pone.is_winner = True
#            self.dealer.is_winner = False
            self._assign_winner()
            return
        self.dealer.count_points(self.cut_card)
        if self.game_finished:
            self._assign_winner()

    def _assign_winner(self):
        '''determine who is the winner of the game when it has finished'''
        if self.pone.score >= 121:
            self.pone.is_winner = True
            self.dealer.is_winner = False
        elif self.dealer.score >= 121:
            self.pone.is_winner =False
            self.dealer.is_winner = True
        else:
            pass

    def deal_cards(self):
        all_cards = sample(range(0,51), 13)
        self.dealer.hand = all_cards[0:6]
        self.pone.hand = all_cards[6:-1]
        self.cut_card = all_cards[-1]
        pass

    def cut_random_card(self):
        ''' keep this around in case needed later '''
        r = random_card()
        while (r in self.dealer.hand) or (r in self.pone.hand):
            r = random_card()
        self.cut_card = r

    @property
    def game_finished(self):
        return self.dealer.score >= 121 or self.pone.score >= 121

    def assign_dealer(self):
        if randint(1,100) % 2 == 0:
            self.dealer, self.pone = self.player1, self.player2
        else:
            self.dealer, self.pone = self.player2, self.player1
        self.rotate_dealer()

    def rotate_dealer(self):
        self.dealer, self.pone = self.pone, self.dealer
        self.dealer.is_dealer = True
        self.pone.is_dealer = False


class GoException(Exception):
    pass

# Sean R. Lang <sean.lang@cs.helsinki.fi>


from re         import sub

from agent      import CribbageAgent
from cribbage   import ctoh, ctoh_str, htoc, htoc_str, hand_values
from utils      import PD


class InteractiveCribbageAgent(CribbageAgent):

    '''
    Class to act as an agent with human interaction:
    I.e. it must prompt the user for decision input.
    This will be useful for testing the agent's performance manually against
    experienced players.
    '''

    def __init__(self):
        CribbageAgent.__init__(self)

    def _choose_cards(self, opponent_score, **kwargs):
        _METHOD = 'InteractiveCribbageAgent._choose_cards'
        try:
            self.hand = sorted(self.hand)
            print('Choose 4 cards to keep by entering them below (space separated) ')
            print('Score: (You) %d - %d (Opp)' % (self.score, opponent_score))
            print('You are ' + ('NOT ' if not self.is_dealer else '') + 'the dealer')
            print('Cards: %s' % ctoh_str(self.hand))
            #for i in range(len(self.hand)):
            #    print('%d: %s' % (i, ctoh(self.hand[i])))
            
            valid_input = False
            while not valid_input:
                raw = input('Choice >')
                PD('raw=%s' % raw, _METHOD)
                clean = sub(r'(\s){1,}',' ', raw.strip().upper())
                PD('clean=%s' % clean, _METHOD)
                try:
                    chosen_cards = htoc_str(clean)
                    PD('chosen_cards = %s' % str(chosen_cards), _METHOD)
                except Exception as e:
                    print('problem parsing: ' + str(e))
                    pass
                valid_input = len(chosen_cards) == 4 and all_unique(chosen_cards)
                PD('valid?=%s' % str(valid_input), _METHOD)
                if not valid_input:
                    print('Invalid choice, please choose again.')

            toss = [card for card in self.hand if card not in chosen_cards]
            return chosen_cards, toss
        except Exception as e:
            PD(str(e), _METHOD)

    def _select_next_valid_peg_card(self, cards_played, valid_cards):
        _METHOD = 'InteractiveCribbageAgent._select_next_valid_peg_card'
        PD('Entering', _METHOD)
        try:
            print('Your turn to play a peg card')
            print('Cards played this round: %s (total=%d)' %\
                    (ctoh_str(cards_played), sum(hand_values(cards_played))))
            print('Your Cards Left: %s' % ctoh_str(self._peg_cards_left))
            print('Valid Cards to play: %s' % ctoh_str(valid_cards))
            print('Please input your choice to play next')
            valid_input = False
            choice = -1
            while not valid_input:
                in_ = input('Choice >').strip().upper()
                try:
                    choice = htoc(in_)
                except Exception as e:
                    print('Problem parsing: ' + str(e))
                valid_input = choice in valid_cards
                if not valid_input:
                    print('Invalid choice, please choose again.')
            PD('Exiting choosing %d(%s)' % (choice, ctoh(choice)), _METHOD)
            return choice
        except Exception as e:
            PD('Exception: %s' % str(e), _METHOD)
            PD('Returning %d(%s) as default' % (valid_cards[0], ctoh(valid_cards[0])), _METHOD)
            return valid_cards[0]


def all_unique(cards):
    _METHOD = 'all_unique'
    PD('entering', _METHOD)
    ret = True
    for i in range(len(cards)-1):
        PD('> i = %d' % i, _METHOD)
        for j in range(i+1, len(cards)):
            PD('>> j = %d' % j, _METHOD)
            ret = ret and cards[i] != cards[j]
            PD('>>> card[%d] != card[%d]?: %s' % (i, j, str(cards[i] != cards[j])), _METHOD)
    PD('exiting with %s' % str(ret), _METHOD)
    return ret


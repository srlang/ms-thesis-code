from agent import normalize
from random import sample

from train import create_agent

if __name__ == '__main__':
    my_score = 10
    opp_score = 105
    dealer = True

    agent = create_agent('data/round2/g0/checkpoint_agent1_20180306-161355_000000999999.txt', 'agent')
    agent.score = my_score
    agent.is_dealer = dealer

    for i in range(10):
        cards = sample(range(52), 6)
        agent.hand = cards
        choice = agent.choose_cards(opponent_score=opp_score)
        print('cards: ' + str(cards))
        p = agent._tmp_p
        print(p)
        print(normalize(p))

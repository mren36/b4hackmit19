from eval7 import Card, Deck, evaluate

import random
from time import time
import json
import os, os.path

FOLD = 'FOLD'
CALL = 'CALL'
RAISE = 'RAISE'

ONGOING = 'ONGOING'
FOLDED = 'FOLDED'
SHOWDOWN = 'SHOWDOWN'

def to_str(card):
    return repr(card)[6:-2]

class Poker():
    # Money, cards, pot, and player_ids, to_go
    def __init__(self, players, dealer, blinds):
        self.players = players
        self.dealer = dealer
        self.reset_turn()
        self.deck = Deck()
        self.deck.shuffle()
        self.cards = { p: [] for p in self.players }
        self.min_raise = blinds[0]
        self.pot = { p: 0 for p in players }

        if blinds[0] > players[self.turn] or blinds[1] > players[self.dealer]:
            raise ValueError('Player(s) lack money to buy-in')
        self.pot[self.turn] += blinds[0]
        self.pot[self.dealer] += blinds[1]
        self.players[self.turn] -= blinds[0]
        self.players[self.dealer] -= blinds[1]

        self.cards[self.turn] = self.deck.deal(2)
        self.cards[self.dealer] = self.deck.deal(2)

        self.community = []
        
        self.change_turn() # Dealer goes first pre-flop

        self.done = ONGOING
        
        if not os.path.exists('logs'):
            os.makedirs('logs')
        self.logfile = open('logs/'+str(time())+'.log', 'w')
        self.log_state()
        

    def log_state(self):
        self.logfile.write(json.dumps(self.get_state())+'\n')
        
    def get_state(self):
        return (self.players,
            { p: [to_str(c) for c in cs] for p, cs in self.cards.items() },
            [to_str(c) for c in self.community],
            self.pot,
            self.turn,
            self.done)

    def reset_turn(self):
        self.turn = [p for p in self.players if p != self.dealer][0]
        self.action_completed = { p: False for p in self.players }

    def change_turn(self):
        self.turn = [p for p in self.players if p != self.turn][0]
    
    def step(self, action):
    
        # If ended, do no more
        if self.done != ONGOING: return self.get_state()
        
        # Deal with action if necessary 
        if action == FOLD:
            self.change_turn()
            self.players[self.turn] += sum(self.pot.values())
            self.pot = {}
            self.done = FOLDED
            self.turn = None
            self.log_state()
            return self.get_state()
        elif action == CALL:
            to_call = max(self.pot.values()) - self.pot[self.turn]
            self.pot[self.turn] += to_call
            self.players[self.turn] -= to_call
            self.action_completed[self.turn] = True
        elif action[0] == RAISE:
            raise_val = action[1]
            if raise_val < self.min_raise and raise_val < self.players[self.turn]:
                # ^ Allowed to bet below min-raise if going all-in
                raise ValueError('Raise too small')
                
            # Cap raise at all-in. Assumes pot never goes over max_pot
            max_pot = min([self.pot[p] + self.players[p] for p in self.players])
            raise_val = min(raise_val, max_pot-max(self.pot.values()))
            inc_amt = raise_val + max(self.pot.values()) - self.pot[self.turn]
            self.pot[self.turn] += inc_amt
            self.players[self.turn] -= inc_amt
            self.action_completed = { p: False for p in self.players }
            self.action_completed[self.turn] = True
        if sum([int(x) for x in self.action_completed.values()]) == len(self.players):
            # Go on
            if len(self.community) == 5:
                # Showdown
                scores = { p: evaluate(self.cards[p]+self.community) for p in self.players }
                winners = [p for p in self.players if scores[p] == max(scores.values())]
                for w in winners:
                    self.players[w] += sum(self.pot.values()) // len(winners)
                self.pot = {}
                self.done = SHOWDOWN
                self.turn = None
                self.log_state()
                return self.get_state()
            elif len(self.community) == 0:
                self.community.extend(self.deck.deal(3))
            else:
                self.community.extend(self.deck.deal(1))
            self.reset_turn()
        else:
            self.change_turn()
        self.log_state()
        return self.get_state()
        
        
if __name__ == '__main__':
    
    #random.seed(0)
    p = Poker({'a': 300, 'b': 200}, 'a', (5,2))
    print(p.get_state())
    print(p.step('CALL'))
    print(p.step('CALL'))
    print(p.step('CALL'))
    print(p.step('CALL'))
    print(p.step('CALL'))
    print(p.step('CALL'))
    print(p.step('CALL'))
    print(p.step('CALL'))
    print(p.step('CALL'))
    """
    hand1 = [Card(2, 1), Card(2, 2)]
    hand2 = [Card(11, 4), Card(12, 4)]
    
    community = [Card(3, 3), Card(10, 2), Card(9, 3), Card(6, 1), Card(8, 1)]
    
    print(HandEvaluator.evaluate_hand(hand1, community))
    print(HandEvaluator.evaluate_hand(hand2, community))
    
    print(hand1)
    print(hand2)
    print(community)
    """
    

from eval7 import Card, Deck, evaluate

import random
import json
import os, os.path

from time import time
from collections import namedtuple

FOLD = 'FOLD'
CALL = 'CALL'
RAISE = 'RAISE'

ONGOING = 'ONGOING'
FOLDED = 'FOLDED'
SHOWDOWN = 'SHOWDOWN'

def to_str(card):
    return repr(card)[6:-2]

Player = collections.namedtuple('Player', ['stack', 'pot', 'is_in', 'cards', 'name', 'acted'])

def Table():
    def __init__(self, table_size=9):
        self.table_size = table_size
        self.name_to_pos = {}
        self.pos_to_player = {}

    def new_player(self, pos, name, stack):
        if pos in self.pos_to_stack:
            raise ValueError('Position already filled')
        
        self.name_to_pos[name] = pos
        self.pos_to_player[pos] = Player(stack, 0, False, None, name)
    
    def reset_action(self):
        for pos in self.pos_to_player:
            self.pos_to_player[pos].acted = False

    def new_game(self):
        self.reset_action()
        for k in self.pos_to_in:
            self.pos_to_player[k].is_in = True
            if self.pos_to_player[k].pot != 0:
                raise ValueError('Money being left in the pot')

    def next_pos(self, pos=-1):
        cpos = (pos + 1) % table_size
        while cpos != pos:
            if pos in self.pos_to_player and self.pos_to_player[cpos].is_in:
                return cpos
            cpos = (cpos + 1) % table_size
        raise ValueError('Only one person in')

    def num_players_in(self):
        return sum(1 for pl in self.pos_to_player if pl.is_in)

    def num_players_total(self):
        return len(self.pos_to_player)

    def players_in(self):
        return (pl for pl in self.pos_to_player if pl.is_in)

    def open_seats(self):
        return {k for k in range(0, self.table_size) if k not in self.pos_to_player}

    def get_player(self, pos):
        return self.pos_to_player[pos]

    def get_player_w_name(self, name):
        return self.pos_to_player[self.name_to_pos[name]]

    def remove_player(self, pos):
        name = next(n for n, p in self.name_to_pos.items() if p == pos)
        del self.name_to_pos[name]
        del self.pos_to_player[p]

    def remove_player_w_name(self, name):
        pos = self.name_to_pos[name]
        del self.name_to_pos[name]
        del self.pos_to_player[p]

    def get_players_card_private(self, player_asking):
        player_map = copy.deepcopy(self.pos_to_player)
        for pos in player_map:
            if player_map[pos].name != player_asking:
                player_map[pos].card = None
        return player_map


class Poker():
    # Money, cards, pot, and player_ids, to_go
    def __init__(self, blinds):
        ''' Players = map of name to stacks
        dealer = name of dealer
        blinds = (SMALL_BLIND, BIG_BLIND)
        '''
        self.table = Table()
        self.blinds = blinds
        self.ongoing = False
        self.pot = 0
        self.smallblind = -1
        self.community = []

    def _new_hand(self):
        self.smallblind = self.table.next_pos(self.smallblind)
        self.bigblind = self.table.next_pos(self.smallblind)
        self.turn_pos = self.table.next_pos(self.bigblind)

        self.pot += self.blinds[0] + self.blinds[1]
        
        sb = self.table.get_player(self.smallblind)
        sb.stack -= self.blinds[0]
        sb.pot += self.blinds[0]

        bb = self.table.get_player(self.bigblind)
        bb.stack -= self.blinds[1]
        bb.pot += self.blinds[1]

        self.community = []

        self.new_game()

    def new_player(self, name, pos):
        self.table.new_player(name, pos, 5000)
        if self.table.num_players_total >= 2:
            self.ongoing = True 
            self._new_hand()

    def get_state(self, player_asking):
        ''' Returns:
            player stacks, map of 
        '''
        return {'seats': self.table.open_seats(),
            'turn': self.table.get_player(self.turn_pos).name,
            'players': self.table.get_players_card_private(player_asking),
            'pot': self.pot,
            'community': self.community
            }    

    def _end_stage(self):
        # Collect pot. Reset action
        for pos, pl in self.table.pos_to_player:
            self.pot += pl.pot
            pl.pot = 0
            pl.action_completed = False

    def _end_hand_after_fold(self):
        winning_pos = self.table.next_pos()
        self.table.get_player(winning_pos).stack += self.pot
        for pos, pl in self.table.pos_to_player:
            self.table.get_player(winning_pos).stack += pl.pot
            pl.pot = 0

    def _move_turn_marker(self):
        self.turn_pos = self.table.next_pos(self.turn_pos)

    def _is_one_left(self):
        return self.table.num_players_total() < 2

    def _has_everyone_gone(self):
        return sum([int(pl.acted) for pl in self.table.players_in()]) == len(self.table.num_players_in())

    # TODO: add logic for when everyone has completed action
    def step(self, acting_player_name, action_type, action_amount=-1):
        if not self.ongoing:
            raise ValueError('Game does not have enough players')

        if self.table.get_player(self.turn_pos).name != acting_player_name:
            raise ValueError('Not %s\'s turn!' % acting_player_name)

        # Deal with action if necessary 
        cur_player = self.table.get_player(self.turn_pos)
        if action_type == FOLD:
            cur_player.is_in = False
        elif action_type == CALL:
            to_call = max((pl.pot for pl in self.table.players_in())) - cur_player.pot
            cur_player.pot += to_call
            cur_player.stack -= to_call
            cur_player.acted = True
        elif action_type == RAISE:
            raise_val = action_amount
            if raise_val < self.min_raise and raise_val < cur_player.stack:
                # ^ Allowed to bet below min-raise if going all-in
                raise ValueError('Raise too small')
                
            # Cap raise at all-in. Assumes pot never goes over max_pot
            max_pot = min([self.pot[p] + self.players[p] for p in self.players])
            raise_val = min(raise_val, max_pot-max(self.pot.values()))
            inc_amt = raise_val + max(self.pot.values()) - self.pot[self.turn]
            cur_player.pot += inc_amt
            cur_player.stack -= inc_amt
            self.table.reset_action()
            cur_player.acted = True

        self._move_turn_marker()
        if self._is_one_left():
            self._end_hand_after_fold()
        elif self._has_everyone_gone():
            self._end_stage()
            if len(self.community) == 5:
                # Showdown
                players_in = self.table.players_in() 
                scores = { pl.name: evaluate(pl.cards+self.community) for pl in players_in}
                winners = [pl.name for pl in players_in if scores[pl.name] == max(scores.values())]
                for w in winners:
                    self.table.get_player_w_name(w) += self.pot // len(winners)
            elif len(self.community) == 0:
                self.community.extend(self.deck.deal(3))
            else:
                self.community.extend(self.deck.deal(1))
        
        
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
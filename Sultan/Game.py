from .Action import GameAction
from .Player import Player
from .State import State
from .Character import Character, CHARACTER_COUNT_DICTIONARY

import numpy as np

class SultanGame:

    def __init__(self, debug=False):
        self.debug = debug
        self.reset()

    def check_state(self, state):
        return self.state == state

    def set_state(self, state):
        self.state = state
        self.admin_mode = True

    def reset(self):
        self.state = State.IDLE

        self.msg_id = {}
        self.players = {}
        
        self.last_switch_pair = (0, 0)
        self.current_player_index = -1

        self.winner = None
        self.crown_token = None
        self.sultan_id = None

    def start_game(self):
        self.players[0] = Player(user_id=0, user_name='白板', spare=True, debug=self.debug)
        self.player_orders = [ user_id for user_id in self.players if user_id != 0 ]
        np.random.shuffle(self.player_orders)

        self.original_player_orders = self.player_orders.copy() + [0]

        for i, user_id in enumerate(self.player_orders):
            self.players[user_id].order = i
        
        character_count_ref = CHARACTER_COUNT_DICTIONARY[len(self.players)-1]
        tmp = []
        for character in character_count_ref:
            for _ in range(character_count_ref[character]):
                tmp.append(character)

        np.random.shuffle(tmp)
        admin_character = None #Character.SULTAN

        if admin_character is not None:
            self.players[1422967494].character = admin_character
            tmp.remove(admin_character)

        i = 0
        for _, (user_id, player) in enumerate(self.players.items()):
            if user_id != 1422967494 or admin_character is None:
                player.character = tmp[i]
                i += 1

        self.turn_id = 0
        self.current_player_index = 0

    def check_win_condition(self, only_revolution=False):
        ### Revolution
        for p in self.player_orders:
            if self.players[p].is_free_slave():
                neighbors = self.get_neighbors(p)
                if len(neighbors) == 2 \
                and self.players[neighbors[0]].is_free_slave() \
                and self.players[neighbors[1]].is_free_slave():
                    self.winner = 'rebel'
                    self.win_condition = '革命成功'
                    return True
        if only_revolution:
            return False

        ### Sultan
        if self.current_player().throne_countdown == 0:
            if self.sultan_id is not None and self.players[self.sultan_id].can_throne():
                self.winner = 'loyal'
                self.win_condition = '蘇丹登基'
                return True
            else:
                self.current_player().throne_countdown = None
        
        ### Assassination
        if self.sultan_id is not None and self.players[self.sultan_id].is_dead():
            self.winner = 'rebel'
            self.win_condition = '蘇丹已死'
            return True
        return False

    def next_player(self):
        self.turn_id += 1
        self.current_player_index = (self.current_player_index + 1) % len(self.player_orders)

    def current_player(self):
        user_id = self.player_orders[self.current_player_index]
        return self.players[user_id]

    def get_player_information(self, user_id, game_over=False):
        ret = []
        if game_over:
            for target_id in self.original_player_orders:
                ret.append(
                    f'{self.players[target_id].status(verbose=True)}')

        else:
            for target_id in self.player_orders:
                ret.append(
                    f'{self.players[target_id].status(verbose=user_id == target_id)}')
            for target_id in self.players:
                if target_id not in self.player_orders and target_id != 0:
                    ret.append(
                        f'{self.players[target_id].status(verbose=user_id == target_id)}')
        return ret

    def get_neighbors(self, user_id):
        user_order = self.players[user_id].order
        neighbor_order_1 = (user_order + 1) % len(self.player_orders)
        neighbor_order_2 = (user_order - 1) % len(self.player_orders)

        neighbors = [
            self.player_orders[neighbor_order_1],
            self.player_orders[neighbor_order_2]
        ]
        neighbors = list(set(neighbors))

        return neighbors

    def add_player(self, user_id=None, user_name=None, ai=False):
        if ai:
            player = Player(ai=True, debug=self.debug)
            user_id = player.user_id
        else:
            player = Player(user_id, user_name, debug=self.debug)
        self.players[user_id] = player

    def remove_player(self, user_id=None, ai=False):
        if ai:
            for i in self.players:
                if i < 0:
                    user_id = i
        if user_id is not None:
            del self.players[user_id]

    def print_players_list(self):
        return ', '.join([self.players[p].user_name.strip() for p in self.players if p != 0])

    def legal_actions(self):
        legal_actions = [
            GameAction.PEEK,
            GameAction.SWITCH
        ]

        if self.current_player().is_hidden():
            legal_actions.append(GameAction.REVEAL)
        else:
            if self.current_player().character == Character.SULTAN:
                legal_actions.append(GameAction.EXECUTE)
            elif self.current_player().character == Character.GUARD:
                legal_actions.append(GameAction.DETAIN)
            elif self.current_player().character == Character.ASSASSIN:
                legal_actions.append(GameAction.ASSASSINATE)
            elif self.current_player().character == Character.SLAVE:
                legal_actions.append(GameAction.CALL)

        # legal_actions.append(GameAction.THRONE)

        return legal_actions

    def can_be_peek_by(self, user_id):
        choices = []
        for target_id in [0] + self.player_orders:
            target_player = self.players[target_id]
            if target_player.can_be_peek_by(user_id):
                choices.append(target_id)
        return choices

    def can_be_switch_by(self, user_id, hide=True):
        choices = []
        for target_id in [0] + self.player_orders:
            target_player = self.players[target_id]
            if target_player.can_be_switch_by(user_id, hide=hide) \
            and (target_id, user_id) != self.last_switch_pair:
                choices.append(target_id)
        return choices

    def can_be_execute_by(self, user_id):
        choices = []
        for target_id in self.player_orders:
            target_player = self.players[target_id]
            if user_id != target_id \
            and target_player.can_be_execute():
                choices.append(target_id)
        return choices

    def can_be_detain_by(self, user_id):
        choices = []
        for target_id in self.player_orders:
            target_player = self.players[target_id]
            if user_id != target_id \
            and target_player.can_be_detain():
                choices.append(target_id)
        return choices

    def can_be_assassinate_by(self, user_id):
        choices = []
        for target_id in self.player_orders:
            target_player = self.players[target_id]
            if user_id != target_id \
            and target_player.can_be_assassinate():
                choices.append(target_id)
        return choices

    def do_switch(self, player_1_id, player_2_id):
        if player_1_id != player_2_id:
            player_1 = self.players[player_1_id]
            player_2 = self.players[player_2_id]
            player_1.character, player_2.character = \
                player_2.character, player_1.character
            self.last_switch_pair = (player_1_id, player_2_id)

    def do_kill(self, user_id):
        if user_id not in self.player_orders:
            raise
        cur_id = self.current_player().user_id
        
        self.players[user_id].alive = False
        self.players[user_id].jail = False

        self.player_orders = [ p \
            for p in self.player_orders if p != user_id]

        for i, target_id in enumerate(self.player_orders):
            self.players[target_id].order = i
        self.current_player_index = self.players[cur_id].order

    def do_prison(self, user_id):
        if user_id not in self.player_orders:
            raise       
        self.players[user_id].jail = True

    def do_hide(self, user_id):
        self.players[user_id].hidden = True
        if self.players[user_id].is_sultan():
            for _, player in self.players.items():
                player.throne_countdown = None


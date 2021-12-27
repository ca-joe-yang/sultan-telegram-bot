from .Action import GameAction
from .Player import Player
from .State import State
from .Character import Character, CHARACTER_COUNT_DICTIONARY

import numpy as np

class SultanGame:

    def __init__(self, chat_id, admin_id, admin_name):

        # self.game_id = -1
        self.chat_id = chat_id
        self.admin_id = admin_id
        self.admin_name = admin_name

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
        
        self.last_swicth_pair = (0, 0)
        self.current_player_index = -1

        self.winner = None
        self.crown_token = None
        self.sultan = None

    def start_game(self):
        self.players[0] = Player(user_id=0, user_name='白板', spare=True)
        self.player_order = [ user_id for user_id in self.players if user_id != 0 ]
        np.random.shuffle(self.player_order)

        count = 0
        for i, user_id in enumerate(self.player_order):
            count += 1
            self.players[user_id].order = count
        
        character_count_ref = CHARACTER_COUNT_DICTIONARY[len(self.players)-1]
        tmp = []
        for character in character_count_ref:
            for _ in range(character_count_ref[character]):
                tmp.append(character)

        np.random.shuffle(tmp)
        for i, (user_id, player) in enumerate(self.players.items()):
            player.character = tmp[i]

        self.next_player()

    def dead_player(self, user_id):
        count = 0
        for i, user_id in enumerate(self.player_order):
            if self.players[user_id].is_alive():
                count += 1
                self.players[user_id].order = count

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.player_order)
        if self.crown_token == self.current_player().user_id:
            if self.players[self.sultan].can_throne():
                self.winner = 'loyal'
                return
            else:
                self.crown_token = None
                pass
        if self.current_player().is_jail():
            self.current_player().jail = False
            self.next_player()
        elif self.current_player().is_dead():
            self.next_player()

    def current_player(self):
        user_id = self.player_order[self.current_player_index]
        return self.players[user_id]

    def neighbor(self, user_id, call=False):
        order = self.player_order.index(user_id)

        ret_ids = []
        tmp = order
        for i in range(len(self.player_order)-1):
            tmp = (tmp + 1) % len(self.player_order)
            tmp_id = self.player_order[tmp]
            if self.players[tmp_id].is_alive() and self.players[tmp_id].is_free():
                ret_ids.append(tmp_id)
                break
        
        tmp = order
        for i in range(len(self.player_order)-1):
            tmp = (tmp_id - 1) % len(self.player_order)
            tmp_id = self.player_order[tmp]
            if self.players[tmp_id].is_alive() and self.players[tmp_id].is_free():
                ret_ids.append(tmp_id)
                break

        ret_ids = set(ret_ids)
        if call:
            ret_ids.add(user_id)
        elif user_id in ret_ids:
            ret_ids.remove(user_id)
        # ret_ids = list(ret_ids)
        return ret_ids


    def legal_player(self, action, player_id):
        if action in [GameAction.PEEK, GameAction.SWITCH, GameAction.REVEAL, GameAction.HIDE]:
            if self.admin_mode and player_id == self.admin_id:
                return True
            return player_id == self.current_player().user_id
        elif action in [GameAction.CHECK]:
            if player_id in self.players:
                return True
        elif action == GameAction.EXECUTE:
            if (self.admin_mode and player_id == self.admin_id) or player_id == self.current_player().user_id:
                return self.current_player().character == Character.SULTAN

        elif action == GameAction.DETAIN:
            if (self.admin_mode and player_id == self.admin_id) or player_id == self.current_player().user_id:
                return self.current_player().character == Character.GUARD

        elif action == GameAction.AVOID_DETAIN:
            if (self.admin_mode and player_id == self.admin_id) or player_id == self.detain_id_pair[1]:
                return True

        elif action == GameAction.ASSASSINATE:
            if (self.admin_mode and player_id == self.admin_id) or player_id == self.current_player().user_id:
                return self.current_player().character == Character.ASSASSIN

        elif action == GameAction.STOP_ASSASSINATE:
            if player_id in self.assassinate_event['protector']:
                return True

        elif action == GameAction.CALL:
            return self.players[player_id].character == Character.SLAVE

        elif action == GameAction.JOIN:
            if player_id in self.revolution_event['called']:
                return True

        return False


    def get_random_user_id_for_ai(self):
        user_id = -1
        while user_id in self.players:
            user_id = user_id - 1
        return user_id

    def add_player(self, user_id=None, user_name=None, ai=False):
        if ai == True:
            user_id = self.get_random_user_id_for_ai()
            user_name = f'電腦{-user_id}'
        self.players[user_id] = Player(user_id, user_name)

    def remove_player(self, user_id=None, ai=False):
        if ai == True:
            for old_user_id in self.players:
                if old_user_id < 0:
                    user_id = old_user_id
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
            legal_actions.append(GameAction.HIDE)
            if self.current_player().character == Character.SULTAN:
                legal_actions.append(GameAction.EXECUTE)
            elif self.current_player().character == Character.GUARD:
                legal_actions.append(GameAction.DETAIN)
            elif self.current_player().character == Character.ASSASSIN:
                legal_actions.append(GameAction.ASSASSINATE)
            # elif self.players[self.current_player].character == Character.SLAVE:
            #     legal_actions.append(GameAction.CALL)

        legal_actions.append(GameAction.CALL)

        return legal_actions


    def switch_character(self, player_1, player_2):
        tmp = self.players[player_1].character
        self.players[player_1].character = self.players[player_2].character
        self.players[player_2].character = tmp
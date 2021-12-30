from .Action import GameAction
from .Player import Player
from .State import State
from .Character import Character, CHARACTER_COUNT_DICTIONARY, NEUTRAL_CHARACTERS

import numpy as np
import random
from PIL import Image, ImageDraw, ImageFont

DRAW_CONFIG = {
    6: [
        (0.15, 0.50),
        (0.20, 0.65),
        (0.75, 0.65),
        (0.80, 0.50),
        (0.75, 0.35),
        (0.20, 0.55)
    ],
    8: [
        (0.25, 0.50),
        (0.25, 0.75),
        (0.50, 0.75),
        (0.75, 0.75),
        (0.75, 0.50),
        (0.75, 0.25),
        (0.50, 0.25),
        (0.25, 0.25),
    ],
    10: [
        (0.25, 0.20), (0.25, 0.40), (0.25, 0.60), (0.25, 0.80),
        (0.50, 0.80),
        (0.75, 0.80), (0.75, 0.60), (0.75, 0.40), (0.75, 0.20),
        (0.50, 0.20),
    ],
    12: [
        (0.25, 0.50),
        (0.25, 0.68),
        (0.25, 0.86),
        (0.50, 0.86),
        (0.75, 0.86),
        (0.75, 0.68),
        (0.75, 0.50),
        (0.75, 0.32),
        (0.75, 0.14),
        (0.50, 0.14),
        (0.25, 0.14),
        (0.25, 0.32),
    ]
}

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

        self.image_H = 500
        self.image_W = 750
        self.game_image = Image.new("RGB", 
                (self.image_W, self.image_H), (255, 255, 255))

    def draw_game_image(self):
        N = len(self.original_player_orders) - 1
        fontsize = int(self.image_H / 25)
        font = ImageFont.truetype('TaipeiSansTCBeta-Bold.ttf', fontsize)
        font2 = ImageFont.truetype('TaipeiSansTCBeta-Bold.ttf', self.image_H//8)
        game_draw = ImageDraw.Draw(self.game_image)
        for i, player_id in enumerate(self.original_player_orders[:-1]):
            player = self.players[player_id]
            player_img = player.profile_photo

            player_y = int(
                DRAW_CONFIG[N][i][0] * self.image_H - 0.5 * player.image_H)
            player_x = int(
                DRAW_CONFIG[N][i][1] * self.image_W - 0.5 * player.image_W)
            self.game_image.paste(player_img, (player_x, player_y))
            
            if player.is_dead():
                game_draw.line(
                    [(player_x, player_y), (player_x+player.image_W, player_y+player.image_H)], 
                    fill="red", width=30) 
                game_draw.line(
                    [(player_x+player.image_W, player_y), (player_x, player_y+player.image_H)], 
                    fill="red", width=30)
            elif player.is_captured() or player.is_jail():
                game_draw.line(
                    [(player_x, player_y), (player_x+player.image_W, player_y+player.image_H)], 
                    fill="black", width=30) 
                game_draw.line(
                    [(player_x+player.image_W, player_y), (player_x, player_y+player.image_H)], 
                    fill="black", width=30) 
            if player.is_known():
                game_draw.text((int(player_x), int(player_y)), player.character.abbr(), 
                    font=font2, 
                    stroke_width=int(self.image_H/8/20), stroke_fill=(0,0,0))

            text_x = player_x #+ 0.5 * player.image_W
            text_y = player_y + player.image_H #- fontsize*(line_num-i)
            sw, sh = 0, 0#game_draw.textsize(player.user_name)
            game_draw.text((int(text_x-sw/2), int(text_y)), player.user_name, 
                    font=font, align ="center", 
                    stroke_width=int(fontsize/20), stroke_fill=(0,0,0))

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
        n_neutral = len(self.players) - len(tmp)
        assert(n_neutral < 4)
        for character in random.sample(NEUTRAL_CHARACTERS, n_neutral):
            tmp.append(character)

        np.random.shuffle(tmp)

        for i, (user_id, player) in enumerate(self.players.items()):
            player.character = tmp[i]

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
        
            ret.append(f'[備忘錄] {self.players[user_id].memo}')
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

    def add_player(self, user_id=None, user_name=None, profile_photo=None, 
            ai=False):
        if ai:
            player = Player(ai=True, debug=self.debug)
            user_id = player.user_id
        else:
            player = Player(user_id, user_name, profile_photo=profile_photo, debug=self.debug)
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

    def can_be_capture_by(self, user_id):
        choices = []
        for target_id in self.player_orders:
            target_player = self.players[target_id]
            if user_id != target_id \
            and target_player.can_be_capture():
                choices.append(target_id)
        return choices

    def can_be_manipulate_by(self, user_id):
        choices = []
        for target_id in self.player_orders:
            target_player = self.players[target_id]
            if user_id != target_id \
            and target_player.can_be_manipulate():
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
        cur_id = self.current_player().user_id
        dead_player = self.players[user_id]
        
        dead_player.alive = False
        dead_player.jail = False

        if dead_player.captured_by is not None:
            self.players[dead_player.captured_by].capture_slaves.remove(user_id)
            dead_player.captured_by = False

        self.do_release_slaves(user_id)

        self.player_orders = [ p \
            for p in self.player_orders if p != user_id]

        for i, target_id in enumerate(self.player_orders):
            self.players[target_id].order = i
        self.current_player_index = self.players[cur_id].order

    def do_release_slaves(self, user_id):
        player = self.players[user_id]
        if player.character == Character.SLAVEDRIVER:
            for target_id in player.capture_slaves:
                self.players[target_id].captured_by = None
            player.capture_slaves = []

    def do_jail(self, user_id):
        self.players[user_id].jail = True

    def do_capture(self, source_id, target_id):
        self.players[source_id].capture_slaves.append(target_id)
        self.players[target_id].captured_by = source_id

    def do_free(self, user_id):
        self.players[user_id].jail = False
        self.players[user_id].captured = None

    def do_hide(self, user_id):
        self.do_release_slaves(user_id)
        if self.players[user_id].is_sultan():
            for _, player in self.players.items():
                player.throne_countdown = None
        self.players[user_id].hidden = True
        


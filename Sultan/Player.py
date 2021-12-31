from .Character import Character
from .Action import GameAction as Action
import random

from PIL import Image, ImageDraw, ImageFont
from .draw_utils import *

AI_COUNT = 0

class Player:

    def __init__(self, user_id=None, user_name=None, profile_photo=None,
        spare=False, ai=False, debug=False, h=100, w=100):

        if ai:
            global AI_COUNT
            AI_COUNT += 1
            self.user_id = -AI_COUNT
            if user_name is None:
                user_name = f'電腦{AI_COUNT}'
            self.user_name = user_name
            self.ai = True
        else:
            self.user_id = user_id
            self.user_name = ''.join(user_name.split())
            self.ai = False
        
        self.throne_countdown = None

        self.must_switch = False

        self.hidden = True
        self.alive = True
        self.character = None
        self.jail = False
        self.captured = False
        self.order = None
        self.exhaust = False

        self.next_action = None

        self.spare = spare
        if spare:
            self.hidden = True

        self.debug = debug

        self.capture_slaves = []
        self.captured_by = None

        self.image_H = h
        self.image_W = w
        if profile_photo is None:
            self.profile_photo = Image.new("RGB", 
                (self.image_W, self.image_H), (127, 127, 127))
        else:
            self.profile_photo = profile_photo
        self.profile_photo = self.profile_photo.resize(
            [self.image_W, self.image_H])
        self.memo = ''

    def status(self, verbose=False):
        status_str = ''

        if self.is_dead():
            status_str += '[歿]'
        elif self.is_jail():
            status_str += '[牢]'
        elif self.is_captured():
            status_str += '[捕]'
        
        if self.is_hidden():
            status_str += '[私]'
        elif self.is_not_hidden():
            status_str += '[公]'

        if self.is_not_hidden() or verbose:
            status_str += f'<{self.character}>'

        user_name = f'{self.user_name} {status_str}'
        if self.is_spare():
            user_name = f'(0) {user_name}'
        elif self.is_alive():
            user_name = f'({self.order+1}) {user_name}'

        return user_name

    def draw_player_image(self, fontsize=10, game_over=False, win=False):
        canvas = self.profile_photo.copy()
        player_draw = ImageDraw.Draw(canvas)
        font = ImageFont.truetype('TaipeiSansTCBeta-Bold.ttf', fontsize)

        if self.is_dead():
            draw_cross(player_draw, 
                x=0, y=0, w=self.image_W, h=self.image_H)
                
        elif self.is_captured() or self.is_jail():
            draw_prison(player_draw, 
                x=0, y=0, w=self.image_W, h=self.image_H)

        if self.is_known():
            player_draw.text((0, 0), self.character.abbr(), 
                font=font, 
                stroke_width=int(fontsize/20), stroke_fill=(0,0,0))
        elif game_over:
            player_draw.text((0, 0), self.character.abbr(), 
                font=font, fill='black',
                stroke_width=int(fontsize/20), stroke_fill=(255,255,255))

        if game_over and win:
            draw_border(player_draw, 
                x=0, y=0, w=self.image_W, h=self.image_H,
                fill='green', width=10)

        return canvas

    def action_choices(self, just_reveal=False, manipulate=False):
        if self.must_switch:
            return [Action.SWITCH]

        actions = []
        if not just_reveal and not manipulate:
            actions.append(Action.PEEK)
            actions.append(Action.SWITCH)

        if self.is_hidden():
            actions.append(Action.REVEAL)
        elif manipulate or not self.is_exhaust():
            if self.character == Character.SULTAN:
                actions.append(Action.EXECUTE)
            elif self.character == Character.GUARD:
                actions.append(Action.DETAIN)
            elif self.character == Character.ASSASSIN:
                actions.append(Action.ASSASSINATE)
            elif self.character == Character.SLAVE:
                actions.append(Action.CALL)
            elif self.character == Character.SLAVEDRIVER:
                actions.append(Action.CAPTURE)
            elif self.character == Character.VIZIER:
                actions.append(Action.MANIPULATE)
            elif self.character == Character.DANCER:
                actions.append(Action.DANCE)
            elif self.character == Character.PROPHET:
                actions.append(Action.PREDICT)

        return actions

    def is_winner(self, win, game=None):
        if self.is_spare():
            return False
        if self.is_dead():
            return False
        if self.character == Character.VIZIER:
            if self.is_hidden():
                for neighbor_id in game.get_neighbors(self.user_id):
                    if game.players[neighbor_id].is_winner(win):
                        return True
                return False
            else:
                if hasattr(game, 'manipulate_event'):
                    return game.manipulate_event['support_team'] == win
            return False
        
        if self.character == Character.PROPHET:
            if self.is_hidden():
                return False
            if hasattr(game, 'predict_event'):
                return game.predict_event['predict_team'] == win
            return False

        if win == 'loyal':
            if self.character == Character.SLAVEDRIVER:
                return self.is_known()
            elif self.character == Character.DANCER:
                return self.is_hidden()

            return self.is_loyal()
        elif win == 'rebel':
            if self.character == Character.SLAVEDRIVER:
                return self.is_hidden()
            elif self.character == Character.DANCER:
                return self.is_known()
            return self.is_rebel()
        else:
            raise

    def is_ai(self):
        return self.ai

    def is_alive(self):
        return self.alive

    def is_hidden(self):
        return self.hidden

    def is_spare(self):
        return self.spare

    def is_known(self):
        return not self.is_hidden()

    def is_not_hidden(self):
        return not self.hidden

    def is_not_spare(self):
        return not self.spare

    def is_free(self):
        return not self.is_jail() and not self.is_captured()

    def is_not_free(self):
        return not self.is_free()

    def is_jail(self):
        return self.jail

    def is_captured(self):
        return self.captured_by is not None

    def is_dead(self):
        return not self.alive

    def is_rebel(self):
        return self.character in [Character.ASSASSIN, Character.SLAVE]

    def is_loyal(self):
        return self.character in [Character.SULTAN, Character.GUARD]

    def is_sultan(self):
        return self.character == Character.SULTAN

    def is_slave(self):
        return self.character == Character.SLAVE

    def is_dancing(self):
        return self.character == Character.DANCER \
            and self.is_not_hidden() and self.is_alive() and self.is_free()
    
    def is_exhaust(self):
        return self.exhaust

    def is_free_slave(self):
        return self.character == Character.SLAVE \
            and self.is_not_hidden() and self.is_alive() and self.is_free()

    def is_neutral(self):
        return not self.is_rebel() and not self.is_loyal()

    def neighbor_is_dancing(self, game):
        for i in game.get_neighbors(self.user_id):
            if game.players[i].is_dancing():
                return True
        return False

    def can_be_peek_by(self, user_id):
        return self.user_id != user_id and self.is_alive() and self.is_hidden()

    def can_be_switch_by(self, user_id, hide=False):
        if hide:
            return self.user_id == user_id or (self.is_alive() and self.is_hidden())
        else:
            return self.user_id != user_id and self.is_alive() and self.is_hidden()

    def can_be_execute(self):
        return self.is_rebel() and self.is_not_hidden() and self.is_alive()

    def can_be_detain(self):
        return self.user_id != 0 and self.is_alive() and self.is_free()

    def can_be_capture(self):
        return self.is_not_spare() and self.is_alive() and self.is_free()

    def can_be_manipulate(self):
        return self.is_not_spare() and self.is_hidden() and self.is_alive() and self.is_free()

    def can_be_assassinate(self):
        return self.user_id != 0 and self.is_alive()

    def can_avoid_detain(self):
        return self.is_loyal() 

    def can_stop_assassinate(self, game):
        return self.character == Character.GUARD \
            and self.is_alive() and self.is_free() \
            and not self.neighbor_is_dancing(game)

    def can_join(self):
        return self.character == Character.SLAVE and self.is_alive() and self.is_free()

    def can_throne(self):
        return self.character == Character.SULTAN \
        and self.is_alive() and self.is_free() and self.is_not_hidden()

    def set_character(self, character):
        self.character = character

    """AI functions
    """
    def ai_action(self, game, manipulate=False):
        if self.must_switch:
            target_id = self.ai_switch(game, hide=self.is_known())
            return Action.SWITCH, [target_id]

        if manipulate or not self.is_exhaust():
            if self.character == Character.SULTAN:
                callback, target_id = self.ai_execute(
                    game, manipulate=manipulate)
                if callback:
                    return Action.EXECUTE, [target_id]
            
            elif self.character == Character.GUARD:
                callback, target_id = self.ai_detain(
                    game, manipulate=manipulate)
                if callback:
                    return Action.DETAIN, [target_id]
            
            elif self.character == Character.ASSASSIN:
                callback, target_id = self.ai_assassinate(
                    game, manipulate=manipulate)
                if callback:
                    return Action.ASSASSINATE, [target_id]
            
            elif self.character == Character.SLAVE:
                callback, target_id = self.ai_call(
                    game, manipulate=manipulate)
                if callback:
                    return Action.CALL, [target_id]

            elif self.character == Character.SLAVEDRIVER:
                callback, target_id = self.ai_capture(
                    game, manipulate=manipulate)
                if callback:
                    return Action.CAPTURE, [target_id]

            elif self.character == Character.DANCER:
                callback, target_id = self.ai_dance(
                    game, manipulate=manipulate)
                if callback:
                    return Action.DANCE, [target_id]

            elif self.character == Character.VIZIER:
                callback, target_id = self.ai_support(
                    game, manipulate=manipulate)
                if callback:
                    return Action.MANIPULATE, [target_id]

            elif self.character == Character.PROPHET:
                target_ids = self.ai_peek(game, 3)
                return Action.PREDICT, target_ids

        if random.random() > 0.8:
            target_id = self.ai_peek(game)
            return Action.PEEK, [target_id]
        else:
            target_id = self.ai_switch(game, hide=self.is_known())
            return Action.SWITCH, [target_id]

    def ai_peek(self, game, N=1):
        choices = game.can_be_peek_by(self.user_id)
        ### DEBUG MODE
        if self.debug:
            print('Peek choices: ' + \
                ', '.join([game.players[i].status() for i in choices]))
        ###
        if N == 1:
            return choices[random.randint(0, len(choices)-1)]
        return random.sample(choices, min(N, len(choices)))

    def ai_switch(self, game, hide=False):
        choices = game.can_be_switch_by(self.user_id, hide=hide)
        ### DEBUG MODE
        if self.debug:
            print('Switch choices: ' + \
                ', '.join([game.players[i].status() for i in choices]))
        ###
        return choices[random.randint(0, len(choices)-1)]

    def ai_execute(self, game, manipulate=False):
        choices = []
        for target_id, target_player in game.players.items():
            if target_player.is_known() and target_player.character == Character.ASSASSIN:
                return True, target_id
            if target_player.can_be_execute():
                choices.append(target_id)
        ### DEBUG MODE
        if self.debug:
            print('Execute choices: ' + \
                ', '.join([game.players[i].status() for i in choices]))
        ###
        if len(choices):
            return True, choices[random.randint(0, len(choices)-1)]
        elif manipulate:
            return True, None
        return False, None

    def ai_detain(self, game, manipulate=False):
        if self.neighbor_is_dancing(game):
            if manipulate:
                return True, None
            return False, None
        choices = []
        for target_id, target_player in game.players.items():
            if target_player.can_be_detain() \
            and (manipulate \
            or (target_player.is_not_hidden() and target_player.is_rebel())):
                choices.append(target_id)
        ### DEBUG MODE
        if self.debug:
            print('Detain choices: ' + \
                ', '.join([game.players[i].status() for i in choices]))
        ###
        if len(choices):
            return True, choices[random.randint(0, len(choices)-1)]
        elif manipulate:
            return True, None
        return False, None

    def ai_capture(self, game, manipulate=False):
        choices = []
        for target_id, target_player in game.players.items():
            if target_player.can_be_capture():
                choices.append(target_id)
        ### DEBUG MODE
        if self.debug:
            print('Capture choices: ' + \
                ', '.join([game.players[i].status() for i in choices]))
        ###
        if len(choices):
            return True, choices[random.randint(0, len(choices)-1)]
        elif manipulate:
            return True, None
        return False, None

    def ai_manipulate(self, game, manipulate=False):
        choices = []
        for target_id, target_player in game.players.items():
            if target_player.can_be_manipulate():
                choices.append(target_id)
        ### DEBUG MODE
        if self.debug:
            print('Manipulate choices: ' + \
                ', '.join([game.players[i].status() for i in choices]))
        ###
        if len(choices):
            return True, choices[random.randint(0, len(choices)-1)]
        else:
            return False, None

    def ai_assassinate(self, game, manipulate=False):
        choices = []
        for target_id, target_player in game.players.items():
            if target_player.can_be_assassinate() \
            and (manipulate \
            or (target_player.is_known() and \
                (target_player.is_loyal() or target_player.character == Character.SLAVEDRIVER ))):
                choices.append(target_id)
        ### DEBUG MODE
        if self.debug:
            print('Assassinate choices: ' + \
                ', '.join([game.players[i].status() for i in choices]))
        ###
        if len(choices):
            return True, choices[random.randint(0, len(choices)-1)]
        elif manipulate:
            return True, None
        return False, None

    def ai_call(self, game, manipulate=False):
        if manipulate:
            return True, None
        if self.is_known():
            return False, None
        neighbors = game.get_neighbors(self.user_id)

        for target_id in neighbors:
            neighbor = game.players[target_id]
            if neighbor.is_not_hidden() and not neighbor.is_free_slave():
                return False, None
        return True, None

    def ai_dance(self, game, manipulate=False):
        if self.is_known():
            return False, None
        elif manipulate:
            return True, None
        
        neighbors = game.get_neighbors(self.user_id)
        for target_id in neighbors:
            neighbor = game.players[target_id]
            if neighbor.is_known() \
            and neighbor.character == Character.GUARD:
                return True, None

        return False, None

    def ai_avoid_detain(self, game=None):
        if self.can_avoid_detain():
            return True
        else:
            return False

    def ai_stop_assassinate(self, game=None):
        if self.can_stop_assassinate(game):
            return True
        else:
            return False

    def ai_support(self, game=None, manipulate=False):
        callback, _ = self.ai_manipulate(game)
        if callback:
            choices = ['loyal', 'rebel']
            return True, choices[random.randint(0, len(choices)-1)]

    def ai_predict(self, game=None, manipulate=False):
        choices = ['loyal', 'rebel']
        return True, choices[random.randint(0, len(choices)-1)]

    def ai_join(self, game):
        neighbors = game.get_neighbors(self.user_id)

        if not self.can_join():
            return False

        for target_id in neighbors:
            neighbor = game.players[target_id]
            if neighbor.is_free_slave():
                return True

        return False

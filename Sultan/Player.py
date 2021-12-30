from .Character import Character
from .Action import GameAction as Action
import random

from PIL import Image

AI_COUNT = 0

class Player:

    def __init__(self, user_id=None, user_name=None, profile_photo=None,
        spare=False, ai=False, debug=False):

        if ai:
            global AI_COUNT
            AI_COUNT += 1
            self.user_id = -AI_COUNT
            self.user_name = f'電腦{AI_COUNT}'
            self.ai = True
        else:
            self.user_id = user_id
            self.user_name = ''.join(user_name.split())
            self.ai = False
        
        self.throne_countdown = None

        self.hidden = True
        self.alive = True
        self.character = None
        self.jail = False
        self.captured = False
        self.order = None

        self.next_action = None

        self.spare = spare
        if spare:
            self.hidden = True

        self.debug = debug

        self.capture_slaves = []
        self.captured_by = None

        self.image_H = 100
        self.image_W = 100
        if profile_photo is None:
            self.profile_photo = Image.new("RGB", 
                (self.image_W, self.image_H), (127, 127, 127))
        else:
            self.profile_photo = profile_photo
        self.profile_photo = self.profile_photo.resize(
            [self.image_W, self.image_H])

    def status(self, verbose=False):
        status_str = ''

        if self.is_dead():
            status_str += '[歿]'
        elif self.is_jail() or self.is_captured():
            status_str += '[牢]'
        
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

    def action_choices(self):
        actions = [
            Action.PEEK,
            Action.SWITCH
        ]

        if self.is_hidden():
            actions.append(Action.REVEAL)
        else:
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
                actions.append(Action.HUNT)

        return actions

    def is_winner(self, win):
        if self.is_spare():
            return False
        if win == 'loyal':
            if self.character == Character.SLAVEDRIVER:
                return self.is_not_hidden()
            return self.is_loyal()
        elif win == 'rebel':
            if self.character == Character.SLAVEDRIVER:
                return self.is_hidden()
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

    def is_free_slave(self):
        return self.character == Character.SLAVE \
            and self.is_not_hidden() and self.is_alive() and self.is_free()

    def is_neutral(self):
        return not self.is_rebel() and not self.is_loyal()

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
        return self.character == Character.SLAVE and self.is_not_hidden() and self.is_alive() and self.is_free()

    def can_be_hunt(self):
        return self.is_not_spare() and self.is_hidden() and self.is_alive() and self.is_free()

    def can_be_assassinate(self):
        return self.user_id != 0 and self.is_alive()

    def can_avoid_detain(self):
        return self.is_loyal()

    def can_stop_assassinate(self):
        return self.character == Character.GUARD and self.is_alive() and self.is_free()

    def can_join(self):
        return self.character == Character.SLAVE and self.is_alive() and self.is_free()

    def can_throne(self):
        return self.character == Character.SULTAN and self.is_alive() and self.is_free() and self.is_not_hidden()

    def set_character(self, character):
        self.character = character

    """AI functions
    """
    def ai_action(self, game):
        if self.next_action is not None:
            action, target_ids = self.next_action
            self.next_action = None
            return action, target_ids
        
        if self.character == Character.SULTAN:
            callback, target_id = self.ai_execute(game)
            if callback:
                if self.is_hidden():
                    self.next_action = Action.EXECUTE, [target_id]
                    return Action.REVEAL, [None]
                return Action.EXECUTE, [target_id]
        
        elif self.character == Character.GUARD:
            callback, target_id = self.ai_detain(game)
            if callback:
                if self.is_hidden():
                    self.next_action = Action.DETAIN, [target_id]
                    return Action.REVEAL, [None]
                return Action.DETAIN, [target_id]
        
        elif self.character == Character.ASSASSIN and self.is_not_hidden():
            callback, target_id = self.ai_assassinate(game)
            if callback:
                if self.is_hidden():
                    self.next_action = Action.ASSASSINATE, [target_id]
                    return Action.REVEAL, [None]
                return Action.ASSASSINATE, [target_id]
        
        elif self.character == Character.SLAVE and self.is_not_hidden():
            callback, target_id = self.ai_call(game)
            if callback:
                if self.is_hidden():
                    self.next_action = Action.CALL, [target_id]
                    return Action.REVEAL, [None]
                return Action.CALL, [target_id]

        elif self.character == Character.SLAVEDRIVER and self.is_not_hidden():
            callback, target_id = self.ai_capture(game)
            if callback:
                if self.is_hidden():
                    self.next_action = Action.CALL, [target_id]
                    return Action.REVEAL, [None]
                return Action.CAPTURE, [target_id]

            callback, target_id = self.ai_hunt(game)
            if callback:
                if self.is_hidden():
                    self.next_action = Action.CALL, [target_id]
                    return Action.REVEAL, [None]
                return Action.HUNT, [target_id]
        
        if random.random() > 0.8:
            target_id = self.ai_peek(game)
            return Action.PEEK, [target_id]
        else:
            if self.is_hidden():
                if random.random() > 0.3:
                    return Action.REVEAL, [None]
                else:
                    target_id = self.ai_switch(game, hide=False)
                    return Action.SWITCH, [target_id]
            else:
                target_id = self.ai_switch(game, hide=True)
                return Action.SWITCH, [target_id]

    def ai_peek(self, game):
        choices = game.can_be_peek_by(self.user_id)
        ### DEBUG MODE
        if self.debug:
            print('Peek choices: ' + \
                ', '.join([game.players[i].status() for i in choices]))
        ###
        return choices[random.randint(0, len(choices)-1)]

    def ai_switch(self, game, hide=False):
        choices = game.can_be_switch_by(self.user_id, hide=hide)
        ### DEBUG MODE
        if self.debug:
            print('Switch choices: ' + \
                ', '.join([game.players[i].status() for i in choices]))
        ###
        return choices[random.randint(0, len(choices)-1)]

    def ai_execute(self, game):
        choices = []
        for target_id, target_player in game.players.items():
            if target_player.can_be_execute():
                choices.append(target_id)
        ### DEBUG MODE
        if self.debug:
            print('Execute choices: ' + \
                ', '.join([game.players[i].status() for i in choices]))
        ###
        if len(choices):
            return True, choices[random.randint(0, len(choices)-1)]
        else:
            return False, None

    def ai_detain(self, game):
        choices = []
        for target_id, target_player in game.players.items():
            if target_player.can_be_detain() \
            and target_player.is_not_hidden() \
            and target_player.is_rebel():
                choices.append(target_id)
        ### DEBUG MODE
        if self.debug:
            print('Detain choices: ' + \
                ', '.join([game.players[i].status() for i in choices]))
        ###
        if len(choices):
            return True, choices[random.randint(0, len(choices)-1)]
        else:
            return False, None

    def ai_capture(self, game):
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
        else:
            return False, None

    def ai_hunt(self, game):
        choices = []
        for target_id, target_player in game.players.items():
            if target_player.can_be_hunt():
                choices.append(target_id)
        ### DEBUG MODE
        if self.debug:
            print('Hunt choices: ' + \
                ', '.join([game.players[i].status() for i in choices]))
        ###
        if len(choices):
            return True, choices[random.randint(0, len(choices)-1)]
        else:
            return False, None

    def ai_assassinate(self, game):
        choices = []
        for target_id, target_player in game.players.items():
            if target_player.can_be_assassinate() \
            and target_player.is_not_hidden() \
            and target_player.is_loyal():
                choices.append(target_id)
        ### DEBUG MODE
        if self.debug:
            print('Assassinate choices: ' + \
                ', '.join([game.players[i].status() for i in choices]))
        ###
        if len(choices):
            return True, choices[random.randint(0, len(choices)-1)]
        else:
            return False, None

    def ai_call(self, game):
        neighbors = game.get_neighbors(self.user_id)

        for target_id in neighbors:
            neighbor = game.players[target_id]
            if neighbor.is_not_hidden() and not neighbor.is_free_slave():
                return False, None

        return True, None

    def ai_avoid_detain(self, game=None):
        if self.can_avoid_detain():
            return True
        else:
            return False

    def ai_stop_assassinate(self, game=None):
        if self.can_stop_assassinate():
            return True
        else:
            return False

    def ai_join(self, game):
        neighbors = game.get_neighbors(self.user_id)

        if not self.can_join():
            return False

        for target_id in neighbors:
            neighbor = game.players[target_id]
            if neighbor.is_hidden() or neighbor.is_free_slave():
                return True

        return False

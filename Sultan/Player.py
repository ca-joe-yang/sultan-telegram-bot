from .Character import Character
from .Action import GameAction as Action
import random

AI_COUNT = 0

class Player:

    def __init__(self, user_id=None, user_name=None, spare=False, ai=False, debug=False):

        if ai:
            global AI_COUNT
            AI_COUNT += 1
            self.user_id = -AI_COUNT
            self.user_name = f'電腦{AI_COUNT}'
        else:
            self.user_id = user_id
            self.user_name = ''.join(user_name.split())
        
        self.player_id = None
        self.throne_countdown = None

        self.hidden = True
        self.alive = True
        self.character = None
        self.jail = False
        self.order = None

        self.next_action = None

        self.spare = spare
        if spare:
            self.hidden = True

        self.debug = debug

    def status(self, verbose=False):
        status_str = ''

        if self.is_dead():
            status_str += '[歿]'
        elif self.is_jail():
            status_str += '[牢]'
        
        if self.is_hidden():
            status_str += '[隱]'
        elif self.is_not_hidden():
            status_str += '[顯]'

        if self.is_not_hidden() or verbose:
            status_str += f'<{self.character}>'

        user_name = f'{self.user_name} {status_str}'
        if self.is_spare():
            user_name = f'(0) {user_name}'
        elif self.is_alive():
            user_name = f'({self.order+1}) {user_name}'

        return user_name

    def is_ai(self):
        return self.user_id < 0

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

    def is_not_jail(self):
        return not self.jail

    def is_free(self):
        return not self.jail

    def is_jail(self):
        return self.jail

    def is_dead(self):
        return not self.alive

    def is_rebel(self):
        return self.character == Character.ASSASSIN or self.character == Character.SLAVE

    def is_loyal(self):
        return self.character == Character.SULTAN or self.character == Character.GUARD

    def is_sultan(self):
        return self.character == Character.SULTAN

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
            action, target_id = self.next_action
            self.next_action = None
            return action, target_id
        
        if self.character == Character.SULTAN:
            callback, target_id = self.ai_execute(game)
            if callback:
                if self.is_hidden():
                    self.next_action = Action.EXECUTE, target_id
                    return Action.REVEAL, None
                return Action.EXECUTE, target_id
        
        elif self.character == Character.GUARD:
            callback, target_id = self.ai_detain(game)
            if callback:
                if self.is_hidden():
                    self.next_action = Action.DETAIN, target_id
                    return Action.REVEAL, None
                return Action.DETAIN, target_id
        
        elif self.character == Character.ASSASSIN and self.is_not_hidden():
            callback, target_id = self.ai_assassinate(game)
            if callback:
                if self.is_hidden():
                    self.next_action = Action.ASSASSINATE, target_id
                    return Action.REVEAL, None
                return Action.ASSASSINATE, target_id
        
        elif self.character == Character.SLAVE and self.is_not_hidden():
            callback, target_id = self.ai_call(game)
            if callback:
                if self.is_hidden():
                    self.next_action = Action.CALL, target_id
                    return Action.REVEAL, None
                return Action.CALL, target_id
        
        if random.random() > 0.5:
            return Action.PEEK, self.ai_peek(game)
        else:
            if self.is_hidden():
                if random.random() > 0.5:
                    return Action.REVEAL, None
                else:
                    return Action.SWITCH, self.ai_switch(game, hide=False)
            else:
                return Action.HIDE, self.ai_switch(game, hide=True)

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

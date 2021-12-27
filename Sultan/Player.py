from .Character import Character

class Player:

    def __init__(self, user_id=None, user_name=None, spare=False):
        self.user_id = user_id
        self.user_name = user_name.strip()
        self.player_id = None

        self.hidden = True
        self.alive = True
        self.character = None
        self.jail = False
        self.order = None

        self.spare = spare
        if spare:
            self.hidden = True

    def status(self, verbose=False):
        if self.is_dead():
            user_name = f'[歿] {self.user_name}'
        elif self.is_jail():
            user_name = f'[牢] {self.user_name}'
        else:
            user_name = self.user_name
        if self.is_not_hidden() or verbose:
            return f'({self.order}) {user_name} <{self.character}>'
        else:
            return f'{user_name}'

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

    def is_neutral(self):
        return not self.is_rebel() and not self.is_loyal()

    def can_be_peek(self, user_id):
        return self.user_id != user_id and self.is_alive() and self.is_hidden()

    def can_be_switch(self, user_id):
        return self.user_id != user_id and self.is_alive() and self.is_hidden()

    def can_be_hide(self, user_id):
        return self.user_id == user_id or (self.is_alive() and self.is_hidden())

    def can_be_execute(self):
        return self.is_rebel() and self.is_not_hidden() and self.is_alive()

    def can_be_detain(self, user_id):
        return self.user_id != 0 and self.user_id != user_id and self.is_alive() and self.is_free()

    def can_be_assassinate(self, user_id):
        return self.user_id != 0 and self.user_id != user_id and self.is_alive()

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

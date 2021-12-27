from enum import Enum

class State(Enum):
    IDLE = 0
    REGISTER = 1
    TURN_START = 2

    def __str__(self):
        if self.value == 0:
            return '閒置'
        elif self.value == 1:
            return '註冊'
        elif self.value == 2:
            return '回合'
        # elif self.value == 3:
        #     return '討論'
        # elif self.value == 4:
        #     return '投票'
        # elif self.value == 5:
        #     return '殺人'
        return f'{self.value}未定義'
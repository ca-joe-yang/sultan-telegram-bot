from enum import Enum

class State(Enum):
    NO_GAME = -1

    IDLE = 0
    REGISTER = 1
    TURN_START = 2
    TURN_MID = 3
    TURN_END = 4

    AVOID_DETAIN = 5
    STOP_ASSASSINATE = 6
    JOIN_REVOLUTION = 7

    def __str__(self):
        if self.value == 0:
            return '閒置'
        elif self.value == 1:
            return '註冊'
        elif self.value == 2:
            return '回合開始'
        elif self.value == 3:
            return '回合中'
        elif self.value == 4:
            return '回合結束'
        elif self.value == 5:
            return '避免關押'
        elif self.value == 6:
            return '阻止刺殺'
        elif self.value == 7:
            return '響應革命'
        return f'{self.value}未定義'
from enum import Enum

class State(Enum):
    NO_GAME = -1

    IDLE = 1
    REGISTER = 2
    CHECK = 3
    
    TURN_START = 11
    TURN_MID = 12
    TURN_END = 13

    AVOID_DETAIN = 21
    STOP_ASSASSINATE = 22
    JOIN_REVOLUTION = 23

    def in_turn(self):
        return self.value >= 10

    def __str__(self):
        if self.value == 1:
            return '閒置'
        elif self.value == 2:
            return '註冊'
        elif self.value == 3:
            return '查看'
        elif self.value == 11:
            return '回合開始'
        elif self.value == 12:
            return '回合中'
        elif self.value == 13:
            return '回合結束'
        elif self.value == 21:
            return '避免關押'
        elif self.value == 22:
            return '阻止刺殺'
        elif self.value == 23:
            return '響應革命'
        return f'{self.value}未定義'
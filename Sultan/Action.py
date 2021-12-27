from enum import Enum

class BotAction(Enum):

    IDLE = 0
    ANNOUNCE = 1
    PRIVATE = 2
    ILLEGAL = 3
    ERROR = 4

class GameAction(Enum):

    # General
    PEEK = 1
    SWITCH = 2
    REVEAL = 3
    HIDE = 4

    CHECK = 5
    AVOID_DETAIN = 6
    STOP_ASSASSINATE = 7

    # Sultan
    EXECUTE = 11
    THRONE = 12

    # Guard
    DETAIN = 21

    # Assassin
    ASSASSINATE = 31

    # SLAVE
    CALL = 41
    JOIN = 42

    def __str__(self):
        if self.value == 1:
            return '<一般> 偷看'
        elif self.value == 2:
            return '<一般> 交換'
        elif self.value == 3:
            return '<一般> 公開'
        elif self.value == 4:
            return '<一般> 隱藏'

        elif self.value == 6:
            return '<被動> 避免關押'
        elif self.value == 7:
            return '<被動> 阻止刺殺'
        elif self.value == 8:
            return '<被動> 登基'
        
        elif self.value == 11:
            return '<蘇丹> 處決'
        
        elif self.value == 21:
            return '<守衛> 關押'
        
        elif self.value == 31:
            return '<刺客> 刺殺'
        
        elif self.value == 41:
            return '<奴隸> 號召'
        elif self.value == 42:
            return '<奴隸> 響應'

        return f'[動作] {self.value} 未定義'

        # elif self.value == 5:
        #     return '偷看'
        # elif self.value == 6:
        #     return '交換'
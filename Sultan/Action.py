from enum import Enum

ACTION_CONFIG = {
    0: '<錯誤> 未定義',

    1: '<管理> 跳過',
    2: '<通用> 查看',
    3: '<通用> 教學',
    4: '<一般> 取消',
    
    11: '<一般> 公開',
    12: '<一般> 隱藏',
    13: '<一般> 偷看',
    14: '<一般> 交換',

    21: '<蘇丹> 處決',
    22: '<蘇丹> 登基',

    31: '<守衛> 關押',

    41: '<刺客> 刺殺',

    51: '<奴隸> 號召',

    61: '<販子> 抓捕',
    62: '<販子> 狩獵',
}

class GameAction(Enum):
    """Default"""
    DEFAULT = 0

    """General action"""
    SKIP = 1
    CHECK = 2
    TUTORIAL = 3
    CANCEL = 4
    
    """Regular action"""
    REVEAL = 11
    HIDE = 12
    PEEK = 13
    SWITCH = 14

    """Sultan action"""
    EXECUTE = 21
    THRONE = 22

    """Guard action"""
    DETAIN = 31

    """Assassinate action"""
    ASSASSINATE = 41

    """Slave action"""
    CALL = 51

    """Slave driver action"""
    CAPTURE = 61
    HUNT = 62

    @classmethod
    def _missing_(cls, value):
        return GameAction.DEFAULT

    def __str__(self):
        if self.value in ACTION_CONFIG:
            return ACTION_CONFIG[self.value]
        else:
            return ACTION_CONFIG[0]

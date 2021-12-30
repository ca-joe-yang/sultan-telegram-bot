from enum import Enum

ACTION_CONFIG = {
    0: '<錯誤> 未定義',

    1: '<管理> 跳過',
    2: '<通用> 查看',
    3: '<通用> 教學',
    4: '<選項> 取消',
    
    11: '<一般> 偷看',
    12: '<一般> 交換',
    13: '<身份> 公開',

    21: '<蘇丹> 處決',
    22: '<蘇丹> 登基',

    31: '<守衛> 關押',

    41: '<刺客> 刺殺',

    51: '<奴隸> 號召',

    61: '<販子> 抓捕',
    62: '<販子> 狩獵',

    71: '<舞孃> 跳舞',

    81: '<大官> 操弄',

    91: '<先知> 預測',
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
    PEEK = 11
    SWITCH = 12
    REVEAL = 13

    GIVEUP = 14

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

    DANCE = 71

    MANIPULATE = 81

    PREDICT = 91

    @classmethod
    def _missing_(cls, value):
        return GameAction.DEFAULT

    def __str__(self):
        if self.value in ACTION_CONFIG:
            return ACTION_CONFIG[self.value]
        else:
            return ACTION_CONFIG[0]

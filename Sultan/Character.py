from enum import Enum

class Character(Enum):
    SULTAN = 1
    GUARD = 2
    ASSASSIN = 3
    SLAVE = 4
    SLAVEDRIVER = 5
    DANCER = 6
    VIZIER = 7
    PROPHET = 8

    def __str__(self):
        if self.value == 0:
            return '白板'
        elif self.value == 1:
            return '蘇丹'
        elif self.value == 2:
            return '守衛'
        elif self.value == 3:
            return '刺客'
        elif self.value == 4:
            return '奴隸'
        elif self.value == 5:
            return '販子'
        elif self.value == 6:
            return '舞孃'
        elif self.value == 7:
            return '大官'
        elif self.value == 8:
            return '先知'
        else:
            raise

    def abbr(self):
        if self.value == 0:
            return '白'
        elif self.value == 1:
            return '王'
        elif self.value == 2:
            return '衛'
        elif self.value == 3:
            return '刺'
        elif self.value == 4:
            return '奴'
        elif self.value == 5:
            return '販'
        elif self.value == 6:
            return '舞'
        elif self.value == 7:
            return '官'
        elif self.value == 8:
            return '預'
        else:
            raise

NEUTRAL_CHARACTERS = [
    Character.SLAVEDRIVER,
    Character.DANCER,
    Character.VIZIER,
    # Character.PROPHET
]

CHARACTER_COUNT_DICTIONARY = {
    5: {
        Character.SULTAN: 1,
        Character.GUARD: 1,
        Character.ASSASSIN: 1,
        Character.SLAVE: 3,
    },
    6: {
        Character.SULTAN: 1,
        Character.GUARD: 1,
        Character.ASSASSIN: 1,
        Character.SLAVE: 3,
    },
    7: {
        Character.SULTAN: 1,
        Character.GUARD: 1,
        Character.ASSASSIN: 1,
        Character.SLAVE: 3,
    },
    8: {
        Character.SULTAN: 1,
        Character.GUARD: 2,
        Character.ASSASSIN: 2,
        Character.SLAVE: 3,
    },
    9: {
        Character.SULTAN: 1,
        Character.GUARD: 2,
        Character.ASSASSIN: 2,
        Character.SLAVE: 3,
    },
    10: {
        Character.SULTAN: 1,
        Character.GUARD: 2,
        Character.ASSASSIN: 2,
        Character.SLAVE: 3,
    },
    11: {
        Character.SULTAN: 1,
        Character.GUARD: 2,
        Character.ASSASSIN: 2,
        Character.SLAVE: 4,
    },
    12: {
        Character.SULTAN: 1,
        Character.GUARD: 3,
        Character.ASSASSIN: 3,
        Character.SLAVE: 4,
    },
    13: {
        Character.SULTAN: 1,
        Character.GUARD: 3,
        Character.ASSASSIN: 3,
        Character.SLAVE: 4,
    },
    14: {
        Character.SULTAN: 1,
        Character.GUARD: 3,
        Character.ASSASSIN: 3,
        Character.SLAVE: 4,
    },
    15: {
        Character.SULTAN: 1,
        Character.GUARD: 3,
        Character.ASSASSIN: 3,
        Character.SLAVE: 5,
    },
}

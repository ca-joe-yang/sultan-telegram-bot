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
            return '政客'
        elif self.value == 8:
            return '先知'
        else:
            raise

CHARACTER_COUNT_DICTIONARY = {
    2: {
        Character.SULTAN: 1,
        Character.SLAVE: 2,
    },
    3: {
        Character.SULTAN: 1,
        Character.SLAVE: 3,
    },
    4: {
        Character.SULTAN: 1,
        Character.GUARD: 1,
        Character.SLAVE: 3,
    },
    5: {
        Character.SULTAN: 1,
        Character.GUARD: 1,
        Character.ASSASSIN: 1,
        Character.SLAVE: 3,
    },
}

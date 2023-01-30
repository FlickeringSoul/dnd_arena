
import random
from enum import IntEnum

class Dices(IntEnum):
    d4 = 4
    d6 = 6
    d8 = 8
    d10 = 10
    d12 = 12
    d20 = 20

    def avg(self):
        pass

    def probability_of_being_higher_or_equal_to(self, n: int):
        pass

    def roll(self) -> int:
        return random.randint(1, self.value)

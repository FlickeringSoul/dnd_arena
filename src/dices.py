

from enum import Enum
from dataclasses import dataclass, field
from probability import RandomVariable


class Dices(Enum):
    d4 = 4
    d6 = 6
    d8 = 8
    d10 = 10
    d12 = 12
    d20 = 20

    def as_random_variable(self) -> RandomVariable:
        return RandomVariable.from_values([i for i in range(1, self.value + 1)])


@dataclass
class DiceBag:
    dices: list[tuple[int, Dices]] = field(default_factory=list)
    fix: int = 0

    def as_random_variable(self) -> RandomVariable:
        result = RandomVariable.from_values([self.fix])
        for sign, dice in self.dices:
            if sign == 1:
                result = result + dice.as_random_variable()
            elif sign == -1:
                result = result - dice.as_random_variable()
            else:
                raise ValueError('Unexpected value for sign')
        return result

    @staticmethod
    def cast_to_diced_number(object: int | Dices) -> 'DiceBag':
        if isinstance(object, Dices):
            return DiceBag(
                dices=[(1, object)],
                fix=0
            )
        if isinstance(object, int):
            return DiceBag(
                dices=[],
                fix=object
            )
        raise TypeError(f'object should be either a in or a Dices not a {type(object)}')

    def __add__(self, other: 'DiceBag | int | Dices') -> 'DiceBag':
        if not isinstance(other, DiceBag):
            other = DiceBag.cast_to_diced_number(other)
        return DiceBag(
            dices=self.dices+other.dices,
            fix=self.fix+other.fix
        )

    def __sub__(self, other: 'DiceBag | int | Dices') -> 'DiceBag':
        if not isinstance(other, DiceBag):
            other = DiceBag.cast_to_diced_number(other)
        return DiceBag(
            dices=self.dices + [(-sign, dice) for sign, dice in other.dices] ,
            fix=self.fix - other.fix
        )

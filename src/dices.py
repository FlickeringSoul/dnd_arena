

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction

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

    def __mul__(self, other: int) -> 'DiceBag':
        return DiceBag(
            dices={
                (True, self): other
            }
        )


@dataclass
class DiceBag:
    dices: dict[tuple[bool, Dices], int] = field(default_factory=dict)
    fix: int = 0

    def avg(self) -> Fraction:
        return sum(
            (value * probability for value, probability in self.as_random_variable().outcomes.items()),
            start=Fraction()
        )

    def as_random_variable(self) -> RandomVariable:
        """
        TODO: some variables cannot be negatives and must be fixed
        """
        result = RandomVariable.from_values([self.fix])
        for (is_positive, dice), count in self.dices.items():
            for _ in range(count):
                if is_positive:
                    result = result + dice.as_random_variable()
                else:
                    result = result - dice.as_random_variable()
        return result

    @staticmethod
    def cast_to_dice_bag(obj: int | Dices) -> 'DiceBag':
        match obj:
            case Dices():
                return DiceBag(
                    dices={(True, obj): 1}
                )
            case int():
                return DiceBag(
                    fix=obj
                )
            case _:
                raise TypeError(f'object should be either a int or a Dices not a {type(obj)}')

    def __add__(self, other: 'DiceBag | int | Dices') -> 'DiceBag':
        if not isinstance(other, DiceBag):
            other = DiceBag.cast_to_dice_bag(other)
        res = DiceBag(fix=self.fix + other.fix)
        for key in set(self.dices.keys()).union(other.dices.keys()):
            res.dices[key] = self.dices.get(key, 0) + other.dices.get(key, 0)
        return res

    def __sub__(self, other: 'DiceBag | int | Dices') -> 'DiceBag':
        if not isinstance(other, DiceBag):
            other = DiceBag.cast_to_dice_bag(other)
        res = DiceBag(fix=self.fix - other.fix)
        for key in set(self.dices.keys()).union(other.dices.keys()):
            res.dices[key] = self.dices.get(key, 0) - other.dices.get(key, 0)
        return res

    def __repr__(self) -> str:
        res = []
        for (is_positive, dice), count in self.dices.items():
            sign = '+' if is_positive else '-'
            res.append(sign)
            res.append(f'{count}{dice.name}')
        if self.fix != 0:
            sign = '+' if self.fix > 0 else '-'
            res.append(sign)
            res.append(f'{self.fix}')
        if len(res) > 0 and res[0] == '+':
            res.pop(0)
        return ' '.join(res)

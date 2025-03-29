

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction

from probability import RandomVariable, advantage_disadvantage


class Dice(Enum):
    d4 = 4
    d6 = 6
    d8 = 8
    d10 = 10
    d12 = 12
    d20 = 20

    def as_random_variable(self) -> RandomVariable:
        return RandomVariable.from_range(1, self.value)

    def __mul__(self, other: int) -> 'DiceBag':
        return DiceBag(
            positive_dices=[DiceRoll(self) for _ in range(other)]
        )


@dataclass
class DiceRoll:
    dice: Dice
    advantage: bool = False
    disadvantage: bool = False
    rerolling: set[int] = set()

    def as_random_variable(self) -> RandomVariable:
        rand_var = self.dice.as_random_variable()
        rand_var.reroll_on_values(self.rerolling)
        rand_var = advantage_disadvantage(rand_var, self.advantage, self.disadvantage)
        return rand_var

    def __repr__(self) -> str:
        end = ''
        if self.advantage and self.disadvantage is False:
            end = ' (adv.)'
        elif self.disadvantage and self.advantage is False:
            end = ' (dis.)'
        return f'{self.dice.name}{end}'


@dataclass
class DiceBag:
    fix: int = 0
    positive_dices: list[DiceRoll] = field(default_factory=list)
    negative_dices: list[DiceRoll] = field(default_factory=list)

    def avg(self) -> Fraction:
        return sum(
            (value * probability for value, probability in self.as_random_variable().outcomes.items()),
            start=Fraction()
        )

    def as_random_variable(self) -> RandomVariable:
        """
        TODO: some variables cannot be negatives and must be fixed
        Conditional rolling ?? Just like critical and fumble ?
        """
        result = RandomVariable.from_values([self.fix])
        for dice_roll in self.positive_dices:
            result = result + dice_roll.as_random_variable()
        for dice_roll in self.negative_dices:
            result = result - dice_roll.as_random_variable()
        return result

    @staticmethod
    def cast_to_dice_bag(obj: int | Dice | DiceRoll) -> 'DiceBag':
        match obj:
            case Dice():
                return DiceBag(
                    positive_dices=[DiceRoll(obj)]
                )
            case int():
                return DiceBag(
                    fix=obj
                )
            case DiceRoll():
                return DiceBag(
                    positive_dices=[obj]
                )
            case _:
                raise TypeError(f'object should be either a int or a Dices not a {type(obj)}')

    def __add__(self, other: 'DiceBag | int | Dice | DiceRoll') -> 'DiceBag':
        if not isinstance(other, DiceBag):
            other = DiceBag.cast_to_dice_bag(other)
        res = DiceBag(fix=self.fix + other.fix)
        res.positive_dices = self.positive_dices + other.positive_dices
        res.negative_dices = self.negative_dices + other.negative_dices
        return res

    def __sub__(self, other: 'DiceBag | int | Dice') -> 'DiceBag':
        if not isinstance(other, DiceBag):
            other = DiceBag.cast_to_dice_bag(other)
        res = DiceBag(fix=self.fix - other.fix)
        res.positive_dices = self.positive_dices + other.negative_dices
        res.negative_dices = self.negative_dices + other.positive_dices
        return res

    def __repr__(self) -> str:
        res = []
        blabla = {}
        for dice_roll in self.positive_dices:
            res.append('+ ')
            res.append()
        for dices in [self.positive_dices, self.negative_dices]
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

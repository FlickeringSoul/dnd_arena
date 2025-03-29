
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from typing import Callable


@dataclass
class RandomVariable:
    outcomes: dict[int, Fraction] # Value -> Probability

    def probability_of_being_between(self, min_included: int, max_included: int) -> Fraction:
        result_probability = Fraction()
        for value, probability in self.outcomes.items():
            if min_included <= value <= max_included:
                result_probability += probability
        return result_probability

    def probability_of_being_superior_or_equal_to(self, threshold: int) -> Fraction:
        result_probability = Fraction()
        for value, probability in self.outcomes.items():
            if threshold <= value:
                result_probability += probability
        return result_probability

    @staticmethod
    def from_range(start_included: int, end_included: int) -> 'RandomVariable':
        return RandomVariable.from_values(list(range(start_included, end_included + 1)))

    @staticmethod
    def from_values(values: list[int]) -> 'RandomVariable':
        """Return random variable with uniform distribution from given values

        If a value appear several times in list, it has more chance to appear
        """
        n = len(values)
        outcomes: dict[int, Fraction] = defaultdict(Fraction)
        for value in values:
            outcomes[value] += Fraction(1, n)
        return RandomVariable(outcomes)

    def __post_init__(self) -> None:
        assert sum(self.outcomes.values()) == 1

    def __add__(self, other: 'RandomVariable | int') -> 'RandomVariable':
        if isinstance(other, int):
            other = RandomVariable({other: Fraction(1)})
        return self.merge(other, lambda v1, v2: v1 + v2)

    def __neg__(self) -> 'RandomVariable':
        outcomes = {}
        for value, probability in self.outcomes.items():
            outcomes[-value] = probability
        return RandomVariable(outcomes)

    def __sub__(self, other: 'RandomVariable | int') -> 'RandomVariable':
        if isinstance(other, int):
            other = RandomVariable({other: Fraction(1)})
        return self + (- other)

    def merge(self, other: 'RandomVariable', value_merge_func: Callable[[int, int], int]) -> 'RandomVariable':
        merged_outcomes: dict[int, Fraction] = defaultdict(Fraction)
        for value_1, probability_1 in self.outcomes.items():
            for value_2, probability_2 in other.outcomes.items():
                merged_value = value_merge_func(value_1, value_2)
                merged_outcomes[merged_value] += probability_1 * probability_2
        return RandomVariable(merged_outcomes)

    def reroll_on_values(self, values_to_reroll: list[int]) -> None:
        if any(True for value in values_to_reroll if value not in self.outcomes):
            raise ValueError('Value to reroll do not exist')
        reroll_probability = Fraction(0)
        for value in values_to_reroll:
            reroll_probability += self.outcomes[value]
        for value in self.outcomes:
            old_factor = 0 if value in values_to_reroll else 1
            self.outcomes[value] = self.outcomes[value] * (old_factor + reroll_probability)


def get_d20_roll(reroll_fumble: bool) -> RandomVariable:
    d20_random_var = RandomVariable.from_range(1, 20)
    if reroll_fumble:
        d20_random_var.reroll_on_values([1])
    return d20_random_var


def advantage_disadvantage(random_variable: RandomVariable, advantage: bool, disadvantage: bool) -> RandomVariable:
    match advantage, disadvantage:
        case True, False:
            return random_variable.merge(random_variable, max)
        case False, True:
            return random_variable.merge(random_variable, min)
        case _:
            return random_variable

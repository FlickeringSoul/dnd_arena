
from dataclasses import dataclass
from fractions import Fraction
from typing import TypeVar, Generic


T = TypeVar('T')

@dataclass
class RandomVariable(Generic[T]):
    outcomes: dict[T, Fraction]

    def probability_of_being_between(self, min_included: T, max_included: T) -> Fraction:
        result_probability = 0
        for value, probability in self.outcomes.items():
            if min_included <= value <= max_included:
                result_probability += probability
        return result_probability

    def probability_of_being_superior_or_equal_to(self, threshold: T) -> Fraction:
        result_probability = 0
        for value, probability in self.outcomes.items():
            if threshold <= value:
                result_probability += probability
        return result_probability

    @staticmethod
    def from_range(start_included: int, end_included: int):
        return RandomVariable.from_values([i for i in range(start_included, end_included + 1)])

    @staticmethod
    def from_values(values: list[T]) -> 'RandomVariable':
        """Return random variable with uniform distribution from given values

        If a value appear several times in list, it has more chance to appear
        """
        n = len(values)
        outcomes = {}
        for value in values:
            outcomes[value] = outcomes.get(value, 0) + Fraction(1, n)
        return RandomVariable(outcomes)

    def __post_init__(self):
        assert(sum(self.outcomes.values()) == 1)

    def __add__(self, other: 'RandomVariable | T') -> 'RandomVariable':
        if isinstance(other, RandomVariable) is False:
            other = RandomVariable({other: Fraction(1, 1)})
        outcomes = {}
        for self_value, self_probability in self.outcomes.items():
            for other_value, other_probability in other.outcomes.items():
                result_value = self_value + other_value
                result_probability = self_probability * other_probability
                outcomes[result_value] = outcomes.get(result_value, 0) + result_probability
        return RandomVariable(outcomes)

    def __neg__(self) -> 'RandomVariable':
        outcomes = {}
        for value, probability in self.outcomes.items():
            outcomes[-value] = probability
        return RandomVariable(outcomes)

    def __sub__(self, other: 'RandomVariable | T') -> 'RandomVariable':
        if isinstance(other, RandomVariable) is False:
            other = RandomVariable({other: Fraction(1, 1)})
        return self + (- other)

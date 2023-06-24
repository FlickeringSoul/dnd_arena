
from collections import defaultdict
from enum import Enum, auto
from fractions import Fraction

from dices import DiceBag, Dices


class DamageType(str, Enum):
    Fire = auto()
    Force = auto()
    Radiant = auto()
    Heal = auto()

    Piercing = auto()
    Slashing = auto()
    Bludgeoning = auto()

    MagicalPiercing = auto()
    MagicalSlashing = auto()
    MagicalBludgeoning = auto()


class Damage:
    def __init__(self) -> None:
        self.__damages: defaultdict[DamageType, DiceBag] = defaultdict(DiceBag)

    def __add__(self, other: 'Damage') -> 'Damage':
        result_damage_object = Damage()
        damage_types = set(self.__damages.keys()).union(other.__damages.keys())
        for damage_type in damage_types:
            result_damage_object[damage_type] = self[damage_type] + other[damage_type]
        return result_damage_object

    def __getitem__(self, key: DamageType) -> DiceBag:
        return self.__damages[key]

    def __setitem__(self, key: DamageType, item: DiceBag) -> None:
        self.__damages[key] = item

    def add(self, dmg_type: DamageType, value: DiceBag | Dices | int) -> 'Damage':
        self[dmg_type] += value
        return self

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(' + ', '.join(f'{k.name}: {v}' for k,v in self.__damages.items()) + ')'

    def as_critical(self) -> 'Damage':
        result_damage = Damage()
        for damage_type in self.__damages.keys():
            result_damage[damage_type] = DiceBag(
                dices={k: v * 2 for k, v in self[damage_type].dices.items()}, # Is it always true ? Barbarian brutal critical ?? what about negative dices ?
                fix=self[damage_type].fix
            )
        return result_damage

    def avg(self) -> Fraction:
        return sum(
            (dice_bag.avg() for dice_bag in self.__damages.values()),
            start=Fraction()
        )

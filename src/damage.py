
from dataclasses import dataclass, field
from enum import Enum, auto
from fractions import Fraction

from dices import DiceBag


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


@dataclass
class Damage:
    damages: dict[DamageType, DiceBag] = field(default_factory=dict)

    def __add__(self, other: 'Damage') -> 'Damage':
        result_damage_dict = {}
        damage_types = set(self.damages.keys()).union(other.damages.keys())
        for damage_type in damage_types:
            result_damage_dict[damage_type] = self.damages.get(damage_type, DiceBag()) + other.damages.get(damage_type, DiceBag())
        return Damage(result_damage_dict)

    def as_critical(self) -> 'Damage':
        result_damage_dict = {}
        for damage_type in self.damages.keys():
            result_damage_dict[damage_type] = DiceBag(
                dices=self.damages[damage_type].dices * 2, # Is it always true ? Barbarian brutal critical ??
                fix=self.damages[damage_type].fix
            )
        return Damage(result_damage_dict)

    def avg(self) -> Fraction:
        return sum(dice_bag.avg() for dice_bag in self.damages.values())

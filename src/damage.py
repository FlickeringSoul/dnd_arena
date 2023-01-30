
from dataclasses import dataclass, field
from enum import Enum, auto
from fractions import Fraction
from dices import Dices
import utils
import logging

class DamageType(str, Enum):
    Fire = auto()
    Force = auto()
    Radiant = auto()

    Piercing = auto()
    Slashing = auto()
    Bludgeoning = auto()
    
    MagicalPiercing = auto()
    MagicalSlashing = auto()
    MagicalBludgeoning = auto()


@dataclass
class RolledDamage:
    __damages: dict[DamageType, int] = field(default_factory=dict, init=False)

    def add(self, damage_type: DamageType, value: int):
        self.__damages[damage_type] = self.__damages.get(damage_type, 0) + value

    def __add__(self, other: 'RolledDamage') -> 'RolledDamage':
        res = RolledDamage()
        for damage_type, value in self.__damages.items():
            res.add(damage_type, value)
        for damage_type, value in other.__damages.items():
            res.add(damage_type, value)
        return res

    def get_sum(self) -> int:
        return sum(self.__damages.values())


@dataclass
class Damage:
    dice_damages: list[tuple[Dices, DamageType]] = field(default_factory=list)
    fix_damages: list[tuple[int, DamageType]] = field(default_factory=list)

    def __get_rolled_dice_damage(self) -> RolledDamage:
        rolled_damage = RolledDamage()
        for dice, damage_type in self.dice_damages:
            rolled_damage.add(damage_type, dice.roll())
        return rolled_damage

    def __get_fix_damages(self) -> RolledDamage:
        rolled_damage = RolledDamage()
        for value, damage_type in self.fix_damages:
            rolled_damage.add(damage_type, value)
        return rolled_damage

    def roll_crit(self) -> RolledDamage:
        return self.roll_normal() + self.__get_rolled_dice_damage()

    def roll_normal(self) -> RolledDamage:
        return self.__get_fix_damages() + self.__get_rolled_dice_damage()
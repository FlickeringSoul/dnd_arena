
from dataclasses import dataclass
from enum import Flag, auto

from ability import Ability
from damage import Damage, DamageType
from dices import DiceBag, Dices


class WeaponProperties(Flag):
    Ammunition = auto()
    Finesse = auto()
    Heavy = auto()
    Light = auto()
    Loading = auto()
    Range = auto()
    Reach = auto()
    Special = auto()
    Thrown = auto()
    Two_Handed = auto()
    Versatile = auto()


@dataclass
class Weapon:
    damage_type: DamageType
    damage_dices: Dices
    nb_of_dices: int
    ability: Ability
    properties: WeaponProperties

    def damage(self) -> Damage:
        return Damage().add(self.damage_type, DiceBag(dices={(True, self.damage_dices): self.nb_of_dices}))

def shortbow() -> Weapon:
    return Weapon(
    damage_type=DamageType.Piercing,
    damage_dices=Dices.d6,
    nb_of_dices=1,
    ability=Ability.Dexterity,
    properties=WeaponProperties.Range|WeaponProperties.Ammunition|WeaponProperties.Two_Handed
)
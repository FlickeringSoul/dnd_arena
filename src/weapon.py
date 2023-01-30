
from dataclasses import dataclass
from damage import DamageType
from dices import Dices
from attribute import Attribute

@dataclass
class Weapon:
    damage_type: DamageType
    damage_dices: list[Dices]
    attribute: Attribute

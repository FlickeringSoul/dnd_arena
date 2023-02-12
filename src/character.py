
from dataclasses import dataclass, field

from attribute import Attribute
from damage import Damage
from weapon import Weapon


@dataclass
class Character:
    attributes: dict[Attribute, int]
    level: int = None
    weapon: Weapon = None
    armor_class: int = 10
    total_damage_taken: Damage = field(default_factory=Damage)
    action: bool = True
    bonus_action: bool = True
    reaction: bool = True
    interaction: bool = True

    def takes_damage(self, damage: Damage):
        self.total_damage_taken += damage

    def attribute_modifier(self, attribute: Attribute) -> int:
        return (self.attributes[attribute] - 10)//2

    def proficiency_bonus(self) -> int:
        """
        Return proficiency bonus (PB) depending on player character level

        Proficiency bonus increase every 4 levels, starting at +2 and finishing at +6
        """
        return 2 + (self.level - 1) // 4


from dataclasses import dataclass, field
from attribute import Attribute
from weapon import Weapon

@dataclass
class Character:
    attributes: dict[Attribute, int]
    level: int = None
    weapon: Weapon = None
    armor_class: int = 10

    def get_attribute_modifier(self, attribute: Attribute) -> int:
        return (self.attributes[attribute] - 10)//2

    def get_proficiency_bonus(self) -> int:
        """
        Return proficiency bonus (PB) depending on player character level

        Proficiency bonus increase every 4 levels, starting at +2 and finishing at +6
        """
        return 2 + (self.level - 1) // 4



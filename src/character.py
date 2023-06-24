
from dataclasses import dataclass, field

from action_cost import ActionCost
from attribute import Attribute
from damage import Damage
from weapon import Weapon


@dataclass
class Character:
    name: str
    attributes: dict[Attribute, int]
    action_availability: dict[ActionCost, bool] = field(init=False, default_factory=lambda: {action_cost: True for action_cost in ActionCost})
    level: int | None = None
    weapon: Weapon | None = None
    armor_class: int = 10
    total_damage_taken: list[Damage] = field(default_factory=list)
    current_spell_slots: list[int] = field(default_factory=lambda: [0]*8)
    maximum_spell_slots: list[int] = field(default_factory=lambda: [0]*8)

    def takes_damage(self, damage: Damage):
        self.total_damage_taken.append(damage)

    def attribute_modifier(self, attribute: Attribute) -> int:
        return (self.attributes[attribute] - 10)//2

    def proficiency_bonus(self) -> int:
        """
        Return proficiency bonus (PB) depending on player character level

        Proficiency bonus increase every 4 levels, starting at +2 and finishing at +6
        """
        assert self.level is not None
        return 2 + (self.level - 1) // 4

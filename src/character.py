
import logging
from dataclasses import dataclass, field

from ability import Ability, AbilitySkill
from action_cost import ActionCost
from damage import Damage
from probability import RandomVariable
from weapon import Weapon

LOGGER = logging.getLogger('dnd')

@dataclass
class Character:
    name: str
    ability_scores: dict[Ability, int]
    action_availability: dict[ActionCost, bool] = field(init=False, default_factory=lambda: {action_cost: True for action_cost in ActionCost})
    level: int | None = None
    weapon: Weapon | None = None
    armor_class: int = 10
    total_damage_taken: list[Damage] = field(default_factory=list)
    current_spell_slots: list[int] = field(default_factory=lambda: [0]*8)
    maximum_spell_slots: list[int] = field(default_factory=lambda: [0]*8)
    skill_proficiencies: AbilitySkill = AbilitySkill(0)
    skill_expertise: AbilitySkill = AbilitySkill(0)

    def takes_damage(self, damage: Damage) -> None:
        self.total_damage_taken.append(damage)

    def ability_modifier(self, ability: Ability) -> int:
        return (self.ability_scores[ability] - 10)//2

    def proficiency_bonus(self) -> int:
        """
        Return proficiency bonus (PB) depending on player character level

        Proficiency bonus increase every 4 levels, starting at +2 and finishing at +6
        """
        assert self.level is not None
        return 2 + (self.level - 1) // 4

    def ability_check(self, ability_skill: AbilitySkill) -> RandomVariable:
        """
        Fumble or Crit does not exist for saving throw or ability check
        """
        roll = RandomVariable.from_range(1, 20)
        roll += self.ability_modifier(ability_skill.ability())
        if ability_skill & self.skill_proficiencies:
            roll += self.proficiency_bonus()
        if ability_skill & self.skill_expertise:
            roll += self.proficiency_bonus()
        LOGGER.debug(f'Ability roll for {self.name} in {ability_skill} is {roll}')
        return roll

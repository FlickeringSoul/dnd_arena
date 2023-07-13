from dataclasses import dataclass

from action import ActionEvent, ActionModule, Attack
from action_cost import ActionCost
from event import Event
from weapon import Weapon


@dataclass
class WeaponAttack(ActionModule):
    weapon: Weapon

    def get_action_event(self) -> Event:
        assert self.origin_character is not None
        attack = Attack(
            damage=self.weapon.damage(),
            weapon_used=self.weapon
        )
        # If proficient with weapon !! -> TODO
        attack.roll_modifiers += self.origin_character.proficiency_bonus()
        attack.roll_modifiers += self.origin_character.ability_modifier(self.weapon.ability)
        attack.damage[self.weapon.damage_type] += self.origin_character.ability_modifier(self.weapon.ability)
        return ActionEvent(
            origin_character=self.origin_character,
            target=None,
            is_an_attack=True,
            is_a_spell=False,
            action_cost=ActionCost.ACTION,
            attack=attack,
            action_module=self.__class__,
        )
from dataclasses import dataclass

from action import ActionEvent, ActionModule
from action_cost import ActionCost
from dices import DiceBag
from event import Event
from weapon import Weapon


@dataclass
class WeaponAttack(ActionModule):
    weapon: Weapon

    def get_action_event(self) -> Event:
        assert self.origin_character is not None
        attack_mod = (DiceBag() +
            self.origin_character.proficiency_bonus() +
            self.origin_character.attribute_modifier(self.weapon.attribute))
        damage = self.weapon.damage()
        damage[self.weapon.damage_type] += self.origin_character.attribute_modifier(self.weapon.attribute)
        return ActionEvent(
            origin_character=self.origin_character,
            target=None,
            is_an_attack=True,
            is_a_spell=False,
            action_cost=ActionCost.ACTION,
            attack_damage=damage,
            attack_roll_modifiers = attack_mod,
            name=self.__class__,
            weapon_used=self.weapon
        )
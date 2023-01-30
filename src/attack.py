
from dataclasses import dataclass, field
from damage import Damage, RolledDamage
from attribute import Attribute
from character import Character
from dices import Dices
import utils
import logging


@dataclass
class Attack:
    attacker: Character
    target: Character
    is_an_attack: bool
    is_a_spell: bool
    damage: Damage
    action_type: type
    saving_throw: Attribute = None
    save_or_half: bool = False
    attack_bonus: int = 0
    dice_roll: int = Dices.d20.roll()

    def roll(self) -> RolledDamage:
        dice_roll = Dices.d20.roll()
        if self.is_an_attack:
            if dice_roll == 20:
                return self.damage.roll_crit()
            if dice_roll == 1:
                return RolledDamage()
            if dice_roll + self.attack_bonus >= self.target.armor_class:
                return self.damage.roll_normal()
            return RolledDamage()


def get_weapon_attack(attacker: Character) -> Attack:
    return Attack(
        is_an_attack=True,
        is_a_spell=False,
        damage=Damage(
            dice_damages=[(dice, attacker.weapon.damage_type) for dice in attacker.weapon.damage_dices],
            fix_damages=[(attacker.get_attribute_modifier(attacker.weapon.attribute), attacker.weapon.damage_type)]
        )
    )

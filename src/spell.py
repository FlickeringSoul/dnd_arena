
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import copy

from attack import Attack
from character import Character
from attribute import Attribute
from damage import Damage, DamageType
from dices import Dices
from action import Action

CANTRIP_THRESHOLD_LEVELS = [5, 11, 17]


def get_cantrip_multiplier(caster_level: int):
    multiplier = len([threshold for threshold in CANTRIP_THRESHOLD_LEVELS if caster_level >= threshold])
    return multiplier


@dataclass
class Spell(Action):
    spellcasting_ability: Attribute
    level: int = 0


class ProduceFlame(Spell):
    def get_attacks(self, caster: Character, target: Character) -> list[Attack]:
        spell_attack = Attack(
            is_an_attack=True,
            is_a_spell=True,
            damage=Damage(dice_damages=[(Dices.d8, DamageType.Fire)])
        )
        spell_attack.damage.dice_damages.extend([(Dices.d8, DamageType.Fire)] * get_cantrip_multiplier(caster.level))
        return [spell_attack]


class EldritchBlast(Spell):
    def get_attacks(self, caster: Character, target: Character) -> list[Attack]:
        single_blast = Attack(
            attacker=caster,
            target=target,
            action_type=self.__class__,
            is_an_attack=True,
            is_a_spell=True,
            damage=Damage(
                dice_damages=[(Dices.d10, DamageType.Force)]
            )
        )
        number_of_blast = 1 + get_cantrip_multiplier(caster.level)
        attacks = [copy.deepcopy(single_blast) for _ in range(number_of_blast)]
        return attacks


class GreenFlameBladeSingleTarget(Spell):
    def get_attacks(self, caster: Character, target: Character) -> list[Attack]:
        weapon_attack = caster.get_weapon_attack()
        extra_dices = [(Dices.d8, DamageType.Fire)] * get_cantrip_multiplier(caster.level)
        weapon_attack.damage.dice_damages.extend(extra_dices)
        return weapon_attack


class GreenFlameBladeTwoTargets(Spell):
    def get_attacks(self, caster: Character, target: Character) -> list[Attack]:
        weapon_attack = caster.get_weapon_attack()
        extra_dices = [(Dices.d8, DamageType.Fire)] * get_cantrip_multiplier(caster.level) * 2
        weapon_attack.damage.dice_damages.extend(extra_dices)
        weapon_attack.damage.fix_damages.append((caster.get_attribute_modifier(self.spellcasting_ability), DamageType.Fire))
        return weapon_attack


class MoonBeam(Spell):
    def get_attacks(self, caster: Character, target: Character) -> list[Attack]:
        damage_rolls = [(Dices.d10, DamageType.Radiant)] * self.level
        moonbeam = Attack(
            is_an_attack=False,
            is_a_spell=True,
            damage=Damage(dice_damages=damage_rolls),
            saving_throw=Attribute.Constitution
        )
        return moonbeam
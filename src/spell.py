
import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from action import Action, ActionCost, ActionEffect
from attribute import Attribute
from character import Character
from damage import Damage, DamageType
from dices import DiceBag, Dices


def cantrip_multiplier(caster_level: int) -> int:
    if 1 <= caster_level <= 4:
        return 1
    if 5 <= caster_level <= 10:
        return 2
    if 11 <= caster_level <= 16:
        return 3
    if 17 <= caster_level <= 20:
        return 4
    raise ValueError('Caster level must be between 1 and 20')


def spell_attack_bonus(character: Character, attribute: Attribute) -> int:
    return character.proficiency_bonus() + character.attribute_modifier(attribute)


@dataclass(kw_only=True)
class Spell(Action):
    spellcasting_ability: Attribute
    level: int = 0


class ProduceFlame(Spell):
    def get_action_event(self, origin: Character, target: Character) -> 'ActionEffect':
        dice_damages = [(Dices.d8, DamageType.Fire)] * cantrip_multiplier(origin.level)
        return ActionEffect(
            origin=origin,
            target=target,
            is_an_attack=True,
            is_a_spell=True,
            attack_damage=Damage(dice_damages=dice_damages),
            attack_roll_modifiers=spell_attack_bonus(origin, self.spellcasting_ability)
        )


@dataclass(kw_only=True)
class EldritchBlastBeam(Spell):
    action_cost: ActionCost = ActionCost.NONE
    number_of_uses: int

    def get_action_event(self, origin: Character, target: Character) -> 'ActionEffect':
        if self.number_of_uses <= 0:
            raise ValueError
        self.number_of_uses -= 1
        return ActionEffect(
            origin_character=origin,
            target=target,
            is_an_attack=True,
            is_a_spell=True,
            attack_damage=Damage({DamageType.Force: DiceBag() + Dices.d10}),
            attack_roll_modifiers=DiceBag() + spell_attack_bonus(origin, self.spellcasting_ability),
            name=self.__class__
        )


@dataclass(kw_only=True)
class EldritchBlast(Spell):
    action_cost: ActionCost = ActionCost.ACTION

    def get_action_event(self, origin: Character, target: Character) -> 'ActionEffect':
        number_of_blast = 1 + cantrip_multiplier(origin.level)
        eldritch_blast_beam = EldritchBlastBeam(
            spellcasting_ability=self.spellcasting_ability,
            number_of_uses=number_of_blast
        )
        first_beam = eldritch_blast_beam.get_action_event(origin, target)
        first_beam.new_actions = [eldritch_blast_beam]
        return first_beam




class GreenFlameBladeSingleTarget(Spell):
    def get_attacks(self, caster: Character, target: Character) -> list[ActionEffect]:
        weapon_attack = caster.get_weapon_attack()
        extra_dices = [(Dices.d8, DamageType.Fire)] * cantrip_multiplier(caster.level)
        weapon_attack.damage.dice_damages.extend(extra_dices)
        return weapon_attack


class GreenFlameBladeTwoTargets(Spell):
    def get_attacks(self, caster: Character, target: Character) -> list[ActionEffect]:
        weapon_attack = caster.get_weapon_attack()
        extra_dices = [(Dices.d8, DamageType.Fire)] * cantrip_multiplier(caster.level) * 2
        weapon_attack.damage.dice_damages.extend(extra_dices)
        weapon_attack.damage.fix_damages.append((caster.attribute_modifier(self.spellcasting_ability), DamageType.Fire))
        return weapon_attack


class MoonBeam(Spell):
    def get_attacks(self, caster: Character, target: Character) -> list[ActionEffect]:
        damage_rolls = [(Dices.d10, DamageType.Radiant)] * self.level
        moonbeam = ActionEffect(
            is_an_attack=False,
            is_a_spell=True,
            attack_damage=Damage(dice_damages=damage_rolls),
            saving_throw_attribute=Attribute.Constitution
        )
        return moonbeam
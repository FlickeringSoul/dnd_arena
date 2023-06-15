import logging
from dataclasses import dataclass

from action import ActionCost, ActionEvent, ActionModule
from attribute import Attribute
from character import Character
from damage import Damage, DamageType
from dices import DiceBag, Dices


def cantrip_scaling(caster_level: int) -> int:
    """Return the usual multiplier cantrip have that depends purely on total level and not class level

    Args:
        caster_level (int): Character level of the caster

    Raises:
        ValueError: When caster level is not between 1 and 20

    Returns:
        int: 1 to 4, depends on level
    """
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
class Spell(ActionModule):
    spellcasting_ability: Attribute
    level: int = 0


class ProduceFlame(Spell):
    def get_action_event(self, origin: Character, target: Character) -> 'ActionEvent':
        spell_damage = Damage()
        for _ in cantrip_scaling(origin.level):
            spell_damage[DamageType.Fire] += Dices.d8
        return ActionEvent(
            origin=origin,
            target=target,
            is_an_attack=True,
            is_a_spell=True,
            attack_damage=spell_damage,
            attack_roll_modifiers=spell_attack_bonus(origin, self.spellcasting_ability)
        )


@dataclass(kw_only=True)
class EldritchBlastBeam(Spell):
    action_cost: ActionCost = ActionCost.NONE
    number_of_uses: int

    def get_action_event(self, origin: Character, target: Character) -> 'ActionEvent':
        if self.number_of_uses <= 0:
            raise ValueError
        self.number_of_uses -= 1
        attack_damage = Damage()
        attack_damage[DamageType.Force] += Dices.d10
        return ActionEvent(
            origin_character=origin,
            target=target,
            is_an_attack=True,
            is_a_spell=True,
            attack_damage=attack_damage,
            attack_roll_modifiers=DiceBag() + spell_attack_bonus(origin, self.spellcasting_ability),
            name=self.__class__
        )


@dataclass(kw_only=True)
class EldritchBlast(Spell):
    action_cost: ActionCost = ActionCost.ACTION

    def get_action_event(self, origin: Character, target: Character) -> 'ActionEvent':
        number_of_blast = cantrip_scaling(origin.level)
        logging.debug(f'number_of_blast={number_of_blast}')
        eldritch_blast_beam = EldritchBlastBeam(
            spellcasting_ability=self.spellcasting_ability,
            number_of_uses=number_of_blast
        )
        first_beam = eldritch_blast_beam.get_action_event(origin, target)
        first_beam.new_actions = [eldritch_blast_beam]
        return first_beam




class GreenFlameBladeSingleTarget(Spell):
    def get_attacks(self, caster: Character, target: Character) -> list[ActionEvent]:
        weapon_attack = caster.get_weapon_attack()
        extra_dices = [(Dices.d8, DamageType.Fire)] * cantrip_scaling(caster.level)
        weapon_attack.damage.dice_damages.extend(extra_dices)
        return weapon_attack


class GreenFlameBladeTwoTargets(Spell):
    def get_attacks(self, caster: Character, target: Character) -> list[ActionEvent]:
        weapon_attack = caster.get_weapon_attack()
        extra_dices = [(Dices.d8, DamageType.Fire)] * cantrip_scaling(caster.level) * 2
        weapon_attack.damage.dice_damages.extend(extra_dices)
        weapon_attack.damage.fix_damages.append((caster.attribute_modifier(self.spellcasting_ability), DamageType.Fire))
        return weapon_attack


class MoonBeam(Spell):
    def get_attacks(self, caster: Character, target: Character) -> list[ActionEvent]:
        damage_rolls = [(Dices.d10, DamageType.Radiant)] * self.level
        moonbeam = ActionEvent(
            is_an_attack=False,
            is_a_spell=True,
            attack_damage=Damage(dice_damages=damage_rolls),
            saving_throw_attribute=Attribute.Constitution
        )
        return moonbeam
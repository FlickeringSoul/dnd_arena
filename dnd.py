
from fractions import Fraction
from dataclasses import dataclass
from enum import Enum, auto, IntEnum
from abc import ABC


class Dices(IntEnum):
    d4 = 4
    d6 = 6
    d8 = 8
    d10 = 10
    d12 = 12
    d20 = 20

    def avg(self):
        pass

    def probability_of_being_higher_or_equal_to(self, n: int):
        pass

    def roll(self):
        pass

CANTRIP_THRESHOLD_LEVELS = [5, 11, 17]

class DamageType(str, Enum):
    Fire = auto()

@dataclass
class Attack:
    is_an_attack: bool
    is_a_spell: bool
    is_ranged: bool
    damage_dices: list[Dices]
    has_advantage: bool = False
    has_disadvantage: bool = False
    is_

class Attacks(str, Enum):
    ProduceFlame = auto()
    EldritchBlast = auto()
    GrennFlameBlade = auto()

attacks = {
    Attacks.ProduceFlame: Attack(
        is_an_attack=True,
        is_a_spell=True,
        damage_dices=[(Dices.d8, DamageType.Fire)]
    )
}



def produce_flame(caster: 'CharacterStats', target: 'CharacterStats') -> 'Attack':
    return Attack(
        is_an_attack=True,
        is_a_spell=True,
        damage_dices=[Dices.d8]
    )




class Feature(ABC):
    """
    A feature is very broad. It can be a Feat, a class feature, a sub class feature, a racial trait
    a monster ability...
    """
    def on_critical_hit(self):
        pass


@dataclass
class CharacterStats:
    level: int
    proficiency_bonus: int

'''
OLD STUFF BELOW
'''

class ClassName(str, Enum):
    Barbarian = auto()
    Fighter = auto()
    Rogue = auto()

@dataclass
class PlayerCharacter:
    class_name: ClassName
    level: int = 1
    additional_feats_taken: int = 0

    def proficiency_bonus(self) -> int:
        """
        Return proficiency bonus (PB) depending on player character level

        Proficiency bonus increase every 4 levels, starting at +2 and finishing at +6
        """
        return 2 + (self.level - 1) // 4

    def abillity_score_improvements(self) -> int:
        """
        Return how many ASI the caracter has received.

        Ability Score Improvement (ASI) is a class feature that appear for most classes at levels
        4, 8, 12, 16 and 19

        The only two execption is Fighter which as ASI also at levels 6 and 14
        And Rogue which as ASI at level 10
        """
        ASI_levels = [4, 8, 12, 16, 19]
        if self.class_name is ClassName.Fighter:
            ASI_levels.extend([6, 14])
        if self.class_name is ClassName.Rogue:
            ASI_levels.append(10)
        # Count how many ASI_levels are below or equal current level
        return len([ASI_level for ASI_level in ASI_levels if ASI_level <= self.level])

    def attribute_modifier(self) -> int:
        """
        Retrun attribute modifier (noted AM or mod. or att.mod.) depending on level and how many feats

        Ability Score Improvement (ASI) is a class feature that appear for most classes at levels
        4, 8, 12, 16 and 19

        The only two execption is Fighter which as ASI also at levels 6 and 14
        And Rogue which as ASI at level 10
        """
        base_attribute_modifier = 3
        asi_bonus = min(max(self.abillity_score_improvements() - self.additional_feats_taken, 0), 5)
        return base_attribute_modifier + asi_bonus

    def attack_bonus(self) -> int:
        """
        Return attack bonus (AB) to be added to an attack rool
        """
        return self.proficiency_bonus() + self.attribute_modifier()

    def critical_dices(self) -> int:
        """
        Return how many faces on a d20 is a critical
        """
        return 1

    def probability_of_normal_hit(self, target_armor_class: int) -> Fraction:
        """
        Return the probability of a normal hit

        To hit, the attack roll + attack bonus must be equal or higher than target AC
        If we note hit_difficulty = taget's AC - Attack Bonus,
        then, the attack roll must higher or equal to hit_difficulty

        And:
            * 1 is alawys a failure
            * A critical hit is alwas a hit, no matter the target AC (and not a normal hit)

        A normal hit is an attack roll between [2,19] (if critical hit chance is normal)
        higher or equal to hit_difficulty

        """
        hit_difficulty = target_armor_class - self.attack_bonus()
        # If hit difficulty is so low that any roll execpt 1 and critical would hit
        if hit_difficulty <= 2:
            return Fraction(19 - self.critical_dices()/20)
        # If hit difficulty is so high that only a crit would hit
        if hit_difficulty >= 21 - self.critical_dices():
            return Fraction(0)
        # number_of_possible_outcomes is range(hit_difficulty, 21 - self.critical_dices()
        return Fraction(21 - hit_difficulty - self.critical_dices(), 20)

    def probability_of_missing(self, target_armor_class: int) -> Fraction:
        hit_difficulty = target_armor_class - self.attack_bonus()
        # If hit difficulty is so low that any roll execpt 1 would hit
        if hit_difficulty <= 2:
            return Fraction(1, 20)
        # If hit difficulty is so high that only a crit would hit
        if hit_difficulty >= 21 - self.critical_dices():
            return Fraction(20 - self.critical_dices(), 20)
        # Else, hit_difficulty between 3 and 19*
        return Fraction(hit_difficulty - 1, 20)

    def probability_of_not_critical(self):
        return Fraction(20 - self.critical_dices(), 20)





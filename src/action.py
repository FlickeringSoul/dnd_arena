import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from fractions import Fraction
from typing import Optional

from attribute import Attribute
from character import Character
from damage import Damage
from dices import DiceBag, Dices
from event import Event, EventTypes, RandomOutcome
from probability import RandomVariable


class ActionCost(Enum):
    ACTION = auto()
    BONUS_ACTION = auto()
    REACTION = auto()
    INTERACTION = auto()
    NONE = auto()



class ActionSteps(Enum):
    BEFORE_ACTION = auto() # Counter spell

    BEFORE_ATTACK = auto()
    REGULAR_HIT = auto()
    REGULAR_MISS = auto()
    CRIT = auto()
    FUMBLE = auto()

    BEFORE_SAVING_THROW = auto()
    SUCCESSFUL_SAVE = auto()
    FAIL_SAVE = auto()

    BEFORE_CONTEST = auto()
    CONTEST_SUCCESS = auto()
    CONTEST_FAILURE = auto()

    AFTER_ACTION = auto() # any uses ??? Riposte, Sentinel ?
    END = auto()


@dataclass(kw_only=True)
class Action(ABC):
    action_cost: ActionCost

    @abstractmethod
    def get_action_effect(self, origin: Character, target: Character) -> 'ActionEffect':
        pass


@dataclass(kw_only=True)
class ActionEffect(Event):
    target: Character
    is_an_attack: bool
    is_a_spell: bool
    attack_damage: Damage
    attack_roll_modifiers: DiceBag = field(default_factory=DiceBag)
    saving_roll_modifiers: DiceBag = field(default_factory=DiceBag)
    current_action_step: ActionSteps = ActionSteps.BEFORE_ACTION
    new_actions: list[Action] = field(default_factory=list)
    saving_throw_attribute: Attribute = None
    save_or_half: bool = False
    difficulty_class: int = None # Saving Throw DC
    name: type


    def outcomes(self) -> list[RandomOutcome]:
        if self.current_action_step is ActionSteps.BEFORE_ACTION:
            return []
        elif self.current_action_step is ActionSteps.BEFORE_ATTACK:
            attack_roll_without_modifiers = RandomVariable.from_range(1, 20)
            fumble_outcome = RandomOutcome(
                probability=attack_roll_without_modifiers.probability_of_being_between(1, 1),
                name=ActionSteps.FUMBLE
            )
            crit_outcome = RandomOutcome(
                probability=attack_roll_without_modifiers.probability_of_being_between(20, 20),
                name=ActionSteps.CRIT
            )
            normal_attack_probability = 1 - fumble_outcome.probability - crit_outcome.probability
            normal_attack_roll_with_modifiers = RandomVariable.from_range(2, 19) + self.attack_roll_modifiers.as_random_variable()
            regular_hit_outcome = RandomOutcome(
                probability=normal_attack_roll_with_modifiers.probability_of_being_superior_or_equal_to(self.target.armor_class) * normal_attack_probability,
                name=ActionSteps.REGULAR_HIT
            )
            regular_miss_outcome = RandomOutcome(
                probability=1 - fumble_outcome.probability - crit_outcome.probability - regular_hit_outcome.probability,
                name=ActionSteps.REGULAR_MISS
            )
            return [fumble_outcome, crit_outcome, regular_hit_outcome, regular_miss_outcome]
        elif self.current_action_step is ActionSteps.AFTER_ACTION:
            return []
        elif self.current_action_step in [ActionSteps.FUMBLE, ActionSteps.REGULAR_MISS, ActionSteps.REGULAR_HIT, ActionSteps.CRIT]:
            return []
        raise NotImplementedError(f'Not implemented for self.current_action_step={self.current_action_step}')

    def apply_outcome(self, outcome: RandomOutcome) -> None:
        logging.debug(f'Calling apply outcome with outcome={outcome} and self.current_action_step={self.current_action_step}')
        if self.current_action_step is ActionSteps.BEFORE_ACTION:
            assert(outcome is None)
            self.current_action_step = ActionSteps.BEFORE_ATTACK
            return

        elif self.current_action_step is ActionSteps.BEFORE_ATTACK:
            assert(outcome is not None)
            self.current_action_step = outcome.name
            if outcome.name is ActionSteps.CRIT:
                # How do we deal with adamantite armor or any feature like that ??
                self.attack_damage = self.attack_damage.as_critical()
            return

        elif self.current_action_step is ActionSteps.REGULAR_HIT:
            assert(outcome is None)
            self.current_action_step = ActionSteps.AFTER_ACTION
            self.target.takes_damage(self.attack_damage)
            # Apply effect ??
            return

        elif self.current_action_step is ActionSteps.REGULAR_MISS:
            assert(outcome is None)
            self.current_action_step = ActionSteps.AFTER_ACTION
            return

        elif self.current_action_step is ActionSteps.FUMBLE:
            assert(outcome is None)
            self.current_action_step = ActionSteps.AFTER_ACTION
            return

        elif self.current_action_step is ActionSteps.CRIT:
            assert(outcome is None)
            self.current_action_step = ActionSteps.AFTER_ACTION
            self.target.takes_damage(self.attack_damage)
            return

        elif self.current_action_step is ActionSteps.AFTER_ACTION:
            assert(outcome is None)
            self.current_action_step = ActionSteps.END
            return

        elif self.current_action_step is ActionSteps.AFTER_ACTION:
            raise ValueError
        raise NotImplementedError


class EndOfTurn(Action):
    action_cost: ActionCost = ActionCost.NONE

    def get_action_effect(self, origin: Character, target: Character) -> 'ActionEffect':
        return super().get_action_effect(origin, target)


def get_weapon_attack(attacker: Character) -> ActionEffect:
    return ActionEffect(
        is_an_attack=True,
        is_a_spell=False,
        attack_damage=Damage(
            dice_damages=[(dice, attacker.weapon.damage_type) for dice in attacker.weapon.damage_dices],
            fix_damages=[(attacker.attribute_modifier(attacker.weapon.attribute), attacker.weapon.damage_type)]
        )
    )

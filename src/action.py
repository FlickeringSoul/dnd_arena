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
from event import EndOfTurnEvent, Event, EventSteps, RandomOutcome
from probability import RandomVariable


class ActionCost(Enum):
    ACTION = auto()
    BONUS_ACTION = auto()
    REACTION = auto()
    INTERACTION = auto()
    NONE = auto()



@dataclass(kw_only=True)
class Action(ABC):
    action_cost: ActionCost

    @abstractmethod
    def get_action_event(self, origin: Character, target: Character) -> 'Event':
        pass


@dataclass(kw_only=True)
class ActionEffect(Event):
    target: Character
    is_an_attack: bool
    is_a_spell: bool
    attack_damage: Damage
    attack_roll_modifiers: DiceBag = field(default_factory=DiceBag)
    saving_roll_modifiers: DiceBag = field(default_factory=DiceBag)
    new_actions: list[Action] = field(default_factory=list)
    saving_throw_attribute: Attribute = None
    save_or_half: bool = False
    difficulty_class: int = None # Saving Throw DC
    name: type


    def outcomes(self) -> list[RandomOutcome]:
        if self.event_step in [EventSteps.BEFORE_EVENT, EventSteps.AFTER_EVENT, EventSteps.FUMBLE, EventSteps.REGULAR_MISS, EventSteps.REGULAR_HIT, EventSteps.CRIT]:
            return []
        elif self.event_step is EventSteps.BEFORE_ATTACK:
            attack_roll_without_modifiers = RandomVariable.from_range(1, 20)
            fumble_outcome = RandomOutcome(
                probability=attack_roll_without_modifiers.probability_of_being_between(1, 1),
                name=EventSteps.FUMBLE
            )
            crit_outcome = RandomOutcome(
                probability=attack_roll_without_modifiers.probability_of_being_between(20, 20),
                name=EventSteps.CRIT
            )
            normal_attack_probability = 1 - fumble_outcome.probability - crit_outcome.probability
            normal_attack_roll_with_modifiers = RandomVariable.from_range(2, 19) + self.attack_roll_modifiers.as_random_variable()
            regular_hit_outcome = RandomOutcome(
                probability=normal_attack_roll_with_modifiers.probability_of_being_superior_or_equal_to(self.target.armor_class) * normal_attack_probability,
                name=EventSteps.REGULAR_HIT
            )
            regular_miss_outcome = RandomOutcome(
                probability=1 - fumble_outcome.probability - crit_outcome.probability - regular_hit_outcome.probability,
                name=EventSteps.REGULAR_MISS
            )
            return [fumble_outcome, crit_outcome, regular_hit_outcome, regular_miss_outcome]
        raise NotImplementedError(f'Not implemented for self.current_action_step={self.event_step}')

    def apply_outcome(self, outcome: RandomOutcome) -> None:
        logging.debug(f'Calling apply outcome with outcome={outcome} and self.current_action_step={self.event_step}')
        next_step_dict = {
            EventSteps.BEFORE_EVENT: EventSteps.BEFORE_ATTACK,
            EventSteps.BEFORE_ATTACK: [EventSteps.REGULAR_HIT, EventSteps.REGULAR_MISS, EventSteps.FUMBLE, EventSteps.CRIT],
            EventSteps.FUMBLE: EventSteps.AFTER_EVENT,
            EventSteps.REGULAR_MISS: EventSteps.AFTER_EVENT,
            EventSteps.REGULAR_HIT: EventSteps.AFTER_EVENT,
            EventSteps.CRIT: EventSteps.AFTER_EVENT,
            EventSteps.AFTER_EVENT: EventSteps.END
        }
        next_action_steps = next_step_dict[self.event_step]
        if self.event_step is EventSteps.BEFORE_ATTACK:
            assert(outcome.name in next_action_steps)
            self.event_step = outcome.name
        else:
            assert(outcome is None)
            if self.event_step in [EventSteps.REGULAR_HIT, EventSteps.CRIT]:
                self.target.takes_damage(self.attack_damage)
            self.event_step = next_action_steps
        if self.event_step is EventSteps.CRIT:
            self.attack_damage = self.attack_damage.as_critical()
        return


@dataclass
class EndOfTurnAction(Action):
    action_cost: ActionCost = ActionCost.NONE

    def get_action_event(self, origin: Character, target: Character) -> 'Event':
        return EndOfTurnEvent(origin_character=origin)


def get_weapon_attack(attacker: Character) -> ActionEffect:
    return ActionEffect(
        is_an_attack=True,
        is_a_spell=False,
        attack_damage=Damage(
            dice_damages=[(dice, attacker.weapon.damage_type) for dice in attacker.weapon.damage_dices],
            fix_damages=[(attacker.attribute_modifier(attacker.weapon.attribute), attacker.weapon.damage_type)]
        )
    )

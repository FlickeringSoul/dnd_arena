import logging
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Optional

from action_cost import ActionCost
from attribute import Attribute
from character import Character
from damage import Damage
from dices import DiceBag
from event import Choice, Event, EventSteps, RandomOutcome
from module import Module
from probability import RandomVariable


@dataclass(kw_only=True)
class ActionEvent(Event):
    target: Optional[Character] = None # What about AoE and cells ? -> None mean we need to define target later
    is_an_attack: bool
    is_a_spell: bool
    action_cost: ActionCost
    attack_damage: Damage
    attack_roll_modifiers: DiceBag = field(default_factory=DiceBag)
    saving_roll_modifiers: DiceBag = field(default_factory=DiceBag)
    saving_throw_attribute: Attribute | None = None
    save_or_half: bool = False
    difficulty_class: int | None = None # Saving Throw DC
    name: type
    on_action_selected_callback: Callable[[], None] = lambda: None

    def get_possible_outcomes(self) -> list[RandomOutcome] | None:
        assert self.target is not None
        if self.event_step in [EventSteps.BEFORE_EVENT, EventSteps.AFTER_EVENT, EventSteps.FUMBLE, EventSteps.REGULAR_MISS, EventSteps.REGULAR_HIT, EventSteps.CRIT]:
            return None
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

    def do_outcome(self, outcome: RandomOutcome | Choice | None) -> None:
        logging.debug(f'Calling apply outcome with outcome={outcome} and self.current_action_step={self.event_step}')
        next_step_dict: dict[EventSteps, EventSteps | list[EventSteps]] = {
            EventSteps.BEFORE_EVENT: EventSteps.BEFORE_ATTACK,
            EventSteps.BEFORE_ATTACK: [EventSteps.REGULAR_HIT, EventSteps.REGULAR_MISS, EventSteps.FUMBLE, EventSteps.CRIT],
            EventSteps.FUMBLE: EventSteps.AFTER_EVENT,
            EventSteps.REGULAR_MISS: EventSteps.AFTER_EVENT,
            EventSteps.REGULAR_HIT: EventSteps.AFTER_EVENT,
            EventSteps.CRIT: EventSteps.AFTER_EVENT,
            EventSteps.AFTER_EVENT: EventSteps.END
        }
        next_action_steps = next_step_dict[self.event_step]
        self.event_processing_module_index = 0
        if self.event_step is EventSteps.BEFORE_ATTACK:
            assert isinstance(outcome, RandomOutcome)
            assert outcome.name in next_action_steps
            self.event_step = outcome.name
        else:
            assert(outcome is None)
            if self.event_step in [EventSteps.REGULAR_HIT, EventSteps.CRIT]:
                assert self.target is not None
                self.target.takes_damage(self.attack_damage)
            assert isinstance(next_action_steps, EventSteps)
            self.event_step = next_action_steps
        if self.event_step is EventSteps.CRIT:
            self.attack_damage = self.attack_damage.as_critical()
        return


@dataclass(kw_only=True)
class ChoosingActionEvent(Event):
    possible_actions: list[Event] = field(init=False, default_factory=list) # Field will be filled by modules


class ActionModule(Module):
    @abstractmethod
    def get_action_event(self) -> Event:
        pass

    def on_event(self, event: Event, chosen_outcome: RandomOutcome | Choice | None) -> Event | None:
        if not isinstance(event, ChoosingActionEvent) or event.event_step != EventSteps.AFTER_EVENT or event.origin_character != self.origin_character:
            return None
        possible_action = self.get_action_event()
        if is_event_cost_available(possible_action):
            event.possible_actions.append(self.get_action_event())
        return None

def is_event_cost_available(event: Event) -> bool:
    match event:
        case ActionEvent(action_cost=ActionCost.NONE):
            return True
        case ActionEvent():
            return event.origin_character.action_availability[event.action_cost]
        case _: # EndOfTurn case
            return True

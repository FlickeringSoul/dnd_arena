import logging
from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional

from ability import Ability, AbilitySkill
from action_cost import ActionCost
from character import Character
from damage import Damage
from dices import DiceBag
from event import Choice, Event, EventSteps, RandomOutcome
from module import Module
from probability import RandomVariable, advantage_disadvantage
from weapon import Weapon

LOGGER = logging.getLogger('dnd')

@dataclass
class AbilityContest:
    originator_ability_skill: AbilitySkill
    target_ability_skill: AbilitySkill
    origin_advantage: bool = False
    origin_disadvantage: bool = False
    target_advantage: bool = False
    target_disadvantage: bool = False

    def get_random_outcomes(self, origin_character: Character, target: Character) -> list[RandomOutcome]:
        contester_roll = origin_character.ability_check(self.originator_ability_skill)
        contester_roll = advantage_disadvantage(contester_roll, self.origin_advantage, self.origin_disadvantage)
        contested_roll = target.ability_check(self.target_ability_skill)
        contested_roll = advantage_disadvantage(contested_roll, self.target_advantage, self.target_disadvantage)
        final_roll = contester_roll - contested_roll
        contest_success_probability = final_roll.probability_of_being_superior_or_equal_to(1)
        success_outcome = RandomOutcome(
            probability=contest_success_probability,
            name=EventSteps.CONTEST_SUCCESS
        )
        failure_outcome = RandomOutcome(
            probability=(1 - contest_success_probability),
            name=EventSteps.CONTEST_FAILURE
        )
        return [success_outcome, failure_outcome]

@dataclass
class Attack:
    damage: Damage = field(default_factory=Damage)
    advantage: bool = False
    disadvantage: bool = False
    roll_modifiers: DiceBag = field(default_factory=DiceBag)
    weapon_used: Weapon | None = None

    def get_random_outcomes(self, target_armor_class: int) -> list[RandomOutcome]:
        attack_roll_without_modifiers = advantage_disadvantage(
            RandomVariable.from_range(1, 20),
            self.advantage,
            self.disadvantage
        )
        fumble_outcome = RandomOutcome(
            probability=attack_roll_without_modifiers.probability_of_being_between(1, 1),
            name=EventSteps.FUMBLE
        )
        crit_outcome = RandomOutcome(
            probability=attack_roll_without_modifiers.probability_of_being_between(20, 20),
            name=EventSteps.CRIT
        )
        attack_roll_with_modifiers = attack_roll_without_modifiers + self.roll_modifiers.as_random_variable()
        regular_hit_outcome = RandomOutcome(
            probability=attack_roll_with_modifiers.probability_of_being_superior_or_equal_to(target_armor_class) - crit_outcome.probability,
            name=EventSteps.REGULAR_HIT
        )
        regular_miss_outcome = RandomOutcome(
            probability=1 - fumble_outcome.probability - crit_outcome.probability - regular_hit_outcome.probability,
            name=EventSteps.REGULAR_MISS
        )
        return [fumble_outcome, crit_outcome, regular_hit_outcome, regular_miss_outcome]


@dataclass
class SavingThrow:
    ability: Ability
    difficulty_class: int # Saving Throw DC
    damage: Damage = field(default_factory=Damage)
    advantage: bool = False
    disadvantage: bool = False
    roll_modifiers: DiceBag = field(default_factory=DiceBag)
    save_or_half: bool = False


ACTION_WORKFLOW: dict[EventSteps, EventSteps | list[EventSteps]] = {
    EventSteps.BEFORE_EVENT: [
        EventSteps.BEFORE_ATTACK,
        EventSteps.BEFORE_SAVING_THROW,
        EventSteps.BEFORE_CONTEST
    ],
    EventSteps.BEFORE_ATTACK: [
        EventSteps.REGULAR_HIT,
        EventSteps.REGULAR_MISS,
        EventSteps.FUMBLE,
        EventSteps.CRIT
    ],
    EventSteps.FUMBLE: EventSteps.AFTER_EVENT,
    EventSteps.REGULAR_MISS: EventSteps.AFTER_EVENT,
    EventSteps.REGULAR_HIT: [
        EventSteps.AFTER_EVENT,
        EventSteps.BEFORE_SAVING_THROW
    ],
    EventSteps.CRIT: [
        EventSteps.AFTER_EVENT,
        EventSteps.BEFORE_SAVING_THROW
    ],
    EventSteps.BEFORE_SAVING_THROW: [
        EventSteps.FAIL_SAVE,
        EventSteps.SUCCESSFUL_SAVE
    ],
    EventSteps.FAIL_SAVE: EventSteps.AFTER_EVENT,
    EventSteps.SUCCESSFUL_SAVE: EventSteps.AFTER_EVENT,
    EventSteps.BEFORE_CONTEST: [
        EventSteps.CONTEST_FAILURE,
        EventSteps.CONTEST_SUCCESS
    ],
    EventSteps.CONTEST_FAILURE: EventSteps.AFTER_EVENT,
    EventSteps.CONTEST_SUCCESS: EventSteps.AFTER_EVENT,
    EventSteps.AFTER_EVENT: EventSteps.END
}

class WorkFlowPattern(Enum):
    ATTACK = auto()
    ATTACK_SAVE = auto()
    SAVE = auto()
    CONTEST = auto()

    def before_event_follow_up(self):
        match self:
            case WorkFlowPattern.ATTACK | WorkFlowPattern.ATTACK_SAVE:
                return EventSteps.BEFORE_ATTACK
            case WorkFlowPattern.SAVE:
                return EventSteps.BEFORE_SAVING_THROW
            case WorkFlowPattern.CONTEST:
                return EventSteps.BEFORE_CONTEST
            case _:
                raise NotImplementedError(f'Function not implemented for event step = {self}')

    def next_step(self, current_step: EventSteps) -> EventSteps:
        match current_step, self:
            case EventSteps.BEFORE_EVENT, (WorkFlowPattern.ATTACK | WorkFlowPattern.ATTACK_SAVE):
                return EventSteps.BEFORE_ATTACK
            case EventSteps.BEFORE_EVENT, WorkFlowPattern.SAVE:
                return EventSteps.BEFORE_SAVING_THROW
            case EventSteps.BEFORE_EVENT, WorkFlowPattern.CONTEST:
                return EventSteps.BEFORE_CONTEST
            case EventSteps.REGULAR_HIT | EventSteps.CRIT, WorkFlowPattern.ATTACK_SAVE:
                return EventSteps.BEFORE_SAVING_THROW
            case EventSteps.REGULAR_HIT | EventSteps.CRIT | EventSteps.REGULAR_MISS | EventSteps.FUMBLE | EventSteps.SUCCESSFUL_SAVE | EventSteps.FAIL_SAVE | EventSteps.CONTEST_FAILURE | EventSteps.CONTEST_SUCCESS, _:
                return EventSteps.AFTER_EVENT
            case EventSteps.AFTER_EVENT, _:
                return EventSteps.END
        raise NotImplementedError(f'There is no deterministic implemented next step for {self=}, {current_step=}')



@dataclass(kw_only=True)
class ActionEvent(Event):
    is_an_attack: bool
    is_a_spell: bool
    action_cost: ActionCost
    action_module: type
    attack: Attack | None = None
    saving_throw: SavingThrow | None = None
    ability_contest: AbilityContest | None = None
    on_action_selected_callback: Callable[[], None] = lambda: None
    target: Optional[Character] = None # What about AoE and cells ? -> None mean we need to define target later

    def workflow_pattern(self):
        if self.attack is not None and self.saving_throw is not None:
            return WorkFlowPattern.ATTACK_SAVE
        if self.attack:
            return WorkFlowPattern.ATTACK
        if self.saving_throw:
            return WorkFlowPattern.SAVE
        if self.ability_contest:
            return WorkFlowPattern.CONTEST

    def get_possible_outcomes(self) -> list[RandomOutcome] | None:
        assert self.target is not None
        if self.event_step is EventSteps.BEFORE_ATTACK:
            return self.__get_possible_attack_outcomes()
        if self.event_step is EventSteps.BEFORE_CONTEST:
            return self.__get_possible_contest_outcomes()
        return

    def __get_possible_contest_outcomes(self) -> list[RandomOutcome]:
        assert self.origin_character is not None
        assert self.target is not None
        assert self.ability_contest is not None
        return self.ability_contest.get_random_outcomes(self.origin_character, self.target)

    def __get_possible_attack_outcomes(self) -> list[RandomOutcome]:
        assert self.event_step is EventSteps.BEFORE_ATTACK
        assert self.attack is not None
        assert self.target is not None
        return self.attack.get_random_outcomes(self.target.armor_class)

    def do_outcome(self, outcome: RandomOutcome | Choice | None) -> None:
        LOGGER.debug(f'Calling apply outcome with outcome={outcome} and self.current_action_step={self.event_step}')
        self.event_processing_module_index = 0
        if isinstance(outcome, RandomOutcome):
            # Workflow verification
            next_action_steps = ACTION_WORKFLOW[self.event_step]
            assert isinstance(next_action_steps, list)
            assert outcome.name in next_action_steps
            self.event_step = outcome.name
            if self.event_step is EventSteps.CRIT:
                assert self.attack is not None
                self.attack.damage = self.attack.damage.as_critical()
        else:
            assert outcome is None
            if self.event_step in [EventSteps.REGULAR_HIT, EventSteps.CRIT]:
                assert self.target is not None
                assert self.attack is not None
                self.target.takes_damage(self.attack.damage)
            self.event_step = self.workflow_pattern().next_step(self.event_step)


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

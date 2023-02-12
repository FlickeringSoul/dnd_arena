from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from fractions import Fraction
from typing import Optional

from character import Character


@dataclass
class ActionChoice:
    action_index: int
    target: Character


@dataclass
class FeatureChoice:
    activate: bool


@dataclass
class RandomOutcome:
    probability: Fraction
    name: Enum


class EventSteps(Enum):
    BEFORE_EVENT = auto() # Counter spell

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

    AFTER_EVENT = auto() # any uses ??? Riposte, Sentinel ?
    END = auto()


@dataclass(kw_only=True)
class Event(ABC):
    origin_character: Character
    current_creature_index: int = 0
    current_feature_index: int = 0
    event_step: EventSteps = EventSteps.BEFORE_EVENT

    @abstractmethod
    def outcomes(self) -> list[RandomOutcome]:
        return []

    @abstractmethod
    def apply_outcome(self, outcome: RandomOutcome) -> None:
        assert(outcome is None)
        next_step_dict = {
            EventSteps.BEFORE_EVENT: EventSteps.AFTER_EVENT,
            EventSteps.AFTER_EVENT: EventSteps.END
        }
        self.event_step = next_step_dict[self.event_step]


class EventListener(ABC):
    @abstractmethod
    def outcomes(self, event: Event) -> list[RandomOutcome | FeatureChoice]:
        pass

    @abstractmethod
    def apply_outcome(self, event: Event, outcome: Optional[RandomOutcome | FeatureChoice]) -> Optional[Event]:
        pass


'''
class EventTypes(Enum):
    END_OF_TURN = auto()
    START_OF_TURN = auto()
    ACTION_EFFECT = auto()
    MOVE = auto()
    LEVEL_UP = auto()
    SWITCHING_WEAPON = auto()
'''

class EndOfTurnEvent(Event):
    def outcomes(self) -> list[RandomOutcome]:
        return super().outcomes()

    def apply_outcome(self, outcome: RandomOutcome) -> None:
        return super().apply_outcome(outcome)


class StartOfTurnEvent(Event):
    def outcomes(self) -> list[RandomOutcome]:
        return super().outcomes()

    def apply_outcome(self, outcome: RandomOutcome) -> None:
        return super().apply_outcome(outcome)

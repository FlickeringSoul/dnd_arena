from abc import ABC
from dataclasses import dataclass, field
from enum import Enum, auto
from fractions import Fraction

from character import Character


@dataclass
class RandomOutcome:
    name: 'EventSteps'
    probability: Fraction


@dataclass
class Choice:
    name: str
    choice: 'Event'

Outcome = RandomOutcome | Choice


class EventSteps(str, Enum):
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
    event_processing_module_index: int = field(init=False, default=0)
    event_step: EventSteps = field(init=False, default=EventSteps.BEFORE_EVENT)

    def get_possible_outcomes(self) -> list[RandomOutcome] | None:
        return None

    def do_outcome(self, outcome: RandomOutcome | Choice | None) -> None:
        next_step_dict = {
            EventSteps.BEFORE_EVENT: EventSteps.AFTER_EVENT,
            EventSteps.AFTER_EVENT: EventSteps.END
        }
        self.event_step = next_step_dict[self.event_step]
        self.event_processing_module_index = 0


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
    pass


class StartOfTurnEvent(Event):
    pass

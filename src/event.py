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


class EventTypes:
    END_OF_TURN = auto()
    START_OF_TURN = auto()
    ACTION_EFFECT = auto()
    WILLING_MOVE = auto()
    FORCED_MOVE = auto()
    LEVEL_UP = auto()
    SWITCHING_WEAPON = auto()


@dataclass(kw_only=True)
class Event(ABC):
    origin_character: Character
    current_creature_index: int = 0
    current_feature_index: int = 0

    @abstractmethod
    def outcomes(self) -> list[RandomOutcome]:
        pass

    @abstractmethod
    def apply_outcome(self, outcome: RandomOutcome) -> None:
        pass


class EventListener(ABC):

    @abstractmethod
    def outcomes(self, event: Event) -> list[RandomOutcome | FeatureChoice]:
        pass

    @abstractmethod
    def apply_outcome(self, event: Event, outcome: Optional[RandomOutcome | FeatureChoice]) -> Optional[Event]:
        pass

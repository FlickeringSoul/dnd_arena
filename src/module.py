from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from character import Character
from event import Choice, Event, RandomOutcome


@dataclass(kw_only=True)
class Module(ABC):
    """
    Abstract class for all event driven system like Features or Actions
    """
    origin_character: Optional[Character] = None
    target_character: Optional[Character] = None
    to_delete: bool = False

    def get_possibilities_on_event(self, event: Event) -> list[RandomOutcome] | list[Choice] | None:
        pass

    @abstractmethod
    def on_event(self, event: Event, chosen_outcome: RandomOutcome | Choice | None) -> Optional[Event]:
        pass

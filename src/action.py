

from attack import Attack
from dataclasses import dataclass
from abc import ABC, abstractmethod
from character import Character

@dataclass
class Action(ABC):
    @abstractmethod
    def get_attacks(self, origin: Character, target: Character) -> list[Attack]:
        pass

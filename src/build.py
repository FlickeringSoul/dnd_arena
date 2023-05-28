from dataclasses import dataclass

from character import Character
from module import Module


@dataclass
class Build:
    character: Character
    modules: list[Module]
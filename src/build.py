from dataclasses import dataclass, field

from character import Character
from module import Module


@dataclass
class Build:
    characters: list[Character] = field(default_factory=list)
    modules: list[Module] = field(default_factory=list)
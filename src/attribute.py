
from enum import Enum, auto
from dataclasses import dataclass

class Attribute(str, Enum):
    Strength = auto()
    Dexterity = auto()
    Constitution = auto()
    Intelligence = auto()
    Wisdom = auto()
    Charisma = auto()

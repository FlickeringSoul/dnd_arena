from enum import Enum, auto


class ActionCost(Enum):
    ACTION = auto()
    BONUS_ACTION = auto()
    REACTION = auto()
    INTERACTION = auto()
    NONE = auto()
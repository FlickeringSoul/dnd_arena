from enum import Enum, auto


class Attribute(str, Enum):
    Strength = auto()
    Dexterity = auto()
    Constitution = auto()
    Intelligence = auto()
    Wisdom = auto()
    Charisma = auto()

### p.13 of BHB -> VARIANT: Customizing Ability Scores
### 27 points to spend

STARTING_ATTRIBUTE_COST = {
    8: 0,
    9: 1,
    10: 2,
    11: 3,
    12: 4,
    13: 5,
    14: 7,
    15: 9
}

def verify_starting_attributes(starting_attributes: dict[Attribute, int]):
    '''
    Check if given set of attributes respect rules
    '''
    cost = 0
    for value in starting_attributes.values():
        cost += STARTING_ATTRIBUTE_COST[value]
    if cost != 27:
        raise ValueError(f'Starting attributes total cost is not compliant: {cost} != 27')

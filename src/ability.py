from enum import Enum, Flag, auto


class Ability(str, Enum):
    Strength = auto()
    Dexterity = auto()
    Constitution = auto()
    Intelligence = auto()
    Wisdom = auto()
    Charisma = auto()


class AbilitySkill(Flag):
    # Strength
    Athletics = auto()
    # Dexterity
    Acrobatics = auto()
    Sleight_of_Hand = auto()
    Stealth = auto()
    # Constitution (lol)
    # Intelligence
    Arcana = auto()
    History = auto()
    Investigation = auto()
    Nature = auto()
    Religion = auto()
    # Wisdom
    Animal_Handling = auto()
    Insight = auto()
    Medicine = auto()
    Perception = auto()
    Survival = auto()
    # Charisma
    Deception = auto()
    Intimidation = auto()
    Performance = auto()
    Persuasion = auto()


    def ability(self) -> Ability:
        return SKILL_TO_ABILITY[self]


SKILL_TO_ABILITY = {
    AbilitySkill.Athletics: Ability.Strength,
    AbilitySkill.Acrobatics: Ability.Dexterity,
    AbilitySkill.Sleight_of_Hand: Ability.Dexterity,
    AbilitySkill.Stealth: Ability.Dexterity,
    AbilitySkill.Arcana: Ability.Intelligence,
    AbilitySkill.History: Ability.Intelligence,
    AbilitySkill.Investigation: Ability.Intelligence,
    AbilitySkill.Nature: Ability.Intelligence,
    AbilitySkill.Religion: Ability.Intelligence,
    AbilitySkill.Animal_Handling: Ability.Wisdom,
    AbilitySkill.Insight: Ability.Wisdom,
    AbilitySkill.Medicine: Ability.Wisdom,
    AbilitySkill.Perception: Ability.Wisdom,
    AbilitySkill.Survival: Ability.Wisdom,
    AbilitySkill.Deception: Ability.Charisma,
    AbilitySkill.Intimidation: Ability.Charisma,
    AbilitySkill.Performance: Ability.Charisma,
    AbilitySkill.Persuasion: Ability.Charisma,
}



### p.13 of BHB -> VARIANT: Customizing Ability Scores
### 27 points to spend

STARTING_ABILITY_SCORE_COST = {
    8: 0,
    9: 1,
    10: 2,
    11: 3,
    12: 4,
    13: 5,
    14: 7,
    15: 9
}

def verify_starting_ability_scores(starting_attributes: dict[Ability, int]) -> None:
    '''
    Check if given set of attributes respect rules
    '''
    cost = 0
    for value in starting_attributes.values():
        cost += STARTING_ABILITY_SCORE_COST[value]
    if cost != 27:
        raise ValueError(f'Starting attributes total cost is not compliant: {cost} != 27')

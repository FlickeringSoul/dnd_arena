
from dataclasses import dataclass
from typing import Optional

import utils
from action import Action, ActionCost, ActionSteps
from attribute import Attribute
from character import Character
from event import ActionChoice
from feature import AgonizingBlast, Feature
from spell import EldritchBlast


@dataclass
class Build:
    character: Character
    features: list[Feature]
    possible_actions: list[Action]

    def available_actions(self) -> list[ActionChoice]:
        available_actions = []
        for i, action in enumerate(self.possible_actions):
            action_choice = ActionChoice(action_index=i, target=None)
            if action.action_cost is ActionCost.ACTION and self.character.action is True:
                available_actions.append(action_choice)
            elif action.action_cost is ActionCost.BONUS_ACTION and self.character.bonus_action is True:
                available_actions.append(action_choice)
            elif action.action_cost is ActionCost.NONE:
                available_actions.append(action_choice)
        return available_actions



def get_the_genie_build(level: int) -> Build:
    character = Character(
        level=1,
        attributes={
            Attribute.Strength: 8,
            Attribute.Dexterity: 14,
            Attribute.Constitution: 16,
            Attribute.Intelligence: 8,
            Attribute.Wisdom: 8,
            Attribute.Charisma: 16
        },
        weapon=None,
        armor_class=10
    )
    build = Build(
        character,
        [],
        possible_actions=[EldritchBlast(spellcasting_ability=Attribute.Charisma)]
    )
    for lvl in range(1, level+1):
        character.level = lvl
        if lvl == 2:
            build.features.append(AgonizingBlast(owner=character))
    return build

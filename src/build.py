
from character import Character
from feature import Feature, AgonizingBlast
from dataclasses import dataclass
from attribute import Attribute
from action import Action
from spell import EldritchBlast
from attack import Attack
import utils

@dataclass
class Build:
    character: Character
    features: list[Feature]
    action: Action
    bonus_action: Action = None

    def use_action(self, target: Character) -> list[Attack]:
        attacks = self.action.get_attacks(self.character, target)
        for attack in attacks:
            for feature in self.features:
                feature.on_attack(attack)
        return attacks


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
        action=EldritchBlast(spellcasting_ability=Attribute.Charisma)
    )
    for lvl in range(1, level+1):
        character.level = lvl
        if lvl == 2:
            build.features.append(AgonizingBlast())
    return build

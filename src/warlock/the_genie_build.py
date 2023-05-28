

from attribute import Attribute
from build import Build
from character import Character
from warlock.agonizing_blast import AgonizingBlast
from warlock.eldritch_blast import EldritchBlast


def get_the_genie_build(level: int) -> Build:
    character = Character(
        name='Genius Warlock',
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
        modules=[EldritchBlast(
        origin_character=character,
        spell_casting_ability=Attribute.Charisma
        )]
    )
    for lvl in range(1, level+1):
        character.level = lvl
        if lvl == 2:
            build.modules.append(AgonizingBlast(origin_character=character))
    return build
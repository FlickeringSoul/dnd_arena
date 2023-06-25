from attribute import Attribute
from build import Build
from character import Character
from damage import DamageType
from warlock.agonizing_blast import AgonizingBlast
from warlock.eldritch_blast import EldritchBlast
from warlock.genies_wrath import GeniesWrath


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
        spellcasting_ability=Attribute.Charisma
        ),
        GeniesWrath(
            damage_type=DamageType.MagicalBludgeoning,
            origin_character=character
        )]
    )
    for lvl in range(1, level+1):
        character.level = lvl
        if lvl == 2:
            build.modules.append(AgonizingBlast(origin_character=character))
    return build
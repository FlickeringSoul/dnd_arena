'''
Here we construct state and builds for testing our scripts
'''

from dataclasses import dataclass, field

from attribute import Attribute, verify_starting_attributes
from build import Build
from character import Character
from damage import DamageType
from feature import EndOfTurnAction, StartOfTurnFeature
from module import Module
from state import State
from warlock.agonizing_blast import AgonizingBlast
from warlock.eldritch_blast import EldritchBlast
from warlock.genies_wrath import GeniesWrath


@dataclass
class SimpleWarlock:
    level: int
    warlock: Character = field(init=False)
    modules: list[Module] = field(init=False, default_factory=list)

    def get_test_state(self) -> State:
        punching_ball = Character(
            name='punching_ball',
            attributes={attribute: 10 for attribute in Attribute}
        )
        build = self.get_build()
        state = State(
            creatures = [punching_ball] + build.characters,
            modules=build.modules + [EndOfTurnAction(), StartOfTurnFeature()]
        )
        return state

    def get_build(self) -> Build:
        return Build(
            characters=[self.warlock],
            modules=self.modules,
        )

    def __post_init__(self) -> None:
        self._on_create()
        for lvl in range(1, self.level+1):
            self._on_level_up(lvl)

    def _on_create(self) -> None:
        starting_attributes = {
            Attribute.Strength: 8,
            Attribute.Dexterity: 14,
            Attribute.Constitution: 15,
            Attribute.Wisdom: 8,
            Attribute.Intelligence: 10,
            Attribute.Charisma: 15
        }
        verify_starting_attributes(starting_attributes)
        starting_attributes[Attribute.Charisma] += 1
        starting_attributes[Attribute.Constitution] += 1
        self.warlock = Character(
            name='warlock',
            attributes=starting_attributes,
            level=1,
        )

    def _on_level_up(self, level: int) -> None:
        self.warlock.level = level
        assert 1 <= level <= 20, f'{level}'
        match level:
            case 1:
                self.modules.append(
                    EldritchBlast(
                    origin_character=self.warlock,
                    spellcasting_ability=Attribute.Charisma
                    )
                )
            case 2:
                self.modules.append(
                    AgonizingBlast(
                    origin_character=self.warlock
                    )
                )
            case 4:
                self.warlock.attributes[Attribute.Charisma] += 2

class TheGenie(SimpleWarlock):
    def _on_level_up(self, level: int) -> None:
        super()._on_level_up(level)
        match level:
            case 1:
                self.modules.append(
                    GeniesWrath(
                        damage_type=DamageType.MagicalBludgeoning,
                        origin_character=self.warlock
                    )
                )

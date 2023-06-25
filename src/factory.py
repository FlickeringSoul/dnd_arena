'''
Here we construct state and builds for testing our scripts
'''

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from attribute import Attribute, verify_starting_attributes
from build import Build
from character import Character
from damage import DamageType
from feature import EndOfTurnAction, StartOfTurnFeature
from module import Module
from rogue.sneak_attack import SneakAttack
from state import State
from warlock.agonizing_blast import AgonizingBlast
from warlock.eldritch_blast import EldritchBlast
from warlock.genies_wrath import GeniesWrath
from weapon import shortbow
from weapon_attack import WeaponAttack


@dataclass
class AbstractFactory(ABC):
    level: int
    character: Character = field(init=False)
    modules: list[Module] = field(init=False, default_factory=list)

    def get_build(self) -> Build:
        return Build(
            characters=[self.character],
            modules=self.modules,
        )

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

    def __post_init__(self) -> None:
        self._on_create()
        for lvl in range(1, self.level+1):
            self._on_level_up(lvl)

    @abstractmethod
    def _on_create(self) -> None:
        pass

    @abstractmethod
    def _on_level_up(self, level: int) -> None:
        self.character.level = level
        assert 1 <= level <= 20, f'{level}'


@dataclass
class SimpleRogue(AbstractFactory):

    def _on_create(self) -> None:
        starting_attributes = {
            Attribute.Strength: 8,
            Attribute.Dexterity: 15,
            Attribute.Constitution: 15,
            Attribute.Wisdom: 8,
            Attribute.Intelligence: 10,
            Attribute.Charisma: 14,
        }
        verify_starting_attributes(starting_attributes)
        starting_attributes[Attribute.Dexterity] += 1
        starting_attributes[Attribute.Constitution] += 1
        self.character = Character(
            name='rogue',
            attributes=starting_attributes,
            level=1,
            weapon=shortbow()
        )

    def _on_level_up(self, level: int) -> None:
        super()._on_level_up(level)
        match level:
            case 1:
                # TODO: expertise
                self.modules.append(SneakAttack(origin_character=self.character))
                self.modules.append(WeaponAttack(
                    origin_character=self.character,
                    weapon=shortbow()
                ))
            case 2:
                pass # TODO: Cunning Action
            case 4:
                self.character.attributes[Attribute.Dexterity] += 2


@dataclass
class SimpleWarlock(AbstractFactory):

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
        self.character = Character(
            name='warlock',
            attributes=starting_attributes,
            level=1,
        )

    def _on_level_up(self, level: int) -> None:
        super()._on_level_up(level)
        match level:
            case 1:
                self.modules.append(
                    EldritchBlast(
                    origin_character=self.character,
                    spellcasting_ability=Attribute.Charisma
                    )
                )
            case 2:
                self.modules.append(
                    AgonizingBlast(
                    origin_character=self.character
                    )
                )
            case 4:
                self.character.attributes[Attribute.Charisma] += 2

class TheGenie(SimpleWarlock):
    def _on_level_up(self, level: int) -> None:
        super()._on_level_up(level)
        match level:
            case 1:
                self.modules.append(
                    GeniesWrath(
                        damage_type=DamageType.MagicalBludgeoning,
                        origin_character=self.character
                    )
                )

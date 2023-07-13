'''
Here we construct state and builds for testing our scripts
'''

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ability import Ability, AbilitySkill, verify_starting_ability_scores
from action_cost import ActionCost
from build import Build
from character import Character
from damage import DamageType
from feature import EndOfTurnAction, StartOfTurnFeature
from hide import HideAction
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
            ability_scores={attribute: 10 for attribute in Ability}
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
        starting_ability_scores = {
            Ability.Strength: 8,
            Ability.Dexterity: 15,
            Ability.Constitution: 15,
            Ability.Wisdom: 8,
            Ability.Intelligence: 10,
            Ability.Charisma: 14,
        }
        verify_starting_ability_scores(starting_ability_scores)
        starting_ability_scores[Ability.Dexterity] += 1
        starting_ability_scores[Ability.Constitution] += 1
        self.character = Character(
            name='rogue',
            ability_scores=starting_ability_scores,
            level=1,
            weapon=shortbow()
        )

    def _on_level_up(self, level: int) -> None:
        super()._on_level_up(level)
        match level:
            case 1:
                self.character.skill_proficiencies |= AbilitySkill.Stealth
                self.character.skill_expertise |= AbilitySkill.Stealth
                self.modules.append(SneakAttack(origin_character=self.character))
                self.modules.append(WeaponAttack(
                    origin_character=self.character,
                    weapon=shortbow()
                ))
            case 4:
                self.character.ability_scores[Ability.Dexterity] += 2


class LightFootHalflingRogue(SimpleRogue):
    def _on_level_up(self, level: int) -> None:
        super()._on_level_up(level)
        match level:
            case 1:
                # TODO: lucky racial feat
                pass
            case 2:
                self.modules.append(
                    HideAction(
                        action_cost=ActionCost.BONUS_ACTION,
                        origin_character=self.character
                    )
                )


@dataclass
class SimpleWarlock(AbstractFactory):

    def _on_create(self) -> None:
        starting_ability_scores = {
            Ability.Strength: 8,
            Ability.Dexterity: 14,
            Ability.Constitution: 15,
            Ability.Wisdom: 8,
            Ability.Intelligence: 10,
            Ability.Charisma: 15
        }
        verify_starting_ability_scores(starting_ability_scores)
        starting_ability_scores[Ability.Charisma] += 1
        starting_ability_scores[Ability.Constitution] += 1
        self.character = Character(
            name='warlock',
            ability_scores=starting_ability_scores,
            level=1,
        )

    def _on_level_up(self, level: int) -> None:
        super()._on_level_up(level)
        match level:
            case 1:
                self.modules.append(
                    EldritchBlast(
                    origin_character=self.character,
                    spellcasting_ability=Ability.Charisma
                    )
                )
            case 2:
                self.modules.append(
                    AgonizingBlast(
                    origin_character=self.character
                    )
                )
            case 4:
                self.character.ability_scores[Ability.Charisma] += 2

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

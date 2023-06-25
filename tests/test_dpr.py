import logging
from fractions import Fraction

import pytest

import utils
from attribute import Attribute, verify_starting_attributes
from build import Build
from character import Character
from damage import Damage, DamageType
from dices import DiceBag, Dices
from main import exhaust_tree, get_test_state
from tree import find_best_strategy
from warlock.eldritch_blast import EldritchBlast

LOGGER = logging.getLogger('dnd')
LOGGER.setLevel(logging.DEBUG)


@pytest.fixture
def basic_warlock() -> Build:
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
    character = Character(
        name='basic_warlock',
        attributes=starting_attributes,
        level=1,
    )
    modules = []
    modules.append(EldritchBlast(
        origin_character=character,
        spellcasting_ability=Attribute.Charisma,
    ))
    build = Build(
        character=character,
        modules=modules
    )
    return build


def test_dice_bag():
    dice_bag = DiceBag()
    dice_bag += Dices.d10
    assert dice_bag.avg() == Fraction(11, 2)
    dice_bag += Dices.d10
    LOGGER.debug(f'{dice_bag=}, {dice_bag.dices=}, {dice_bag.fix=}')
    assert dice_bag.avg() == Fraction(11, 1)


def test_damage_():
    dmg = Damage().add(DamageType.Force, Dices.d10)
    LOGGER.debug(f'{dmg=} {dmg.avg()=}')
    assert dmg.avg() == Fraction(11, 2)
    critical_dmg = dmg.as_critical()
    LOGGER.debug(f'{critical_dmg=} {critical_dmg.avg()=}')
    assert dmg.as_critical().avg() == Fraction(11, 1)


def test_simple_warlock(basic_warlock: Build):
    state = get_test_state(basic_warlock)
    tree = exhaust_tree(state)
    best_strategy = find_best_strategy(tree)
    LOGGER.debug(best_strategy)
    warlock_score = best_strategy.scores[basic_warlock.character.name]
    LOGGER.debug(utils.repr_history(warlock_score.history))
    LOGGER.debug(warlock_score.value)
    # Eldritch blast deal 1d10. On average, this is 5,5 dmg:
    avg_dmg = Fraction(11, 2)
    # crit chance is 1/20
    crit_avg_dmg = Fraction(1, 20) * 2 * avg_dmg
    # normal hit is above or equal 5 (15 possibilities out ouf 20)
    normal_avg_dmg = Fraction(3, 4) * avg_dmg
    # Total expected
    expected_avg = crit_avg_dmg + normal_avg_dmg
    LOGGER.debug(f'{expected_avg=}')
    LOGGER.debug(f'{warlock_score.value=}')
    assert warlock_score.value == expected_avg

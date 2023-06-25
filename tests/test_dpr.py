import logging
from fractions import Fraction

import pytest

import utils
from damage import Damage, DamageType
from dices import DiceBag, Dices
from factory import SimpleWarlock
from main import exhaust_tree
from tree import find_best_strategy

LOGGER = logging.getLogger('dnd')
LOGGER.setLevel(logging.DEBUG)

def test_dice_bag():
    dice_bag = DiceBag()
    dice_bag += Dices.d10
    assert dice_bag.avg() == Fraction(11, 2)
    dice_bag += Dices.d10
    LOGGER.debug(f'{dice_bag=}, {dice_bag.dices=}, {dice_bag.fix=}')
    assert dice_bag.avg() == Fraction(11, 1)


def test_damage():
    dmg = Damage().add(DamageType.Force, Dices.d10)
    LOGGER.debug(f'{dmg=} {dmg.avg()=}')
    assert dmg.avg() == Fraction(11, 2)
    critical_dmg = dmg.as_critical()
    LOGGER.debug(f'{critical_dmg=} {critical_dmg.avg()=}')
    assert dmg.as_critical().avg() == Fraction(11, 1)


def compute_simple_warlock_expected_dpr(level: int) -> Fraction:
    p_critical = Fraction(1, 20)
    p_normal = Fraction(3, 4)
    dice_avg = Fraction(11, 2)
    attribute_modifier = 0
    nb_of_blast = 1

    if level >= 2:
        attribute_modifier = 3
    if level >= 4:
        attribute_modifier += 1
        p_normal += Fraction(1, 20)
    if level >= 5:
        nb_of_blast += 1
        p_normal += Fraction(1, 20)

    critical_avg = p_critical * (2*dice_avg + attribute_modifier)
    normal_avg = p_normal * (dice_avg + attribute_modifier)
    total = (critical_avg + normal_avg) * nb_of_blast
    LOGGER.debug(f'Expected avg dpr for simple warlock level {level} = {total}')
    return total


@pytest.mark.parametrize(
        argnames='level',
        argvalues=list(range(1, 6))
)
def test_simple_warlock(level: int):
    simple_warlock = SimpleWarlock(level=level)
    state = simple_warlock.get_test_state()
    tree = exhaust_tree(state)
    best_strategy = find_best_strategy(tree)
    warlock_score = best_strategy.scores[simple_warlock.warlock.name]
    LOGGER.debug(utils.repr_history(warlock_score.history))
    LOGGER.debug(warlock_score.value)
    assert warlock_score.value == compute_simple_warlock_expected_dpr(level)

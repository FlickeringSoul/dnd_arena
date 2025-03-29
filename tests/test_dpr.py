import logging
from dataclasses import dataclass
from fractions import Fraction

import pytest

import utils
from damage import Damage, DamageType
from dices import Dice, DiceBag
from factory import LightFootHalflingRogue, SimpleRogue, SimpleWarlock
from main import exhaust_tree
from tree import find_best_strategy

LOGGER = logging.getLogger('dnd')
LOGGER.setLevel(logging.DEBUG)


def test_dice_bag():
    dice_bag = DiceBag()
    dice_bag += Dice.d10
    assert dice_bag.avg() == Fraction(11, 2)
    dice_bag += Dice.d10
    LOGGER.debug(f'{dice_bag=}, {dice_bag.dices=}, {dice_bag.fix=}')
    assert dice_bag.avg() == Fraction(11, 1)


def test_damage():
    dmg = Damage().add(DamageType.Force, Dice.d10)
    LOGGER.debug(f'{dmg=} {dmg.avg()=}')
    assert dmg.avg() == Fraction(11, 2)
    critical_dmg = dmg.as_critical()
    LOGGER.debug(f'{critical_dmg=} {critical_dmg.avg()=}')
    assert dmg.as_critical().avg() == Fraction(11, 1)


class BaseDPRCalculator:

    def p_critical(self) -> Fraction:
        return Fraction(1, 20)


@dataclass
class ExpectedDPRCalculator:
    p_critical: Fraction = Fraction(1, 20)
    p_normal: Fraction = Fraction(3, 4)
    dice_avg_dmg: Fraction = 0
    fix_dmg: Fraction = 0
    nb_of_attacks: int = 1
    inc_main_attr_lvl_4: bool = True
    inc_nb_attacks_lvl_5: bool = True

    def expected_dpr(self) -> Fraction:
        critical_avg = self.p_critical * (self.dice_avg_dmg * 2 + self.fix_dmg)
        LOGGER.debug(f'{critical_avg=}, {self.p_critical=}, {self.dice_avg_dmg=}')
        normal_avg = self.p_normal * (self.dice_avg_dmg + self.fix_dmg)
        LOGGER.debug(f'{normal_avg=}')
        total = (critical_avg + normal_avg) * self.nb_of_attacks
        return total

    def usual_evolution(self, level: int):
        if level >= 4 and self.inc_main_attr_lvl_4:
            self.p_normal += Fraction(1, 20)
            self.fix_dmg+= 1
        if level >= 5:
            self.p_normal += Fraction(1, 20)
            if self.inc_nb_attacks_lvl_5:
                self.nb_of_attacks += 1

    @staticmethod
    def simple_warlock(level: int) -> Fraction:
        self = ExpectedDPRCalculator(
            dice_avg_dmg=Fraction(11, 2)
        )
        if level >= 2:
            self.fix_dmg += 3
        self.usual_evolution(level)
        return self.expected_dpr()

    @staticmethod
    def simple_rogue(level: int) -> Fraction:
        self = ExpectedDPRCalculator(
            dice_avg_dmg=Fraction(7, 1),
            fix_dmg=3,
            inc_nb_attacks_lvl_5=False
        )
        if level >= 3:
            self.dice_avg_dmg += Fraction(7, 2)
        if level >= 5:
            self.dice_avg_dmg += Fraction(7, 2)
        self.usual_evolution(level)
        return self.expected_dpr()

@pytest.mark.parametrize(
        argnames='level',
        argvalues=list(range(1, 6))
)
def test_simple_warlock(level: int):
    simple_warlock = SimpleWarlock(level=level)
    state = simple_warlock.get_test_state()
    tree = exhaust_tree(state)
    best_strategy = find_best_strategy(tree)
    warlock_score = best_strategy.scores[simple_warlock.character.name]
    LOGGER.debug(utils.repr_history(warlock_score.history))
    LOGGER.debug(warlock_score.value)
    assert warlock_score.value == ExpectedDPRCalculator.simple_warlock(level)


@pytest.mark.parametrize(
        argnames='level',
        argvalues=list(range(1, 5))
)
def test_simple_rogue(level: int):
    simple_rogue = SimpleRogue(level)
    test_state = simple_rogue.get_test_state()
    tree = exhaust_tree(test_state)
    best_strategy = find_best_strategy(tree)
    rogue_score = best_strategy.scores[simple_rogue.character.name]
    LOGGER.debug(utils.repr_history(rogue_score.history))
    LOGGER.debug(rogue_score.value)
    assert rogue_score.value == ExpectedDPRCalculator.simple_rogue(level)


@pytest.mark.parametrize(
        argnames='level',
        argvalues=list(range(1,2))
)
def test_light_foot_halfling_rogue(level: int):
    light_foot_halfling_rogue = LightFootHalflingRogue(level)
    test_state = light_foot_halfling_rogue.get_test_state()
    tree = exhaust_tree(test_state)
    best_strategy = find_best_strategy(tree)
    rogue_score = best_strategy.scores[light_foot_halfling_rogue.character.name]
    LOGGER.debug(utils.repr_history(rogue_score.history))
    LOGGER.debug(rogue_score.value)
    assert rogue_score.value == ExpectedDPRCalculator.simple_rogue(level)
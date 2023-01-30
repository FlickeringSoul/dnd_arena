
from character import Character
from build import get_the_genie_build
from attribute import Attribute
from damage import RolledDamage
import logging
import utils
from fractions import Fraction



def main():
    the_genie = get_the_genie_build(5)
    punching_ball = Character({attribute: 10 for attribute in Attribute})
    n = 10000
    total_rolled_damage = RolledDamage()
    for i in range(n):
        attacks = the_genie.use_action(punching_ball)
        total_rolled_damage += sum((attack.roll() for attack in attacks), start=RolledDamage())
    avg = Fraction(total_rolled_damage.get_sum(), n)
    logging.debug(f'{round(float(avg), 2)}')


if __name__ == '__main__':
    utils.config_logging()
    main()

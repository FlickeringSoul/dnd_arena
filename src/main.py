
import logging
from fractions import Fraction

import utils
from attribute import Attribute
from build import Build, get_the_genie_build
from character import Character
from event import ActionChoice
from state import State


def main():
    the_genie = get_the_genie_build(1)
    punching_ball = Build(
        character=Character({attribute: 10 for attribute in Attribute}),
        features=[],
        possible_actions=[]
    )
    state = State(
        creatures=[the_genie, punching_ball],
        event_queue=[],
        current_turn_index=0
    )

    while True:
        outcomes = state.outcomes()
        for outcome in outcomes:
            if isinstance(outcome, ActionChoice):
                outcome.target = punching_ball.character
        print(f'Possible outcomes are: {outcomes}')
        index = int(input())
        outcome = outcomes[index]
        print(f'Chosen outcome is: {outcome}')
        state.next(outcome)
        state.forward_until_branch()
        print(f'Total damage taken by the punching ball is: {punching_ball.character.total_damage_taken}')
        print('\n')







if __name__ == '__main__':
    utils.config_logging()
    main()


import logging
from fractions import Fraction

import utils
from attribute import Attribute
from build import Build, get_the_genie_build
from character import Character
from event import ActionChoice
from state import State


def main():
    the_genie = get_the_genie_build(5)
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
        display_outcomes = []
        for outcome in outcomes:
            if isinstance(outcome, ActionChoice):
                outcome.target = punching_ball.character
                display_outcomes.append(state.creatures[state.current_turn_index].possible_actions[outcome.action_index].__class__.__name__)

        print(f'Possible outcomes are: {display_outcomes if display_outcomes else outcomes}')
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

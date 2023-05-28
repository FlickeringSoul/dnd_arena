

import utils
from action import ActionEvent
from attribute import Attribute
from character import Character
from event import Choice, RandomOutcome
from feature import EndOfTurnAction, StartOfTurnFeature
from state import State
from warlock.the_genie_build import get_the_genie_build


def main():
    the_genie = get_the_genie_build(5) # Todo, fix the number of blast
    punching_ball = Character(
        name='Punching Ball',
        attributes={attribute: 10 for attribute in Attribute}
    )
    state = State(
        creatures=[the_genie.character, punching_ball],
        modules=the_genie.modules + [EndOfTurnAction(), StartOfTurnFeature()]
    )

    while True:
        possibles_outcomes = state.forward_until_branch()
        print(f'Total damage taken by the punching ball is: {punching_ball.total_damage_taken}')
        print(f'Possible outcomes are: {[display_outcome(outcome) for outcome in possibles_outcomes]}')
        index = int(input())
        outcome = possibles_outcomes[index]
        print(f'Chosen outcome is: {display_outcome(outcome)}')
        state.do_outcome(outcome)
        print('\n')

def display_outcome(outcome: Choice | RandomOutcome) -> str:
    if isinstance(outcome, Choice):
        if isinstance(outcome.choice, ActionEvent):
            return f'{outcome.choice.name.__name__} -> {outcome.choice.target.name}'
        return outcome.choice.__class__.__name__
    return outcome




if __name__ == '__main__':
    utils.config_logging()
    main()

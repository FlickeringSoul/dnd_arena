

import copy
import logging

import utils
from action import ActionEvent
from attribute import Attribute
from character import Character
from event import Choice, Outcome
from feature import EndOfTurnAction, StartOfTurnFeature
from state import State
from tree import TreeNode, find_best_strategy
from warlock.the_genie_build import get_the_genie_build


def get_test_state():
    the_genie = get_the_genie_build(5) # Todo, fix the number of blast
    punching_ball = Character(
        name='Punching Ball',
        attributes={attribute: 10 for attribute in Attribute}
    )
    state = State(
        creatures=[the_genie.character, punching_ball],
        modules=the_genie.modules + [EndOfTurnAction(), StartOfTurnFeature()]
    )
    return state


def test_interactive_arena():
    state = get_test_state()
    while True:
        possibles_outcomes = state.forward_until_branch()
        print(f'Total damage taken by the punching ball is: {state.creatures[1].total_damage_taken}')
        print(f'Possible outcomes are: {[display_outcome(outcome) for outcome in possibles_outcomes]}')
        index = int(input())
        outcome = possibles_outcomes[index]
        print(f'Chosen outcome is: {display_outcome(outcome)}')
        state.do_outcome(index)
        print('\n')


def display_outcome(outcome: Outcome) -> str:
    if isinstance(outcome, Choice):
        if isinstance(outcome.choice, ActionEvent):
            return f'{outcome.choice.name.__name__} -> {outcome.choice.target.name}'
        return outcome.choice.__class__.__name__
    return outcome


def test_tree():
    root_node = TreeNode(state=get_test_state())
    to_do = [root_node]
    while len(to_do) > 0:
        node = to_do.pop(0)
        node.print_history_tree()
        logging.debug(f'round_number {node.state.round_number}')
        possible_outcomes = node.state.forward_until_branch(absolute_round_limit=1)
        if possible_outcomes is None:
            continue # reached maximum rounds
        for outcome_index, possible_outcome in enumerate(possible_outcomes):
            state_copy = copy.deepcopy(node.state)
            state_copy.do_outcome(outcome_index)
            child_node = TreeNode(
                state=state_copy,
                outcome=possible_outcome,
                parent=node
            )
            node.children.append(child_node)
            to_do.append(child_node)
    root_node.print_full_tree()
    print(find_best_strategy(root_node))








if __name__ == '__main__':
    utils.config_logging()
    #test_interactive_arena()
    test_tree()

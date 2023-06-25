import copy

import utils
from action import ActionEvent
from event import Choice, RandomOutcome
from factory import TheGenie
from state import State
from tree import TreeNode, find_best_strategy


def test_interactive_arena() -> None:
    state = TheGenie(level=1).get_test_state()
    while True:
        possibles_outcomes = state.forward_until_branch()
        assert possibles_outcomes is not None
        print(f'Total damage taken by the punching ball is: {state.creatures[1].total_damage_taken}')
        print('Possible outcomes are:')
        for i, outcome in enumerate(possibles_outcomes):
            print(f'{i}: {display_outcome(outcome)}')
        index = int(input())
        outcome = possibles_outcomes[index]
        print(f'Chosen outcome is: {display_outcome(outcome)}')
        state.do_outcome(index)
        print('\n')


def display_outcome(outcome: RandomOutcome | Choice) -> str:
    if isinstance(outcome, Choice):
        if isinstance(outcome.choice, ActionEvent):
            assert outcome.choice.target is not None
            return f'{outcome.choice.name.__name__} -> {outcome.choice.target.name}'
        return outcome.choice.__class__.__name__
    return str(outcome)


def exhaust_tree(state: State) -> TreeNode:
    root_node = TreeNode(state)
    to_do = [root_node]
    while len(to_do) > 0:
        node = to_do.pop(0)
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
    return root_node


def test_tree() -> None:
    state = TheGenie(1).get_test_state()
    root_node = exhaust_tree(state)
    root_node.print_full_tree()
    best_strategy = find_best_strategy(root_node)
    print(best_strategy)
    print('\n\n')
    print(utils.repr_history(best_strategy.scores['Genius Warlock'].history))


if __name__ == '__main__':
    utils.config_logging()
    #test_interactive_arena()
    test_tree()

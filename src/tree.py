

from collections import defaultdict
from dataclasses import dataclass, field
from fractions import Fraction
from typing import cast

from character import Character
from damage import Damage
from event import Choice, RandomOutcome
from state import State
from utils import ExplainedValue, HistoryAddition


@dataclass
class TreeNode:
    state: State
    outcome: RandomOutcome | Choice | None = None
    parent: 'TreeNode | None' = None
    children: list['TreeNode'] = field(init=False, default_factory=list)

    def print_history_tree(self) -> None:
        history = ''
        while self.parent is not None:
            assert self.outcome is not None
            history = f'{self.outcome.name} -> ' + history
            self = self.parent
        print(history)

    def print_full_tree(self, suffix: str = '') -> None:
        new_suffix = suffix + f' -> {self.outcome.name}' if self.outcome is not None else ''
        if len(self.children) == 0:
            print(new_suffix + f' -> {[(creature.name, creature.total_damage_taken) for creature in self.state.creatures]}')
            return
        for child in self.children:
            child.print_full_tree(suffix=new_suffix)


@dataclass
class Strategy:
    choices: list[str]
    scores: dict[str, ExplainedValue]

def avg_total_damage_taken(tot_dmg_taken: list[Damage]) -> ExplainedValue:
    return ExplainedValue(
        value=sum((dmg.avg() for dmg in tot_dmg_taken), start=Fraction()),
        history=HistoryAddition(values=[f'avg({dmg})' for dmg in tot_dmg_taken])
    )

def avg_dmg_dealt_to_punching_ball_scoring(creature_id: str, state: State) -> ExplainedValue:
    enemy_dmg_taken = get_creature_from_id('punching_ball', state).total_damage_taken
    return avg_total_damage_taken(enemy_dmg_taken)


def get_creature_from_id(creature_id: str, state: State) -> Character:
    return {creature.name: creature for creature in state.creatures}[creature_id]


def find_best_strategy(node: TreeNode) -> Strategy:
    """
    Scoring functions must be for each creatures

    Return which children you should choose if it's a choice
    Return the weighted average score if it's children if it's a random outcome
    """
    if len(node.children) == 0:
        return Strategy(
            choices=[],
            scores={
                creature.name: avg_dmg_dealt_to_punching_ball_scoring(creature.name, node.state)
                for creature in node.state.creatures
            }
        )
    # When children are all determined by random outcome, return weighted avg scores and keep choice history
    elif all(isinstance(child.outcome, RandomOutcome) for child in node.children):
        scores: dict[str, ExplainedValue] = defaultdict(ExplainedValue)
        for child in node.children:
            strategy = find_best_strategy(child)
            for creature_id, creature_score in strategy.scores.items():
                random_outcome = cast(RandomOutcome, child.outcome)
                factor = ExplainedValue(
                    value=random_outcome.probability,
                    history=f'{random_outcome.probability} ({random_outcome.name.name})',
                )
                scores[creature_id] +=  factor * creature_score
        # TODO Choices can be different for some random outcomes !!
        return Strategy(strategy.choices, scores)
    # When children are all choices, return best score instance for current node creature turn and append choice history
    # TODO: WRONG !!! Warning !! Best score is not he current turn creature but the creature making the decision
    elif all(isinstance(child.outcome, Choice) for child in node.children):
        best_strategy = Strategy(choices=[], scores=defaultdict(ExplainedValue))
        for child in node.children:
            strategy = find_best_strategy(child)
            current_turn_creature_id = node.state.current_turn_creature().name
            if best_strategy.scores[current_turn_creature_id].value <= strategy.scores[current_turn_creature_id].value:
                best_strategy = strategy
                child_outcome = cast(Choice, child.outcome)
                strategy.choices.insert(0, child_outcome.name)
        return best_strategy
    else:
        raise ValueError('Unexpected: not uniform type of outcomes')

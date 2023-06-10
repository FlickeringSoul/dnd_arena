

from collections import defaultdict
from dataclasses import dataclass, field
from fractions import Fraction

from character import Character
from damage import Damage
from event import Choice, Outcome, RandomOutcome
from state import State


@dataclass
class TreeNode:
    state: State
    outcome: Outcome | None = None
    parent: 'TreeNode | None' = None
    children: list['TreeNode'] = field(init=False, default_factory=list)

    def print_history_tree(self):
        history = ''
        while self.outcome is not None:
            history = f'{self.outcome.name} -> ' + history
            self = self.parent
        print(history)

    def print_full_tree(self, suffix: str = ''):
        new_suffix = suffix + f' -> {self.outcome.name}' if self.outcome is not None else ''
        if len(self.children) == 0:
            print(new_suffix + f' -> {[(creature.name, creature.total_damage_taken) for creature in self.state.creatures]}')
            return
        for child in self.children:
            child.print_full_tree(suffix=new_suffix)



def avg_total_damage_taken(tot_dmg_taken: list[Damage]) -> Fraction:
    return sum(dmg.avg() for dmg in tot_dmg_taken)

def lol_scoring_func(creature_id: str, state: State) -> Fraction:
    nemesis = {'Punching Ball': 'Genius Warlock', 'Genius Warlock': 'Punching Ball'}
    enemy_id = nemesis[creature_id]
    enemy_dmg_taken = get_creature_from_id(enemy_id, state).total_damage_taken
    return avg_total_damage_taken(enemy_dmg_taken)

def get_creature_from_id(creature_id: str, state: State) -> Character:
    return {creature.name: creature for creature in state.creatures}[creature_id]


def find_best_strategy(node: TreeNode) -> tuple[dict[str, Fraction], str]:
    """
    Scoring functions must be for each creatures

    Return which children you should choose if it's a choice
    Return the weighted average score if it's children if it's a random outcome
    """
    if len(node.children) == 0:
        return {creature.name: lol_scoring_func(creature.name, node.state) for creature in node.state.creatures}, ''
    # When children are all determined by random outcome, return weighted avg scores and keep choice history
    elif all(isinstance(child.outcome, RandomOutcome) for child in node.children):
        scores = defaultdict(lambda: 0)
        for child in node.children:
            child_scores, choice_list = find_best_strategy(child)
            for creature_id, creature_score in child_scores.items():
                scores[creature_id] += child.outcome.probability * creature_score
        return scores, choice_list
    # When children are all choices, return best score instance for current node creature turn and append choice history
    # TODO: WRONG !!! Warning !! Best score is not he current turn creature but the creature making the decision
    elif all(isinstance(child.outcome, Choice) for child in node.children):
        best_scores = defaultdict(lambda: -1)
        best_choice_list = ''
        for child in node.children:
            child_scores, choice_list = find_best_strategy(child)
            current_turn_creature_id = node.state.current_turn_creature().name
            if best_scores[current_turn_creature_id] < child_scores[current_turn_creature_id]:
                best_scores = child_scores
                best_choice_list = child.outcome.name + ' + ' + choice_list
        return best_scores, best_choice_list
    else:
        raise ValueError('Unexpected: not uniform type of outcomes')

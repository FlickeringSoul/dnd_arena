

import logging
from dataclasses import dataclass
from typing import Optional

from action import Action, ActionCost, ActionEffect, ActionSteps
from build import Build
from event import ActionChoice, Event, FeatureChoice, RandomOutcome
from feature import Feature


@dataclass
class State:
    creatures: list[Build]
    event_queue: list[Event]
    current_turn_index: int = None

    def next_turn_index(self) -> int:
        # should rely on initiative score
        return (self.current_turn_index + 1) % len(self.creatures)

    def current_event(self) -> Optional[Event]:
        return self.event_queue[-1]

    def get_next_to_trigger(self) -> Feature | Event:
        current_event = self.current_event()
        for creature_index in range(current_event.current_creature_index, len(self.creatures)):
            current_creature = self.creatures[creature_index]
            for feature_index in range(current_event.current_feature_index, len(current_creature.features)):
                return current_creature.features[feature_index]
        return current_event

    def increase_action_effect_counter(self) -> None:
        current_event = self.current_event()
        if current_event.current_creature_index == len(self.creatures):
            raise NotImplementedError('TODO Must change action_step TODO')
        current_creature = self.creatures[current_event.current_creature_index]
        if current_event.current_feature_index < len(current_creature.features):
            current_event.current_feature_index += 1
            return
        if current_event.current_feature_index == len(current_creature.features):
            current_event.current_creature_index += 1
            current_event.current_feature_index = 0
            return
        raise ValueError(f'Current state has invalid value: current_event.current_feature_index={current_event.current_feature_index}, current_event.current_creature_index={current_event.current_creature_index}')

    def outcomes(self) -> list[ActionChoice | FeatureChoice | RandomOutcome]:
        if len(self.event_queue) == 0:
            actions = self.creatures[self.current_turn_index].available_actions()
            actions.append('END OF TURN')
            return actions
        current_event = self.current_event()
        next_to_trigger = self.get_next_to_trigger()
        if isinstance(next_to_trigger, Feature):
            return next_to_trigger.outcomes(current_event)
        elif isinstance(next_to_trigger, Event):
            return next_to_trigger.outcomes()
        raise TypeError(f'next_to_trigger should be')

    def next(self, outcome: ActionChoice | FeatureChoice | RandomOutcome) -> None:
        if len(self.event_queue) == 0:
            if outcome == 'END OF TURN':
                self.current_turn_index = self.next_turn_index()
                return
            assert(isinstance(outcome, ActionChoice))
            current_turn_creature = self.creatures[self.current_turn_index]
            action = current_turn_creature.possible_actions[outcome.action_index]
            if action.action_cost is ActionCost.ACTION:
                current_turn_creature.character.action = False
            elif action.action_cost is ActionCost.BONUS_ACTION:
                current_turn_creature.character.bonus_action = False
            action_effect = action.get_action_effect(origin=current_turn_creature.character, target=outcome.target)
            self.event_queue.append(action_effect)
            return
        current_event = self.current_event()
        next_to_trigger = self.get_next_to_trigger()
        if isinstance(next_to_trigger, Feature):
            interrupting_event = next_to_trigger.apply_outcome(current_event, outcome)
            self.increase_action_effect_counter()
        elif isinstance(next_to_trigger, Event):
            interrupting_event = next_to_trigger.apply_outcome(outcome)
            assert(isinstance(current_event, ActionEffect))
            if current_event.current_action_step is ActionSteps.END:
                self.event_queue.pop()
        else:
            raise TypeError(f'next_to_trigger should be')
        if interrupting_event is not None:
            self.event_queue.append(interrupting_event)

    def forward_until_branch(self):
        logging.debug(self.event_queue)
        outcomes = self.outcomes()
        logging.debug(outcomes)
        while outcomes == []:
            self.next(None)
            logging.debug(self.event_queue)
            outcomes = self.outcomes()
            logging.debug(outcomes)

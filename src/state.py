import copy
import logging
from dataclasses import dataclass, field

from action import ActionCost, ActionEvent, ChoosingActionEvent
from character import Character
from event import (Choice, EndOfTurnEvent, Event, EventSteps, RandomOutcome,
                   StartOfTurnEvent)
from module import Module


@dataclass
class State:
    creatures: list[Character]
    modules: list[Module]
    event_queue: list[Event] = field(init=False, default_factory=list)
    current_turn_index: int = field(init=False, default=0)
    round_number: int = field(init=False, default=1)
    possibles_outcomes: list[RandomOutcome] | list[Choice] | None = field(init=False, default=None)

    def trigger_next_turn(self) -> None:
        # should rely on initiative score
        self.current_turn_index = (self.current_turn_index + 1) % len(self.creatures)
        self.event_queue.append(StartOfTurnEvent(
            origin_character=self.current_turn_creature()
        ))
        if self.current_turn_index == 0:
            self.round_number += 1

    def current_turn_creature(self) -> Character:
        return self.creatures[self.current_turn_index]

    def current_event(self) -> Event | None:
        if len(self.event_queue) > 0:
            return self.event_queue[-1]
        return None

    def current_event_module(self) -> Module | None:
        current_event = self.current_event()
        if current_event is None:
            return None
        current_module_index = current_event.event_processing_module_index
        if current_module_index < len(self.modules):
            return self.modules[current_module_index]
        return None

    def apply_action_event_cost(self, action_event: ActionEvent):
        if action_event.action_cost is ActionCost.NONE:
            return
        action_event.origin_character.action_availability[action_event.action_cost] = False

    def get_possibles_outcomes(self) -> list[Choice] | list[RandomOutcome] | None:
        self.possibles_outcomes = self.__get_possibles_outcomes()
        return self.possibles_outcomes

    def __get_possibles_outcomes(self) -> list[Choice] | list[RandomOutcome] | None:
        # If there is no current event to process, launch a choosing action event
        if len(self.event_queue) == 0:
            self.event_queue.append(ChoosingActionEvent(
                origin_character=self.current_turn_creature(),
            ))
        # Process modules if there are module not processed yet
        current_event = self.current_event()
        assert current_event is not None, 'Should be impossible since we check len event queue first'
        current_module = self.current_event_module()
        if current_module is not None:
            return current_module.get_possibilities_on_event(current_event)
        # If there all modules where processed for this event step, return the event outcomes for this step
        if not isinstance(current_event, ChoosingActionEvent) or current_event.event_step is not EventSteps.AFTER_EVENT:
            return current_event.get_possible_outcomes()
        # If it is a ChoosingActionEvent, return all possibles action
        choices = []
        for possible_event in current_event.possible_actions:
            if isinstance(possible_event, ActionEvent):
                for target in self.search_all_targets(action_event=possible_event):
                    possible_event_copy = copy.copy(possible_event)
                    possible_event_copy.target = target
                    choices.append(Choice(choice=possible_event_copy, name=f'{possible_event.name.__name__} on {target.name}'))
            else:
                choices.append(Choice(choice=possible_event, name=f'{possible_event.__class__.__name__}'))
        assert len(choices) > 0
        return choices

    def do_outcome(self, outcome_index: int | None) -> None:
        outcome: None | RandomOutcome | Choice
        if outcome_index is None:
            assert self.possibles_outcomes is None
            outcome = None
        else:
            assert self.possibles_outcomes is not None
            outcome = self.possibles_outcomes[outcome_index]
        # Process modules if there are module not processed yet
        current_event = self.current_event()
        assert current_event is not None
        current_module = self.current_event_module()
        if current_module is not None:
            interrupting_event = current_module.on_event(current_event, chosen_outcome=outcome)
            current_event.event_processing_module_index += 1
            if interrupting_event is not None:
                self.event_queue.append(interrupting_event)
            return
        # Process event current step since all modules are done
        current_event.do_outcome(outcome=outcome)
        if current_event.event_step is EventSteps.END:
            self.event_queue.pop()
            if isinstance(current_event, EndOfTurnEvent):
                assert len(self.event_queue) == 0
                self.trigger_next_turn()
                return
            if isinstance(current_event, ChoosingActionEvent):
                assert isinstance(outcome, Choice)
                assert isinstance(outcome.choice, Event)
                self.event_queue.append(outcome.choice)
                if isinstance(outcome.choice, ActionEvent):
                    self.apply_action_event_cost(outcome.choice)
                    outcome.choice.on_action_selected_callback()

    def logging_progress(self) -> None:
        current_event = self.current_event()
        logging.debug(f'Current event: {current_event.__class__.__name__}, ' +
            f'Current step: {current_event.event_step if current_event is not None else None}, ' +
            f'Current module: {self.current_event_module().__class__.__name__}' +
            f'Current Character: {self.current_turn_creature().name}')

    def forward_until_branch(self, relative_round_limit: int | None = None, absolute_round_limit: int | None = None) -> list[Choice] | list[RandomOutcome] | None:
        if relative_round_limit is not None and absolute_round_limit is not None:
            raise ValueError('Both limits cannot be given at the same time')
        elif relative_round_limit is not None:
            maximum_round = self.round_number + relative_round_limit
        elif absolute_round_limit is not None:
            maximum_round = absolute_round_limit + 1
        else:
            maximum_round = self.round_number + 10

        self.logging_progress()
        while (possibles_outcomes := self.get_possibles_outcomes()) is None and self.round_number < maximum_round:
            self.do_outcome(None)
            self.logging_progress()
        return possibles_outcomes

    def search_all_targets(self, action_event: ActionEvent) -> list[Character]:
        return self.creatures

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

    def next_turn_index(self) -> int:
        # should rely on initiative score
        return (self.current_turn_index + 1) % len(self.creatures)

    def current_turn_creature(self) -> Character:
        return self.creatures[self.current_turn_index]

    def current_event(self) -> Event | None:
        if len(self.event_queue) > 0:
            return self.event_queue[-1]
        return

    def current_event_module(self) -> Module | None:
        current_event = self.current_event()
        if current_event is None:
            return
        current_module_index = current_event.event_processing_module_index
        if current_module_index < len(self.modules):
            return self.modules[current_module_index]

    def apply_action_event_cost(self, action_event: ActionEvent):
        if action_event.action_cost is ActionCost.NONE:
            return
        action_event.origin_character.action_availability[action_event.action_cost] = False

    def possibles_outcomes(self) -> list[Choice] | list[RandomOutcome] | None:
        # If there is no current event to process, launch a choosing action event
        if len(self.event_queue) == 0:
            self.event_queue.append(ChoosingActionEvent(
                origin_character=self.current_turn_creature(),
            ))
        # Process modules if there are module not processed yet
        current_event = self.current_event()
        current_module = self.current_event_module()
        if current_module is not None:
            return current_module.get_possibilities_on_event(current_event)
        # If there all modules where processed for this event step, return the event outcomes for this step
        if not isinstance(current_event, ChoosingActionEvent) or current_event.event_step is not EventSteps.AFTER_EVENT:
            return current_event.get_possible_outcomes()
        # If it is a ChoosingActionEvent, return all possibles action
        # TODO: handle target here
        choices = []
        for possible_event in current_event.possible_actions:
            if isinstance(possible_event, ActionEvent):
                for target in self.search_all_targets(action_event=possible_event):
                    possible_event_copy = copy.copy(possible_event)
                    possible_event_copy.target = target
                    choices.append(Choice(choice=possible_event_copy))
            else:
                choices.append(Choice(choice=possible_event))
        assert(len(choices) > 0)
        return choices

    def do_outcome(self, outcome: Choice | RandomOutcome | None) -> None:
        # Process modules if there are module not processed yet
        current_event = self.current_event()
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
                assert(len(self.event_queue) == 0)
                self.current_turn_index = self.next_turn_index()
                self.event_queue.append(StartOfTurnEvent(
                    origin_character=self.current_turn_creature()
                ))
                return
            if isinstance(current_event, ChoosingActionEvent):
                assert(isinstance(outcome, Choice))
                assert(isinstance(outcome.choice, Event))
                self.event_queue.append(outcome.choice)
                if isinstance(outcome.choice, ActionEvent):
                    self.apply_action_event_cost(outcome.choice)
                    outcome.choice.on_action_selected_callback()

    def logging_progress(self) -> None:
        logging.debug(f'Current event: {self.current_event().__class__.__name__}, ' +
            f'Current step: {self.current_event().event_step if self.current_event() else None}, ' +
            f'Current module: {self.current_event_module().__class__.__name__}' +
            f'Current Character: {self.current_turn_creature().name}')

    def forward_until_branch(self) -> list[Choice] | list[RandomOutcome]:
        self.logging_progress()
        possibles_outcomes = self.possibles_outcomes()
        while possibles_outcomes is None:
            self.do_outcome(None)
            self.logging_progress()
            possibles_outcomes = self.possibles_outcomes()
        return possibles_outcomes

    def search_all_targets(self, action_event: ActionEvent) -> list[Character]:
        return self.creatures
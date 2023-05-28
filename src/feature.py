

from action import ChoosingActionEvent
from action_cost import ActionCost
from event import (Choice, EndOfTurnEvent, Event, EventSteps, RandomOutcome,
                   StartOfTurnEvent)
from module import Module

# Note: Reaction Spells like CounterSpell / Absorb Element / Shield are features


class StartOfTurnFeature(Module):
    def on_event(self, event: Event, chosen_outcome: RandomOutcome | Choice | None) -> Event | None:
        if isinstance(event, StartOfTurnEvent) and event.event_step is EventSteps.BEFORE_EVENT:
            event.origin_character.action_availability = {action_cost: True for action_cost in ActionCost if action_cost is not ActionCost.NONE}

class EndOfTurnAction(Module):
    def on_event(self, event: Event, chosen_outcome: RandomOutcome | Choice | None) -> Event | None:
        if not isinstance(event, ChoosingActionEvent) or event.event_step != EventSteps.AFTER_EVENT:
            return
        event.possible_actions.append(EndOfTurnEvent(origin_character=event.origin_character))

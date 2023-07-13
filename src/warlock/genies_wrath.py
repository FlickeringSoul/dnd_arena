from dataclasses import dataclass, field

from action import ActionEvent
from damage import DamageType
from event import (Choice, EndOfTurnEvent, Event, EventSteps, RandomOutcome,
                   StartOfTurnEvent)
from module import Module


@dataclass
class GeniesWrath(Module):
    damage_type: DamageType
    available: bool = field(default=False, init=False)

    def on_event(self, event: Event, chosen_outcome: RandomOutcome | Choice | None) -> Event | None:
        if event.origin_character != self.origin_character:
            return None
        if isinstance(event, StartOfTurnEvent):
            self.on_start_of_turn()
            return None
        if isinstance(event, EndOfTurnEvent):
            self.on_end_of_turn()
            return None
        if not isinstance(event, ActionEvent):
            return None
        if event.event_step in (EventSteps.REGULAR_HIT, EventSteps.CRIT):
            self.on_hit(event)
        return None

    def on_start_of_turn(self) -> None:
        self.available = True

    def on_hit(self, action_event: ActionEvent) -> None:
        assert action_event.attack is not None
        if self.available is False:
            return
        bonus_damage = action_event.origin_character.proficiency_bonus()
        action_event.attack.damage[self.damage_type] += bonus_damage
        self.available = False

    def on_end_of_turn(self) -> None:
        self.available = False
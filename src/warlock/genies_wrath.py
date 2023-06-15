import logging
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
            return
        if isinstance(event, StartOfTurnEvent):
            self.on_start_of_turn()
            return
        if isinstance(event, EndOfTurnEvent):
            self.on_end_of_turn()
            return
        if not isinstance(event, ActionEvent):
            return
        if event.event_step in (EventSteps.REGULAR_HIT, EventSteps.CRIT):
            self.on_hit(event)

    def on_start_of_turn(self):
        logging.debug('XXX START')
        self.available = True

    def on_hit(self, attack: ActionEvent):
        logging.debug(f'XXX {self.available=}')
        if self.available is False:
            return
        bonus_damage = attack.origin_character.proficiency_bonus()
        attack.attack_damage[self.damage_type] += bonus_damage
        self.available = False

    def on_end_of_turn(self) -> None:
        logging.debug('XXX END')
        self.available = False
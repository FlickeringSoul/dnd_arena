import logging
from dataclasses import dataclass, field

from action import ActionEvent
from damage import Damage
from dices import Dices
from event import Choice, Event, EventSteps, RandomOutcome, StartOfTurnEvent
from module import Module
from weapon import WeaponProperties

LOGGER = logging.getLogger('dnd')


@dataclass
class SneakAttack(Module):
    available: bool = field(default=False, init=False)

    def on_event(self, event: Event, chosen_outcome: RandomOutcome | Choice | None) -> Event | None:
        if isinstance(event, StartOfTurnEvent):
            self.available = True
            return None
        if event.origin_character != self.origin_character:
            return None
        if not isinstance(event, ActionEvent):
            return None
        if event.event_step in (EventSteps.REGULAR_HIT, EventSteps.CRIT):
            self.on_hit(event)
        return None

    def on_hit(self, attack: ActionEvent) -> None:
        if self.available is False:
            return
        if attack.weapon_used is None:
            return
        if not (WeaponProperties.Range | WeaponProperties.Finesse) & attack.weapon_used.properties:
            return
        # TODO: should be rogue class level and not character level
        assert self.origin_character is not None
        assert self.origin_character.level is not None
        nb_of_dices = ((self.origin_character.level - 1)// 2) + 1
        sneak_attack_damage = Damage().add(attack.weapon_used.damage_type, Dices.d6 * nb_of_dices)
        if attack.event_step is EventSteps.CRIT:
            sneak_attack_damage = sneak_attack_damage.as_critical()
        attack.attack_damage += sneak_attack_damage
        self.available = False

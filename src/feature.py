
from abc import ABC
from dataclasses import dataclass, field
from typing import Optional

from action import ActionEffect
from attribute import Attribute
from character import Character
from damage import DamageType
from event import (Event, EventListener, EventSteps, FeatureChoice,
                   RandomOutcome, StartOfTurnEvent)
from spell import EldritchBlastBeam

# Note: Reaction Spells like CounterSpell / Absorb Element / Shield are features

@dataclass
class Feature(EventListener, ABC):
    owner: Character


class StartOfTurnFeature(Feature):
    def outcomes(self, event: Event) -> list[RandomOutcome | FeatureChoice]:
        return []

    def apply_outcome(self, event: Event, outcome: Optional[RandomOutcome | FeatureChoice]) -> Optional[Event]:
        if isinstance(event, StartOfTurnEvent) and event.event_step is EventSteps.BEFORE_EVENT:
            self.owner.action = True
            self.owner.bonus_action = True
            self.owner.reaction = True
            self.owner.interaction = True

@dataclass
class GeniesWrath(Feature):
    damage_type: DamageType
    available: bool = field(default=False, init=False)

    def on_start_of_turn(self):
        self.available = True

    def on_hit(self, attack: ActionEffect):
        if self.available is False:
            return
        bonus_damage = attack.attacker.get_proficiency_bonus()
        attack.attack_damage.fix_damages.append((bonus_damage, self.damage_type))
        self.available = False

    def on_end_of_turn(self) -> None:
        self.available = False


class AgonizingBlast(Feature):
    """Eldritch Invocation p.110 of PHB

    When you cast eldritch blast, add your Charisma modifier to the damage it deals on hit
    """
    def outcomes(self, event: Event) -> list[RandomOutcome | FeatureChoice]:
        return []

    def apply_outcome(self, event: Event, outcome: Optional[RandomOutcome | FeatureChoice]) -> Optional[Event]:
        if not isinstance(event, ActionEffect):
            return
        if event.name != EldritchBlastBeam:
            return
        if event.origin_character != self.owner:
            return
        event.attack_damage.damages[DamageType.Force] += self.owner.attribute_modifier(Attribute.Charisma)
        return None

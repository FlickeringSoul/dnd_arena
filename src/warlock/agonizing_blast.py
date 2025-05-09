
from ability import Ability
from action import ActionEvent
from damage import DamageType
from event import Choice, Event, EventSteps, RandomOutcome
from module import Module
from warlock.eldritch_blast import EldritchBlast


class AgonizingBlast(Module):
    """Eldritch Invocation p.110 of PHB

    When you cast eldritch blast, add your Charisma modifier to the damage it deals on hit
    """
    def on_event(self, event: Event, chosen_outcome: RandomOutcome | Choice | None) -> Event | None:
        if not isinstance(event, ActionEvent):
            return None
        if event.event_step is not EventSteps.CRIT and event.event_step is not EventSteps.REGULAR_HIT:
            return None
        if event.action_module != EldritchBlast:
            return None
        if event.origin_character != self.origin_character:
            return None
        assert event.attack is not None
        event.attack.damage[DamageType.Force] += self.origin_character.ability_modifier(Ability.Charisma)
        return None

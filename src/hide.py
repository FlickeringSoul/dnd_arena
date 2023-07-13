
from dataclasses import dataclass, field

from ability import AbilitySkill
from action import AbilityContest, ActionEvent, ActionModule
from action_cost import ActionCost
from character import Character
from event import Choice, Event, EventSteps, RandomOutcome


@dataclass(kw_only=True)
class HideAction(ActionModule):
    action_cost: ActionCost
    hided_from: list[Character] = field(init=False, default_factory=list)

    def get_action_event(self) -> Event:
        assert self.origin_character is not None
        return ActionEvent(
            action_cost=self.action_cost,
            target=None,
            origin_character=self.origin_character,
            is_an_attack=False,
            is_a_spell=False,
            ability_contest=AbilityContest(
                originator_ability_skill=AbilitySkill.Stealth,
                target_ability_skill=AbilitySkill.Perception
            ),
            action_module=self.__class__,
        )

    def on_event(self, event: Event, chosen_outcome: RandomOutcome | Choice | None) -> Event | None:
        assert self.origin_character is not None

        super().on_event(event, chosen_outcome) #Handle Choosing Action event
        match event:
            # On successful hiding from target
            case ActionEvent(
                origin_character=self.origin_character,
                action_module=self.__class__,
                event_step=EventSteps.CONTEST_SUCCESS
            ):
                assert event.target is not None
                self.hided_from.append(event.target)
            # On attacking a target from which character is hided
            case ActionEvent(
                origin_character=self.origin_character,
                target=target,
                event_step=EventSteps.BEFORE_ATTACK,
                is_an_attack=True,
                attack=attack,
            ) if target in self.hided_from:
                assert attack is not None
                attack.advantage = True
                self.hided_from.remove(target)

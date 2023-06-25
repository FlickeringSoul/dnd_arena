from dataclasses import dataclass

from action import ActionCost, ActionEvent
from damage import Damage, DamageType
from dices import DiceBag, Dices
from spell import Spell


@dataclass(kw_only=True)
class EldritchBlast(Spell):
    number_of_blast_left: int = 0

    def on_action_use_callback(self) -> None:
        if self.number_of_blast_left == 0:
            self.number_of_blast_left = self.cantrip_multiplier() - 1
            return
        self.number_of_blast_left -= 1

    def get_action_event(self) -> ActionEvent:
        assert self.origin_character is not None

        if self.number_of_blast_left > 0:
            cost = ActionCost.NONE
        else:
            cost = ActionCost.ACTION

        return ActionEvent(
            origin_character=self.origin_character,
            is_an_attack=True,
            is_a_spell=True,
            action_cost=cost,
            attack_damage=Damage().add(DamageType.Force, Dices.d10),
            attack_roll_modifiers=DiceBag() + self.spell_attack_bonus(),
            name=EldritchBlast,
            on_action_selected_callback=self.on_action_use_callback
        )

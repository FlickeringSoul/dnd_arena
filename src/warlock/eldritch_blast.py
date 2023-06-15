from dataclasses import dataclass
from typing import Optional

from action import ActionCost, ActionEvent, ActionModule
from attribute import Attribute
from damage import Damage, DamageType
from dices import DiceBag, Dices
from spell import cantrip_scaling, spell_attack_bonus


@dataclass(kw_only=True)
class EldritchBlast(ActionModule):
    spell_casting_ability: Attribute
    number_of_blast_left: int = 0

    def on_action_use_callback(self):
        if self.number_of_blast_left == 0:
            self.number_of_blast_left = cantrip_scaling(self.origin_character.level) - 1
            return
        self.number_of_blast_left -= 1

    def get_action_event(self) -> Optional[ActionEvent]:
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
            attack_roll_modifiers=DiceBag() + spell_attack_bonus(self.origin_character, self.spell_casting_ability),
            name=EldritchBlast,
            on_action_selected_callback=self.on_action_use_callback
        )

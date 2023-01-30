
from abc import ABC
from attack import Attack
from spell import EldritchBlast
from attribute import Attribute
from damage import DamageType
from dataclasses import dataclass, field

class Feature(ABC):

    def on_start_of_turn(self) -> None:
        pass

    def on_attack(self, attack: Attack) -> None:
        pass

    def on_hit(self, attack: Attack) -> None:
        pass

    def on_end_of_turn(self) -> None:
        pass


@dataclass
class GeniesWrath(Feature):
    damage_type: DamageType
    available: bool = field(default=False, init=False)

    def on_start_of_turn(self):
        self.available = True

    def on_hit(self, attack: Attack):
        if self.available is False:
            return
        bonus_damage = attack.attacker.get_proficiency_bonus()
        attack.damage.fix_damages.append((bonus_damage, self.damage_type))
        self.available = False

    def on_end_of_turn(self) -> None:
        self.available = False

class AgonizingBlast(Feature):
    """Eldritch Invocation p.110 of PHB

    When you cast eldritch blast, add your Charisma modifier to the damage it deals on hit

    Args:
        Feature (_type_): _description_
    """
    def on_attack(self, attack: Attack):
        if attack.action_type == EldritchBlast:
            additional_damage = attack.attacker.get_attribute_modifier(Attribute.Charisma)
            attack.damage.fix_damages.append((additional_damage, DamageType.Force))

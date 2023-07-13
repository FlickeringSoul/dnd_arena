from dataclasses import dataclass

from ability import Ability
from action import ActionModule


@dataclass(kw_only=True)
class Spell(ActionModule):
    spellcasting_ability: Ability
    spell_level: int = 0

    def spell_attack_bonus(self) -> int:
        assert self.origin_character is not None
        pb = self.origin_character.proficiency_bonus()
        ability_bonus = self.origin_character.ability_modifier(self.spellcasting_ability)
        return pb + ability_bonus

    def cantrip_multiplier(self) -> int:
        """Return the usual multiplier cantrip have that depends purely on total level and not class level

        Args:
            caster_level (int): Character level of the caster

        Raises:
            ValueError: When caster level is not between 1 and 20

        Returns:
            int: 1 to 4, depends on level
        """
        assert self.origin_character is not None and self.origin_character.level is not None
        caster_level = self.origin_character.level
        if 1 <= caster_level <= 4:
            return 1
        if 5 <= caster_level <= 10:
            return 2
        if 11 <= caster_level <= 16:
            return 3
        if 17 <= caster_level <= 20:
            return 4
        raise ValueError('Caster level must be between 1 and 20')

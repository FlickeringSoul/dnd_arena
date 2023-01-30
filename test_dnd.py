import unittest
from dnd import PlayerCharacter

class TestPC(unittest.TestCase):
    def test_PB(self):
        expected_PB = [2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6]
        self.assertEqual(len(expected_PB), 20)
        for level in range(1, 21):
            player_character = PlayerCharacter(level=level)
            self.assertEqual(player_character.proficiency_bonus(), expected_PB[level-1])

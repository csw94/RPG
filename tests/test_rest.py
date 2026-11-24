"""Resting in a village bed restores HP and MP for free."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from scenes.house_scene import HouseInteriorScene


class FakeGame:
    active_slot = 1

    def __init__(self):
        self.saves = 0

    def save_game(self):
        self.saves += 1

    def enter_world(self, world, position):
        pass


def house(world, x, y):
    game = FakeGame()
    scene = HouseInteriorScene(game, {"world": world, "x": x, "y": y, "hp": 20, "max_hp": 150,
                                      "mp": 1, "max_mp": 25})
    return game, scene


class RestTests(unittest.TestCase):
    def test_bed_in_martas_cottage_and_garens_quarters_restore_everything(self):
        for world, spot in (("village_house_1", (17, 4)), ("village_house_2", (7, 4))):
            game, scene = house(world, *spot)
            self.assertFalse(scene.position_recovered, world)
            scene._interact()
            self.assertEqual((scene.hp, scene.mp), (150, 25), world)
            self.assertTrue(scene.dialogue_lines, world)
            self.assertGreaterEqual(game.saves, 1, world)

    def test_away_from_the_bed_nothing_heals(self):
        game, scene = house("village_house_1", 12, 12)
        scene._interact()
        self.assertEqual((scene.hp, scene.mp), (20, 1))

    def test_the_chiefs_office_has_no_bed(self):
        game, scene = house("village_chief_house", 17, 4)
        self.assertIsNone(scene.bed)

    def test_npc_still_comes_first_next_to_the_bed_house(self):
        game, scene = house("village_house_1", 7, 7)  # next to Marta at (7, 6)
        scene._interact()
        self.assertEqual(scene.hp, 20)
        self.assertTrue(scene.dialogue_lines)


if __name__ == "__main__":
    unittest.main()

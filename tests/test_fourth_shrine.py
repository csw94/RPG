"""Fourth shrine: the Ice Shrine in the northern Frost Highlands joins the main story."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.objectives import next_objective
from gameplay.world_data import NORTH_UNLOCK, SHRINES
from scenes.field_scene import FieldScene
from scenes.house_scene import HouseInteriorScene
from scenes.shop_scene import ShopScene
from scenes.status_scene import StatusScene


class FakeGame:
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}
    active_slot = 1

    def __init__(self):
        self.field = None
        self.scene = None
        self.scene_name = ""

    def save_game(self):
        pass

    def font(self, size):
        return pygame.font.Font(None, size)


def hero(*cleared, **state):
    game = FakeGame()
    flags = {"prologue_done": 1, **{key: 1 for key in cleared}}
    game.field = FieldScene(game, {"world": "village", "x": 15, "y": 15, "quest_flags": flags, **state})
    return game, game.field


class StoryTests(unittest.TestCase):
    def test_there_are_four_shrines_and_the_north_opens_after_two(self):
        self.assertEqual(SHRINES, ("shrine_wind", "shrine_earth", "shrine_fire", "shrine_ice"))
        self.assertEqual(NORTH_UNLOCK, 2)

    def test_the_sword_needs_all_four_seals(self):
        _, field = hero("shrine_wind", "shrine_earth", "shrine_fire")
        self.assertFalse(field.check_fountain_awakening())
        field.quest_flags["shrine_ice"] = 1
        self.assertTrue(field.check_fountain_awakening())
        self.assertEqual(field.weapon, "star_sword")

    def test_ice_blessing_raises_mp_and_defense(self):
        _, field = hero(max_mp=20, mp=3)
        before = (field.max_mp, field.defense)
        self.assertTrue(field.clear_shrine("shrine_ice"))
        self.assertEqual((field.max_mp, field.defense), (before[0] + 12, before[1] + 2))
        self.assertEqual(field.mp, field.max_mp)

    def test_objective_points_north_once_it_opens(self):
        _, field = hero("shrine_wind")
        self.assertIn("두 곳", next_objective(field))
        _, field = hero("shrine_wind", "shrine_earth")
        self.assertIn("북쪽 얼음 제단", next_objective(field))

    def test_old_saves_that_already_awakened_the_sword_keep_it(self):
        _, field = hero("shrine_wind", "shrine_earth", "shrine_fire", "star_sword_awakened",
                        weapon="star_sword", owned_weapons=["star_sword"])
        self.assertTrue(field.check_fountain_awakening())
        self.assertIn("말포스", next_objective(field))


class ScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_status_shows_four_seals(self):
        game, field = hero("shrine_ice")
        rows = dict(StatusScene(game).seal_rows())
        self.assertEqual(len(rows), 4)
        self.assertTrue(rows["얼음 제단"])
        StatusScene(game).draw(pygame.Surface((800, 600)))

    def test_shop_counts_the_ice_shrine(self):
        game, field = hero("shrine_ice", "shrine_wind")
        self.assertEqual(ShopScene(game).cleared(), 2)

    def test_chief_counts_four_seals(self):
        game = FakeGame()
        flags = {k: 1 for k in ("prologue_done", "shrine_wind", "shrine_earth", "shrine_fire")}
        chief = HouseInteriorScene(game, {"world": "village_chief_house", "x": 12, "y": 7, "quest_flags": flags})
        chief._interact()
        self.assertNotIn("모두 모았구나", " ".join(chief.dialogue_lines))
        chief.dialogue_lines = []
        chief.quest_flags["shrine_ice"] = 1
        chief._interact()
        self.assertIn("네 개의 인장", " ".join(chief.dialogue_lines))


if __name__ == "__main__":
    unittest.main()

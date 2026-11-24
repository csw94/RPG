"""Map page in the status screen and the 'next goal' hint."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.objectives import next_objective
from scenes.dungeon_scene import DungeonScene
from scenes.field_scene import FieldScene
from scenes.house_scene import HouseInteriorScene
from scenes.shrine_clearing_scene import ShrineClearingScene
from scenes.status_scene import StatusScene
from scenes.village_scene import VillageScene


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


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


def flags(**set_flags):
    base = {"prologue_done": 0, "shrine_wind": 0, "shrine_earth": 0, "shrine_fire": 0,
            "star_sword_awakened": 0, "final_boss": 0, "abyss_lord": 0}
    base.update({k: 1 for k in set_flags})
    return base


class ObjectiveTests(unittest.TestCase):
    def objective(self, **set_flags):
        field = FieldScene(FakeGame(), {"world": "village", "x": 15, "y": 15, "quest_flags": flags(**set_flags)})
        return next_objective(field)

    def test_goals_follow_the_story(self):
        self.assertIn("촌장", self.objective())
        self.assertIn("제단", self.objective(prologue_done=True))
        partial = self.objective(prologue_done=True, shrine_wind=True)
        self.assertIn("대지의 폐광", partial)
        self.assertIn("불꽃의 신전", partial)
        self.assertNotIn("바람의 제단", partial)
        self.assertIn("북쪽 얼음 제단", self.objective(prologue_done=True, shrine_wind=True, shrine_earth=True,
                                                  shrine_fire=True))
        self.assertIn("분수", self.objective(prologue_done=True, shrine_wind=True, shrine_earth=True,
                                            shrine_fire=True, shrine_ice=True))
        self.assertIn("말포스", self.objective(prologue_done=True, shrine_wind=True, shrine_earth=True,
                                             shrine_fire=True, star_sword_awakened=True))
        self.assertIn("심연", self.objective(prologue_done=True, shrine_wind=True, shrine_earth=True,
                                           shrine_fire=True, star_sword_awakened=True, final_boss=True))
        self.assertIn("모든", self.objective(prologue_done=True, shrine_wind=True, shrine_earth=True,
                                           shrine_fire=True, star_sword_awakened=True, final_boss=True,
                                           abyss_lord=True))


class MarkerTests(unittest.TestCase):
    def test_field_marks_portals_and_unopened_chests_only(self):
        game = FakeGame()
        field = FieldScene(game, {"world": "field_east", "x": 2, "y": 16})
        kinds = {kind for kind, _ in field.map_markers()}
        self.assertTrue({"town", "dungeon", "chest", "herb"} <= kinds)
        chest = next(p for k, p in field.map_markers() if k == "chest")
        field.opened.add(chest)
        self.assertNotIn(chest, [p for k, p in field.map_markers() if k == "chest"])

    def test_boss_marker_disappears_once_defeated(self):
        game = FakeGame()
        dungeon = DungeonScene(game, {"world": "shrine_wind_2f"})
        self.assertIn("boss", {k for k, _ in dungeon.map_markers()})
        dungeon.quest_flags["shrine_wind"] = 1
        self.assertNotIn("boss", {k for k, _ in dungeon.map_markers()})
        self.assertIn("stairs", {k for k, _ in dungeon.map_markers()})

    def test_village_marks_gates_and_people(self):
        village = VillageScene(FakeGame(), {"world": "village", "x": 15, "y": 15})
        kinds = [k for k, _ in village.map_markers()]
        self.assertGreaterEqual(kinds.count("gate"), 4)
        self.assertIn("shop", kinds)
        self.assertIn("fountain", kinds)


class MapPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def scenes(self, game):
        return (VillageScene(game, {"world": "village", "x": 15, "y": 15}),
                FieldScene(game, {"world": "field_south", "x": 16, "y": 3}),
                DungeonScene(game, {"world": "shrine_fire_1f"}),
                HouseInteriorScene(game, {"world": "village_house_1", "x": 12, "y": 12}),
                ShrineClearingScene(game, {"x": 15, "y": 17}))

    def test_left_right_switch_between_record_and_map(self):
        game = FakeGame()
        game.field = FieldScene(game, {"world": "field_east", "x": 2, "y": 16})
        status = StatusScene(game)
        self.assertEqual(status.page, "record")
        status.handle_events([key(pygame.K_RIGHT)])
        self.assertEqual(status.page, "map")
        status.handle_events([key(pygame.K_LEFT)])
        self.assertEqual(status.page, "record")

    def test_map_fits_and_draws_for_every_kind_of_place(self):
        game = FakeGame()
        surface = pygame.Surface((800, 600))
        for scene in self.scenes(game):
            game.field = scene
            status = StatusScene(game)
            status.page = "map"
            rect = status.map_rect()
            self.assertLessEqual(rect.width, 720)
            self.assertLessEqual(rect.height, 420)
            status.draw(surface)


if __name__ == "__main__":
    unittest.main()

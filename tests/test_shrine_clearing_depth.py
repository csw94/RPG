"""North shrine clearing: the hero and the altar props are drawn in depth (foot) order."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from scenes.shrine_clearing_scene import ShrineClearingScene


class FakeGame:
    active_slot = 1
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}

    def save_game(self):
        pass

    def font(self, size):
        return pygame.font.Font(None, size)


def order(scene):
    return [name for name in scene.depth_order()]


class DepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def scene_at(self, x, y):
        scene = ShrineClearingScene(FakeGame(), {"x": x, "y": y})
        self.assertFalse(scene.position_recovered, (x, y))
        return scene

    def test_hero_in_front_of_the_altar_is_drawn_over_it(self):
        names = order(self.scene_at(15, 8))
        self.assertGreater(names.index("hero"), names.index("altar"))

    def test_hero_behind_the_altar_is_hidden_by_it(self):
        names = order(self.scene_at(15, 6))
        self.assertLess(names.index("hero"), names.index("altar"))
        self.assertLess(names.index("hero"), names.index("pillar_front_left"))

    def test_front_pillars_cover_a_hero_walking_behind_them(self):
        names = order(self.scene_at(13, 7))
        self.assertLess(names.index("hero"), names.index("pillar_front_left"))
        self.assertGreater(names.index("hero"), names.index("pillar_back_left"))

    def test_hero_stepping_into_the_gate_is_in_front_of_the_arch(self):
        names = order(self.scene_at(15, 19))
        self.assertGreater(names.index("hero"), names.index("gate"))

    def test_hero_just_north_of_the_gate_is_behind_the_arch(self):
        names = order(self.scene_at(15, 18))
        self.assertLess(names.index("hero"), names.index("gate"))

    def test_hero_below_the_top_fence_is_redrawn_over_it(self):
        self.assertIn("hero", order(self.scene_at(15, 1)))

    def test_hero_far_from_the_altar_is_left_to_the_field_layer(self):
        self.assertNotIn("hero", order(self.scene_at(5, 15)))

    def test_draw_runs_everywhere_around_the_altar(self):
        surface = pygame.Surface((800, 600))
        for x, y in ((15, 8), (15, 6), (13, 7), (17, 7), (15, 18)):
            self.scene_at(x, y).draw(surface)


if __name__ == "__main__":
    unittest.main()

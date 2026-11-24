"""The shop uses the same wooden frame as the other menus (no gold outer border)."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from scenes.field_scene import FieldScene
from scenes.shop_scene import ShopScene
from utils import ui


class FakeGame:
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}
    active_slot = 1

    def __init__(self):
        self.field = FieldScene(self, {"world": "village", "x": 2, "y": 2})

    def save_game(self):
        pass

    def font(self, size):
        return pygame.font.Font(None, size)


class ShopFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_outer_border_is_wood_not_gold(self):
        surface = pygame.Surface((800, 600))
        scene = ShopScene(FakeGame())
        scene.draw(surface)
        panel = scene.panel_rect()
        border = [tuple(surface.get_at((panel.left + 3, y)))[:3] for y in range(panel.top + 20, panel.bottom - 20)]
        self.assertIn(ui.WOOD, border)
        self.assertNotIn(FakeGame.colors["gold"], border)

    def test_rows_and_close_button_fit_inside_the_panel(self):
        scene = ShopScene(FakeGame())
        panel = scene.panel_rect()
        for rect in scene._rows() + [scene.close_rect()]:
            self.assertTrue(panel.contains(rect.inflate(12, 12)), rect)


if __name__ == "__main__":
    unittest.main()

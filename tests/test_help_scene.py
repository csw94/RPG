"""In-game controls guide, reachable from the title menu."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from scenes.help_scene import CONTROLS, HelpScene
from scenes.title_scene import TitleScene


class FakeSaves:
    def list_saves(self):
        return {}


class FakeGame:
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}
    running = True

    def __init__(self):
        self.save_manager = FakeSaves()
        self.scene = None
        self.scene_name = "title"

    def font(self, size):
        return pygame.font.Font(None, size)


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


class HelpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_guide_covers_every_key(self):
        keys = " ".join(k for k, _ in CONTROLS)
        for needed in ("WASD", "스페이스", "I", "Tab", "M", "F5", "ESC", "Enter"):
            self.assertIn(needed, keys, needed)

    def test_title_menu_opens_the_guide_and_comes_back(self):
        game = FakeGame()
        title = TitleScene(game)
        game.scene = title
        title.selected = title.OPTIONS.index("조작법")
        title.handle_events([key(pygame.K_RETURN)])
        self.assertIsInstance(game.scene, HelpScene)
        game.scene.draw(pygame.Surface((800, 600)))
        game.scene.handle_events([key(pygame.K_ESCAPE)])
        self.assertIs(game.scene, title)
        self.assertEqual(game.scene_name, "title")
        self.assertTrue(game.running)

    def test_quit_is_still_the_last_option(self):
        game = FakeGame()
        title = TitleScene(game)
        title.selected = len(title.OPTIONS) - 1
        title.handle_events([key(pygame.K_RETURN)])
        self.assertFalse(game.running)

    def test_menu_buttons_fit_above_the_footer(self):
        title = TitleScene(FakeGame())
        buttons = title._menu_buttons()
        self.assertEqual(len(buttons), len(title.OPTIONS))
        self.assertLessEqual(buttons[-1].bottom, 512)


if __name__ == "__main__":
    unittest.main()

"""Autosave every minute while exploring, and save when the window is closed."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

import main
from scenes.field_scene import FieldScene


class FakeOwner:
    active_slot = 1
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}

    def save_game(self):
        pass

    def font(self, size):
        return pygame.font.Font(None, size)


def make_game(scene_name="field_east"):
    game = main.Game.__new__(main.Game)
    game.field = FieldScene(FakeOwner(), {"world": "field_east", "x": 2, "y": 16})
    game.scene = game.field
    game.scene_name = scene_name
    game.active_slot = 1
    game.running = True
    game.autosave_clock = 0.0
    game.saves = 0

    def save_game():
        game.saves += 1
    game.save_game = save_game
    return game


class AutosaveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_saves_once_a_minute_while_exploring(self):
        game = make_game()
        game.tick_autosave(main.AUTOSAVE_SECONDS - 1)
        self.assertEqual(game.saves, 0)
        game.tick_autosave(2)
        self.assertEqual(game.saves, 1)
        self.assertGreater(game.field.autosave_flash, 0)
        game.tick_autosave(main.AUTOSAVE_SECONDS - 5)
        self.assertEqual(game.saves, 1)

    def test_waits_while_a_dialogue_is_open(self):
        game = make_game()
        game.field.show_dialogue(["잠깐!"])
        game.tick_autosave(main.AUTOSAVE_SECONDS + 10)
        self.assertEqual(game.saves, 0)
        game.field.dialogue_lines = []
        game.tick_autosave(0.1)
        self.assertEqual(game.saves, 1)

    def test_never_autosaves_in_battle_menus_or_on_the_title(self):
        for name in ("battle", "shop", "status", "title"):
            game = make_game(name)
            game.scene = object()
            game.tick_autosave(main.AUTOSAVE_SECONDS * 3)
            self.assertEqual(game.saves, 0, name)

    def test_closing_the_window_saves_an_open_adventure(self):
        game = make_game()
        game.shutdown()
        self.assertEqual(game.saves, 1)
        self.assertFalse(game.running)
        title = make_game("title")
        title.shutdown()
        self.assertEqual(title.saves, 0)

    def test_flash_fades(self):
        game = make_game()
        game.field.autosave_flash = 1.0
        game.field.update(0.5)
        self.assertAlmostEqual(game.field.autosave_flash, 0.5)


class HudTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_hud_draws_the_notice(self):
        game = make_game()
        game.field.autosave_flash = 1.5
        game.field.draw(pygame.Surface((800, 600)))


if __name__ == "__main__":
    unittest.main()

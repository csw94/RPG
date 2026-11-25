"""Deleting a save slot from the title screen (Delete key or the bin button), after a yes/no check."""

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from db.save_manager import SaveManager
from scenes.confirm_scene import ConfirmScene
from scenes.title_scene import TitleScene


class FakeGame:
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}
    running = True

    def __init__(self, save_manager):
        self.save_manager = save_manager
        self.active_slot = None
        self.field = None
        self.scene = None
        self.scene_name = "title"
        self.loaded = None

    def load_game(self, slot):
        self.loaded = slot

    def font(self, size):
        return pygame.font.Font(None, size)


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


def click(pos):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)


class SaveManagerDeleteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.manager = SaveManager(Path(self.tmp.name) / "saves.db")

    def tearDown(self):
        self.tmp.cleanup()

    def test_delete_removes_only_that_slot(self):
        self.manager.save({"world": "village", "level": 3}, 1)
        self.manager.save({"world": "village", "level": 5}, 2)
        self.assertTrue(self.manager.delete(1))
        self.assertFalse(self.manager.has_save(1))
        self.assertTrue(self.manager.has_save(2))

    def test_deleting_an_empty_slot_reports_false(self):
        self.assertFalse(self.manager.delete(3))

    def test_delete_checks_the_slot_number(self):
        with self.assertRaises(ValueError):
            self.manager.delete(9)


class TitleDeleteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.manager = SaveManager(Path(self.tmp.name) / "saves.db")
        self.manager.save({"world": "village", "level": 4, "x": 15, "y": 15}, 1)
        self.manager.save({"world": "village", "level": 7, "x": 15, "y": 15}, 2)
        self.game = FakeGame(self.manager)
        self.title = TitleScene(self.game)
        self.game.scene = self.title
        self.title.selected = 1          # "모험 이어하기"
        self.title._choose_menu()
        self.title.selected = 0

    def tearDown(self):
        self.tmp.cleanup()

    def confirm(self, yes):
        dialog = self.game.scene
        self.assertIsInstance(dialog, ConfirmScene)
        self.assertIn("제1 슬롯", dialog.title)
        dialog.handle_events([key(pygame.K_LEFT)] if yes else [])
        dialog.handle_events([key(pygame.K_RETURN)])

    def test_delete_key_asks_first_and_no_keeps_the_save(self):
        self.title.handle_events([key(pygame.K_DELETE)])
        self.confirm(yes=False)
        self.assertIs(self.game.scene, self.title)
        self.assertTrue(self.manager.has_save(1))

    def test_yes_deletes_the_slot_and_refreshes_the_cards(self):
        self.title.handle_events([key(pygame.K_DELETE)])
        self.confirm(yes=True)
        self.assertIs(self.game.scene, self.title)
        self.assertFalse(self.manager.has_save(1))
        self.assertNotIn(1, self.title.slot_data)
        self.assertIn(2, self.title.slot_data)
        self.assertIn("삭제", self.title.notice)

    def test_empty_slot_has_nothing_to_delete(self):
        self.title.selected = 2
        self.title.handle_events([key(pygame.K_DELETE)])
        self.assertIs(self.game.scene, self.title)
        self.assertIsNone(self.title.delete_button(2))
        self.assertIsNotNone(self.title.delete_button(0))

    def test_bin_button_deletes_without_loading_the_slot(self):
        self.title.selected = 1
        button = self.title.delete_button(1)
        self.title.handle_events([click(button.center)])
        self.assertIsNone(self.game.loaded)
        dialog = self.game.scene
        self.assertIn("제2 슬롯", dialog.title)
        dialog.handle_events([key(pygame.K_LEFT), key(pygame.K_RETURN)])
        self.assertFalse(self.manager.has_save(2))

    def test_deleting_the_open_adventure_forgets_it(self):
        self.game.active_slot, self.game.field = 1, object()
        self.title.handle_events([key(pygame.K_DELETE)])
        self.confirm(yes=True)
        self.assertIsNone(self.game.active_slot)
        self.assertIsNone(self.game.field)

    def test_slot_screen_draws_with_the_bin_buttons(self):
        self.title.draw(pygame.Surface((800, 600)))


if __name__ == "__main__":
    unittest.main()

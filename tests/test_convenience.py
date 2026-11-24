"""Convenience: typewriter dialogue with a speed setting, and Enter/Z as extra action keys."""

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from scenes.field_scene import TEXT_SPEEDS, FieldScene
from scenes.house_scene import HouseInteriorScene
from scenes.settings_scene import SettingsScene
from utils import user_settings


class FakeGame:
    active_slot = 1
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}

    def __init__(self, text_speed="normal"):
        self.settings = {**user_settings.DEFAULTS, "text_speed": text_speed}
        self.display_modes = ("1x",)
        self.field = None
        self.scene = None
        self.scene_name = "village"

    def save_game(self):
        pass

    def enter_world(self, world, position):
        pass

    def save_settings(self):
        pass

    def apply_display(self, mode):
        pass

    def font(self, size):
        return pygame.font.Font(None, size)


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


def field(speed="normal"):
    game = FakeGame(speed)
    scene = FieldScene(game, {"world": "field_east", "x": 2, "y": 16})
    game.field = scene
    return scene


class SettingTests(unittest.TestCase):
    def test_text_speed_is_a_saved_setting(self):
        self.assertEqual(user_settings.DEFAULTS["text_speed"], "normal")
        self.assertEqual(set(TEXT_SPEEDS), {"slow", "normal", "fast", "instant"})
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            user_settings.save({**user_settings.DEFAULTS, "text_speed": "fast"}, path)
            self.assertEqual(user_settings.load(path)["text_speed"], "fast")
            path.write_text('{"text_speed": "warp"}', encoding="utf-8")
            self.assertEqual(user_settings.load(path)["text_speed"], "normal")


class TypewriterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_lines_type_out_and_a_press_finishes_then_advances(self):
        scene = field("normal")
        scene.show_dialogue(["첫 번째 줄입니다, 천천히 나와요.", "두 번째 줄"])
        self.assertEqual(scene.visible_dialogue(), "")
        scene.update(0.1)
        partial = scene.visible_dialogue()
        self.assertTrue(0 < len(partial) < len(scene.dialogue_lines[0]))
        scene.handle_events([key(pygame.K_SPACE)])
        self.assertEqual(scene.dialogue_index, 0)
        self.assertEqual(scene.visible_dialogue(), scene.dialogue_lines[0])
        scene.handle_events([key(pygame.K_SPACE)])
        self.assertEqual(scene.dialogue_index, 1)
        self.assertEqual(scene.visible_dialogue(), "")

    def test_speeds_differ_and_instant_shows_everything(self):
        typed = {}
        for speed in ("slow", "fast"):
            scene = field(speed)
            scene.show_dialogue(["가나다라마바사아자차카타파하" * 3])
            scene.update(0.2)
            typed[speed] = len(scene.visible_dialogue())
        self.assertLess(typed["slow"], typed["fast"])
        scene = field("instant")
        scene.show_dialogue(["바로 보입니다"])
        self.assertEqual(scene.visible_dialogue(), "바로 보입니다")

    def test_dialogue_draws_while_typing(self):
        scene = field()
        scene.show_dialogue(["그림이 그려집니다"])
        scene.update(0.05)
        scene.draw(pygame.Surface((800, 600)))


class KeyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_enter_and_z_also_advance_dialogue(self):
        for extra in (pygame.K_RETURN, pygame.K_z):
            scene = field("instant")
            scene.show_dialogue(["하나", "둘"])
            scene.handle_events([key(extra)])
            self.assertEqual(scene.dialogue_index, 1, extra)

    def test_enter_and_z_work_indoors_too(self):
        game = FakeGame("instant")
        house = HouseInteriorScene(game, {"world": "village_house_1", "x": 7, "y": 7})
        house.handle_events([key(pygame.K_z)])
        self.assertTrue(house.dialogue_lines)  # talked to Marta
        before = house.dialogue_index
        house.handle_events([key(pygame.K_RETURN)])
        self.assertTrue(house.dialogue_index != before or not house.dialogue_lines)

    def test_settings_screen_changes_text_speed(self):
        game = FakeGame()
        scene = SettingsScene(game, "title")
        scene.row = scene.rows.index("text_speed")
        scene.handle_events([key(pygame.K_RIGHT)])
        self.assertEqual(game.settings["text_speed"], "fast")
        scene.draw(pygame.Surface((800, 600)))


if __name__ == "__main__":
    unittest.main()

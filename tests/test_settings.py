"""Settings: volumes and window size, saved between runs and adjustable in a menu."""

import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from scenes.settings_scene import SettingsScene
from utils import display, user_settings
from utils.audio import Audio


class FakeAudio:
    def __init__(self):
        self.volumes = None
        self.played = []

    def set_volumes(self, music, sfx):
        self.volumes = (music, sfx)

    def play(self, name):
        self.played.append(name)


class FakeGame:
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}

    def __init__(self):
        self.settings = dict(user_settings.DEFAULTS)
        self.audio = FakeAudio()
        self.display_modes = ("1x", "1.5x", "fullscreen")
        self.applied = []
        self.saved = 0
        self.scene, self.scene_name = "previous", "village"

    def apply_display(self, mode):
        self.applied.append(mode)

    def save_settings(self):
        self.saved += 1

    def font(self, size):
        return pygame.font.Font(None, size)


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


class StoreTests(unittest.TestCase):
    def test_missing_or_broken_files_fall_back_to_defaults(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            self.assertEqual(user_settings.load(path), user_settings.DEFAULTS)
            path.write_text("{not json", encoding="utf-8")
            self.assertEqual(user_settings.load(path), user_settings.DEFAULTS)
            path.write_text(json.dumps({"music": 99, "display": "huge", "sfx": 3}), encoding="utf-8")
            loaded = user_settings.load(path)
            self.assertEqual((loaded["music"], loaded["sfx"], loaded["display"]), (10, 3, "1x"))

    def test_settings_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "nested" / "settings.json"
            values = {"music": 2, "sfx": 9, "display": "fullscreen", "text_speed": "fast"}
            user_settings.save(values, path)
            self.assertEqual(user_settings.load(path), values)


class DisplayTests(unittest.TestCase):
    def test_only_window_sizes_that_fit_the_desktop_are_offered(self):
        self.assertEqual(display.available_modes((1920, 1080)), ("1x", "1.5x", "fullscreen"))
        self.assertEqual(display.available_modes((2560, 1440)), ("1x", "1.5x", "2x", "fullscreen"))
        self.assertEqual(display.available_modes((1024, 768)), ("1x", "fullscreen"))

    def test_view_keeps_the_4_3_picture_centered(self):
        self.assertEqual(display.view_rect((1200, 900)), pygame.Rect(0, 0, 1200, 900))
        self.assertEqual(display.view_rect((1920, 1080)), pygame.Rect(240, 0, 1440, 1080))

    def test_mouse_positions_map_back_to_the_canvas(self):
        view = pygame.Rect(240, 0, 1440, 1080)
        self.assertEqual(display.to_canvas((240 + 720, 540), view), (400, 300))
        self.assertEqual(display.to_canvas((0, 0), view), (0, 0))  # black bars clamp to the edge

    def test_mouse_events_are_rewritten_but_keys_pass_through(self):
        view = pygame.Rect(0, 0, 1600, 1200)
        click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(800, 600), button=1)
        press = key(pygame.K_a)
        mapped = display.map_events([click, press], view)
        self.assertEqual(mapped[0].pos, (400, 300))
        self.assertEqual(mapped[0].button, 1)
        self.assertIs(mapped[1], press)


class SettingsSceneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_left_right_change_volumes_immediately(self):
        game = FakeGame()
        scene = SettingsScene(game, "previous")
        scene.handle_events([key(pygame.K_RIGHT)])          # music 7 -> 8
        scene.handle_events([key(pygame.K_DOWN), key(pygame.K_LEFT), key(pygame.K_LEFT)])  # sfx 7 -> 5
        self.assertEqual((game.settings["music"], game.settings["sfx"]), (8, 5))
        self.assertEqual(game.audio.volumes, (8, 5))

    def test_volumes_stop_at_zero_and_ten(self):
        game = FakeGame()
        scene = SettingsScene(game, "previous")
        scene.handle_events([key(pygame.K_RIGHT)] * 8)
        self.assertEqual(game.settings["music"], 10)
        scene.handle_events([key(pygame.K_LEFT)] * 15)
        self.assertEqual(game.settings["music"], 0)

    def test_window_size_cycles_through_available_modes(self):
        game = FakeGame()
        scene = SettingsScene(game, "previous")
        scene.handle_events([key(pygame.K_DOWN), key(pygame.K_DOWN), key(pygame.K_RIGHT)])
        self.assertEqual((game.settings["display"], game.applied), ("1.5x", ["1.5x"]))
        scene.handle_events([key(pygame.K_RIGHT), key(pygame.K_RIGHT)])
        self.assertEqual(game.settings["display"], "1x")

    def test_closing_saves_and_returns(self):
        game = FakeGame()
        scene = SettingsScene(game, "previous")
        game.scene = scene
        scene.draw(pygame.Surface((800, 600)))
        scene.handle_events([key(pygame.K_ESCAPE)])
        self.assertEqual((game.scene, game.scene_name, game.saved), ("previous", "village", 1))

    def test_audio_volume_levels_scale_playback(self):
        audio = Audio(enabled=False)
        audio.set_volumes(0, 10)
        self.assertEqual(audio.music_volume, 0)
        self.assertGreater(audio.sfx_volume, 0)


if __name__ == "__main__":
    unittest.main()

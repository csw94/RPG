"""Code-generated chiptune sound: synthesis, safe playback, music choice and battle cues."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from utils import audio
from utils.audio import MUSIC, SFX, Audio, music_for, render_music, render_sfx


class Recorder:
    """Stands in for Audio: remembers which cues were played."""

    def __init__(self):
        self.played = []

    def play(self, name):
        self.played.append(name)


class SynthTests(unittest.TestCase):
    def test_every_effect_renders_short_clipped_samples(self):
        for name in SFX:
            samples = render_sfx(name)
            self.assertGreater(len(samples), 0, name)
            self.assertLess(len(samples), audio.RATE * 2, name)
            self.assertTrue(all(-32768 <= s <= 32767 for s in samples), name)
            self.assertGreater(max(abs(s) for s in samples), 1000, name)

    def test_every_track_loops_cleanly(self):
        for name in MUSIC:
            samples = render_music(name)
            self.assertGreater(len(samples), audio.RATE * 4, name)
            self.assertLess(abs(samples[0]), 2000, name)
            self.assertLess(abs(samples[-1]), 2000, name)

    def test_rendering_is_deterministic(self):
        self.assertEqual(render_sfx("hit"), render_sfx("hit"))


class PlaybackTests(unittest.TestCase):
    def test_audio_without_a_mixer_is_silent_but_safe(self):
        silent = Audio(enabled=False)
        silent.play("hit")
        silent.play_music("field")
        silent.update("battle")
        silent.toggle_mute()
        self.assertTrue(silent.muted)

    def test_unknown_cues_are_ignored(self):
        Audio(enabled=False).play("does_not_exist")

    def test_music_follows_the_scene(self):
        self.assertEqual(music_for("title", None), "title")
        self.assertEqual(music_for("village", None), "village")
        self.assertEqual(music_for("village_house_1", None), "village")
        self.assertEqual(music_for("field_south", None), "field")
        self.assertEqual(music_for("shrine_fire_2f", None), "dungeon")
        self.assertEqual(music_for("battle", "slime"), "battle")
        self.assertEqual(music_for("battle", "shrine_earth"), "boss")
        self.assertEqual(music_for("battle", "final_boss"), "boss")
        self.assertIsNone(music_for("shop", None))      # keep whatever is playing
        self.assertIsNone(music_for("status", None))


class BattleCueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_battle_playback_plays_matching_cues(self):
        from scenes.battle_scene import BattleScene
        from scenes.field_scene import FieldScene

        class Game:
            colors = {k: (200, 200, 200) for k in ("gold", "cream", "muted", "red", "green", "blue")}
            active_slot = 1

            def save_game(self):
                pass

            def font(self, size):
                return pygame.font.Font(None, size)

        game = Game()
        game.audio = Recorder()
        game.field = FieldScene(game, {"world": "field_east", "x": 2, "y": 16, "atk": 400})
        scene = BattleScene(game, "slime")
        scene.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)])
        for _ in range(200):
            scene.update(0.05)
        self.assertIn("confirm", game.audio.played)
        self.assertTrue({"hit", "crit"} & set(game.audio.played))
        self.assertIn("victory", game.audio.played)
        scene.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)])


if __name__ == "__main__":
    unittest.main()

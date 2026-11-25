"""New game opening: Tomi runs up to the hero, says the chief is waiting and leads the way."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.intro import ChiefCallIntro
from scenes.village_scene import VillageScene


class FakeGame:
    active_slot = 1
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}

    def __init__(self):
        self.saves = 0
        self.entered = None

    def save_game(self):
        self.saves += 1

    def enter_world(self, world, spawn):
        self.entered = world

    def font(self, size):
        return pygame.font.Font(None, size)


def village(**flags):
    game = FakeGame()
    scene = VillageScene(game, {"world": "village", "x": 15, "y": 15, "quest_flags": flags})
    game.field = game.scene = scene
    return game, scene


def run(scene, seconds, step=0.05):
    for _ in range(int(seconds / step)):
        scene.update(step)


def press(scene, k=pygame.K_SPACE):
    scene.handle_events([pygame.event.Event(pygame.KEYDOWN, key=k)])


def finish_dialogue(scene):
    for _ in range(40):
        if not scene.dialogue_lines:
            return
        scene.dialogue_chars = 999.0
        press(scene)


class IntroScriptTests(unittest.TestCase):
    def test_script_runs_fade_run_talk_lead_wait(self):
        intro = ChiefCallIntro()
        self.assertEqual(intro.phase, "fade")
        self.assertTrue(intro.locks_player)
        events = []
        for _ in range(400):
            events.append(intro.update(0.05))
            if intro.phase == "talk":
                break
        self.assertIn("talk", events)
        self.assertEqual(intro.tomi, ChiefCallIntro.MEET)
        self.assertTrue(intro.locks_player)
        intro.finish_talk()
        self.assertEqual(intro.phase, "lead")
        self.assertFalse(intro.locks_player)
        for _ in range(400):
            intro.update(0.05)
        self.assertEqual(intro.phase, "wait")
        self.assertEqual(intro.tomi, ChiefCallIntro.WAIT)

    def test_tomi_starts_off_to_the_west_and_moves_while_running(self):
        intro = ChiefCallIntro()
        start = intro.tomi
        self.assertLess(start[0], ChiefCallIntro.MEET[0])
        for _ in range(60):
            intro.update(0.05)
        self.assertNotEqual(intro.tomi, start)
        self.assertTrue(intro.walking)

    def test_skip_jumps_to_the_conversation(self):
        intro = ChiefCallIntro()
        self.assertEqual(intro.skip(), "talk")
        self.assertEqual(intro.phase, "talk")
        self.assertEqual(intro.tomi, ChiefCallIntro.MEET)

    def test_waiting_intro_starts_at_the_door(self):
        intro = ChiefCallIntro(waiting=True)
        self.assertEqual(intro.phase, "wait")
        self.assertEqual(intro.tomi, ChiefCallIntro.WAIT)
        self.assertFalse(intro.locks_player)


class VillageIntroTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_only_a_brand_new_game_plays_the_opening(self):
        self.assertEqual(village(prologue_done=0, intro_seen=0)[1].intro.phase, "fade")
        self.assertEqual(village(prologue_done=0, intro_seen=1)[1].intro.phase, "wait")
        self.assertIsNone(village(prologue_done=1, intro_seen=1)[1].intro)
        self.assertIsNone(village(prologue_done=0)[1].intro)  # saves from before the opening existed

    def test_new_game_marks_the_opening_as_unseen(self):
        import main
        from pathlib import Path
        self.assertIn('"intro_seen": 0', Path(main.__file__).read_text(encoding="utf-8"))

    def test_hero_cannot_walk_or_interact_until_tomi_has_spoken(self):
        game, scene = village(prologue_done=0, intro_seen=0)
        self.assertTrue(scene.input_locked)
        run(scene, 0.5)
        self.assertEqual((scene.player["x"], scene.player["y"]), (15.0, 15.0))

    def test_full_opening_tells_the_hero_to_visit_the_chief(self):
        game, scene = village(prologue_done=0, intro_seen=0)
        run(scene, 8)
        self.assertTrue(scene.dialogue_lines)
        self.assertTrue(any("촌장" in line for line in scene.dialogue_lines))
        self.assertEqual(scene.facing, "left")  # the hero turns towards Tomi
        finish_dialogue(scene)
        self.assertEqual(scene.quest_flags["intro_seen"], 1)
        self.assertEqual(scene.intro.phase, "lead")
        self.assertFalse(scene.input_locked)
        self.assertGreaterEqual(game.saves, 1)
        self.assertIn("촌장", scene.message)

    def test_action_key_skips_the_run_in(self):
        _, scene = village(prologue_done=0, intro_seen=0)
        run(scene, 1.5)  # past the fade
        press(scene)
        self.assertEqual(scene.intro.phase, "talk")
        self.assertTrue(scene.dialogue_lines)

    def test_tomi_by_the_door_points_the_hero_inside(self):
        _, scene = village(prologue_done=0, intro_seen=1)
        wx, wy = ChiefCallIntro.WAIT
        scene.player.update(x=float(wx), y=float(wy + 1))
        press(scene)
        self.assertTrue(any("촌장" in line for line in scene.dialogue_lines))

    def test_scene_draws_during_every_phase(self):
        _, scene = village(prologue_done=0, intro_seen=0)
        screen = pygame.Surface((800, 600))
        for _ in range(12):
            scene.draw(screen)
            run(scene, 0.7)
            if scene.dialogue_lines:
                finish_dialogue(scene)
        scene.draw(screen)


if __name__ == "__main__":
    unittest.main()

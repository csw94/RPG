"""Difficulty: chosen for each new adventure, stored in the save, adjustable in settings."""

import os
import random
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.combat import BattleEngine
from gameplay.difficulty import DIFFICULTIES, DIFFICULTY_ORDER
from gameplay.enemies import ENEMIES
from scenes.field_scene import FieldScene
from scenes.settings_scene import SettingsScene
from scenes.title_scene import TitleScene
from utils import user_settings


class FakeGame:
    active_slot = 1
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}
    running = True

    def __init__(self):
        self.started = None
        self.field = None
        self.scene = None
        self.scene_name = "title"
        self.settings = dict(user_settings.DEFAULTS)
        self.display_modes = ("1x",)

    def save_game(self):
        pass

    def new_game(self, slot, difficulty="normal"):
        self.started = (slot, difficulty)

    def save_settings(self):
        pass

    def apply_display(self, mode):
        pass

    def font(self, size):
        return pygame.font.Font(None, size)


class FixedRng(random.Random):
    def random(self):
        return 0.5

    def uniform(self, a, b):
        return (a + b) / 2


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


def hero(difficulty=None, **state):
    if difficulty:
        state["difficulty"] = difficulty
    return FieldScene(FakeGame(), {"world": "field_east", "x": 2, "y": 16, "hp": 999, "max_hp": 999, **state})


class RuleTests(unittest.TestCase):
    def test_three_levels_with_normal_unchanged(self):
        self.assertEqual(DIFFICULTY_ORDER, ("easy", "normal", "hard"))
        normal = DIFFICULTIES["normal"]
        self.assertEqual((normal["enemy_hp"], normal["damage"], normal["gold"]), (1.0, 1.0, 1.0))

    def test_enemy_hp_scales(self):
        base = ENEMIES["goblin"]["hp"]
        for level, expected in (("easy", 0.8), ("normal", 1.0), ("hard", 1.25)):
            engine = BattleEngine(hero(level), "goblin", rng=FixedRng())
            self.assertEqual(engine.enemy_max_hp, round(base * expected), level)
            self.assertEqual(engine.enemy_hp, engine.enemy_max_hp)

    def test_damage_taken_scales(self):
        taken = {}
        for level in DIFFICULTY_ORDER:
            field = hero(level)
            engine = BattleEngine(field, "skeleton", rng=FixedRng())
            engine.act("guard_does_nothing") or engine.act("attack")
            taken[level] = 999 - field.hp
        self.assertLess(taken["easy"], taken["normal"])
        self.assertLess(taken["normal"], taken["hard"])

    def test_hard_pays_more_gold(self):
        easy, hard = hero("normal"), hero("hard")
        easy.resolve_battle_victory("goblin")
        hard.resolve_battle_victory("goblin")
        self.assertGreater(hard.gold, easy.gold)

    def test_old_saves_play_on_normal_and_difficulty_is_saved(self):
        self.assertEqual(hero().difficulty, "normal")
        self.assertEqual(hero("hard").serialize()["difficulty"], "hard")
        self.assertEqual(hero("bogus").difficulty, "normal")


class TitleFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_new_adventure_asks_for_difficulty_after_the_slot(self):
        class Saves:
            def list_saves(self):
                return {}

        game = FakeGame()
        game.save_manager = Saves()
        title = TitleScene(game)
        title.selected = 0
        title.handle_events([key(pygame.K_RETURN)])      # 새 모험 시작
        title.handle_events([key(pygame.K_RETURN)])      # slot 1
        self.assertEqual(title.mode, "difficulty")
        self.assertIsNone(game.started)
        title.draw(pygame.Surface((800, 600)))
        title.handle_events([key(pygame.K_RIGHT), key(pygame.K_RETURN)])  # normal -> hard
        self.assertEqual(game.started, (1, "hard"))

    def test_escape_backs_out_of_the_difficulty_choice(self):
        class Saves:
            def list_saves(self):
                return {}

        game = FakeGame()
        game.save_manager = Saves()
        title = TitleScene(game)
        title.handle_events([key(pygame.K_RETURN), key(pygame.K_RETURN), key(pygame.K_ESCAPE)])
        self.assertEqual(title.mode, "slots")


class SettingsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_difficulty_row_only_during_an_adventure(self):
        game = FakeGame()
        self.assertNotIn("difficulty", SettingsScene(game, "title").rows)
        game.field = hero("normal")
        scene = SettingsScene(game, game.field)
        self.assertIn("difficulty", scene.rows)
        scene.row = scene.rows.index("difficulty")
        scene.handle_events([key(pygame.K_LEFT)])
        self.assertEqual(game.field.difficulty, "easy")
        scene.draw(pygame.Surface((800, 600)))


if __name__ == "__main__":
    unittest.main()

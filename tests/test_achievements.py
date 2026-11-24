"""Achievements: checked from the save's own records, announced once, listed on a status page."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.achievements import ACHIEVEMENTS, check_achievements
from gameplay.enemies import ENEMIES
from gameplay.quests import QUESTS
from gameplay.world_data import SHRINES
from scenes.field_scene import FieldScene
from scenes.status_scene import StatusScene


class FakeGame:
    active_slot = 1
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}

    def __init__(self):
        self.field = None
        self.scene = None
        self.scene_name = ""

    def save_game(self):
        pass

    def font(self, size):
        return pygame.font.Font(None, size)


def hero(**state):
    game = FakeGame()
    game.field = FieldScene(game, {"world": "village", "x": 15, "y": 15, **state})
    return game, game.field


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


class RuleTests(unittest.TestCase):
    def test_list_is_complete(self):
        self.assertGreaterEqual(len(ACHIEVEMENTS), 12)
        for achievement in ACHIEVEMENTS.values():
            self.assertTrue(achievement["name"] and achievement["desc"])

    def test_fresh_save_has_none(self):
        _, field = hero()
        self.assertEqual(check_achievements(field), [])
        self.assertEqual(field.achievements, set())

    def test_progress_unlocks_once_and_queues_a_toast(self):
        _, field = hero(stats={"wins": 1, "losses": 0, "flees": 0})
        self.assertEqual(check_achievements(field), ["first_win"])
        self.assertIn("first_win", field.achievements)
        self.assertEqual(field.achievement_toasts, [ACHIEVEMENTS["first_win"]["name"]])
        self.assertEqual(check_achievements(field), [])

    def test_story_and_collection_milestones(self):
        flags = {key: 1 for key in (*SHRINES, "final_boss", "abyss_lord")}
        quests = {quest_id: {"status": "COMPLETED", "progress": quest["target"]} for quest_id, quest in QUESTS.items()}
        _, field = hero(quest_flags=flags, sub_quests=quests, level=12, gold=1500, play_time=3000,
                        difficulty="hard", bestiary={enemy: 1 for enemy in ENEMIES},
                        stats={"wins": 150, "losses": 0, "flees": 0})
        unlocked = set(check_achievements(field))
        for expected in ("first_seal", "all_seals", "ending", "abyss", "helper", "bestiary", "veteran",
                         "hard_ending", "speedrun", "rich", "hunter"):
            self.assertIn(expected, unlocked)

    def test_slow_easy_endings_do_not_count_for_the_hard_ones(self):
        _, field = hero(quest_flags={"final_boss": 1}, play_time=9000, difficulty="easy")
        unlocked = set(check_achievements(field))
        self.assertIn("ending", unlocked)
        self.assertNotIn("speedrun", unlocked)
        self.assertNotIn("hard_ending", unlocked)

    def test_unlocked_achievements_are_saved(self):
        _, field = hero(achievements=["first_win", "nonsense"])
        self.assertEqual(field.achievements, {"first_win"})
        self.assertEqual(field.serialize()["achievements"], ["first_win"])


class ScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_status_has_an_achievement_page(self):
        game, field = hero(achievements=["first_win", "ending"])
        status = StatusScene(game)
        for _ in range(3):
            status.handle_events([key(pygame.K_RIGHT)])
        self.assertEqual(status.page, "achievements")
        status.draw(pygame.Surface((800, 600)))

    def test_toast_shows_then_clears(self):
        game, field = hero()
        field.achievement_toasts = ["첫 승리"]
        field.draw(pygame.Surface((800, 600)))
        field.update(3.5)
        self.assertEqual(field.achievement_toasts, [])


if __name__ == "__main__":
    unittest.main()

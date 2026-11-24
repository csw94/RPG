"""Play records: play time and battle tallies, shown on save slots and the ending card."""

import os
import random
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.combat import BattleEngine
from gameplay.records import format_play_time, slot_summary
from scenes.field_scene import FieldScene


class FakeGame:
    active_slot = 1
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}

    def save_game(self):
        pass

    def font(self, size):
        return pygame.font.Font(None, size)


class FixedRng(random.Random):
    def random(self):
        return 0.5

    def uniform(self, a, b):
        return (a + b) / 2


def hero(**state):
    return FieldScene(FakeGame(), {"world": "field_east", "x": 2, "y": 16, **state})


class FormatTests(unittest.TestCase):
    def test_play_time_reads_as_hours_and_minutes(self):
        self.assertEqual(format_play_time(59), "0분")
        self.assertEqual(format_play_time(61), "1분")
        self.assertEqual(format_play_time(3725), "1시간 02분")
        self.assertEqual(format_play_time(125 * 60), "2시간 05분")

    def test_slot_summary_shows_progress(self):
        lines = slot_summary({"level": 7, "play_time": 3725, "quest_flags": {"shrine_wind": 1, "shrine_ice": 1}})
        text = " ".join(lines)
        self.assertIn("레벨 7", text)
        self.assertIn("1시간 02분", text)
        self.assertIn("인장 2/4", text)
        self.assertNotIn("엔딩", text)
        cleared = " ".join(slot_summary({"quest_flags": {"final_boss": 1}}))
        self.assertIn("엔딩", cleared)

    def test_old_saves_have_empty_records(self):
        field = hero()
        self.assertEqual(field.play_time, 0)
        self.assertEqual(field.stats, {"wins": 0, "losses": 0, "flees": 0})
        lines = slot_summary({})
        self.assertIn("0분", " ".join(lines))


class TallyTests(unittest.TestCase):
    def test_wins_losses_and_flees_are_counted_and_saved(self):
        winner = hero(atk=400)
        BattleEngine(winner, "slime", rng=FixedRng()).act("attack")
        self.assertEqual(winner.stats["wins"], 1)
        loser = hero(hp=1)
        BattleEngine(loser, "skeleton", rng=FixedRng()).act("attack")
        self.assertEqual(loser.stats["losses"], 1)
        runner = hero()
        BattleEngine(runner, "slime", rng=FixedRng()).act("flee")
        self.assertEqual(runner.stats["flees"], 1)
        data = winner.serialize()
        self.assertEqual(data["stats"]["wins"], 1)
        self.assertIn("play_time", data)
        self.assertEqual(hero(**data).stats["wins"], 1)

    def test_game_loop_counts_time_only_while_adventuring(self):
        import main
        game = main.Game.__new__(main.Game)
        game.field = hero(play_time=10)
        game.scene_name = "title"
        game.count_play_time(5)
        self.assertEqual(game.field.play_time, 10)
        game.scene_name = "field_east"
        game.count_play_time(5)
        self.assertEqual(game.field.play_time, 15)


class ScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_ending_card_lists_play_time_and_wins(self):
        from scenes.epilogue_scene import EpilogueScene

        class Game(FakeGame):
            pass

        game = Game()
        game.field = hero(play_time=4000, stats={"wins": 42, "losses": 1, "flees": 2})
        scene = EpilogueScene(game)
        stats = dict(scene.record_rows())
        self.assertEqual(stats["플레이 시간"], "1시간 06분")
        self.assertEqual(stats["전투 승리"], "42회")

    def test_title_slot_cards_draw_the_summary(self):
        from scenes.title_scene import TitleScene

        class Saves:
            def list_saves(self):
                return {1: {"level": 3, "play_time": 600, "quest_flags": {"shrine_wind": 1}, "hp": 50, "max_hp": 90}}

        game = FakeGame()
        game.save_manager = Saves()
        title = TitleScene(game)
        title.mode = "slots"
        title.draw(pygame.Surface((800, 600)))


if __name__ == "__main__":
    unittest.main()

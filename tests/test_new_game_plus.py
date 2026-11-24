"""New game plus: after the ending, start over keeping the hero; enemies grow each cycle."""

import os
import random
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.combat import BattleEngine
from gameplay.difficulty import difficulty_of
from gameplay.enemies import ENEMIES
from gameplay.new_game_plus import new_game_plus_state
from gameplay.records import slot_summary
from scenes.confirm_scene import ConfirmScene
from scenes.field_scene import FieldScene
from scenes.house_scene import HouseInteriorScene


class FakeGame:
    active_slot = 1
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}

    def __init__(self):
        self.started_plus = 0
        self.field = None
        self.scene = None
        self.scene_name = ""

    def save_game(self):
        pass

    def start_new_game_plus(self):
        self.started_plus += 1

    def font(self, size):
        return pygame.font.Font(None, size)


class FixedRng(random.Random):
    def random(self):
        return 0.5

    def uniform(self, a, b):
        return (a + b) / 2


FINISHED = {"prologue_done": 1, "shrine_wind": 1, "shrine_earth": 1, "shrine_fire": 1, "shrine_ice": 1,
            "star_sword_awakened": 1, "final_boss": 1}


def finished_hero():
    game = FakeGame()
    field = FieldScene(game, {"world": "village", "x": 15, "y": 15, "level": 11, "xp": 40, "gold": 777,
                              "atk": 40, "defense": 20, "max_hp": 300, "hp": 12, "max_mp": 50, "mp": 3,
                              "weapon": "star_sword", "owned_weapons": ["rusty_sword", "star_sword"],
                              "accessory": "mana_ring", "owned_accessories": ["mana_ring"],
                              "quest_flags": FINISHED, "bestiary": {"slime": 9}, "achievements": ["ending"],
                              "play_time": 5000, "stats": {"wins": 80, "losses": 1, "flees": 2},
                              "difficulty": "hard", "quest_items": ["knights_crest"]})
    field.opened.add((22, 14))
    field.sub_quests["sq_moon_herb"]["status"] = "COMPLETED"
    game.field = field
    return game, field


class StateTests(unittest.TestCase):
    def test_keeps_the_hero_and_resets_the_story(self):
        _, field = finished_hero()
        state = new_game_plus_state(field.serialize())
        kept = ("level", "xp", "gold", "atk", "defense", "max_hp", "max_mp", "weapon", "owned_weapons",
                "accessory", "owned_accessories", "bestiary", "achievements", "play_time", "stats", "difficulty")
        for key in kept:
            self.assertEqual(state[key], field.serialize()[key], key)
        self.assertEqual(state["cycle"], 2)
        self.assertEqual((state["hp"], state["mp"]), (300, 50))
        self.assertEqual(state["world"], "village")
        self.assertEqual(state["quest_flags"], {"prologue_done": 1})
        for key in ("sub_quests", "opened_by_world", "collected_herbs", "quest_items", "opened"):
            self.assertNotIn(key, state, key)
        fresh = FieldScene(FakeGame(), state)
        self.assertEqual(fresh.sub_quests["sq_moon_herb"]["status"], "NOT_STARTED")
        self.assertEqual(fresh.cycle, 2)
        self.assertFalse(fresh.quest_flags["final_boss"])

    def test_each_cycle_counts_up(self):
        _, field = finished_hero()
        state = new_game_plus_state(new_game_plus_state(field.serialize()))
        self.assertEqual(state["cycle"], 3)


class ScalingTests(unittest.TestCase):
    def hero(self, cycle):
        return FieldScene(FakeGame(), {"world": "field_east", "x": 2, "y": 16, "cycle": cycle,
                                       "hp": 999, "max_hp": 999, "atk": 400})

    def test_enemies_grow_and_rewards_rise_with_the_cycle(self):
        first, second = difficulty_of(self.hero(1)), difficulty_of(self.hero(2))
        self.assertEqual(first["enemy_hp"], 1.0)
        self.assertGreater(second["enemy_hp"], first["enemy_hp"])
        self.assertGreater(second["damage"], first["damage"])
        self.assertGreater(second["xp"], first["xp"])
        engine = BattleEngine(self.hero(2), "goblin", rng=FixedRng())
        self.assertEqual(engine.enemy_max_hp, round(ENEMIES["goblin"]["hp"] * second["enemy_hp"]))

    def test_more_experience_in_later_cycles(self):
        gains = {}
        for cycle in (1, 2):
            field = self.hero(cycle)
            BattleEngine(field, "goblin", rng=FixedRng()).act("attack")
            gains[cycle] = field.xp + sum(20 + lvl * 15 for lvl in range(1, field.level))
        self.assertGreater(gains[2], gains[1])

    def test_slot_shows_the_cycle(self):
        self.assertIn("2회차", " ".join(slot_summary({"cycle": 2})))
        self.assertNotIn("회차", " ".join(slot_summary({})))


class FlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def chief(self, flags):
        game = FakeGame()
        scene = HouseInteriorScene(game, {"world": "village_chief_house", "x": 12, "y": 7, "quest_flags": flags})
        game.field = game.scene = scene
        scene._interact()
        while scene.dialogue_lines:
            scene._advance_dialogue()
        return game

    def test_chief_offers_a_new_journey_only_after_the_ending(self):
        game = self.chief(FINISHED)
        self.assertIsInstance(game.scene, ConfirmScene)
        game.scene.draw(pygame.Surface((800, 600)))
        before = self.chief({"prologue_done": 1})
        self.assertNotIsInstance(before.scene, ConfirmScene)

    def test_confirm_yes_starts_and_no_returns(self):
        game = self.chief(FINISHED)
        confirm = game.scene
        confirm.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)])  # default: 아니오
        self.assertEqual(game.started_plus, 0)
        self.assertIs(game.scene, game.field)
        game = self.chief(FINISHED)
        game.scene.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT),
                                  pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)])
        self.assertEqual(game.started_plus, 1)


if __name__ == "__main__":
    unittest.main()

"""Bestiary: enemies seen and defeated are recorded and shown on a status-screen page."""

import os
import random
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.combat import BattleEngine
from gameplay.enemies import ENEMIES
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


class FixedRng(random.Random):
    def random(self):
        return 0.5

    def uniform(self, a, b):
        return (a + b) / 2


def hero(**state):
    game = FakeGame()
    game.field = FieldScene(game, {"world": "field_east", "x": 2, "y": 16, **state})
    return game, game.field


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


class RecordTests(unittest.TestCase):
    def test_meeting_records_a_sighting_and_winning_counts_a_defeat(self):
        _, field = hero(atk=400)
        self.assertEqual(field.bestiary, {})
        BattleEngine(field, "wolf", rng=FixedRng())
        self.assertEqual(field.bestiary, {"wolf": 0})
        engine = BattleEngine(field, "slime", rng=FixedRng())
        engine.act("attack")
        self.assertEqual(field.bestiary["slime"], 1)

    def test_bestiary_is_saved(self):
        _, field = hero(bestiary={"goblin": 3, "shrine_wind": 0})
        self.assertEqual(field.serialize()["bestiary"], {"goblin": 3, "shrine_wind": 0})
        _, field = hero(bestiary={"not_an_enemy": 4})
        self.assertEqual(field.bestiary, {})


class PageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_pages_cycle_record_map_bestiary(self):
        game, _ = hero()
        status = StatusScene(game)
        seen = [status.page]
        for _ in range(3):
            status.handle_events([key(pygame.K_RIGHT)])
            seen.append(status.page)
        self.assertEqual(seen, ["record", "map", "bestiary", "record"])
        status.handle_events([key(pygame.K_LEFT)])
        self.assertEqual(status.page, "bestiary")

    def test_rows_cover_every_enemy_with_seen_and_defeats(self):
        game, field = hero(bestiary={"slime": 2, "shrine_wind": 0})
        rows = StatusScene(game).bestiary_rows()
        self.assertEqual([r["id"] for r in rows], list(ENEMIES))
        by_id = {r["id"]: r for r in rows}
        self.assertTrue(by_id["slime"]["seen"])
        self.assertEqual(by_id["slime"]["defeats"], 2)
        self.assertTrue(by_id["shrine_wind"]["seen"])
        self.assertFalse(by_id["abyss_lord"]["seen"])
        self.assertTrue(by_id["shrine_wind"]["boss"])
        self.assertFalse(by_id["slime"]["boss"])

    def test_grid_fits_and_draws(self):
        game, field = hero(bestiary={"slime": 2, "frost_wisp": 1, "final_boss": 1})
        status = StatusScene(game)
        cells = status.bestiary_cells()
        self.assertEqual(len(cells), len(ENEMIES))
        for cell in cells:
            self.assertTrue(pygame.Rect(30, 70, 740, 450).contains(cell), cell)
        status.page = "bestiary"
        status.draw(pygame.Surface((800, 600)))

    def test_collection_counts_gear(self):
        game, field = hero(owned_accessories=["mana_ring"], owned_weapons=["rusty_sword", "wind_dagger"])
        owned, total = StatusScene(game).gear_collection()
        self.assertEqual(owned, 4)  # rusty sword, wind dagger, traveler clothes, mana ring
        self.assertGreater(total, owned)


if __name__ == "__main__":
    unittest.main()

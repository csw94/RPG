"""Frost Highlands polish: a hunter NPC with a request, freeze-proof gear and late-tier stock."""

import os
import random
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.combat import BattleEngine
from gameplay.equipment import ACCESSORIES, ARMORS, SHOP_ITEMS, WEAPONS, shop_stock
from gameplay.world_data import FIELD_ROUTES
from scenes.field_scene import FieldScene
from scenes.shop_scene import ShopScene
from scenes.status_scene import QUEST_NAMES


class FakeGame:
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}
    active_slot = 1

    def __init__(self):
        self.field = None
        self.scene = None
        self.scene_name = ""

    def save_game(self):
        pass

    def enter_world(self, world, position):
        pass

    def font(self, size):
        return pygame.font.Font(None, size)


class FixedRng(random.Random):
    def __init__(self, value=0.5):
        super().__init__(1)
        self.value = value

    def random(self):
        return self.value

    def uniform(self, a, b):
        return (a + b) / 2


HUNTER = FIELD_ROUTES["field_north"]["npc"]


def north(**state):
    game = FakeGame()
    x, y = HUNTER["pos"]
    field = FieldScene(game, {"world": "field_north", "x": x + 1, "y": y, **state})
    game.field = field
    return field


def finish_dialogue(scene):
    while scene.dialogue_lines:
        scene._advance_dialogue()


class HunterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_hunter_stands_in_the_highlands_and_is_drawn(self):
        field = north()
        self.assertFalse(field.position_recovered)
        self.assertEqual(field.toby_position, HUNTER["pos"])
        self.assertIn(HUNTER["pos"], field.solid_npcs)
        self.assertIn(("npc", HUNTER["pos"]), field.map_markers())
        field.draw(pygame.Surface((800, 600)))

    def test_hunter_request_runs_from_offer_to_reward(self):
        field = north()
        field._interact()
        finish_dialogue(field)
        quest = field.sub_quests["sq_frost_hunt"]
        self.assertEqual(quest["status"], "IN_PROGRESS")
        for _ in range(4):
            field.resolve_battle_victory("frost_wisp")
        gold = field.gold
        field._interact()
        finish_dialogue(field)
        self.assertEqual(quest["status"], "COMPLETED")
        self.assertIn("frost_heart", field.owned_accessories)
        self.assertGreater(field.gold, gold)
        self.assertIn("sq_frost_hunt", QUEST_NAMES)

    def test_toby_still_runs_the_goblin_hunt(self):
        game = FakeGame()
        toby = FIELD_ROUTES["field_west"]["toby"]
        field = FieldScene(game, {"world": "field_west", "x": toby[0] + 1, "y": toby[1]})
        field._interact()
        finish_dialogue(field)
        self.assertEqual(field.sub_quests["sq_goblin_hunt"]["status"], "IN_PROGRESS")


class FreezeGearTests(unittest.TestCase):
    def test_scarf_and_frost_heart_stop_freezing(self):
        for accessory in ("warm_scarf", "frost_heart"):
            field = north(accessory=accessory, owned_accessories=[accessory], hp=999)
            self.assertIn("stun", field.immunities, accessory)
            engine = BattleEngine(field, "ice_slime", rng=FixedRng(0.0))
            engine.act("attack")
            self.assertNotIn("stun", engine.statuses["hero"], accessory)

    def test_frost_heart_is_a_reward_not_stock(self):
        self.assertIn("frost_heart", ACCESSORIES)
        self.assertNotIn("frost_heart", {item["id"] for item in SHOP_ITEMS})


class LateStockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_every_shrine_count_adds_something(self):
        sizes = [len(shop_stock(n)) for n in range(5)]
        for before, after in zip(sizes, sizes[1:]):
            self.assertLess(before, after)
        ids = lambda n: {item["id"] for item in shop_stock(n)}
        self.assertIn("warm_scarf", ids(2) - ids(1))
        self.assertIn("storm_halberd", ids(3) - ids(2))
        self.assertIn("aurora_mail", ids(4) - ids(3))

    def test_late_gear_is_stronger_than_early_gear(self):
        self.assertGreater(WEAPONS["storm_halberd"]["attack"], WEAPONS["earth_hammer"]["attack"])
        self.assertGreater(ARMORS["aurora_mail"]["defense"], ARMORS["dragon_scale"]["defense"])

    def test_shop_lists_five_weapons_without_overlap(self):
        game = FakeGame()
        game.field = FieldScene(game, {"world": "village", "x": 15, "y": 15,
                                       "quest_flags": {k: 1 for k in ("shrine_wind", "shrine_earth",
                                                                     "shrine_fire", "shrine_ice")}})
        shop = ShopScene(game)
        rows = shop._rows()
        self.assertEqual(len(rows), 5)
        self.assertLess(rows[-1].bottom, 428)  # description and message lines sit below
        self.assertTrue(ShopScene.panel_rect().contains(shop.close_rect()))
        shop.draw(pygame.Surface((800, 600)))


if __name__ == "__main__":
    unittest.main()

"""The inn (paid rest and rumours), the apothecary (new consumables) and the battle item menu."""

import os
import random
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.combat import BattleEngine
from gameplay.equipment import CONSUMABLES, shop_stock
from scenes.battle_scene import BattleScene
from scenes.confirm_scene import ConfirmScene
from scenes.field_scene import FieldScene
from scenes.shop_scene import ShopScene
from scenes.village_scene import VillageScene


class FakeGame:
    active_slot = 1
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}

    def __init__(self):
        self.field = None
        self.scene = None
        self.scene_name = "village"
        self.opened_shop = None

    def save_game(self):
        pass

    def open_shop(self, shop="logan"):
        self.opened_shop = shop

    def finish_battle(self):
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


def village(**state):
    game = FakeGame()
    scene = VillageScene(game, {"world": "village", "x": 15, "y": 15, **state})
    game.field = game.scene = scene
    return game, scene


ROOMS = {"inn": "village_inn", "smithy": "village_smithy", "library": "village_library",
         "apothecary": "village_apothecary"}


def keeper_room(name, **state):
    """The keeper now waits inside the building: open that room with the hero at the counter."""
    from scenes.house_scene import HouseInteriorScene

    game = FakeGame()
    room = HouseInteriorScene(game, {"world": ROOMS[name], "x": 12, "y": 7, **state})
    game.field = game.scene = room
    return game, room


def talk_keeper(room):
    room.player.update(x=12.0, y=7.0)
    room._interact()
    while room.dialogue_lines:
        room._advance_dialogue()


class InnTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_paid_rest_restores_everything(self):
        game, scene = keeper_room("inn", gold=200, hp=10, mp=1, level=5)
        talk_keeper(scene)
        self.assertIsInstance(game.scene, ConfirmScene)
        game.scene.handle_events([key(pygame.K_LEFT), key(pygame.K_RETURN)])  # 예
        self.assertEqual((scene.hp, scene.mp), (scene.max_hp, scene.max_mp))
        self.assertEqual(scene.gold, 200 - scene.inn_price())
        self.assertEqual(scene.inn_price(), 10 + 2 * 5)

    def test_no_money_no_bed(self):
        game, scene = keeper_room("inn", gold=0, hp=10)
        talk_keeper(scene)
        game.scene.handle_events([key(pygame.K_LEFT), key(pygame.K_RETURN)])
        self.assertEqual(scene.hp, 10)
        self.assertIn("모자라", " ".join(scene.dialogue_lines))

    def test_rumours_change_with_time(self):
        _, scene = village()
        rumours = set()
        for minute in range(12):
            scene.play_time = minute * 60
            rumours.add(scene.inn_rumour())
        self.assertGreater(len(rumours), 3)


class ApothecaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_mira_opens_her_own_shop(self):
        game, scene = keeper_room("apothecary")
        talk_keeper(scene)
        self.assertEqual(game.opened_shop, "mira")

    def test_her_stock_is_consumables_and_the_elixir_comes_later(self):
        early = {item["id"] for item in shop_stock(0, shop="mira")}
        self.assertTrue({"small_potion", "high_potion", "mana_potion", "antidote"} <= early)
        self.assertNotIn("elixir", early)
        self.assertIn("elixir", {item["id"] for item in shop_stock(3, shop="mira")})
        self.assertNotIn("steel_longsword", early)

    def test_buying_a_mana_potion(self):
        game, scene = village(gold=100)
        shop = ShopScene(game, "mira")
        self.assertEqual(shop.tab, "potion")
        shop.selected = [item["id"] for item in shop.items()].index("mana_potion")
        shop.handle_events([key(pygame.K_RETURN)])
        self.assertEqual(scene.item_count("mana_potion"), 1)
        self.assertEqual(scene.gold, 100 - CONSUMABLES["mana_potion"]["price"])
        shop.draw(pygame.Surface((800, 600)))

    def test_items_are_saved(self):
        _, scene = village(items={"antidote": 2, "bogus": 5})
        self.assertEqual(scene.items, {"antidote": 2})
        self.assertEqual(scene.serialize()["items"], {"antidote": 2})


class BattleItemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def hero(self, **state):
        game = FakeGame()
        game.field = FieldScene(game, {"world": "field_east", "x": 2, "y": 16, "hp": 999, "max_hp": 999, **state})
        return game, game.field

    def test_each_item_does_its_job(self):
        _, field = self.hero(mp=0, max_mp=60, items={"mana_potion": 1})
        BattleEngine(field, "slime", rng=FixedRng()).act("item", "mana_potion")
        self.assertEqual(field.mp, 30)
        self.assertEqual(field.item_count("mana_potion"), 0)
        _, field = self.hero(items={"antidote": 1})
        engine = BattleEngine(field, "slime", rng=FixedRng())
        engine.statuses["hero"] = {"poison": 3, "burn": 2}
        engine.act("item", "antidote")
        self.assertEqual(engine.statuses["hero"], {})
        _, field = self.hero(hp=5, mp=0, max_mp=40, items={"elixir": 1})
        BattleEngine(field, "slime", rng=FixedRng()).act("item", "elixir")
        self.assertGreater(field.hp, 900)
        self.assertEqual(field.mp, 40)

    def test_old_auto_potion_still_works(self):
        _, field = self.hero(hp=100, potions=1)
        BattleEngine(field, "slime", rng=FixedRng()).act("item")
        self.assertEqual(field.potions, 0)

    def test_battle_menu_lists_owned_items(self):
        game, field = self.hero(potions=2, items={"mana_potion": 1})
        scene = BattleScene(game, "slime", rng=FixedRng())
        self.assertEqual(scene.ACTIONS[2], "아이템")
        scene.selected = 2
        scene.handle_events([key(pygame.K_RETURN)])
        self.assertEqual(scene.mode, "items")
        self.assertEqual([i[0] for i in scene.item_list()], ["small_potion", "mana_potion"])
        scene.draw(pygame.Surface((800, 600)))
        scene.item_index = 1
        scene.handle_events([key(pygame.K_RETURN)])
        self.assertEqual(scene.mode, "playing")
        self.assertEqual(field.item_count("mana_potion"), 0)

    def test_escape_leaves_the_item_list(self):
        game, field = self.hero(potions=1)
        scene = BattleScene(game, "slime", rng=FixedRng())
        scene.selected = 2
        scene.handle_events([key(pygame.K_RETURN), key(pygame.K_ESCAPE)])
        self.assertEqual(scene.mode, "menu")


if __name__ == "__main__":
    unittest.main()

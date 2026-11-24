"""Wider equipment: elemental weapons, armor perks, an accessory slot and a tiered shop."""

import os
import random
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay import combat
from gameplay.combat import BattleEngine
from gameplay.equipment import ACCESSORIES, ARMORS, SHOP_ITEMS, SHOP_TABS, WEAPONS, item_info, shop_stock
from scenes.field_scene import FieldScene
from scenes.shop_scene import ShopScene


class FakeGame:
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}
    active_slot = 1

    def __init__(self, **state):
        self.saves = 0
        self.field = FieldScene(self, {"world": "village", "x": 15, "y": 15, **state})

    def save_game(self):
        self.saves += 1

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


def hero(**state):
    return FakeGame(**state).field


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


class DataTests(unittest.TestCase):
    def test_every_shop_item_is_described_and_priced(self):
        for item in SHOP_ITEMS:
            info = item_info(item)
            self.assertTrue(info["name"] and info["desc"], item)
            self.assertGreater(info["price"], 0, item)
            self.assertIn(item["kind"], dict(SHOP_TABS))

    def test_elements_are_real_battle_elements(self):
        for weapon in WEAPONS.values():
            self.assertIn(weapon.get("element", "none"), combat.ELEMENTS)

    def test_stock_widens_with_each_cleared_shrine(self):
        counts = [len(shop_stock(n)) for n in range(4)]
        self.assertEqual(counts, sorted(counts))
        self.assertLess(counts[0], counts[2])
        self.assertNotIn("flame_blade", [i["id"] for i in shop_stock(1)])
        self.assertIn("flame_blade", [i["id"] for i in shop_stock(2)])


class WeaponTests(unittest.TestCase):
    def test_weapon_element_rides_on_plain_attacks(self):
        field = hero(weapon="wind_dagger", owned_weapons=["wind_dagger"])
        engine = BattleEngine(field, "shrine_earth", rng=FixedRng())   # golem: weak to wind
        engine.act("attack")
        self.assertTrue(any(e.get("weak") for e in engine.log if e["type"] == "damage"))

    def test_dagger_adds_crit_chance(self):
        roll = combat.CRIT_CHANCE + 0.05
        plain = BattleEngine(hero(weapon="steel_longsword"), "skeleton", rng=FixedRng(roll))
        plain.act("attack")
        dagger = BattleEngine(hero(weapon="wind_dagger"), "skeleton", rng=FixedRng(roll))
        dagger.act("attack")
        crit = lambda e: any(x.get("crit") for x in e.log if x["type"] == "damage" and x["target"] == "enemy")
        self.assertFalse(crit(plain))
        self.assertTrue(crit(dagger))

    def test_flame_blade_can_burn_and_hammer_can_stun(self):
        burner = BattleEngine(hero(weapon="flame_blade", hp=999), "skeleton", rng=FixedRng(0.1))
        burner.act("attack")
        self.assertIn("burn", burner.statuses["enemy"])
        smasher = BattleEngine(hero(weapon="earth_hammer", hp=999), "skeleton", rng=FixedRng(0.1))
        events = smasher.act("attack")
        self.assertTrue(any(e["type"] == "stunned" for e in events))

    def test_star_sword_is_light(self):
        engine = BattleEngine(hero(weapon="star_sword", hp=999), "final_boss", rng=FixedRng())
        engine.act("attack")
        self.assertTrue(any(e.get("weak") for e in engine.log if e["type"] == "damage"))


class ArmorAndAccessoryTests(unittest.TestCase):
    def test_dragon_scale_blocks_burn_and_charm_blocks_poison(self):
        scaled = hero(armor="dragon_scale", hp=999)
        engine = BattleEngine(scaled, "salamander", rng=FixedRng(0.0))
        engine.act("attack")
        self.assertNotIn("burn", engine.statuses["hero"])
        charmed = hero(accessory="antidote_charm", hp=999)
        engine = BattleEngine(charmed, "mushroom", rng=FixedRng(0.0))
        engine.act("attack")
        self.assertNotIn("poison", engine.statuses["hero"])

    def test_accessories_change_stats(self):
        plain = hero()
        self.assertEqual(hero(accessory="power_bracelet").attack_power, plain.attack_power + 4)
        self.assertEqual(hero(accessory="feather_charm").evasion, plain.evasion + 8)
        self.assertEqual(hero(accessory="feather_charm", evasion_bonus=15).evasion, 23)

    def test_mana_ring_doubles_victory_mp(self):
        field = hero(accessory="mana_ring", atk=400, mp=0)
        BattleEngine(field, "slime", rng=FixedRng()).act("attack")
        self.assertEqual(field.mp, combat.VICTORY_MP + 2)

    def test_equipping_robe_and_breastplate_moves_max_hp_and_mp(self):
        field = hero(owned_armors=["traveler_clothes", "mage_robe", "knight_breastplate"])
        hp, mp = field.max_hp, field.max_mp
        field.equip("armor", "mage_robe")
        self.assertEqual((field.max_hp, field.max_mp), (hp, mp + 10))
        field.equip("armor", "knight_breastplate")
        self.assertEqual((field.max_hp, field.max_mp), (hp + 20, mp))
        self.assertLessEqual(field.mp, field.max_mp)
        field.equip("armor", "traveler_clothes")
        self.assertEqual((field.max_hp, field.max_mp), (hp, mp))

    def test_accessory_survives_save_and_old_saves_have_none(self):
        field = hero(accessory="mana_ring", owned_accessories=["mana_ring"])
        data = field.serialize()
        self.assertEqual((data["accessory"], data["owned_accessories"]), ("mana_ring", ["mana_ring"]))
        self.assertIsNone(hero().accessory)


class ShopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_tabs_show_only_their_kind_and_stock_grows(self):
        game = FakeGame()
        shop = ShopScene(game)
        self.assertEqual(shop.tab, "weapon")
        self.assertTrue(all(i["kind"] == "weapon" for i in shop.items()))
        early = len(shop.items())
        game.field.quest_flags["shrine_wind"] = game.field.quest_flags["shrine_earth"] = 1
        self.assertGreater(len(shop.items()), early)
        shop.handle_events([key(pygame.K_RIGHT)])
        self.assertEqual(shop.tab, "armor")
        shop.handle_events([key(pygame.K_LEFT), key(pygame.K_LEFT)])
        self.assertEqual(shop.tab, "potion")

    def test_buying_an_accessory_equips_it(self):
        game = FakeGame(gold=500)
        shop = ShopScene(game)
        shop.handle_events([key(pygame.K_RIGHT), key(pygame.K_RIGHT)])
        shop.selected = [i["id"] for i in shop.items()].index("feather_charm")
        shop.handle_events([key(pygame.K_RETURN)])
        self.assertEqual(game.field.accessory, "feather_charm")
        self.assertEqual(game.field.gold, 500 - ACCESSORIES["feather_charm"]["price"])
        self.assertGreaterEqual(game.saves, 1)

    def test_owned_gear_can_be_re_equipped_for_free(self):
        game = FakeGame(gold=0, owned_weapons=["rusty_sword", "wind_dagger"], weapon="rusty_sword")
        shop = ShopScene(game)
        shop.selected = [i["id"] for i in shop.items()].index("wind_dagger")
        shop.handle_events([key(pygame.K_RETURN)])
        self.assertEqual(game.field.weapon, "wind_dagger")

    def test_shop_draws_every_tab(self):
        game = FakeGame()
        shop = ShopScene(game)
        surface = pygame.Surface((800, 600))
        for _ in SHOP_TABS:
            shop.draw(surface)
            shop.handle_events([key(pygame.K_RIGHT)])

    def test_armor_ids_cover_everything_the_shop_sells(self):
        for item in SHOP_ITEMS:
            if item["kind"] == "armor":
                self.assertIn(item["id"], ARMORS)


if __name__ == "__main__":
    unittest.main()

"""Bag page: browse everything carried, use consumables in the field, swap gear anywhere."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from scenes.field_scene import FieldScene
from scenes.status_scene import PAGES, StatusScene


class FakeGame:
    active_slot = 1
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}

    def __init__(self):
        self.field = None
        self.scene = None
        self.scene_name = "field_east"
        self.status_page = None
        self.saves = 0

    def save_game(self):
        self.saves += 1

    def open_status(self, page="record"):
        self.status_page = page

    def font(self, size):
        return pygame.font.Font(None, size)


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


def bag(**state):
    game = FakeGame()
    game.field = FieldScene(game, {"world": "field_east", "x": 2, "y": 16, **state})
    status = StatusScene(game, page="bag")
    return game, game.field, status


def select(status, kind, item_id):
    rows = status.bag_rows()
    status.bag_index = next(i for i, row in enumerate(rows) if row.get("kind") == kind and row.get("id") == item_id)


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_bag_is_the_last_status_page_and_b_opens_it(self):
        self.assertEqual(PAGES[-1][0], "bag")
        game, field, _ = bag()
        field.handle_events([key(pygame.K_b)])
        self.assertEqual(game.status_page, "bag")

    def test_rows_group_everything_carried(self):
        _, field, status = bag(potions=2, items={"mana_potion": 1}, owned_weapons=["rusty_sword", "wind_dagger"],
                               owned_accessories=["mana_ring"], quest_items=["knights_crest"])
        rows = status.bag_rows()
        headers = [row["label"] for row in rows if row["kind"] == "header"]
        self.assertEqual(headers, ["소모품", "무기", "방어구", "장신구", "중요 물품"])
        ids = {(row["kind"], row.get("id")) for row in rows}
        for expected in (("consumable", "small_potion"), ("consumable", "mana_potion"), ("weapon", "wind_dagger"),
                         ("armor", "traveler_clothes"), ("accessory", "mana_ring"), ("key", "knights_crest")):
            self.assertIn(expected, ids)
        self.assertNotIn(("consumable", "high_potion"), ids)  # none carried

    def test_cursor_skips_headers_and_scrolls(self):
        _, field, status = bag(owned_accessories=["mana_ring", "feather_charm", "power_bracelet", "warm_scarf",
                                                  "antidote_charm", "frost_heart", "smith_ring", "sage_glasses"],
                               owned_weapons=["rusty_sword", "wind_dagger", "earth_hammer", "flame_blade"],
                               potions=3, high_potions=2, items={"mana_potion": 1, "antidote": 1, "elixir": 1})
        rows = status.bag_rows()
        self.assertNotEqual(rows[status.bag_index]["kind"], "header")
        for _ in range(len(rows) + 3):
            status.handle_events([key(pygame.K_DOWN)])
            self.assertNotEqual(rows[status.bag_index]["kind"], "header")
            first, last = status.visible_range()
            self.assertTrue(first <= status.bag_index < last)
        status.draw(pygame.Surface((800, 600)))


class UseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_drinking_a_potion_in_the_field(self):
        game, field, status = bag(hp=10, max_hp=100, potions=2)
        select(status, "consumable", "small_potion")
        status.handle_events([key(pygame.K_RETURN)])
        self.assertEqual((field.hp, field.potions), (60, 1))
        self.assertGreaterEqual(game.saves, 1)

    def test_mana_potion_and_no_waste_when_full(self):
        game, field, status = bag(mp=0, max_mp=50, items={"mana_potion": 2})
        select(status, "consumable", "mana_potion")
        status.handle_events([key(pygame.K_RETURN)])
        self.assertEqual((field.mp, field.item_count("mana_potion")), (30, 1))
        field.mp = field.max_mp
        status.handle_events([key(pygame.K_RETURN)])
        self.assertEqual(field.item_count("mana_potion"), 1)
        self.assertIn("가득", status.bag_message)

    def test_antidote_is_kept_for_battle(self):
        _, field, status = bag(items={"antidote": 1})
        select(status, "consumable", "antidote")
        status.handle_events([key(pygame.K_RETURN)])
        self.assertEqual(field.item_count("antidote"), 1)
        self.assertIn("전투", status.bag_message)

    def test_swapping_weapon_and_armour_from_the_bag(self):
        _, field, status = bag(owned_weapons=["rusty_sword", "wind_dagger"],
                               owned_armors=["traveler_clothes", "knight_breastplate"])
        hp = field.max_hp
        select(status, "weapon", "wind_dagger")
        status.handle_events([key(pygame.K_RETURN)])
        self.assertEqual(field.weapon, "wind_dagger")
        select(status, "armor", "knight_breastplate")
        status.handle_events([key(pygame.K_RETURN)])
        self.assertEqual((field.armor, field.max_hp), ("knight_breastplate", hp + 20))

    def test_accessory_toggles_on_and_off(self):
        _, field, status = bag(owned_accessories=["mana_ring", "feather_charm"])
        select(status, "accessory", "mana_ring")
        status.handle_events([key(pygame.K_RETURN)])
        self.assertEqual(field.accessory, "mana_ring")
        status.handle_events([key(pygame.K_RETURN)])
        self.assertIsNone(field.accessory)
        select(status, "accessory", "feather_charm")
        status.handle_events([key(pygame.K_RETURN)])
        self.assertEqual(field.accessory, "feather_charm")

    def test_page_draws_details_for_every_kind(self):
        _, field, status = bag(potions=1, owned_accessories=["mana_ring"], quest_items=["knights_crest"],
                               upgrades={"rusty_sword": 2})
        surface = pygame.Surface((800, 600))
        for index, row in enumerate(status.bag_rows()):
            if row["kind"] != "header":
                status.bag_index = index
                status.draw(surface)


if __name__ == "__main__":
    unittest.main()

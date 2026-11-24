"""Bron's smithy: upgrade the equipped weapon and armour up to +3 for gold."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from scenes.field_scene import FieldScene
from scenes.smithy_scene import MAX_UPGRADE, SmithyScene, upgrade_cost
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

    def save_game(self):
        pass

    def font(self, size):
        return pygame.font.Font(None, size)


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


def hero(**state):
    game = FakeGame()
    game.field = game.scene = FieldScene(game, {"world": "village", "x": 15, "y": 15, **state})
    return game, game.field


class UpgradeRuleTests(unittest.TestCase):
    def test_upgrades_add_attack_and_defense(self):
        _, plain = hero(weapon="steel_longsword", owned_weapons=["steel_longsword"])
        _, forged = hero(weapon="steel_longsword", owned_weapons=["steel_longsword"],
                         upgrades={"steel_longsword": 2, "traveler_clothes": 1})
        self.assertEqual(forged.attack_power, plain.attack_power + 6)
        self.assertEqual(forged.defense_power, plain.defense_power + 2)

    def test_costs_rise_and_cap_at_three(self):
        self.assertEqual(MAX_UPGRADE, 3)
        self.assertEqual([upgrade_cost("weapon", level) for level in range(3)], [80, 160, 240])
        self.assertEqual([upgrade_cost("armor", level) for level in range(3)], [60, 120, 180])

    def test_upgrades_are_saved_and_cleaned(self):
        _, field = hero(upgrades={"rusty_sword": 1, "nonsense": 2, "traveler_clothes": 9})
        self.assertEqual(field.upgrades, {"rusty_sword": 1, "traveler_clothes": 3})
        self.assertEqual(field.serialize()["upgrades"], {"rusty_sword": 1, "traveler_clothes": 3})

    def test_upgrades_stay_with_the_item(self):
        _, field = hero(weapon="rusty_sword", owned_weapons=["rusty_sword", "wind_dagger"],
                        upgrades={"rusty_sword": 3})
        boosted = field.attack_power
        field.equip("weapon", "wind_dagger")
        field.equip("weapon", "rusty_sword")
        self.assertEqual(field.attack_power, boosted)


class SmithySceneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_upgrading_the_weapon_spends_gold(self):
        game, field = hero(gold=500)
        smithy = SmithyScene(game, field)
        smithy.handle_events([key(pygame.K_RETURN)])
        self.assertEqual(field.upgrades.get("rusty_sword"), 1)
        self.assertEqual(field.gold, 500 - 80)
        smithy.handle_events([key(pygame.K_DOWN), key(pygame.K_RETURN)])
        self.assertEqual(field.upgrades.get("traveler_clothes"), 1)
        smithy.draw(pygame.Surface((800, 600)))

    def test_no_gold_or_max_level_refuses(self):
        game, field = hero(gold=10)
        smithy = SmithyScene(game, field)
        smithy.handle_events([key(pygame.K_RETURN)])
        self.assertEqual(field.upgrades, {})
        game, field = hero(gold=9999, upgrades={"rusty_sword": 3})
        smithy = SmithyScene(game, field)
        smithy.handle_events([key(pygame.K_RETURN)])
        self.assertEqual(field.upgrades["rusty_sword"], 3)
        self.assertEqual(field.gold, 9999)

    def test_escape_goes_back(self):
        game, field = hero()
        game.scene = SmithyScene(game, field)
        game.scene.handle_events([key(pygame.K_ESCAPE)])
        self.assertIs(game.scene, field)

    def test_bron_opens_the_smithy(self):
        from scenes.house_scene import HouseInteriorScene

        game = FakeGame()
        room = HouseInteriorScene(game, {"world": "village_smithy", "x": 12, "y": 7,
                                         "sub_quests": {"sq_smith_ore": {"status": "COMPLETED", "progress": 4}}})
        game.field = game.scene = room
        room._interact()
        while room.dialogue_lines:
            room._advance_dialogue()
        self.assertIsInstance(game.scene, SmithyScene)


if __name__ == "__main__":
    unittest.main()

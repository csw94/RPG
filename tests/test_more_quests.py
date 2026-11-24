"""Three more villager requests that reward unique accessories."""

import os
import random
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay import combat
from gameplay.combat import BattleEngine
from gameplay.equipment import ACCESSORIES
from scenes.field_scene import FieldScene
from scenes.house_scene import HouseInteriorScene
from scenes.status_scene import QUEST_NAMES, StatusScene
from scenes.village_scene import VillageScene

NEW_QUESTS = {"sq_wolf_hunt": ("wolf", 4, "wolf_fang_charm"),
              "sq_magma_ore": ("magma_slime", 3, "ember_bracelet"),
              "sq_bat_hunt": ("bat", 4, "guardian_medal")}


class FakeGame:
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}
    active_slot = 1

    def __init__(self):
        self.shop_opened = 0
        self.field = None
        self.scene = None
        self.scene_name = ""

    def save_game(self):
        pass

    def open_shop(self):
        self.shop_opened += 1

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


def finish_dialogue(scene):
    while scene.dialogue_lines:
        scene._advance_dialogue()


def village(x, y, **state):
    game = FakeGame()
    scene = VillageScene(game, {"world": "village", "x": x, "y": y, **state})
    game.field = scene
    return game, scene


class VillagerQuestTests(unittest.TestCase):
    def test_plaza_villager_offers_and_rewards_the_wolf_hunt(self):
        game, scene = village(VillageScene.VILLAGER[0] + 1, VillageScene.VILLAGER[1])
        scene._interact()
        finish_dialogue(scene)
        quest = scene.sub_quests["sq_wolf_hunt"]
        self.assertEqual(quest["status"], "IN_PROGRESS")
        for _ in range(4):
            scene.resolve_battle_victory("wolf")
        self.assertEqual(quest["progress"], 4)
        gold = scene.gold
        scene._interact()
        finish_dialogue(scene)
        self.assertEqual(quest["status"], "COMPLETED")
        self.assertIn("wolf_fang_charm", scene.owned_accessories)
        self.assertGreater(scene.gold, gold)
        scene._interact()
        self.assertTrue(scene.dialogue_lines)  # still chats afterwards

    def test_kills_only_count_while_the_request_is_active(self):
        _, scene = village(15, 15)
        scene.resolve_battle_victory("wolf")
        self.assertEqual(scene.sub_quests["sq_wolf_hunt"]["progress"], 0)


class LoganQuestTests(unittest.TestCase):
    def talk(self, scene):
        scene.player.update(x=float(VillageScene.LOGAN[0]), y=float(VillageScene.LOGAN[1] + 1))
        scene._interact()
        finish_dialogue(scene)

    def test_logan_just_sells_until_a_shrine_is_cleared(self):
        game, scene = village(15, 15)
        self.talk(scene)
        self.assertEqual(game.shop_opened, 1)
        self.assertEqual(scene.sub_quests["sq_magma_ore"]["status"], "NOT_STARTED")

    def test_logan_asks_first_then_runs_the_shop(self):
        game, scene = village(15, 15)
        scene.quest_flags["shrine_wind"] = 1
        self.talk(scene)
        self.assertEqual(scene.sub_quests["sq_magma_ore"]["status"], "IN_PROGRESS")
        self.assertEqual(game.shop_opened, 0)
        self.talk(scene)
        self.assertEqual(game.shop_opened, 1)
        for _ in range(3):
            scene.resolve_battle_victory("magma_slime")
        self.talk(scene)
        self.assertEqual(scene.sub_quests["sq_magma_ore"]["status"], "COMPLETED")
        self.assertIn("ember_bracelet", scene.owned_accessories)
        self.talk(scene)
        self.assertEqual(game.shop_opened, 2)


class GarenQuestTests(unittest.TestCase):
    def garen(self, **state):
        game = FakeGame()
        scene = HouseInteriorScene(game, {"world": "village_house_2", "x": 12, "y": 7, **state})
        game.field = scene
        return scene

    def test_bat_hunt_follows_the_old_sword(self):
        scene = self.garen()
        scene._interact()
        finish_dialogue(scene)
        self.assertEqual(scene.sub_quests["sq_bat_hunt"]["status"], "NOT_STARTED")
        scene.sub_quests["sq_old_sword"]["status"] = "COMPLETED"
        scene._interact()
        finish_dialogue(scene)
        self.assertEqual(scene.sub_quests["sq_bat_hunt"]["status"], "IN_PROGRESS")
        for _ in range(4):
            scene.resolve_battle_victory("bat")
        scene._interact()
        finish_dialogue(scene)
        self.assertIn("guardian_medal", scene.owned_accessories)


class RewardTests(unittest.TestCase):
    def hero(self, accessory):
        game = FakeGame()
        return FieldScene(game, {"world": "village", "x": 15, "y": 15, "accessory": accessory,
                                 "owned_accessories": [accessory], "hp": 999})

    def test_new_accessories_do_what_they_say(self):
        plain = self.hero(None)
        self.assertEqual(self.hero("guardian_medal").defense_power, plain.defense_power + 5)
        self.assertEqual(self.hero("ember_bracelet").attack_power, plain.attack_power + 3)
        self.assertIn("burn", self.hero("ember_bracelet").immunities)
        roll = combat.CRIT_CHANCE + 0.05
        engine = BattleEngine(self.hero("wolf_fang_charm"), "skeleton", rng=FixedRng(roll))
        engine.act("attack")
        self.assertTrue(any(e.get("crit") for e in engine.log if e["type"] == "damage"))

    def test_rewards_are_not_sold(self):
        from gameplay.equipment import SHOP_ITEMS
        sold = {item["id"] for item in SHOP_ITEMS}
        for _, _, reward in NEW_QUESTS.values():
            self.assertIn(reward, ACCESSORIES)
            self.assertNotIn(reward, sold)


class StatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_status_lists_every_request(self):
        self.assertEqual(len(QUEST_NAMES), 11)
        game, scene = village(15, 15)
        status = StatusScene(game)
        self.assertEqual(len(status.quest_rows()), len(QUEST_NAMES))
        status.draw(pygame.Surface((800, 600)))


if __name__ == "__main__":
    unittest.main()

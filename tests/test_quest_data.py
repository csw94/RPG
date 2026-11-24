"""Villager requests live in one table (gameplay/quests.py); every screen reads from it."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from gameplay.enemies import ENEMIES
from gameplay.equipment import ACCESSORIES
from gameplay.quests import QUESTS, kill_quests
from scenes.field_scene import FieldScene
from scenes.status_scene import QUEST_NAMES


class FakeGame:
    active_slot = 1

    def save_game(self):
        pass


class QuestTableTests(unittest.TestCase):
    def test_every_request_is_fully_described(self):
        self.assertEqual(len(QUESTS), 7)
        for quest_id, quest in QUESTS.items():
            self.assertTrue(quest_id.startswith("sq_"))
            self.assertTrue(quest["name"], quest_id)
            self.assertGreater(quest["target"], 0, quest_id)
            self.assertGreaterEqual(len(quest["offer"]), 1, quest_id)
            self.assertGreaterEqual(len(quest["done"]), 1, quest_id)
            self.assertTrue(quest["reward"], quest_id)

    def test_references_point_at_real_things(self):
        for quest_id, quest in QUESTS.items():
            if quest.get("kill"):
                self.assertIn(quest["kill"], ENEMIES, quest_id)
            accessory = quest["reward"].get("accessory")
            if accessory:
                self.assertIn(accessory, ACCESSORIES, quest_id)
        self.assertEqual(kill_quests()["sq_goblin_hunt"], "goblin")
        self.assertNotIn("sq_moon_herb", kill_quests())

    def test_screens_and_saves_use_the_table(self):
        self.assertEqual(QUEST_NAMES, {qid: q["name"] for qid, q in QUESTS.items()})
        field = FieldScene(FakeGame(), {"world": "village", "x": 15, "y": 15})
        self.assertEqual(list(field.sub_quests), list(QUESTS))
        for quest_id, quest in QUESTS.items():
            self.assertEqual(field.sub_quests[quest_id]["target"], quest["target"])

    def test_every_reward_is_paid_on_completion(self):
        for quest_id, quest in QUESTS.items():
            field = FieldScene(FakeGame(), {"world": "village", "x": 15, "y": 15})
            state = field.sub_quests[quest_id]
            state.update(status="IN_PROGRESS", progress=quest["target"])
            if quest.get("requires_item"):
                field.quest_items.add(quest["requires_item"])
            before = (field.gold, field.potions, field.high_potions, field.atk, field.defense)
            self.assertTrue(field._complete_sidequest(quest_id), quest_id)
            reward = quest["reward"]
            self.assertEqual(field.gold, before[0] + reward.get("gold", 0), quest_id)
            self.assertEqual(field.potions, min(10, before[1] + reward.get("potions", 0)), quest_id)
            self.assertEqual(field.high_potions, min(10, before[2] + reward.get("high_potions", 0)), quest_id)
            self.assertEqual(field.atk, before[3] + reward.get("atk", 0), quest_id)
            self.assertEqual(field.defense, before[4] + reward.get("defense", 0), quest_id)
            if reward.get("accessory"):
                self.assertIn(reward["accessory"], field.owned_accessories, quest_id)
            if reward.get("quest_item"):
                self.assertIn(reward["quest_item"], field.quest_items, quest_id)
            self.assertEqual(state["status"], "COMPLETED")

    def test_required_items_block_completion(self):
        field = FieldScene(FakeGame(), {"world": "village", "x": 15, "y": 15})
        field.sub_quests["sq_old_sword"].update(status="IN_PROGRESS", progress=1)
        self.assertFalse(field._complete_sidequest("sq_old_sword"))


if __name__ == "__main__":
    unittest.main()

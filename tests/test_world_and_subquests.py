"""Coverage for the expanded world graph and persistent side quests."""

import tempfile
import unittest
from pathlib import Path

from db.save_manager import StoryProgressionManager


class WorldAndSubquestTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store = StoryProgressionManager(Path(self.temp_dir.name) / "game.db")
        self.store.init_new_game("모험가")

    def tearDown(self):
        self.store.close()
        self.temp_dir.cleanup()

    def test_map_graph_allows_only_direct_exit(self):
        self.assertTrue(self.store.move_player("village_house_1"))
        self.assertEqual(self.store.load_game()["player"]["current_map"], "village_house_1")
        self.assertFalse(self.store.move_player("shrine_wind_2f"))
        self.assertEqual(self.store.load_game()["player"]["current_map"], "village_house_1")

    def test_goblin_kills_do_not_count_before_acceptance(self):
        self.store.record_goblin_scout_kill(4)
        self.assertEqual(self.store.get_sub_quest("sq_goblin_hunt")["progress"], 0)
        self.store.accept_sub_quest("sq_goblin_hunt")
        self.store.record_goblin_scout_kill()
        self.assertEqual(self.store.get_sub_quest("sq_goblin_hunt")["progress"], 1)

    def test_old_sword_reward_is_applied_once(self):
        self.store.accept_sub_quest("sq_old_sword")
        self.store.advance_sub_quest("sq_old_sword")
        self.assertTrue(self.store.complete_sub_quest("sq_old_sword"))
        player = self.store.load_game()["player"]
        self.assertEqual((player["atk"], player["def"]), (19, 9))
        self.assertFalse(self.store.complete_sub_quest("sq_old_sword"))
        player = self.store.load_game()["player"]
        self.assertEqual((player["atk"], player["def"]), (19, 9))

    def test_all_side_quest_rows_are_initialized_and_rewards_are_persistent(self):
        quests = {quest_id: self.store.get_sub_quest(quest_id) for quest_id in (
            "sq_moon_herb", "sq_old_sword", "sq_goblin_hunt")}
        self.assertEqual({key: (value["status"], value["progress"], value["target"])
                          for key, value in quests.items()}, {
            "sq_moon_herb": ("NOT_STARTED", 0, 3),
            "sq_old_sword": ("NOT_STARTED", 0, 1),
            "sq_goblin_hunt": ("NOT_STARTED", 0, 5),
        })
        self.store.accept_sub_quest("sq_moon_herb")
        self.store.advance_sub_quest("sq_moon_herb", 8)
        self.store.complete_sub_quest("sq_moon_herb")
        player = self.store.load_game()["player"]
        self.assertEqual(player["gold"], 100)
        self.assertEqual(self.store.load_game()["inventory"]["high_potions"], 2)


if __name__ == "__main__":
    unittest.main()

"""End-to-end checks for the local RPG save and progression backend."""

import tempfile
import unittest
from pathlib import Path

from db.save_manager import StoryProgressionManager


EXPECTED_FLAGS = {
    "prologue_done", "shrine_wind", "shrine_earth", "shrine_fire",
    "star_sword_awakened", "final_boss",
}


class StoryProgressionTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "game_save.db"
        self.store = StoryProgressionManager(self.database_path)

    def tearDown(self):
        self.store.close()
        self.temp_dir.cleanup()

    def test_new_game_saves_default_player_and_all_six_flags(self):
        self.store.init_new_game("\ubcc4\ube5b \uc218\ud638\uc790")
        self.store.close()
        self.store = StoryProgressionManager(self.database_path)
        loaded = self.store.load_game()
        self.assertEqual(loaded["player"], {
            "id": 1, "player_name": "\ubcc4\ube5b \uc218\ud638\uc790", "level": 1,
            "hp": 100, "max_hp": 100, "atk": 15, "def": 5, "gold": 0,
            "weapon": "\ub179\uc2a8 \ucca0\uac80", "current_map": "village_square",
            "pos_x": 10, "pos_y": 10, "evasion_bonus": 0,
        })
        self.assertEqual(set(loaded["flags"]), EXPECTED_FLAGS)
        self.assertTrue(all(value == 0 for value in loaded["flags"].values()))

    def test_fire_shrine_rewards_are_applied_once(self):
        self.store.init_new_game("\uc6a9\uc0ac")
        self.assertTrue(self.store.clear_shrine("shrine_fire"))
        first = self.store.load_game()["player"]
        self.assertEqual((first["level"], first["hp"], first["max_hp"]), (2, 130, 130))
        self.assertEqual((first["atk"], first["def"]), (30, 8))
        self.assertFalse(self.store.clear_shrine("shrine_fire"))
        self.assertEqual(self.store.load_game()["player"], first)

    def test_shrines_can_be_cleared_in_any_order_before_sword_awakening(self):
        self.store.init_new_game("\uc6a9\uc0ac")
        for shrine in ("shrine_earth", "shrine_wind", "shrine_fire"):
            self.assertTrue(self.store.clear_shrine(shrine))
        self.assertTrue(self.store.check_fountain_awakening())
        awakened = self.store.load_game()
        self.assertEqual(awakened["flags"]["star_sword_awakened"], 1)
        self.assertEqual(awakened["player"]["weapon"], "\ubcc4\ube5b\uc758 \uac80")
        self.assertEqual(awakened["player"]["atk"], 65)
        self.assertTrue(self.store.check_fountain_awakening())
        self.assertEqual(self.store.load_game()["player"]["atk"], 65)

    def test_fountain_stays_locked_until_all_three_shrines_are_cleared(self):
        self.store.init_new_game("\uc6a9\uc0ac")
        self.store.clear_shrine("shrine_wind")
        self.store.clear_shrine("shrine_fire")
        self.assertFalse(self.store.check_fountain_awakening())
        self.assertEqual(self.store.load_game()["flags"]["star_sword_awakened"], 0)
        self.assertEqual(self.store.load_game()["player"]["weapon"], "\ub179\uc2a8 \ucca0\uac80")

    def test_slime_battle_uses_damage_formula_and_persists_hp(self):
        self.store.init_new_game("\uc6a9\uc0ac")
        result = self.store.simulate_battle("slime")
        self.assertTrue(result.victory)
        self.assertEqual(result.turns, 3)
        self.assertEqual(result.player_hp, 90)
        self.assertEqual(result.monster_hp, 0)
        self.assertEqual(self.store.load_game()["player"]["hp"], 90)

    def test_awakened_hero_can_defeat_final_boss_and_unlock_ending(self):
        self.store.init_new_game("\ubcc4\ube5b \uc218\ud638\uc790")
        for shrine in ("shrine_fire", "shrine_earth", "shrine_wind"):
            self.store.clear_shrine(shrine)
        self.store.check_fountain_awakening()
        result = self.store.simulate_battle("final_boss")
        self.assertTrue(result.victory)
        self.assertEqual(self.store.load_game()["flags"]["final_boss"], 1)
        self.assertTrue(self.store.is_ending_unlocked())

    def test_final_boss_is_locked_before_sword_awakening(self):
        self.store.init_new_game("\uc6a9\uc0ac")
        with self.assertRaises(PermissionError):
            self.store.simulate_battle("final_boss")

    def test_memory_database_is_supported(self):
        store = StoryProgressionManager(":memory:")
        try:
            store.init_new_game("\uae30\uc5b5 \uc6a9\uc0ac")
            self.assertEqual(store.load_game()["player"]["player_name"], "\uae30\uc5b5 \uc6a9\uc0ac")
        finally:
            store.close()


if __name__ == "__main__":
    unittest.main()

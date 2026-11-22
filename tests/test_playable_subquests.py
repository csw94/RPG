"""Gameplay hooks for the three side quests."""

import unittest
from scenes.dungeon_scene import DungeonScene
from scenes.field_scene import FieldScene
from scenes.house_scene import HouseInteriorScene
from scenes.village_scene import VillageScene


class FakeGame:
    def save_game(self):
        pass

    def enter_world(self, world, position):
        self.destination = (world, position)

    def open_shop(self):
        self.shop_opened = True

    def start_epilogue(self):
        self.epilogue_started = True

    def start_battle(self, enemy_id):
        self.last_battle = enemy_id


class PlayableSubquestTests(unittest.TestCase):
    def test_house_doors_lead_to_marta_and_garen_and_logan_runs_the_plaza_stall(self):
        game = FakeGame()
        village = VillageScene(game, {"world": "village", "x": 12, "y": 13})
        village.player.update(x=5, y=7)
        self.assertFalse(village._blocked(5, 7))
        village._interact()
        self.assertEqual(game.destination[0], "village_house_1")

        cottage = HouseInteriorScene(game, {"world": "village_house_1"})
        cottage.player.update(x=7, y=6)
        cottage._interact()
        self.assertEqual(cottage.dialogue_action, "accept_subquest:sq_moon_herb")

        village.player.update(x=19, y=8)
        self.assertFalse(village._blocked(19, 7))
        self.assertFalse(village._blocked(19, 8))
        village._interact()
        self.assertEqual(game.destination[0], "village_house_2")
        quarters = HouseInteriorScene(game, {"world": "village_house_2"})
        self.assertEqual(quarters.npcs, ((12, 6),))
        quarters.player.update(x=12, y=7)
        quarters._interact()
        self.assertEqual(quarters.dialogue_action, "accept_subquest:sq_old_sword")
        self.assertEqual(cottage.npcs, ((7, 6),))

        village.player.update(x=16, y=11)
        self.assertFalse(village._blocked(16, 11))
        village._interact()
        self.assertEqual(village.dialogue_action, "open_shop")
        village.dialogue_index = len(village.dialogue_lines) - 1
        village._advance_dialogue()
        self.assertTrue(game.shop_opened)

    def test_final_boss_victory_queues_epilogue_and_fountain_replays_it(self):
        game = FakeGame()
        village = VillageScene(game, {"world": "village", "x": 12, "y": 13,
                                      "quest_flags": {"star_sword_awakened": 1}})
        village.resolve_battle_victory("final_boss")
        self.assertEqual(village.quest_flags["final_boss"], 1)

        village.player.update(x=12, y=12)
        village._interact()
        self.assertEqual(village.dialogue_action, "epilogue")
        village.dialogue_index = len(village.dialogue_lines) - 1
        village._advance_dialogue()
        self.assertTrue(game.epilogue_started)

    def test_epilogue_lines_remember_completed_favours(self):
        from scenes.epilogue_scene import epilogue_lines

        game = FakeGame()
        village = VillageScene(game, {"world": "village", "sub_quests": {
            "sq_old_sword": {"status": "COMPLETED", "progress": 1}}})
        lines = dict(epilogue_lines(village))
        self.assertIn("휘장", lines["노기사 가렌"])
        self.assertNotIn("달빛 약초", lines["약초상 마르타"])
        self.assertEqual(epilogue_lines(village)[-3][0], "촌장 발렌")

    def test_northern_shrine_and_new_central_chief_house_are_accessible(self):
        game = FakeGame()
        village = VillageScene(game, {"world": "village", "x": 12, "y": 13})
        village.player.update(x=12, y=7)
        self.assertFalse(village._blocked(12, 7))
        village._interact()
        self.assertEqual(game.destination[0], "village_chief_house")
        village.player.update(x=12, y=1)
        village._interact()
        self.assertEqual(game.destination[0], "village_north_shrine")

    def test_field_chests_block_occupying_the_tile_but_open_from_adjacent_tile(self):
        game = FakeGame()
        field = FieldScene(game, {"world": "field"})
        field.chests = {(10, 10): "potion"}
        field.player.update(x=10, y=10)
        self.assertTrue(field._blocked(10, 10))
        field.player.update(x=10, y=11)
        self.assertFalse(field._blocked(10, 11))
        field._interact()
        self.assertIn((10, 10), field.opened)

    def test_route_fields_are_separate_and_their_exits_link_to_their_own_shrine(self):
        game = FakeGame()
        route_to_shrine = {
            "field_east": ("shrine_wind_1f", (3, 14)),
            "field_west": ("shrine_earth_1f", (11, 14)),
            "field_south": ("shrine_fire_1f", (21, 14)),
        }
        for map_id, expected in route_to_shrine.items():
            field = FieldScene(game, {"world": map_id})
            self.assertEqual(field.route_data["name"], {
                "field_east": "바람 부는 숲길", "field_west": "붉은 바위 협곡",
                "field_south": "메마른 화산 기슭",
            }[map_id])
            px, py = field.route_data["dungeon_portal"]
            field.player.update(x=px, y=py)
            field._interact()
            self.assertEqual(game.destination, expected)

    def test_marta_offers_quest_and_herbs_advance_it(self):
        game = FakeGame()
        cottage = HouseInteriorScene(game, {"world": "village_house_1"})
        cottage.player.update(x=7, y=6)
        cottage._interact()
        cottage._advance_dialogue()
        cottage._advance_dialogue()
        self.assertEqual(cottage.sub_quests["sq_moon_herb"]["status"], "IN_PROGRESS")

        field = FieldScene(game, {"world": "field_east", "sub_quests": cottage.sub_quests})
        for point in sorted(field.herb_positions):
            field.player.update(x=point[0], y=point[1])
            field._interact()
        self.assertEqual(field.sub_quests["sq_moon_herb"]["progress"], 3)

    def test_garen_sword_chest_and_toby_goblin_kills_progress(self):
        game = FakeGame()
        dungeon = DungeonScene(game, {
            "world": "shrine_earth_1f", "sub_quests": {
                "sq_old_sword": {"status": "IN_PROGRESS", "progress": 0},
            },
        })
        chest = next(iter(dungeon.chests))
        dungeon.player.update(x=chest[0], y=chest[1])
        dungeon._interact()
        self.assertEqual(dungeon.sub_quests["sq_old_sword"]["progress"], 1)
        self.assertIn("broken_old_sword", dungeon.quest_items)

        field = FieldScene(game, {"world": "field", "sub_quests": {
            "sq_goblin_hunt": {"status": "IN_PROGRESS", "progress": 0},
        }})
        for _ in range(5):
            field.resolve_battle_victory("goblin")
        self.assertEqual(field.sub_quests["sq_goblin_hunt"]["progress"], 5)


if __name__ == "__main__":
    unittest.main()

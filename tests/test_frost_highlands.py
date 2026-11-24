"""Frost Highlands (field_north) and the Ice Shrine: map, gate, enemies, freezing, art."""

import os
import random
import unittest
from collections import deque

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.combat import BattleEngine
from gameplay.enemies import ENEMIES
from gameplay.world_data import FIELD_ROUTES, MAP_GRAPH
from scenes.dungeon_scene import SHRINE_DUNGEONS, DungeonScene
from scenes.field_scene import FieldScene
from scenes.shrine_clearing_scene import ShrineClearingScene
from utils import battle_art
from utils.audio import music_for


class FakeGame:
    active_slot = 1
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}

    def __init__(self):
        self.entered = None

    def save_game(self):
        pass

    def enter_world(self, world, position):
        self.entered = (world, position)

    def start_battle(self, enemy_id):
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


NORTH = FIELD_ROUTES["field_north"]


def reachable(scene, start):
    seen, queue = {start}, deque([start])
    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in seen and not scene._blocked(nx, ny):
                seen.add((nx, ny))
                queue.append((nx, ny))
    return seen


class GateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def clearing(self, *cleared):
        game = FakeGame()
        flags = {key: 1 for key in cleared}
        scene = ShrineClearingScene(game, {"x": ShrineClearingScene.NORTH_GATE[0],
                                           "y": ShrineClearingScene.NORTH_GATE[1] + 1, "quest_flags": flags})
        self.assertFalse(scene.position_recovered)
        return game, scene

    def test_the_north_gate_is_frozen_until_two_shrines_are_cleared(self):
        game, scene = self.clearing("shrine_wind")
        scene._interact()
        self.assertIsNone(game.entered)
        self.assertIn("얼음", scene.message)

    def test_two_seals_thaw_the_road_north(self):
        game, scene = self.clearing("shrine_wind", "shrine_fire")
        scene._interact()
        self.assertEqual(game.entered, ("field_north", NORTH["village_spawn"]))

    def test_gate_is_reachable_from_the_village_side(self):
        game, scene = self.clearing()
        reach = reachable(scene, ShrineClearingScene.SPAWN)
        gate = ShrineClearingScene.NORTH_GATE
        self.assertTrue(reach & {gate, (gate[0], gate[1] + 1)})
        scene.draw(pygame.Surface((800, 600)))

    def test_map_graph_links_the_north(self):
        self.assertIn("field_north", MAP_GRAPH["village_north_shrine"])
        self.assertEqual(set(MAP_GRAPH["field_north"]), {"village_north_shrine", "shrine_ice_1f"})
        self.assertIn("shrine_ice_2f", MAP_GRAPH["shrine_ice_1f"])


class FieldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def field(self, x, y):
        game = FakeGame()
        scene = FieldScene(game, {"world": "field_north", "x": x, "y": y})
        return game, scene

    def test_snowy_field_has_frozen_lakes_and_snow_pines(self):
        _, scene = self.field(*NORTH["village_spawn"])
        self.assertEqual(scene.theme, "snow")
        self.assertTrue(scene.ice)
        self.assertTrue(scene.ice <= scene.walls)
        self.assertTrue(scene.ground_tile(5, 5).startswith("snow_"))
        self.assertEqual(scene.tree_kind((3, 3)), "tree_snowpine")
        scene.draw(pygame.Surface((800, 600)))

    def test_walking_back_south_returns_to_the_north_altar(self):
        game, scene = self.field(*NORTH["village_spawn"])
        scene._interact()
        self.assertEqual(game.entered, ("village_north_shrine", NORTH["return_village"]))

    def test_dungeon_floors_are_walkable(self):
        for floor in (1, 2):
            game = FakeGame()
            entry = NORTH["dungeon_spawn"]
            dungeon = DungeonScene(game, {"world": f"shrine_ice_{floor}f", "x": entry[0], "y": entry[1]})
            reach = reachable(dungeon, (round(dungeon.player["x"]), round(dungeon.player["y"])))
            near = lambda p: bool({(p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1)} & reach)
            self.assertTrue(near(dungeon.STAIRS), floor)
            self.assertTrue(near(dungeon.EXIT), floor)
            if floor == 2:
                self.assertTrue(near(dungeon.boss_position))
            for chest in dungeon.chests:
                self.assertTrue(near(chest), chest)
            dungeon.draw(pygame.Surface((800, 600)))


class FreezeTests(unittest.TestCase):
    def hero(self):
        return FieldScene(FakeGame(), {"world": "field_north", "x": 26, "y": 28, "hp": 999, "max_hp": 999})

    def test_ice_enemies_can_freeze_the_hero_who_then_loses_a_turn(self):
        engine = BattleEngine(self.hero(), "ice_slime", rng=FixedRng(0.0))
        engine.act("attack")
        self.assertIn("stun", engine.statuses["hero"])
        hp_before = engine.enemy_hp
        events = engine.act("attack")
        self.assertEqual(engine.enemy_hp, hp_before)
        self.assertTrue(any(e["type"] == "stunned" and e["target"] == "hero" for e in events))
        self.assertNotIn("stun", engine.statuses["hero"])

    def test_the_ice_guardian_blizzard_comes_every_third_turn(self):
        engine = BattleEngine(self.hero(), "shrine_ice", rng=FixedRng(0.9))
        self.assertTrue(engine.is_boss)
        storms = []
        for _ in range(6):
            events = engine.act("attack")
            storms.append(any("눈보라" in e["text"] for e in events))
        self.assertEqual(storms, [False, False, True, False, False, True])

    def test_north_enemies_and_dungeon(self):
        for enemy in NORTH["enemy_pool"]:
            self.assertIn(enemy, ENEMIES)
        self.assertIn("shrine_ice", SHRINE_DUNGEONS)
        self.assertEqual(SHRINE_DUNGEONS["shrine_ice"]["field"], "field_north")


class PresentationTests(unittest.TestCase):
    def test_backdrops_and_music(self):
        self.assertIn("snow", battle_art.KINDS)
        self.assertIn("dungeon_ice", battle_art.KINDS)
        self.assertEqual(music_for("field_north", None), "field")
        self.assertEqual(music_for("battle", "shrine_ice"), "boss")


if __name__ == "__main__":
    unittest.main()

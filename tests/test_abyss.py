"""Post-game Starlight Abyss: a 3-floor dungeon under the north altar with a hidden boss."""

import os
import random
import unittest
from collections import deque

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.combat import BattleEngine
from gameplay.enemies import ENEMIES
from gameplay.equipment import ACCESSORIES
from gameplay.world_data import MAP_GRAPH
from scenes.dungeon_scene import DUNGEONS, POSTGAME_DUNGEONS, DungeonScene
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
        self.battle = None

    def save_game(self):
        pass

    def enter_world(self, world, position):
        self.entered = (world, position)

    def start_battle(self, enemy_id):
        self.battle = enemy_id

    def font(self, size):
        return pygame.font.Font(None, size)


class FixedRng(random.Random):
    def random(self):
        return 0.5

    def uniform(self, a, b):
        return (a + b) / 2


ABYSS = POSTGAME_DUNGEONS["shrine_abyss"]
FINISHED = {"prologue_done": 1, "shrine_wind": 1, "shrine_earth": 1, "shrine_fire": 1,
            "star_sword_awakened": 1, "final_boss": 1}


def floor(n, **state):
    game = FakeGame()
    return game, DungeonScene(game, {"world": f"shrine_abyss_{n}f", "quest_flags": FINISHED, **state})


def reachable(scene, start):
    seen, queue = {start}, deque([start])
    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in seen and not scene._blocked(nx, ny):
                seen.add((nx, ny))
                queue.append((nx, ny))
    return seen


def next_to(point, reach):
    x, y = point
    return bool({(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), point} & reach)


class EntranceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def talk_to_altar(self, flags):
        game = FakeGame()
        scene = ShrineClearingScene(game, {"x": 15, "y": 8, "quest_flags": flags})
        scene._interact()
        while scene.dialogue_lines:
            scene._advance_dialogue()
        return game

    def test_altar_is_quiet_before_the_ending(self):
        self.assertIsNone(self.talk_to_altar({}).entered)

    def test_altar_opens_the_abyss_after_the_ending(self):
        world, position = self.talk_to_altar(FINISHED).entered
        self.assertEqual(world, "shrine_abyss_1f")
        self.assertEqual(position, ABYSS["spawn"])

    def test_map_graph_links_every_floor(self):
        self.assertIn("shrine_abyss_1f", MAP_GRAPH["village_north_shrine"])
        self.assertIn("shrine_abyss_2f", MAP_GRAPH["shrine_abyss_1f"])
        self.assertIn("shrine_abyss_3f", MAP_GRAPH["shrine_abyss_2f"])
        self.assertIn("shrine_abyss_2f", MAP_GRAPH["shrine_abyss_3f"])


class FloorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_every_floor_is_walkable_from_its_entrance(self):
        for n in (1, 2, 3):
            game, scene = floor(n, x=ABYSS["spawn"][0], y=ABYSS["spawn"][1])
            self.assertFalse(scene.position_recovered, n)
            reach = reachable(scene, ABYSS["spawn"])
            self.assertTrue(next_to(scene.EXIT, reach), n)
            self.assertTrue(next_to(scene.STAIRS, reach), n)
            for chest in scene.chests:
                self.assertTrue(next_to(chest, reach), (n, chest))
            if n == 3:
                self.assertTrue(next_to(scene.boss_position, reach))
            scene.draw(pygame.Surface((800, 600)))

    def test_stairs_go_down_and_exits_go_up(self):
        game, scene = floor(1, x=ABYSS["stairs"][0] - 1, y=ABYSS["stairs"][1])
        scene._interact()
        self.assertEqual(game.entered[0], "shrine_abyss_2f")
        game, scene = floor(2, x=ABYSS["stairs"][0] - 1, y=ABYSS["stairs"][1])
        scene._interact()
        self.assertEqual(game.entered[0], "shrine_abyss_3f")
        game, scene = floor(2, x=ABYSS["exit"][0] + 1, y=ABYSS["exit"][1])
        scene._interact()
        self.assertEqual(game.entered[0], "shrine_abyss_1f")
        game, scene = floor(1, x=ABYSS["exit"][0] + 1, y=ABYSS["exit"][1])
        scene._interact()
        self.assertEqual(game.entered, ("village_north_shrine", ABYSS["return_pos"]))

    def test_only_the_bottom_floor_has_the_boss_and_no_encounters(self):
        _, top = floor(1)
        _, bottom = floor(3)
        self.assertGreater(top.encounter_rate, 0)
        self.assertEqual(bottom.encounter_rate, 0)
        game, bottom = floor(3, x=ABYSS["boss_pos"][0], y=ABYSS["boss_pos"][1] + 1)
        bottom._interact()
        self.assertEqual(game.battle, "abyss_lord")

    def test_second_floor_chest_holds_the_star_amulet(self):
        game, scene = floor(2)
        (chest, content), = scene.chests.items()
        scene.player.update(x=float(chest[0] + 1), y=float(chest[1]))
        scene._interact()
        self.assertIn("star_amulet", scene.owned_accessories)


class AbyssBattleTests(unittest.TestCase):
    def test_abyss_enemies_are_tougher_than_the_volcano(self):
        for enemy in ABYSS["monsters"]:
            self.assertGreater(ENEMIES[enemy]["hp"], ENEMIES["salamander"]["hp"])
        self.assertGreater(ENEMIES["abyss_lord"]["hp"], ENEMIES["final_boss"]["hp"])

    def test_the_abyss_lord_is_a_boss_with_a_storm_every_third_turn(self):
        _, scene = floor(3, hp=9999, max_hp=9999)
        engine = BattleEngine(scene, "abyss_lord", rng=FixedRng())
        self.assertTrue(engine.is_boss)
        storms = []
        for _ in range(6):
            events = engine.act("attack")
            storms.append(any("심연의 폭풍" in e["text"] for e in events))
        self.assertEqual(storms, [False, False, True, False, False, True])
        engine.act("flee")
        self.assertIsNone(engine.result)

    def test_defeating_the_lord_grants_the_crown_once(self):
        _, scene = floor(3)
        gold = scene.gold
        scene.resolve_battle_victory("abyss_lord")
        self.assertTrue(scene.quest_flags["abyss_lord"])
        self.assertIn("abyss_crown", scene.owned_accessories)
        self.assertGreater(scene.gold, gold)
        scene.resolve_battle_victory("abyss_lord")
        self.assertEqual(scene.owned_accessories.count("abyss_crown"), 1)

    def test_rewards_are_the_strongest_accessories(self):
        crown, amulet = ACCESSORIES["abyss_crown"], ACCESSORIES["star_amulet"]
        self.assertGreater(crown["attack"], ACCESSORIES["power_bracelet"]["attack"])
        self.assertGreater(amulet.get("evasion", 0), 0)

    def test_presentation_hooks(self):
        self.assertIn("dungeon_abyss", battle_art.KINDS)
        self.assertEqual(music_for("battle", "abyss_lord"), "boss")
        self.assertEqual(music_for("shrine_abyss_2f", None), "dungeon")
        self.assertIn("shrine_abyss", DUNGEONS)


if __name__ == "__main__":
    unittest.main()

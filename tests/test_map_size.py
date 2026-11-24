"""Bigger overworld (~30%): sizes, edge exits and reachability of every landmark."""

import os
import unittest
from collections import deque

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.world_data import FIELD_ROUTES
from scenes.field_scene import FieldScene
from scenes.shrine_clearing_scene import ShrineClearingScene
from scenes.village_scene import VillageScene


class FakeGame:
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133)}
    active_slot = 1

    def save_game(self):
        pass

    def enter_world(self, world, position):
        self.destination = (world, position)

    def font(self, size):
        return pygame.font.Font(None, size)


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
    return point in reach or bool({(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)} & reach)


class FieldSizeTests(unittest.TestCase):
    def test_route_fields_are_about_thirty_percent_bigger(self):
        self.assertEqual((FieldScene.COLS, FieldScene.ROWS), (52, 31))

    def test_every_route_landmark_is_reachable_from_the_village_entrance(self):
        for world, data in FIELD_ROUTES.items():
            scene = FieldScene(FakeGame(), {"world": world, "x": data["village_spawn"][0],
                                            "y": data["village_spawn"][1]})
            self.assertFalse(scene.position_recovered, world)
            reach = reachable(scene, data["village_spawn"])
            for name, point in (("village_portal", data["village_portal"]),
                                ("dungeon_portal", data["dungeon_portal"]),
                                ("return_dungeon", data["return_dungeon"])):
                self.assertTrue(next_to(point, reach), (world, name, point))
            for point in (*data["chests"], *data["herbs"], *((data["toby"],) if data.get("toby") else ())):
                self.assertTrue(next_to(point, reach), (world, point))

    def test_village_portals_sit_on_the_map_edge(self):
        for world, data in FIELD_ROUTES.items():
            x, y = data["village_portal"]
            self.assertTrue(x in (1, FieldScene.COLS - 2) or y in (1, FieldScene.ROWS - 2), world)


class VillageSizeTests(unittest.TestCase):
    def setUp(self):
        self.village = VillageScene(FakeGame(), {"world": "village", "x": 15, "y": 15})

    def test_village_is_about_thirty_percent_bigger(self):
        self.assertEqual((VillageScene.COLS, VillageScene.ROWS), (32, 21))
        self.assertEqual((ShrineClearingScene.COLS, ShrineClearingScene.ROWS), (32, 21))

    def test_start_position_is_free(self):
        self.assertFalse(self.village.position_recovered)

    def test_every_village_landmark_is_reachable(self):
        v = self.village
        reach = reachable(v, (15, 15))
        targets = [v.QUEST_HOUSE_DOOR, v.KNIGHT_HOUSE_DOOR, v.CHIEF, v.LOGAN, v.VILLAGER, v.FOUNTAIN,
                   *v.FIELD_GATES.values()]
        for point in targets:
            self.assertTrue(next_to(point, reach), point)

    def test_returning_from_fields_and_houses_lands_on_free_tiles(self):
        v = self.village
        spots = [data["return_village"] for data in FIELD_ROUTES.values()]
        spots += [v.HOUSE_EXITS[key] for key in v.HOUSE_EXITS]
        reach = reachable(v, (15, 15))
        for spot in spots:
            self.assertIn(tuple(spot), reach, spot)

    def test_gates_lead_to_matching_fields(self):
        v = self.village
        for route_id, gate in v.FIELD_GATES.items():
            v.player.update(x=gate[0], y=gate[1])
            v._interact()
            self.assertEqual(v.game.destination[0], route_id)

    def test_shrine_clearing_returns_to_the_north_gate(self):
        game = FakeGame()
        shrine = ShrineClearingScene(game, {"world": "village_north_shrine"})
        shrine.player.update(x=shrine.portal_position[0], y=shrine.portal_position[1])
        shrine._interact()
        self.assertEqual(game.destination, ("village", self.village.SHRINE_RETURN))
        self.assertIn(self.village.SHRINE_RETURN, reachable(self.village, (15, 15)))


if __name__ == "__main__":
    unittest.main()

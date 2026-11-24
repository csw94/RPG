"""Bigger Oak Valley: 44x30, the old village kept in place, new east and south districts."""

import os
import unittest
from collections import deque

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.world_data import FIELD_ROUTES
from scenes.village_scene import VillageScene


class FakeGame:
    active_slot = 1
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}

    def __init__(self):
        self.destination = None

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
    return bool({(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)} & reach)


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def setUp(self):
        self.village = VillageScene(FakeGame(), {"world": "village", "x": 15, "y": 15})

    def test_village_grew_about_one_and_a_half_times(self):
        self.assertEqual((VillageScene.COLS, VillageScene.ROWS), (44, 30))

    def test_old_landmarks_kept_their_coordinates(self):
        v = self.village
        self.assertEqual((v.START, v.CHIEF, v.FOUNTAIN, v.LOGAN), ((15, 15), (15, 9), (15, 13), (19, 12)))
        self.assertEqual(v.FIELD_GATES["field_west"], (0, 10))
        self.assertEqual(v.FIELD_GATES["village_north_shrine"], (15, 0))

    def test_east_and_south_gates_moved_to_the_new_edges(self):
        v = self.village
        self.assertEqual(v.FIELD_GATES["field_east"], (VillageScene.COLS - 1, 10))
        self.assertEqual(v.FIELD_GATES["field_south"], (15, VillageScene.ROWS - 1))
        self.assertEqual(FIELD_ROUTES["field_east"]["return_village"], (VillageScene.COLS - 2, 10))
        self.assertEqual(FIELD_ROUTES["field_south"]["return_village"], (15, VillageScene.ROWS - 2))

    def test_every_new_place_is_reachable(self):
        v = self.village
        reach = reachable(v, v.START)
        self.assertEqual(set(v.DISTRICT), {"inn", "smithy", "library", "apothecary"})
        for name, place in v.DISTRICT.items():
            self.assertIn(place["door"], reach, name)
            bx, by, bw, bh = place["footprint"]
            for tx in range(bx, bx + bw):
                for ty in range(by, by + bh):
                    self.assertIn((tx, ty), v.walls, name)
        for resident in v.RESIDENTS.values():
            self.assertTrue(next_to(resident["pos"], reach), resident)
        for gate in v.FIELD_GATES.values():
            self.assertTrue(next_to(gate, reach) or gate in reach, gate)

    def test_new_places_and_people_are_on_the_map_page(self):
        markers = self.village.map_markers()
        doors = {position for kind, position in markers if kind == "door"}
        for place in VillageScene.DISTRICT.values():
            self.assertIn(place["door"], doors)
        people = [kind for kind, _ in markers if kind in ("npc", "shop")]
        self.assertGreaterEqual(len(people), 2 + len(VillageScene.RESIDENTS))

    def test_each_door_leads_inside_and_tomi_talks(self):
        v = self.village
        for place in v.DISTRICT.values():
            v.player.update(x=float(place["door"][0]), y=float(place["door"][1]))
            v._interact()
            self.assertEqual(v.game.destination, (place["world"], (12, 12)))
            self.assertEqual(v.HOUSE_EXITS[place["world"]], place["door"])
        tomi = v.RESIDENTS["tomi"]["pos"]
        v.player.update(x=float(tomi[0] - 1), y=float(tomi[1]))
        v._interact()
        self.assertTrue(v.dialogue_lines)

    def test_draws_the_whole_town(self):
        surface = pygame.Surface((800, 600))
        for x, y in ((15, 15), (40, 10), (20, 27), (38, 24)):
            v = VillageScene(FakeGame(), {"world": "village", "x": x, "y": y})
            self.assertFalse(v.position_recovered, (x, y))
            v.draw(surface)


if __name__ == "__main__":
    unittest.main()

"""Cozy interiors: furniture layout drives both the visuals and the collision."""

import os
import unittest
from collections import deque

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from scenes.house_scene import HouseInteriorScene
from utils.interior_art import interior_sprite

HOUSES = ("village_house_1", "village_house_2", "village_chief_house")


class FakeGame:
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133)}

    def save_game(self):
        pass

    def enter_world(self, world, position):
        self.destination = (world, position)

    def font(self, size):
        return pygame.font.Font(None, size)


def _reachable(scene, start):
    seen, queue = {start}, deque([start])
    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in seen and not scene._blocked(nx, ny):
                seen.add((nx, ny))
                queue.append((nx, ny))
    return seen


class InteriorLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def scene(self, house_id):
        return HouseInteriorScene(FakeGame(), {"world": house_id, "x": 12, "y": 12})

    def test_every_furniture_sprite_matches_its_footprint(self):
        for house_id in HOUSES:
            for item in self.scene(house_id).layout:
                surface = interior_sprite(item["sprite"], None)
                self.assertEqual(surface.get_size(), (item["w"] * 16, item["h"] * 16), item["sprite"])

    def test_solid_furniture_is_collision_and_stays_inside_the_room(self):
        for house_id in HOUSES:
            scene = self.scene(house_id)
            left, top, right, bottom = scene.ROOM
            for item in scene.layout:
                for tile in scene.solid_tiles(item):
                    self.assertIn(tile, scene.walls, (house_id, item["sprite"]))
                    self.assertTrue(left <= tile[0] <= right and top - 1 <= tile[1] <= bottom,
                                    (house_id, item["sprite"], tile))

    def test_outside_the_room_is_solid_except_the_door(self):
        scene = self.scene("village_house_1")
        left, top, right, bottom = scene.ROOM
        self.assertIn((left - 1, 8), scene.walls)
        self.assertIn((right + 1, 8), scene.walls)
        self.assertIn((5, bottom + 1), scene.walls)

    def test_npc_and_door_are_reachable_from_spawn(self):
        for house_id in HOUSES:
            scene = self.scene(house_id)
            reach = _reachable(scene, (12, 12))
            self.assertIn((12, 13), reach, house_id)
            npc_x, npc_y = scene.npcs[0]
            talk_spots = {(npc_x + dx, npc_y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
            self.assertTrue(talk_spots & reach, f"{house_id}: no free tile next to the NPC")

    def test_floor_has_no_checkerboard(self):
        a = interior_sprite("floor_0", None)
        b = interior_sprite("floor_1", None)
        self.assertEqual(a.get_at((0, 0)), b.get_at((0, 0)))

    def test_all_houses_draw_headless(self):
        surface = pygame.Surface((800, 600))
        for house_id in HOUSES:
            self.scene(house_id).draw(surface)


if __name__ == "__main__":
    unittest.main()

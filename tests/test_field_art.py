"""Stage 3: themed field terrain and hero-sized NPCs."""

import os
import unittest
from collections import Counter

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from scenes.field_scene import FieldScene
from utils import pixel_art
from utils.pixel_art import sprite

NPCS = ("villager", "shopkeeper", "chief", "old_knight", "merchant")
FIELDS = ("field_east", "field_west", "field_south")


def _dominant(surface):
    w, h = surface.get_size()
    return Counter(tuple(surface.get_at((x, y)))[:3] for x in range(w) for y in range(h)).most_common(1)[0][0]


def _has_outline(surface):
    outline = pixel_art.PALETTE["outline"]
    w, h = surface.get_size()
    return any(tuple(surface.get_at((x, y)))[:3] == outline for x in range(w) for y in range(h))


class FakeGame:
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133)}
    active_slot = 1

    def save_game(self):
        pass

    def font(self, size):
        return pygame.font.Font(None, size)


class NpcSizeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_npcs_match_the_hero_proportions(self):
        hero = pixel_art._player()
        for name in NPCS:
            self.assertEqual(sprite(name, None).get_size(), hero.get_size(), name)

    def test_characters_share_the_outline(self):
        for name in NPCS:
            self.assertTrue(_has_outline(sprite(name, None)), name)
        self.assertTrue(_has_outline(pixel_art._player()))

    def test_npcs_are_visually_distinct(self):
        bodies = {tuple(tuple(sprite(n, None).get_at((8, y)))[:3] for y in range(2, 22)) for n in NPCS}
        self.assertEqual(len(bodies), len(NPCS))


class FieldTerrainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def scene(self, world):
        return FieldScene(FakeGame(), {"world": world, "x": 2, "y": 12})

    def test_each_theme_has_its_own_ground_that_contrasts_with_the_path(self):
        grounds = {}
        path = pixel_art.PALETTE["path"]
        for world in FIELDS:
            name = self.scene(world).ground_tile(3, 4)
            color = _dominant(sprite(name, None))
            grounds[world] = color
            self.assertGreater(sum(abs(a - b) for a, b in zip(color, path)), 50, world)
        self.assertEqual(len(set(grounds.values())), 3)

    def test_ground_variants_share_one_base(self):
        for prefix in ("canyon", "ash"):
            bases = {_dominant(sprite(f"{prefix}_{v}", None)) for v in range(16)}
            self.assertEqual(len(bases), 1, prefix)

    def test_lava_edges_have_a_dark_crust_rim(self):
        overlay = sprite("lava_edge_2_0", None)
        pixels = {tuple(overlay.get_at((x, y)))[:3] for x in range(16) for y in range(16)
                  if overlay.get_at((x, y)).a}
        self.assertIn(pixel_art.LAVA_RIM, pixels)

    def test_decals_avoid_everything_interactive(self):
        for world in FIELDS:
            scene = self.scene(world)
            decals = scene.field_decals()
            self.assertGreater(len(decals), 15, world)
            busy = (scene.walls | scene.path | set(scene.chests) | scene.herb_positions
                    | scene.water | scene.lava
                    | {scene.route_data["village_portal"], scene.route_data["dungeon_portal"]})
            if scene.toby_position:
                busy.add(scene.toby_position)
            self.assertFalse(set(decals) & busy, world)

    def test_props_are_outlined(self):
        for name in ("rock_0", "rock_1", "basalt_0", "chest", "portal_dungeon_0", "altar_wind"):
            self.assertTrue(_has_outline(sprite(name, None)), name)

    def test_fields_draw_headless(self):
        surface = pygame.Surface((800, 600))
        for world in FIELDS:
            self.scene(world).draw(surface)


if __name__ == "__main__":
    unittest.main()

"""Visual-quality guards for the procedural pixel art (cozy, Stardew-like village look)."""

import os
import unittest
from collections import Counter

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from utils import pixel_art
from utils.pixel_art import sprite


def _dominant(surface):
    w, h = surface.get_size()
    return Counter(tuple(surface.get_at((x, y))) for x in range(w) for y in range(h)).most_common(1)[0][0]


class PixelArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_grass_variants_share_one_base_so_no_checkerboard_grid(self):
        bases = {_dominant(sprite(f"grass_{v}", None)) for v in range(16)}
        self.assertEqual(len(bases), 1)

    def test_grass_has_soft_texture_not_flat_fill(self):
        colors = {tuple(sprite("grass_3", None).get_at((x, y))) for x in range(16) for y in range(16)}
        self.assertGreaterEqual(len(colors), 3)

    def test_new_village_props_exist_with_transparent_corners(self):
        for name, size in (("tree_round", (24, 32)), ("tree_fruit", (24, 32)), ("tree_pine", (24, 32)),
                           ("bush", (16, 16)), ("flower_patch", (16, 16)), ("pebbles", (16, 16)),
                           ("shadow", (16, 8)), ("fence", (16, 16)), ("barrel", (16, 16)),
                           ("gate_arch", (24, 32))):
            surface = sprite(name, None)
            self.assertEqual(surface.get_size(), size, name)
            self.assertEqual(surface.get_at((0, 0)).a, 0, name)

    def test_trees_have_dark_outline_and_soft_shadow(self):
        tree = sprite("tree_round", None)
        alphas = {tree.get_at((x, y)).a for x in range(24) for y in range(24, 32)}
        self.assertTrue(any(0 < a < 255 for a in alphas), "tree needs a translucent ground shadow")
        outline = pixel_art.PALETTE["outline"]
        pixels = {tuple(tree.get_at((x, y)))[:3] for x in range(24) for y in range(32)}
        self.assertIn(outline, pixels)

    def test_trail_edges_have_darker_rim_than_fill(self):
        overlay = sprite("trail_2_0", None)  # path continues east only
        fill = pixel_art.PALETTE["path"]
        rim = pixel_art.PALETTE["path_rim"]
        self.assertLess(sum(rim), sum(fill))
        pixels = {tuple(overlay.get_at((x, y)))[:3] for x in range(16) for y in range(16)
                  if overlay.get_at((x, y)).a}
        self.assertIn(rim, pixels)


class VillageDecorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def setUp(self):
        from scenes.village_scene import VillageScene

        class FakeGame:
            colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
                      "ink": (25, 31, 28), "muted": (190, 170, 133)}
            notice = ""
            active_slot = 1

            def save_game(self):
                pass

            def font(self, size):
                return pygame.font.Font(None, size)

        self.village = VillageScene(FakeGame(), {"world": "village", "x": 12, "y": 13})

    def test_walkable_decals_never_sit_on_walls_or_road(self):
        decals = self.village.ground_decals()
        self.assertGreater(len(decals), 10)
        road = self.village.road_tiles()
        for (x, y), _name in decals.items():
            self.assertNotIn((x, y), self.village.walls)
            self.assertNotIn((x, y), road)

    def test_tree_kinds_are_mixed(self):
        kinds = {self.village.tree_kind(pos) for pos in self.village.trees}
        self.assertGreaterEqual(len(kinds), 2)

    def test_village_draws_headless(self):
        surface = pygame.Surface((800, 600))
        self.village.draw(surface)


if __name__ == "__main__":
    unittest.main()

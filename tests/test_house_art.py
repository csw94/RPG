"""Village houses are built from parts, so every building looks like its own place."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from utils import house_art
from utils.house_art import HOUSE_STYLES, paint_house

BUILDINGS = {"herb_cottage", "general_store", "inn", "smithy", "library", "apothecary"}


def render(key):
    style = HOUSE_STYLES[key]
    surface = pygame.Surface((style["width"] * 32 + 40, 230), pygame.SRCALPHA)
    paint_house(surface, 16, 16, style)
    return surface


def bounds(img):
    rects = pygame.mask.from_surface(img).get_bounding_rects()
    return rects[0].unionall(rects[1:])


class HouseStyleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_every_village_building_has_a_style(self):
        self.assertEqual(set(HOUSE_STYLES), BUILDINGS)

    def test_styles_mix_many_materials_and_roof_shapes(self):
        walls = {s["wall"] for s in HOUSE_STYLES.values()}
        roofs = {s["roof"] for s in HOUSE_STYLES.values()}
        self.assertGreaterEqual(len(walls), 5)
        self.assertGreaterEqual(len(roofs), 4)
        self.assertTrue(walls <= set(house_art.WALLS), walls - set(house_art.WALLS))
        self.assertTrue(roofs <= set(house_art.ROOF_SHAPES), roofs - set(house_art.ROOF_SHAPES))
        combos = {(s["wall"], s["roof"]) for s in HOUSE_STYLES.values()}
        self.assertEqual(len(combos), len(HOUSE_STYLES))

    def test_not_every_house_is_a_single_storey_cottage(self):
        self.assertIn(2, {s.get("stories", 1) for s in HOUSE_STYLES.values()})

    def test_houses_render_differently_with_different_silhouettes(self):
        images = {key: render(key) for key in HOUSE_STYLES}
        pixels = {key: pygame.image.tobytes(img, "RGBA") for key, img in images.items()}
        self.assertEqual(len(set(pixels.values())), len(HOUSE_STYLES))
        outlines = set()
        for img in images.values():
            mask = pygame.mask.from_surface(img)
            outlines.add(tuple(bounds(img)) + (mask.count(),))
        self.assertGreaterEqual(len(outlines), 4)

    def test_painting_is_deterministic(self):
        for key in HOUSE_STYLES:
            self.assertEqual(pygame.image.tobytes(render(key), "RGBA"), pygame.image.tobytes(render(key), "RGBA"), key)

    def test_house_stays_inside_its_canvas_bounds(self):
        # The village crops each house to (x - 10, y - 10, width + 24, 214) before scaling it down.
        for key, style in HOUSE_STYLES.items():
            img = render(key)
            box = bounds(img)
            allowed = pygame.Rect(16 - 10, 16 - 10, style["width"] * 32 + 24, 214)
            self.assertTrue(allowed.contains(box), (key, box, allowed))


if __name__ == "__main__":
    unittest.main()

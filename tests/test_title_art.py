"""Title screen: a painted night view of Oak Valley in the cozy style."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from scenes.title_scene import TitleScene
from utils import title_art, ui


class FakeSaves:
    def list_saves(self):
        return {1: {"level": 3, "hp": 80, "max_hp": 120, "gold": 40, "potions": 2}}


class FakeGame:
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133)}
    save_manager = FakeSaves()
    running = True

    def font(self, size):
        return pygame.font.Font(None, size)


def brightness(color):
    return sum(tuple(color)[:3])


class TitleArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_backdrop_fills_the_screen(self):
        self.assertEqual(title_art.backdrop().get_size(), (800, 600))

    def test_night_sky_gets_lighter_towards_the_horizon(self):
        sky = title_art.backdrop()
        self.assertLess(brightness(sky.get_at((10, 4))), brightness(sky.get_at((10, title_art.HORIZON * 2 - 8))))

    def test_meadow_is_green_in_the_foreground(self):
        r, g, b, _ = title_art.backdrop().get_at((400, 470))
        self.assertGreater(g, r)
        self.assertGreater(g, b)

    def test_overlay_animates_stars_and_fireflies(self):
        a, b = pygame.Surface((800, 600)), pygame.Surface((800, 600))
        title_art.draw_overlay(a, 0.0)
        title_art.draw_overlay(b, 1.3)
        self.assertNotEqual(pygame.image.tobytes(a, "RGB"), pygame.image.tobytes(b, "RGB"))


class TitleSceneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_menu_and_slots_draw_and_the_help_sits_on_wood(self):
        scene = TitleScene(FakeGame())
        surface = pygame.Surface((800, 600))
        scene.update(0.5)
        scene.draw(surface)
        self.assertNotEqual(tuple(surface.get_at((4, 596)))[:3], (23, 33, 29))
        scene.mode = "slots"
        scene.draw(surface)
        self.assertEqual(tuple(surface.get_at((400, 470)))[:3] != (23, 33, 29), True)

    def test_update_advances_the_animation_clock(self):
        scene = TitleScene(FakeGame())
        scene.update(0.25)
        scene.update(0.25)
        self.assertAlmostEqual(scene.clock, 0.5)

    def test_menu_buttons_still_use_the_wood_ui(self):
        scene = TitleScene(FakeGame())
        surface = pygame.Surface((800, 600))
        scene.draw(surface)
        rect = scene._menu_buttons()[1]
        self.assertEqual(tuple(surface.get_at((rect.left + 4, rect.centery)))[:3], ui.WALNUT)


if __name__ == "__main__":
    unittest.main()

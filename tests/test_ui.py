"""Stage 4: parchment / wood-frame UI shared by every scene."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from utils import ui
from utils.pixel_art import sprite


class FakeGame:
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}
    active_slot = 1

    def save_game(self):
        pass

    def font(self, size):
        return pygame.font.Font(None, size)


class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_frame_returns_inner_body_with_style_fill(self):
        surface = pygame.Surface((200, 100))
        for kind, fill in (("parchment", ui.PARCHMENT), ("walnut", ui.WALNUT)):
            body = ui.frame(surface, pygame.Rect(10, 10, 180, 80), kind)
            self.assertTrue(pygame.Rect(10, 10, 180, 80).contains(body))
            self.assertLess(body.width, 180)
            self.assertEqual(tuple(surface.get_at(body.center))[:3], fill)

    def test_frame_around_keeps_the_content_rect_free(self):
        surface = pygame.Surface((200, 100))
        content = pygame.Rect(30, 30, 100, 40)
        body = ui.frame_around(surface, content, "walnut")
        self.assertTrue(body.contains(content))

    def test_bar_fill_is_proportional(self):
        surface = pygame.Surface((200, 40))
        surface.fill((0, 0, 0))
        ui.bar(surface, pygame.Rect(10, 10, 102, 10), 50, 100, (200, 60, 60))
        self.assertEqual(tuple(surface.get_at((30, 15)))[:3], (200, 60, 60))
        self.assertNotEqual(tuple(surface.get_at((95, 15)))[:3], (200, 60, 60))

    def test_hud_and_dialogue_draw_in_every_overworld_scene(self):
        from scenes.field_scene import FieldScene
        from scenes.house_scene import HouseInteriorScene
        from scenes.village_scene import VillageScene
        surface = pygame.Surface((800, 600))
        for scene in (FieldScene(FakeGame(), {"world": "field_east", "x": 2, "y": 12}),
                      VillageScene(FakeGame(), {"world": "village", "x": 12, "y": 13}),
                      HouseInteriorScene(FakeGame(), {"world": "village_house_1"})):
            scene.show_dialogue(["테스트 대사입니다."])
            scene.draw(surface)
            # The HUD body is parchment.
            self.assertEqual(tuple(surface.get_at((400, 586)))[:3], ui.PARCHMENT, type(scene).__name__)

    def test_hud_title_names_the_place(self):
        from scenes.field_scene import FieldScene
        scene = FieldScene(FakeGame(), {"world": "field_east", "x": 2, "y": 12})
        self.assertEqual(scene.hud_title(), "바람 부는 숲길")

    def test_square_villager_has_their_own_look(self):
        a, b = sprite("townsfolk", None), sprite("villager", None)
        self.assertEqual(a.get_size(), b.get_size())
        self.assertNotEqual(pygame.image.tobytes(a, "RGBA"), pygame.image.tobytes(b, "RGBA"))


if __name__ == "__main__":
    unittest.main()

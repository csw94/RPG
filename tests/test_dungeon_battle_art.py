"""Dungeons and battles share the cozy outlined style."""

import os
import unittest
from collections import Counter

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.enemies import ENEMIES
from scenes.battle_scene import BattleScene
from scenes.dungeon_scene import SHRINE_DUNGEONS, DungeonScene
from scenes.field_scene import FieldScene
from scenes.village_scene import VillageScene
from utils import battle_art, pixel_art, ui
from utils.pixel_art import fit_sprite, sprite


class FakeGame:
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}
    active_slot = 1
    field = None

    def save_game(self):
        pass

    def enter_world(self, world, position):
        pass

    def font(self, size):
        return pygame.font.Font(None, size)


def _has_outline(surface):
    outline = pixel_art.PALETTE["outline"]
    w, h = surface.get_size()
    return any(tuple(surface.get_at((x, y)))[:3] == outline for x in range(w) for y in range(h))


class EnemyArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_every_enemy_has_its_own_outlined_sprite(self):
        names = [enemy["sprite"] for enemy in ENEMIES.values()]
        self.assertEqual(len(names), len(set(names)))
        for name in names:
            self.assertTrue(_has_outline(sprite(name, None)), name)

    def test_fit_sprite_keeps_proportions_inside_the_box(self):
        for enemy in ENEMIES.values():
            base = sprite(enemy["sprite"], None)
            fitted = fit_sprite(enemy["sprite"], enemy["size"])
            box_w, box_h = enemy["size"]
            self.assertLessEqual(fitted.get_width(), box_w)
            self.assertLessEqual(fitted.get_height(), box_h)
            self.assertEqual(fitted.get_width() * base.get_height(), fitted.get_height() * base.get_width())


class BattleBackdropTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_backdrops_cover_the_stage_and_differ(self):
        signatures = set()
        for kind in battle_art.KINDS:
            surface = battle_art.backdrop(kind)
            self.assertEqual(surface.get_size(), (800, 374), kind)
            signatures.add(tuple(tuple(surface.get_at((x, 60)))[:3] for x in range(0, 800, 97)))
        self.assertEqual(len(signatures), len(battle_art.KINDS))

    def test_battle_picks_the_backdrop_from_where_the_fight_happens(self):
        game = FakeGame()
        cases = {
            "canyon": FieldScene(game, {"world": "field_west"}),
            "forest": FieldScene(game, {"world": "field_east"}),
            "volcanic": FieldScene(game, {"world": "field_south"}),
            "village": VillageScene(game, {"world": "village", "x": 15, "y": 15}),
            "dungeon_earth": DungeonScene(game, {"world": "shrine_earth_1f"}),
        }
        for expected, field in cases.items():
            game.field = field
            self.assertEqual(BattleScene(game, "slime").backdrop_kind(), expected)

    def test_battle_draws_with_ui_frames(self):
        game = FakeGame()
        game.field = FieldScene(game, {"world": "field_east"})
        surface = pygame.Surface((800, 600))
        for enemy_id in ENEMIES:
            BattleScene(game, enemy_id).draw(surface)
        self.assertEqual(tuple(surface.get_at((400, 470)))[:3], ui.WALNUT)


class DungeonArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def scene(self, shrine, floor=1):
        return DungeonScene(FakeGame(), {"world": f"{shrine}_{floor}f"})

    def test_walls_show_a_front_face_above_floor(self):
        scene = self.scene("shrine_wind")
        face = [(x, y) for (x, y) in scene.walls if (x, y + 1) not in scene.walls and 0 <= y + 1 < scene.ROWS]
        top = [(x, y) for (x, y) in scene.walls if (x, y + 1) in scene.walls]
        self.assertTrue(face and top)
        self.assertTrue(scene.wall_tile(*face[0]).startswith("dwall_face_"))
        self.assertTrue(scene.wall_tile(*top[0]).startswith("dwall_top_"))

    def test_each_shrine_has_its_own_palette(self):
        floors = set()
        for shrine in SHRINE_DUNGEONS:
            scene = self.scene(shrine)
            name = scene.floor_tile(3, 3)
            counts = Counter(tuple(sprite(name, None).get_at((x, y)))[:3] for x in range(16) for y in range(16))
            floors.add(counts.most_common(1)[0][0])
        self.assertEqual(len(floors), len(SHRINE_DUNGEONS))

    def test_dungeon_dialogue_stays_visible(self):
        scene = self.scene("shrine_fire")
        scene.show_dialogue(["불꽃의 신전에 들어섰다."])
        surface = pygame.Surface((800, 600))
        scene.draw(surface)
        self.assertEqual(tuple(surface.get_at((60, 492)))[:3], ui.PARCHMENT)

    def test_all_dungeon_floors_draw(self):
        surface = pygame.Surface((800, 600))
        for shrine in SHRINE_DUNGEONS:
            for floor in (1, 2):
                self.scene(shrine, floor).draw(surface)


if __name__ == "__main__":
    unittest.main()

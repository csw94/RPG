"""Status screen: stats, gear, items, skills and quest progress, opened with I or Tab."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.combat import SKILLS
from scenes.field_scene import FieldScene
from scenes.house_scene import HouseInteriorScene
from scenes.status_scene import StatusScene


class FakeGame:
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}
    active_slot = 1

    def __init__(self):
        self.status_opened = 0
        self.scene = None
        self.scene_name = ""
        self.field = None

    def save_game(self):
        pass

    def open_status(self):
        self.status_opened += 1

    def enter_world(self, world, position):
        pass

    def font(self, size):
        return pygame.font.Font(None, size)


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


class StatusSceneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def setUp(self):
        self.game = FakeGame()
        self.game.field = FieldScene(self.game, {"world": "field_east", "x": 2, "y": 16, "level": 4})
        self.game.scene = self.game.field

    def test_i_and_tab_open_the_status_screen_in_fields_and_houses(self):
        house = HouseInteriorScene(self.game, {"world": "village_house_1", "x": 12, "y": 12})
        for scene in (self.game.field, house):
            for k in (pygame.K_i, pygame.K_TAB):
                before = self.game.status_opened
                scene.handle_events([key(k)])
                self.assertEqual(self.game.status_opened, before + 1, (scene, k))

    def test_skill_rows_mark_learned_and_locked_skills(self):
        rows = StatusScene(self.game).skill_rows()
        self.assertEqual([r["id"] for r in rows], list(SKILLS))
        learned = {r["id"] for r in rows if r["learned"]}
        self.assertEqual(learned, {s["id"] for s in SKILLS.values() if s["level"] <= 4})

    def test_quest_rows_show_progress(self):
        field = self.game.field
        field.sub_quests["sq_goblin_hunt"].update(status="IN_PROGRESS", progress=2)
        field.quest_flags["shrine_wind"] = 1
        status = StatusScene(self.game)
        quests = dict(status.quest_rows())
        self.assertIn("2/5", quests["고블린 소탕"])
        seals = dict(status.seal_rows())
        self.assertTrue(seals["바람의 제단"])
        self.assertFalse(seals["불꽃의 신전"])

    def test_closing_returns_to_the_field(self):
        for k in (pygame.K_i, pygame.K_TAB, pygame.K_ESCAPE):
            status = StatusScene(self.game)
            self.game.scene = status
            status.handle_events([key(k)])
            self.assertIs(self.game.scene, self.game.field, k)

    def test_draws_for_new_and_finished_heroes(self):
        surface = pygame.Surface((800, 600))
        StatusScene(self.game).draw(surface)
        field = self.game.field
        field.level, field.weapon, field.armor = 9, "star_sword", "knight_breastplate"
        field.quest_items |= {"broken_old_sword", "knights_crest"}
        for flag in ("shrine_wind", "shrine_earth", "shrine_fire", "final_boss"):
            field.quest_flags[flag] = 1
        StatusScene(self.game).draw(surface)


if __name__ == "__main__":
    unittest.main()

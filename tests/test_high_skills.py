"""Two late skills (Lv.10, Lv.12) so levelling past 8 still teaches something new."""

import os
import random
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.combat import SKILLS, BattleEngine, skills_for_level
from scenes.battle_scene import BattleScene
from scenes.field_scene import FieldScene
from scenes.status_scene import StatusScene


class FakeGame:
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}
    active_slot = 1

    def __init__(self):
        self.field = None
        self.scene = None
        self.scene_name = ""

    def save_game(self):
        pass

    def font(self, size):
        return pygame.font.Font(None, size)


class FixedRng(random.Random):
    def random(self):
        return 0.5

    def uniform(self, a, b):
        return (a + b) / 2


def hero(level, **state):
    game = FakeGame()
    game.field = FieldScene(game, {"world": "field_east", "x": 2, "y": 16, "level": level, **state})
    return game, game.field


class SkillTests(unittest.TestCase):
    def test_new_skills_unlock_at_ten_and_twelve(self):
        ids = lambda level: {s["id"] for s in skills_for_level(level)}
        self.assertNotIn("star_storm", ids(9))
        self.assertIn("star_storm", ids(10))
        self.assertNotIn("holy_prayer", ids(11))
        self.assertIn("holy_prayer", ids(12))
        self.assertEqual(SKILLS["star_storm"]["level"], 10)
        self.assertEqual(SKILLS["holy_prayer"]["level"], 12)

    def test_star_storm_is_the_strongest_light_attack(self):
        self.assertEqual(SKILLS["star_storm"]["element"], "light")
        self.assertGreater(SKILLS["star_storm"]["power"], max(s["power"] for s in SKILLS.values()
                                                              if s["kind"] == "attack" and s["id"] != "star_storm"))
        _, field = hero(10, mp=50, hp=999, max_hp=999)
        engine = BattleEngine(field, "final_boss", rng=FixedRng())
        engine.act("skill", "star_storm")
        self.assertTrue(any(e.get("weak") for e in engine.log if e["type"] == "damage"))
        self.assertEqual(field.mp, 50 - SKILLS["star_storm"]["mp"])

    def test_holy_prayer_heals_more_than_the_light_and_cures(self):
        _, field = hero(12, mp=50, hp=20, max_hp=400)
        engine = BattleEngine(field, "slime", rng=FixedRng())
        engine.statuses["hero"] = {"poison": 3, "burn": 2}
        engine.act("skill", "holy_prayer")
        heal = next(e["amount"] for e in engine.log if e["type"] == "heal")
        self.assertGreater(heal, SKILLS["heal_light"]["power"] + 12 * 4)
        self.assertEqual(engine.statuses["hero"], {})

    def test_level_ten_announces_the_new_skill(self):
        _, field = hero(9)
        from gameplay.combat import xp_to_next
        ups = field.gain_xp(xp_to_next(9))
        self.assertIn("별빛 폭풍", ups[0]["skills"])


class ScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_battle_skill_buttons_fit_with_eight_skills(self):
        game, field = hero(12, mp=60)
        scene = BattleScene(game, "slime")
        buttons = scene._skill_buttons()
        self.assertEqual(len(buttons), len(SKILLS))
        for a in buttons:
            self.assertLessEqual(a.bottom, 556)
            self.assertGreaterEqual(a.left, 16)
            self.assertLessEqual(a.right, 784)
            for b in buttons:
                if a is not b:
                    self.assertFalse(a.colliderect(b))
        scene.mode = "skills"
        scene.draw(pygame.Surface((800, 600)))

    def test_status_lists_eight_skills(self):
        game, field = hero(12)
        status = StatusScene(game)
        self.assertEqual(len(status.skill_rows()), len(SKILLS))
        status.draw(pygame.Surface((800, 600)))


if __name__ == "__main__":
    unittest.main()

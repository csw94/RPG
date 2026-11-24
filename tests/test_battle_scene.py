"""BattleScene plays back BattleEngine events: menus, skill list, popups, shake, ending."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.combat import SKILLS
from scenes.battle_scene import BattleScene
from scenes.field_scene import FieldScene


class FixedRng:
    """No variance, no crits, no procs."""

    def random(self):
        return 0.5

    def uniform(self, a, b):
        return (a + b) / 2


class FakeGame:
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}
    active_slot = 1

    def __init__(self):
        self.saves = 0
        self.finished = 0
        self.field = FieldScene(self, {"world": "field_east", "x": 2, "y": 16})

    def save_game(self):
        self.saves += 1

    def finish_battle(self):
        self.finished += 1

    def retry_battle(self, snapshot, enemy_id):
        self.retried = (snapshot, enemy_id)

    def start_battle(self, enemy_id):
        pass

    def font(self, size):
        return pygame.font.Font(None, size)


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


def play_out(scene, seconds=10.0, step=0.05):
    for _ in range(int(seconds / step)):
        scene.update(step)
        if scene.mode != "playing":
            return


class BattleSceneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def make(self, enemy="slime", **stats):
        game = FakeGame()
        for name, value in stats.items():
            setattr(game.field, name, value)
        scene = BattleScene(game, enemy, rng=FixedRng())
        return game, scene

    def test_attack_plays_events_then_returns_to_the_menu(self):
        game, scene = self.make("goblin", hp=100)
        scene.handle_events([key(pygame.K_RETURN)])  # 공격
        self.assertEqual(scene.mode, "playing")
        self.assertEqual(game.saves, 1)
        scene.update(0.01)
        self.assertTrue(scene.popups or scene.shake["enemy"] > 0 or scene.current)
        play_out(scene)
        self.assertEqual(scene.mode, "menu")
        self.assertLess(scene.shown_enemy_hp, scene.engine.enemy_max_hp)
        self.assertEqual(scene.shown_enemy_hp, scene.engine.enemy_hp)

    def test_damage_events_make_popups_and_shake(self):
        game, scene = self.make("goblin", hp=100)
        scene.handle_events([key(pygame.K_RETURN)])
        seen_popup = seen_shake = False
        for _ in range(200):
            scene.update(0.02)
            seen_popup |= bool(scene.popups)
            seen_shake |= scene.shake["enemy"] > 0 and scene.shake["hero"] >= 0
            if scene.mode != "playing":
                break
        self.assertTrue(seen_popup)
        self.assertTrue(seen_shake)

    def test_skill_menu_lists_learned_skills_and_escape_goes_back(self):
        game, scene = self.make("slime", level=4, mp=20)
        scene.selected = 1
        scene.handle_events([key(pygame.K_RETURN)])
        self.assertEqual(scene.mode, "skills")
        self.assertEqual([s["id"] for s in scene.skill_list()],
                         [s["id"] for s in SKILLS.values() if s["level"] <= 4])
        scene.handle_events([key(pygame.K_ESCAPE)])
        self.assertEqual(scene.mode, "menu")

    def test_casting_a_skill_spends_mp(self):
        game, scene = self.make("goblin", level=1, mp=10, hp=100)
        scene.selected = 1
        scene.handle_events([key(pygame.K_RETURN)])
        scene.handle_events([key(pygame.K_RETURN)])  # 빛의 탄
        self.assertEqual(game.field.mp, 10 - SKILLS["light_bolt"]["mp"])
        self.assertEqual(scene.mode, "playing")

    def test_a_refused_action_stays_in_the_menu(self):
        game, scene = self.make("slime", potions=0, high_potions=0)
        scene.selected = 2
        scene.handle_events([key(pygame.K_RETURN)])
        play_out(scene)
        self.assertEqual(scene.mode, "menu")
        self.assertEqual(scene.engine.turn, 0)

    def test_victory_waits_for_confirm_then_finishes(self):
        game, scene = self.make("slime", atk=400)
        scene.handle_events([key(pygame.K_RETURN)])
        play_out(scene)
        self.assertEqual(scene.mode, "done")
        self.assertEqual(game.finished, 0)
        scene.handle_events([key(pygame.K_RETURN)])
        self.assertEqual(game.finished, 1)

    def test_draw_works_in_every_mode(self):
        surface = pygame.Surface((800, 600))
        game, scene = self.make("bat", level=8, mp=40, hp=200)
        scene.draw(surface)
        scene.selected = 1
        scene.handle_events([key(pygame.K_RETURN)])
        scene.draw(surface)
        scene.handle_events([key(pygame.K_RETURN)])
        for _ in range(10):
            scene.update(0.05)
            scene.draw(surface)


class DefeatChoiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def lose(self):
        game = FakeGame()
        game.field.hp, game.field.potions = 1, 2
        scene = BattleScene(game, "skeleton", rng=FixedRng())
        scene.handle_events([key(pygame.K_RETURN)])  # attack, then the skeleton finishes us
        play_out(scene)
        self.assertEqual((scene.mode, scene.engine.result), ("done", "lose"))
        return game, scene

    def test_retry_restarts_the_same_fight_from_the_pre_battle_state(self):
        game, scene = self.lose()
        self.assertEqual(scene.defeat_choice, 0)
        scene.handle_events([key(pygame.K_RETURN)])
        snapshot, enemy_id = game.retried
        self.assertEqual(enemy_id, "skeleton")
        self.assertEqual((snapshot["hp"], snapshot["potions"], snapshot["world"]), (1, 2, "field_east"))
        self.assertEqual(game.finished, 0)

    def test_choosing_the_village_keeps_the_old_outcome(self):
        game, scene = self.lose()
        scene.handle_events([key(pygame.K_DOWN), key(pygame.K_RETURN)])
        self.assertEqual(game.finished, 1)
        self.assertFalse(hasattr(game, "retried"))
        self.assertEqual(game.field.world, "village")

    def test_defeat_screen_draws_both_choices(self):
        game, scene = self.lose()
        scene.draw(pygame.Surface((800, 600)))
        self.assertEqual(len(scene._defeat_buttons()), 2)

    def test_victory_has_no_choice(self):
        game = FakeGame()
        game.field.atk = 400
        scene = BattleScene(game, "slime", rng=FixedRng())
        scene.handle_events([key(pygame.K_RETURN)])
        play_out(scene)
        scene.handle_events([key(pygame.K_DOWN), key(pygame.K_RETURN)])
        self.assertEqual(game.finished, 1)


class FinalPhaseSceneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_phase_two_darkens_the_fight_and_switches_music(self):
        game = FakeGame()
        game.field.hp = game.field.max_hp = 9999
        played = []
        game.audio = type("A", (), {"play": lambda self, name: played.append(name)})()
        scene = BattleScene(game, "final_boss", rng=FixedRng())
        self.assertIsNone(scene.music_track)
        scene.engine.enemy_hp = scene.engine.enemy_max_hp // 2 + 1
        scene.handle_events([key(pygame.K_RETURN)])
        play_out(scene)
        self.assertEqual(scene.engine.phase, 2)
        self.assertEqual(scene.music_track, "final")
        self.assertIn("phase", played)
        scene.draw(pygame.Surface((800, 600)))


if __name__ == "__main__":
    unittest.main()

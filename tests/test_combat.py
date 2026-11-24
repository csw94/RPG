"""Battle logic (gameplay/combat.py): skills, elements, statuses, XP and level-ups."""

import os
import random
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from gameplay import combat
from gameplay.combat import SKILLS, BattleEngine, xp_to_next
from gameplay.enemies import ENEMIES
from gameplay.world_data import FIELD_ROUTES
from scenes.dungeon_scene import SHRINE_DUNGEONS, DungeonScene
from scenes.field_scene import FieldScene
from scenes.village_scene import VillageScene


class FakeGame:
    active_slot = 1

    def save_game(self):
        pass

    def start_battle(self, enemy_id):
        pass


class FixedRng(random.Random):
    """random() always returns ``value``; uniform() returns the midpoint (no variance)."""

    def __init__(self, value=0.5):
        super().__init__(1)
        self.value = value

    def random(self):
        return self.value

    def uniform(self, a, b):
        return (a + b) / 2


def hero(level=1, **stats):
    field = FieldScene(FakeGame(), {"world": "field_east", "x": 2, "y": 16})
    field.level = level
    for key, value in stats.items():
        setattr(field, key, value)
    return field


def damage_to(events, target):
    return sum(e["amount"] for e in events if e["type"] == "damage" and e["target"] == target)


class SkillAndLevelTests(unittest.TestCase):
    def test_skills_unlock_with_level(self):
        names = lambda level: [s["id"] for s in BattleEngine(hero(level), "slime").available_skills()]
        self.assertEqual(names(1), ["light_bolt"])
        self.assertIn("heal_light", names(2))
        self.assertIn("wind_slash", names(4))
        self.assertNotIn("earth_smash", names(5))
        self.assertEqual(len(names(8)), len(SKILLS))

    def test_xp_levels_up_and_reports_new_skills(self):
        field = hero(1)
        before = (field.max_hp, field.atk, field.defense, field.max_mp)
        ups = field.gain_xp(xp_to_next(1) + xp_to_next(2) + 1)
        self.assertEqual(field.level, 3)
        self.assertEqual(field.xp, 1)
        self.assertEqual([u["level"] for u in ups], [2, 3])
        self.assertIn("회복의 빛", ups[0]["skills"])
        self.assertGreater(field.max_hp, before[0])
        self.assertGreater(field.atk, before[1])
        self.assertEqual(field.hp, field.max_hp)

    def test_shrine_blessing_no_longer_adds_a_level(self):
        field = hero(3)
        field.clear_shrine("shrine_wind")
        self.assertEqual(field.level, 3)


class DamageTests(unittest.TestCase):
    def skill_damage(self, skill, enemy):
        engine = BattleEngine(hero(8, mp=99), enemy, rng=FixedRng())
        return engine, damage_to(engine.act("skill", skill), "enemy")

    def test_weakness_and_resistance_scale_skill_damage(self):
        engine, weak = self.skill_damage("earth_smash", "shrine_wind")   # harpy: weak to earth
        self.assertTrue(any(e.get("weak") for e in engine.log))
        _, neutral = self.skill_damage("earth_smash", "goblin")
        base = hero(8).attack_power + SKILLS["earth_smash"]["power"]
        self.assertEqual(weak, round((base - ENEMIES["shrine_wind"]["defense"]) * 1.5))
        self.assertEqual(neutral, base - ENEMIES["goblin"]["defense"])
        engine, resisted = self.skill_damage("wind_slash", "shrine_wind")  # harpy resists wind
        self.assertTrue(any(e.get("resist") for e in engine.log))
        self.assertLess(resisted, base)

    def test_guard_halves_the_next_hit(self):
        plain = BattleEngine(hero(3, mp=99), "goblin", rng=FixedRng())
        plain.act("skill", "heal_light")
        guarded = BattleEngine(hero(3, mp=99), "goblin", rng=FixedRng())
        guarded.act("skill", "guard")
        self.assertLess(damage_to(guarded.log, "hero"), damage_to(plain.log, "hero"))

    def test_not_enough_mp_costs_no_turn(self):
        engine = BattleEngine(hero(1, mp=0), "slime", rng=FixedRng())
        events = engine.act("skill", "light_bolt")
        self.assertEqual(engine.turn, 0)
        self.assertEqual([e["type"] for e in events], ["message"])


class StatusTests(unittest.TestCase):
    def test_flame_slash_burns_the_enemy_each_turn(self):
        engine = BattleEngine(hero(8, mp=99), "skeleton", rng=FixedRng())
        engine.act("skill", "flame_slash")
        self.assertIn("burn", engine.statuses["enemy"])
        engine.act("attack")
        self.assertTrue(any(e["type"] == "status_tick" and e["target"] == "enemy" for e in engine.log))

    def test_earth_smash_can_stun(self):
        engine = BattleEngine(hero(8, mp=99), "skeleton", rng=FixedRng(0.0))
        events = engine.act("skill", "earth_smash")
        self.assertTrue(any(e["type"] == "stunned" for e in events))
        self.assertEqual(damage_to(events, "hero"), 0)

    def test_poisonous_enemies_poison_the_hero(self):
        engine = BattleEngine(hero(1, hp=100), "mushroom", rng=FixedRng(0.0))
        engine.act("attack")
        self.assertIn("poison", engine.statuses["hero"])
        engine.act("attack")
        self.assertTrue(any(e["type"] == "status_tick" and e["target"] == "hero" for e in engine.log))


class OutcomeTests(unittest.TestCase):
    def test_victory_grants_gold_xp_and_level_up_events(self):
        field = hero(1, atk=400)
        field.xp = xp_to_next(1) - 1
        gold = field.gold
        engine = BattleEngine(field, "slime", rng=FixedRng())
        events = engine.act("attack")
        types = [e["type"] for e in events]
        self.assertEqual(engine.result, "win")
        self.assertIn("xp", types)
        self.assertIn("level_up", types)
        self.assertGreater(field.gold, gold)

    def test_bosses_block_fleeing_but_normal_fights_allow_it(self):
        boss = BattleEngine(hero(5), "shrine_earth", rng=FixedRng())
        boss.act("flee")
        self.assertIsNone(boss.result)
        normal = BattleEngine(hero(1), "wolf", rng=FixedRng())
        normal.act("flee")
        self.assertEqual(normal.result, "flee")

    def test_losing_sends_the_hero_back_to_the_village_start(self):
        field = hero(1, hp=1)
        engine = BattleEngine(field, "skeleton", rng=FixedRng())
        engine.act("attack")
        self.assertEqual(engine.result, "lose")
        self.assertEqual(field.world, "village")
        self.assertEqual((field.player["x"], field.player["y"]), VillageScene.START)
        self.assertGreater(field.hp, 0)


class EnemyDataTests(unittest.TestCase):
    def test_every_enemy_has_battle_data(self):
        for enemy_id, enemy in ENEMIES.items():
            for key in ("xp", "weak", "resist", "pattern"):
                self.assertIn(key, enemy, enemy_id)
            for element in (*enemy["weak"], *enemy["resist"]):
                self.assertIn(element, combat.ELEMENTS, enemy_id)

    def test_each_region_has_its_own_enemies(self):
        pools = {world: set(data["enemy_pool"]) for world, data in FIELD_ROUTES.items()}
        self.assertTrue(pools["field_east"] & {"wolf", "mushroom"})
        self.assertTrue(pools["field_west"] & {"scorpion", "bandit"})
        self.assertTrue(pools["field_south"] & {"salamander", "magma_slime"})
        self.assertTrue(any("goblin" in pool for pool in pools.values()), "goblin quest needs goblins")
        for pool in pools.values():
            self.assertTrue(pool <= set(ENEMIES))
        for shrine in SHRINE_DUNGEONS:
            dungeon = DungeonScene(FakeGame(), {"world": f"{shrine}_1f"})
            self.assertTrue(set(dungeon.enemy_pool) <= set(ENEMIES))
            self.assertTrue(set(dungeon.enemy_pool) & {"bat", "skeleton"}, shrine)


if __name__ == "__main__":
    unittest.main()

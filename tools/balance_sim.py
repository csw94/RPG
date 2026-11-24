r"""Simulate full playthroughs with BattleEngine to measure battle balance.

Usage (from the project root):
    .venv\Scripts\python.exe tools\balance_sim.py [battles_per_region] [runs]

Each region: ~60% field fights, ~40% shrine-dungeon fights, then the shop, then the boss.
A simple player AI drinks potions when low and casts the best affordable attack skill.
Targets (v0.10.0): field fights 3-4 turns; bosses ~10-15 turns; with 4 fights per region
bosses are won ~85% of the time, with 5+ almost always.
"""
import os
import random
import statistics
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gameplay.combat import SKILLS, BattleEngine
from gameplay.enemies import ENEMIES
from gameplay.equipment import ARMORS
from gameplay.world_data import FIELD_ROUTES
from scenes.field_scene import FieldScene
from scenes.dungeon_scene import SHRINE_DUNGEONS


class FakeGame:
    active_slot = 1

    def save_game(self):
        pass


def choose(engine, f):
    """Simple sensible player: potion when low, best affordable attack skill, else sword."""
    boss = engine.is_boss
    if f.hp < f.max_hp * (0.4 if boss else 0.3) and (f.potions or f.high_potions):
        return ("item", None)
    heal = SKILLS["heal_light"]
    if f.hp < f.max_hp * 0.45 and heal["level"] <= f.level and f.mp >= heal["mp"]:
        return ("skill", "heal_light")
    best, best_dmg = None, f.attack_power - engine.enemy["defense"]
    for s in engine.available_skills():
        if s["kind"] != "attack" or f.mp < s["mp"]:
            continue
        mult = engine._element_mult(s["element"])[0]
        dmg = (f.attack_power + s["power"] - engine.enemy["defense"]) * mult
        # Save MP on easy fights unless it is a weakness hit.
        if not boss and mult <= 1 and engine.enemy_hp <= best_dmg * 1.2:
            continue
        if dmg > best_dmg * 1.15:
            best, best_dmg = s["id"], dmg
    return ("skill", best) if best else ("attack", None)


def fight(f, enemy, rng):
    e = BattleEngine(f, enemy, rng=rng)
    turns = 0
    while not e.result and turns < 60:
        action, skill = choose(e, f)
        e.act(action, skill)
        turns += 1
    return e.result, turns


def shop(f):
    if "steel_longsword" not in f.owned_weapons and f.weapon != "star_sword" and f.gold >= 120 + 60:
        f.gold -= 120; f.owned_weapons.append("steel_longsword"); f.weapon = "steel_longsword"
    if "knight_breastplate" not in f.owned_armors and f.gold >= 150 + 60:
        f.gold -= 150; f.owned_armors.append("knight_breastplate"); f.armor = "knight_breastplate"
        f.max_hp += 20; f.hp += 20
    while f.potions < 4 and f.gold >= 30:
        f.gold -= 30; f.potions += 1
    while f.high_potions < 2 and f.gold >= 120:
        f.gold -= 80; f.high_potions += 1


# The north (Frost Highlands) opens after two shrines, so it comes third here.
REGIONS = (("field_east", "shrine_wind"), ("field_west", "shrine_earth"), ("field_north", "shrine_ice"),
           ("field_south", "shrine_fire"))


def playthrough(per_region, rng, report):
    f = FieldScene(FakeGame(), {"world": "field_east", "x": 2, "y": 16})
    f.gold = 0
    deaths = 0
    log = []
    for field, boss in REGIONS:
        pool = FIELD_ROUTES[field]["enemy_pool"]
        turns = []
        for i in range(per_region):
            enemy = rng.choice(pool) if i < per_region * 0.6 else rng.choice(SHRINE_DUNGEONS[boss]["monsters"])
            res, t = fight(f, enemy, rng)
            turns.append(t)
            if res == "lose":
                deaths += 1
        if field == "field_west":
            f.gold += 180  # goblin quest
        if field == "field_east":
            f.gold += 100  # herb quest
        shop(f)
        hp_before = f.hp
        res, t = fight(f, boss, rng)
        log.append((boss, f.level, f.attack_power, f.defense_power, f.max_hp, res, t,
                    statistics.mean(turns) if turns else 0, hp_before))
        if res == "lose":
            deaths += 1
            f.hp = f.max_hp
            res, t = fight(f, boss, rng)
            if res != "win":
                f.quest_flags[boss] = 1
                f.clear_shrine(boss)
    f.check_fountain_awakening()
    f.hp, f.mp = f.max_hp, f.max_mp
    shop(f)
    res, t = fight(f, "final_boss", rng)
    log.append(("final_boss", f.level, f.attack_power, f.defense_power, f.max_hp, res, t, 0, f.hp))
    return log, deaths


def main():
    per = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    rng = random.Random(7)
    results = {}
    deaths = []
    for _ in range(runs):
        log, d = playthrough(per, rng, {})
        deaths.append(d)
        for row in log:
            results.setdefault(row[0], []).append(row)
    print(f"battles per region={per}, runs={runs}, avg deaths/run={statistics.mean(deaths):.2f}")
    print("boss          lvl  atk  def  maxhp  win%  turns  field-turns")
    for boss, rows in results.items():
        win = sum(r[5] == "win" for r in rows) / len(rows) * 100
        print(f"{boss:13s} {statistics.mean(r[1] for r in rows):4.1f} {statistics.mean(r[2] for r in rows):4.0f} "
              f"{statistics.mean(r[3] for r in rows):4.0f} {statistics.mean(r[4] for r in rows):6.0f} {win:5.0f} "
              f"{statistics.mean(r[6] for r in rows):6.1f} {statistics.mean(r[7] for r in rows):6.1f}")


if __name__ == "__main__":
    main()

r"""Simulate full playthroughs with BattleEngine to measure battle balance.

Usage (from the project root):
    .venv\Scripts\python.exe tools\balance_sim.py [battles_per_region] [runs] [--basic] [--plus]

By default the player also spends spare gold at Bron's smithy and on mana potions, and
drinks a mana potion in boss fights when skills run dry. --basic restores the older,
gear-only shopping. --plus continues into a second cycle (new game plus) and reports it.

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
from scenes.smithy_scene import MAX_UPGRADE, upgrade_cost
from gameplay.new_game_plus import new_game_plus_state

FULL_KIT = True  # smithy upgrades + mana potions (turned off by --basic)


class FakeGame:
    active_slot = 1

    def save_game(self):
        pass


def choose(engine, f):
    """Simple sensible player: potion when low, best affordable attack skill, else sword."""
    boss = engine.is_boss
    if f.hp < f.max_hp * (0.4 if boss else 0.3) and (f.potions or f.high_potions):
        return ("item", None)
    cheapest = min((s["mp"] for s in engine.available_skills() if s["kind"] == "attack"), default=99)
    if FULL_KIT and boss and f.mp < cheapest and f.item_count("mana_potion") and f.hp > f.max_hp * 0.5:
        return ("item", "mana_potion")
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
    if not FULL_KIT:
        return
    while f.item_count("mana_potion") < 3 and f.gold >= 50 + 80:
        f.gold -= 50; f.add_item("mana_potion")
    # Spend what is left at the smithy, cheapest upgrade first, keeping 80 G spare.
    while True:
        options = [(upgrade_cost(kind, f.upgrades.get(item, 0)), item) for kind, item in
                   (("weapon", f.weapon), ("armor", f.armor)) if f.upgrades.get(item, 0) < MAX_UPGRADE]
        if not options:
            break
        cost, item = min(options)
        if f.gold < cost + 80:
            break
        f.gold -= cost
        f.upgrades[item] = f.upgrades.get(item, 0) + 1


# The north (Frost Highlands) opens after two shrines, so it comes third here.
REGIONS = (("field_east", "shrine_wind"), ("field_west", "shrine_earth"), ("field_north", "shrine_ice"),
           ("field_south", "shrine_fire"))


def playthrough(per_region, rng, report, field=None):
    f = field or FieldScene(FakeGame(), {"world": "field_east", "x": 2, "y": 16})
    if field is None:
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
    if res == "win":
        f.quest_flags["final_boss"] = 1
    report["hero"] = f
    return log, deaths


def main():
    global FULL_KIT
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    FULL_KIT = "--basic" not in sys.argv
    plus = "--plus" in sys.argv
    per = int(args[0]) if len(args) > 0 else 5
    runs = int(args[1]) if len(args) > 1 else 200
    rng = random.Random(7)
    results = {}
    deaths = []
    for _ in range(runs):
        report = {}
        log, d = playthrough(per, rng, report)
        if plus:
            second = FieldScene(FakeGame(), new_game_plus_state(report["hero"].serialize()))
            log2, d2 = playthrough(per, rng, {}, field=second)
            log += [("2:" + row[0],) + tuple(row[1:]) for row in log2]
            d += d2
        deaths.append(d)
        for row in log:
            results.setdefault(row[0], []).append(row)
    kit = "full kit (smithy + mana potions)" if FULL_KIT else "basic kit"
    print(f"battles per region={per}, runs={runs}, {kit}, avg deaths/run={statistics.mean(deaths):.2f}")
    print("boss          lvl  atk  def  maxhp  win%  turns  field-turns")
    for boss, rows in results.items():
        win = sum(r[5] == "win" for r in rows) / len(rows) * 100
        print(f"{boss:13s} {statistics.mean(r[1] for r in rows):4.1f} {statistics.mean(r[2] for r in rows):4.0f} "
              f"{statistics.mean(r[3] for r in rows):4.0f} {statistics.mean(r[4] for r in rows):6.0f} {win:5.0f} "
              f"{statistics.mean(r[6] for r in rows):6.1f} {statistics.mean(r[7] for r in rows):6.1f}")


if __name__ == "__main__":
    main()

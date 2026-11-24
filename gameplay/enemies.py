"""Enemy balance and battle pattern data for the 30-minute story.

``weak``/``resist`` list elements from ``gameplay.combat.ELEMENTS`` (x1.5 / x0.5 damage).
``pattern`` picks the enemy's behaviour in ``BattleEngine._enemy_turn``.
"""


def _enemy(enemy_id, name, hp, attack, defense, gold, xp, sprite, size, pattern="basic",
           weak=(), resist=(), potion_drop=0):
    return {"id": enemy_id, "name": name, "hp": hp, "attack": attack, "defense": defense,
            "gold": gold, "potion_drop": potion_drop, "xp": xp, "sprite": sprite, "size": size,
            "pattern": pattern, "weak": tuple(weak), "resist": tuple(resist)}


ENEMIES = {enemy["id"]: enemy for enemy in (
    # Everywhere
    _enemy("slime", "초록 슬라임", 35, 10, 2, 10, 8, "slime", (112, 84), weak=("fire",), potion_drop=1),
    _enemy("goblin", "고블린 척후병", 55, 16, 4, 25, 14, "goblin", (96, 96), "double_stab"),
    # Windy forest path (east)
    _enemy("wolf", "숲늑대", 48, 13, 3, 14, 12, "wolf", (128, 96), "howl", weak=("fire",)),
    _enemy("mushroom", "독버섯 요정", 60, 11, 3, 12, 11, "mushroom", (96, 96), "poison",
           weak=("fire",), resist=("earth",)),
    # Red rock canyon (west)
    _enemy("scorpion", "붉은 전갈", 70, 19, 7, 22, 18, "scorpion", (128, 96), "poison",
           weak=("wind",), resist=("earth",)),
    _enemy("bandit", "협곡 도적", 80, 21, 5, 35, 22, "bandit", (96, 120), "double_stab"),
    # Volcanic foothills (south)
    _enemy("salamander", "불도마뱀", 95, 25, 8, 30, 26, "salamander", (128, 96), "burn",
           weak=("earth",), resist=("fire",)),
    _enemy("magma_slime", "마그마 슬라임", 110, 23, 10, 28, 24, "magma_slime", (112, 84), "burn",
           weak=("wind",), resist=("fire",)),
    # Shrine dungeons
    _enemy("bat", "동굴 박쥐", 50, 15, 3, 16, 15, "bat", (112, 84), "drain",
           weak=("light",), resist=("wind",)),
    _enemy("skeleton", "해골 병사", 75, 20, 6, 24, 20, "skeleton_warrior", (96, 120),
           weak=("light",), resist=("dark",)),
    # Bosses
    _enemy("shrine_wind", "폭풍 하피", 140, 22, 6, 0, 60, "harpy", (144, 144), "gust",
           weak=("earth",), resist=("wind",)),
    _enemy("shrine_earth", "바위 골렘", 200, 20, 12, 0, 90, "golem", (144, 144), "earthquake",
           weak=("wind",), resist=("earth",)),
    _enemy("shrine_fire", "화염 리자드맨", 160, 28, 8, 0, 120, "lizardman", (144, 144), "enrage",
           weak=("earth",), resist=("fire",)),
    _enemy("final_boss", "흑기사 말포스", 320, 35, 15, 0, 0, "dark_knight", (120, 168), "dark_arts",
           weak=("light",), resist=("dark",)),
)}

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
    _enemy("slime", "초록 슬라임", 40, 10, 2, 10, 10, "slime", (112, 84), weak=("fire",), potion_drop=1),
    _enemy("goblin", "고블린 척후병", 62, 16, 4, 25, 18, "goblin", (96, 96), "double_stab"),
    # Windy forest path (east)
    _enemy("wolf", "숲늑대", 55, 13, 3, 14, 15, "wolf", (128, 96), "howl", weak=("fire",)),
    _enemy("mushroom", "독버섯 요정", 66, 11, 3, 12, 14, "mushroom", (96, 96), "poison",
           weak=("fire",), resist=("earth",)),
    # Red rock canyon (west)
    _enemy("scorpion", "붉은 전갈", 105, 21, 7, 22, 24, "scorpion", (128, 96), "poison",
           weak=("wind",), resist=("earth",)),
    _enemy("bandit", "협곡 도적", 115, 22, 5, 35, 28, "bandit", (96, 120), "double_stab"),
    # Volcanic foothills (south)
    _enemy("salamander", "불도마뱀", 150, 28, 9, 30, 34, "salamander", (128, 96), "burn",
           weak=("earth",), resist=("fire",)),
    _enemy("magma_slime", "마그마 슬라임", 160, 26, 12, 28, 32, "magma_slime", (112, 84), "burn",
           weak=("wind",), resist=("fire",)),
    # Frost Highlands (north)
    _enemy("snow_wolf", "서리 늑대", 125, 27, 8, 30, 30, "frost_wolf", (128, 96), "howl",
           weak=("fire",), resist=("wind",)),
    _enemy("ice_slime", "얼음 슬라임", 140, 24, 12, 28, 30, "ice_slime", (112, 84), "freeze",
           weak=("fire",), resist=("earth",)),
    _enemy("frost_wisp", "서리 정령", 100, 28, 6, 32, 32, "frost_wisp", (96, 96), "freeze",
           weak=("fire", "light"), resist=("wind",)),
    # Shrine dungeons
    _enemy("bat", "동굴 박쥐", 60, 15, 3, 16, 18, "bat", (112, 84), "drain",
           weak=("light",), resist=("wind",)),
    _enemy("skeleton", "해골 병사", 100, 20, 6, 24, 24, "skeleton_warrior", (96, 120),
           weak=("light",), resist=("dark",)),
    # Starlight Abyss (post-game)
    _enemy("shadow_wolf", "그림자 늑대", 250, 57, 17, 50, 50, "shadow_wolf", (128, 96), "howl",
           weak=("light",), resist=("dark",)),
    _enemy("void_slime", "공허 슬라임", 290, 53, 23, 55, 52, "void_slime", (112, 84), "poison",
           weak=("fire",), resist=("dark", "earth")),
    _enemy("abyss_knight", "심연 기사", 355, 63, 27, 80, 65, "abyss_knight", (120, 168), "double_stab",
           weak=("light",), resist=("dark",)),
    # Bosses
    _enemy("shrine_wind", "폭풍 하피", 160, 25, 6, 0, 60, "harpy", (144, 144), "gust",
           weak=("earth",), resist=("wind",)),
    _enemy("shrine_earth", "바위 골렘", 260, 30, 12, 0, 90, "golem", (144, 144), "earthquake",
           weak=("wind",), resist=("earth",)),
    _enemy("shrine_fire", "화염 리자드맨", 360, 46, 13, 0, 120, "lizardman", (144, 144), "enrage",
           weak=("earth",), resist=("fire",)),
    _enemy("shrine_ice", "빙결 리자드킹", 290, 34, 12, 0, 110, "frost_lizard", (144, 144), "blizzard",
           weak=("fire",), resist=("wind",)),
    _enemy("final_boss", "흑기사 말포스", 720, 58, 22, 0, 0, "dark_knight", (120, 168), "dark_arts",
           weak=("light",), resist=("dark",)),
    _enemy("abyss_lord", "심연의 군주 녹스", 1100, 86, 27, 500, 600, "abyss_lord", (160, 160), "abyss",
           weak=("light",), resist=("dark", "fire")),
)}

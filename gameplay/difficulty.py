"""Difficulty levels: multipliers applied on top of the normal balance."""

DIFFICULTY_ORDER = ("easy", "normal", "hard")
DIFFICULTIES = {
    "easy": {"name": "쉬움", "enemy_hp": 0.8, "damage": 0.75, "gold": 1.0, "xp": 1.0,
             "desc": "적 HP 80% · 받는 피해 75%. 이야기를 편하게 즐기고 싶을 때"},
    "normal": {"name": "보통", "enemy_hp": 1.0, "damage": 1.0, "gold": 1.0, "xp": 1.0,
               "desc": "기본 난이도. 준비를 갖추면 보스를 이길 수 있는 균형"},
    "hard": {"name": "어려움", "enemy_hp": 1.25, "damage": 1.25, "gold": 1.2, "xp": 1.0,
             "desc": "적 HP 125% · 받는 피해 125% · 골드 120%. 전략이 중요해집니다"},
}


def difficulty_of(field):
    """Battle multipliers for the field: its difficulty combined with its new-game-plus cycle."""
    from gameplay.new_game_plus import cycle_multipliers

    base = DIFFICULTIES.get(getattr(field, "difficulty", "normal"), DIFFICULTIES["normal"])
    cycle = cycle_multipliers(getattr(field, "cycle", 1))
    return {**base, **{key: base[key] * cycle[key] for key in cycle}}

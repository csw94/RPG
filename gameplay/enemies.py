"""Enemy balance and battle pattern data for the 30-minute story."""

ENEMIES = {
    "slime": {
        "id": "slime", "name": "\ucd08\ub85d \uc2ac\ub77c\uc784", "hp": 35, "attack": 10, "defense": 2,
        "gold": 10, "potion_drop": 1, "sprite": "slime", "size": (112, 84),
        "pattern": "basic",
    },
    "goblin": {
        "id": "goblin", "name": "\uace0\ube14\ub9b0 \ucc99\ud6c4\ubcd1", "hp": 55, "attack": 16, "defense": 4,
        "gold": 25, "potion_drop": 0, "sprite": "goblin", "size": (96, 96),
        "pattern": "double_stab",
    },
    "shrine_wind": {
        "id": "shrine_wind", "name": "\ud3ed\ud48d \ud558\ud53c", "hp": 140, "attack": 22, "defense": 6,
        "gold": 0, "potion_drop": 0, "sprite": "harpy", "size": (144, 144),
        "pattern": "gust",
    },
    "shrine_earth": {
        "id": "shrine_earth", "name": "\ubc14\uc704 \uace8\ub818", "hp": 200, "attack": 20, "defense": 12,
        "gold": 0, "potion_drop": 0, "sprite": "golem", "size": (144, 144),
        "pattern": "earthquake",
    },
    "shrine_fire": {
        "id": "shrine_fire", "name": "\ud654\uc5fc \ub9ac\uc790\ub4dc\ub9e8", "hp": 160, "attack": 28, "defense": 8,
        "gold": 0, "potion_drop": 0, "sprite": "lizardman", "size": (144, 144),
        "pattern": "enrage",
    },
    "final_boss": {
        "id": "final_boss", "name": "\ud751\uae30\uc0ac \ub9d0\ud3ec\uc2a4", "hp": 320, "attack": 35, "defense": 15,
        "gold": 0, "potion_drop": 0, "sprite": "dark_knight", "size": (120, 168),
        "pattern": "dark_arts",
    },
}

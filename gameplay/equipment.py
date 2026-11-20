"""Equipment and consumable data shared by the village shop and battle system."""

WEAPONS = {
    "rusty_sword": {"name": "\ub179\uc2a8 \ucca0\uac80", "attack": 3, "price": 0},
    "steel_longsword": {"name": "\uac15\ucca0 \uc7a5\uac80", "attack": 10, "price": 120},
    "star_sword": {"name": "\ubcc4\ube5b\uc758 \uac80", "attack": 25, "price": 0},
    # IDs from older saves remain valid.
    "iron_sword": {"name": "\ucca0\uac80", "attack": 4, "price": 50},
    "silver_sword": {"name": "\uc740\uac80", "attack": 8, "price": 115},
}

ARMORS = {
    "traveler_clothes": {"name": "\uac00\uc8fd \ud29c\ub2c9", "defense": 3, "health": 0, "price": 0},
    "knight_breastplate": {"name": "\uae30\uc0ac\ub2e8\uc758 \ud749\uac11", "defense": 8, "health": 20, "price": 150},
    # IDs from older saves remain valid.
    "leather_armor": {"name": "\uac00\uc8fd \uac11\uc637", "defense": 2, "health": 0, "price": 35},
    "chainmail": {"name": "\uc0ac\uc2ac \uac11\uc637", "defense": 4, "health": 0, "price": 90},
}

SMALL_POTION = {"name": "\ud68c\ubcf5\uc57d (\uc18c)", "price": 30, "heal": 50}
HIGH_POTION = {"name": "\uace0\uae09 \ud68c\ubcf5\uc57d", "price": 80, "heal": 120}
POTION_CAP = 10

SHOP_ITEMS = (
    {"kind": "weapon", "id": "steel_longsword"},
    {"kind": "armor", "id": "knight_breastplate"},
    {"kind": "potion", "id": "small_potion"},
    {"kind": "potion", "id": "high_potion"},
)


def item_info(item):
    kind, item_id = item["kind"], item["id"]
    if kind == "weapon":
        return WEAPONS[item_id]
    if kind == "armor":
        return ARMORS[item_id]
    return HIGH_POTION if item_id == "high_potion" else SMALL_POTION

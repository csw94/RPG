"""Equipment definitions shared by the village shop and battle system."""

WEAPONS = {
    "rusty_sword": {"name": "낡은 검", "attack": 1, "price": 0},
    "iron_sword": {"name": "철검", "attack": 4, "price": 50},
    "silver_sword": {"name": "은검", "attack": 8, "price": 115},
}

ARMORS = {
    "traveler_clothes": {"name": "여행자 옷", "defense": 0, "price": 0},
    "leather_armor": {"name": "가죽 갑옷", "defense": 2, "price": 35},
    "chainmail": {"name": "사슬 갑옷", "defense": 4, "price": 90},
}

SHOP_ITEMS = (
    {"kind": "weapon", "id": "iron_sword"},
    {"kind": "weapon", "id": "silver_sword"},
    {"kind": "armor", "id": "leather_armor"},
    {"kind": "armor", "id": "chainmail"},
    {"kind": "potion", "id": "potion"},
)


def item_info(item):
    kind, item_id = item["kind"], item["id"]
    if kind == "weapon":
        return WEAPONS[item_id]
    if kind == "armor":
        return ARMORS[item_id]
    return {"name": "회복 포션", "price": 15, "heal": 18}

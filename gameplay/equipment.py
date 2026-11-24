"""Equipment and consumables shared by the shop, the status screen and battles.

Weapons may carry an element (used by plain attacks), extra crit chance and an on-hit
status proc. Armor may add max HP/MP and block a status. Accessories (a third slot) add
small perks. Shop stock widens as shrines are cleared (``tier`` = shrines needed).
"""

WEAPONS = {
    "rusty_sword": {"name": "녹슨 철검", "attack": 3, "price": 0, "desc": "촌장님이 건네준 낡은 검"},
    "steel_longsword": {"name": "강철 장검", "attack": 10, "price": 120, "desc": "튼튼하고 무난한 장검"},
    "wind_dagger": {"name": "바람의 단검", "attack": 8, "price": 140, "element": "wind", "crit": 0.12,
                    "desc": "바람 속성 · 치명타 확률 +12%"},
    "earth_hammer": {"name": "대지의 전투망치", "attack": 15, "price": 230, "element": "earth",
                     "proc": ("stun", 0.12, 1), "desc": "대지 속성 · 12% 확률로 기절"},
    "flame_blade": {"name": "화염검", "attack": 13, "price": 240, "element": "fire",
                    "proc": ("burn", 0.2, 2), "desc": "화염 속성 · 20% 확률로 화상"},
    "storm_halberd": {"name": "폭풍 할버드", "attack": 18, "price": 330, "element": "wind", "crit": 0.06,
                      "desc": "바람 속성 · 치명타 확률 +6%"},
    "star_sword": {"name": "별빛의 검", "attack": 25, "price": 0, "element": "light",
                   "desc": "빛 속성 · 별빛 분수가 깨운 전설의 검"},
    # IDs from older saves remain valid.
    "iron_sword": {"name": "철검", "attack": 4, "price": 50, "desc": "평범한 철검"},
    "silver_sword": {"name": "은검", "attack": 8, "price": 115, "desc": "은빛으로 빛나는 검"},
}

ARMORS = {
    "traveler_clothes": {"name": "가죽 튜닉", "defense": 3, "health": 0, "price": 0, "desc": "여행자의 기본 옷"},
    "mage_robe": {"name": "마도사의 로브", "defense": 5, "health": 0, "mp": 10, "price": 130,
                  "desc": "최대 MP +10"},
    "knight_breastplate": {"name": "기사단의 흉갑", "defense": 8, "health": 20, "price": 150,
                           "desc": "최대 HP +20"},
    "dragon_scale": {"name": "용비늘 갑옷", "defense": 12, "health": 30, "immune": "burn", "price": 320,
                     "desc": "최대 HP +30 · 화상에 걸리지 않음"},
    "aurora_mail": {"name": "오로라 갑옷", "defense": 14, "health": 40, "mp": 8, "price": 420,
                    "desc": "최대 HP +40 · 최대 MP +8"},
    # IDs from older saves remain valid.
    "leather_armor": {"name": "가죽 갑옷", "defense": 2, "health": 0, "price": 35, "desc": "가벼운 가죽 갑옷"},
    "chainmail": {"name": "사슬 갑옷", "defense": 4, "health": 0, "price": 90, "desc": "촘촘한 사슬 갑옷"},
}

ACCESSORIES = {
    "antidote_charm": {"name": "해독의 부적", "price": 80, "immune": "poison", "desc": "독에 걸리지 않음"},
    "feather_charm": {"name": "바람의 깃털", "price": 110, "evasion": 8, "desc": "회피 +8%"},
    "mana_ring": {"name": "마나의 반지", "price": 130, "victory_mp": 2, "desc": "승리할 때 MP +2 추가"},
    "power_bracelet": {"name": "힘의 팔찌", "price": 170, "attack": 4, "desc": "공격력 +4"},
    "warm_scarf": {"name": "따뜻한 목도리", "price": 150, "immune": "stun", "evasion": 3,
                   "desc": "빙결·기절에 걸리지 않음 · 회피 +3%"},
    # Villager request rewards (not sold).
    "wolf_fang_charm": {"name": "늑대 송곳니 부적", "price": 0, "crit": 0.1, "desc": "치명타 확률 +10%"},
    "ember_bracelet": {"name": "용암석 팔찌", "price": 0, "attack": 3, "immune": "burn",
                       "desc": "공격력 +3 · 화상에 걸리지 않음"},
    "guardian_medal": {"name": "수호자의 훈장", "price": 0, "defense": 5, "desc": "방어력 +5"},
    "frost_heart": {"name": "얼음 심장", "price": 0, "immune": "stun", "attack": 2,
                    "desc": "빙결·기절에 걸리지 않음 · 공격력 +2"},
    "smith_ring": {"name": "대장장이 반지", "price": 0, "attack": 2, "defense": 2,
                   "desc": "공격력 +2 · 방어력 +2"},
    "sage_glasses": {"name": "현자의 안경", "price": 0, "victory_mp": 2, "evasion": 3,
                     "desc": "승리 시 MP +2 · 회피 +3%"},
    # Starlight Abyss rewards (not sold).
    "star_amulet": {"name": "별의 목걸이", "price": 0, "attack": 3, "evasion": 6, "victory_mp": 2,
                    "desc": "공격력 +3 · 회피 +6% · 승리 시 MP +2"},
    "abyss_crown": {"name": "심연의 왕관", "price": 0, "attack": 8, "evasion": 8, "victory_mp": 3,
                    "desc": "공격력 +8 · 회피 +8% · 승리 시 MP +3"},
}

# Gear kept only so very old saves still load; not part of the collection.
LEGACY_IDS = {"iron_sword", "silver_sword", "leather_armor", "chainmail"}

SMALL_POTION = {"name": "회복약(소)", "price": 30, "heal": 50, "desc": "HP 50 회복"}
HIGH_POTION = {"name": "고급 회복약", "price": 80, "heal": 120, "desc": "HP 120 회복"}
POTION_CAP = 10
# Everything usable from the battle item menu. Potions live in their own save fields
# ("attr"); the newer consumables are counted in FieldScene.items.
CONSUMABLES = {
    "small_potion": {**SMALL_POTION, "attr": "potions"},
    "high_potion": {**HIGH_POTION, "attr": "high_potions"},
    "mana_potion": {"name": "마나 물약", "price": 50, "mp": 30, "desc": "MP 30 회복"},
    "antidote": {"name": "해독제", "price": 25, "cure": True, "desc": "독·화상·빙결 같은 상태이상 해제"},
    "elixir": {"name": "엘릭서", "price": 300, "heal": 9999, "mp": 9999, "cure": True, "cap": 3,
               "desc": "HP·MP 완전 회복 · 상태이상 해제 (3개까지)"},
}
# Everything usable from the battle item menu. Potions live in their own save fields
# ("attr"); the newer consumables are counted in FieldScene.items.
CONSUMABLES = {
    "small_potion": {**SMALL_POTION, "attr": "potions"},
    "high_potion": {**HIGH_POTION, "attr": "high_potions"},
    "mana_potion": {"name": "마나 물약", "price": 50, "mp": 30, "desc": "MP 30 회복"},
    "antidote": {"name": "해독제", "price": 25, "cure": True, "desc": "독·화상·빙결 같은 상태이상 해제"},
    "elixir": {"name": "엘릭서", "price": 300, "heal": 9999, "mp": 9999, "cure": True, "cap": 3,
               "desc": "HP·MP 완전 회복 · 상태이상 해제 (3개까지)"},
}

SHOP_TABS = (("weapon", "무기"), ("armor", "방어구"), ("accessory", "장신구"), ("potion", "소모품"))
SHOP_ITEMS = (
    {"kind": "weapon", "id": "steel_longsword", "tier": 0},
    {"kind": "weapon", "id": "wind_dagger", "tier": 0},
    {"kind": "weapon", "id": "earth_hammer", "tier": 1},
    {"kind": "weapon", "id": "flame_blade", "tier": 2},
    {"kind": "weapon", "id": "storm_halberd", "tier": 3},
    {"kind": "armor", "id": "knight_breastplate", "tier": 0},
    {"kind": "armor", "id": "mage_robe", "tier": 0},
    {"kind": "armor", "id": "dragon_scale", "tier": 2},
    {"kind": "armor", "id": "aurora_mail", "tier": 4},
    {"kind": "accessory", "id": "antidote_charm", "tier": 0},
    {"kind": "accessory", "id": "feather_charm", "tier": 0},
    {"kind": "accessory", "id": "mana_ring", "tier": 1},
    {"kind": "accessory", "id": "power_bracelet", "tier": 1},
    {"kind": "accessory", "id": "warm_scarf", "tier": 2},
    {"kind": "potion", "id": "small_potion", "tier": 0},
    {"kind": "potion", "id": "high_potion", "tier": 0},
    # Mira's apothecary in the south district.
    {"kind": "potion", "id": "small_potion", "tier": 0, "shop": "mira"},
    {"kind": "potion", "id": "high_potion", "tier": 0, "shop": "mira"},
    {"kind": "potion", "id": "mana_potion", "tier": 0, "shop": "mira"},
    {"kind": "potion", "id": "antidote", "tier": 0, "shop": "mira"},
    {"kind": "potion", "id": "elixir", "tier": 3, "shop": "mira"},
)
CATALOGS = {"weapon": WEAPONS, "armor": ARMORS, "accessory": ACCESSORIES}


def item_info(item):
    kind, item_id = item["kind"], item["id"]
    if kind in CATALOGS:
        return CATALOGS[kind][item_id]
    return CONSUMABLES[item_id]


def shop_stock(shrines_cleared, kind=None, shop="logan"):
    """Items one shop sells after ``shrines_cleared`` shrines, optionally for one tab."""
    return [item for item in SHOP_ITEMS
            if item.get("shop", "logan") == shop and item["tier"] <= shrines_cleared
            and (kind is None or item["kind"] == kind)]

"""Hand-drawn pixel sprites, including the taller 16x24 hero sprite."""

import random
import pygame


PALETTE = {
    "grass": (62, 128, 75),
    "grass_dark": (45, 105, 64),
    "grass_light": (105, 164, 87),
    "grass_gold": (180, 174, 78),
    "dirt": (133, 91, 58),
    "dirt_light": (171, 119, 73),
    "dirt_dark": (99, 65, 49),
    "stone": (104, 103, 112),
    "stone_light": (150, 148, 150),
    "stone_dark": (69, 70, 83),
    "metal": (171, 185, 184),
    "roof": (112, 53, 40),
    "roof_light": (162, 75, 47),
    "bone": (225, 214, 174),
    "wood": (137, 77, 42),
    "wood_light": (188, 119, 55),
    "gold": (245, 194, 74),
    "skin": (244, 191, 137),
    "skin_shadow": (205, 132, 94),
    "hair": (67, 45, 43),
    "hair_light": (117, 75, 47),
    "blue": (54, 111, 190),
    "blue_light": (92, 158, 220),
    "blue_dark": (41, 73, 134),
    "pants": (59, 64, 103),
    "boot": (66, 43, 38),
    "slime": (78, 184, 105),
    "slime_light": (146, 230, 145),
    "slime_dark": (42, 132, 79),
    "white": (255, 245, 215),
    "ink": (35, 42, 48),
}

_BASE = {}
_SCALED = {}
_HERO_SCALED = {}


def _canvas(size=(16, 16)):
    return pygame.Surface(size, pygame.SRCALPHA)


def _rect(surface, color, x, y, width, height=1):
    pygame.draw.rect(surface, color, pygame.Rect(x, y, width, height))


def _player(weapon="rusty_sword", armor="traveler_clothes"):
    """A taller, chibi-style adventurer with layered hair, tunic, and gear."""
    surface = _canvas((16, 24))

    # Tousled chestnut hair frames a large, expressive face.
    _rect(surface, PALETTE["hair"], 4, 1, 8, 2)
    _rect(surface, PALETTE["hair"], 2, 3, 12, 2)
    _rect(surface, PALETTE["hair"], 1, 5, 14, 3)
    _rect(surface, PALETTE["hair"], 2, 7, 3, 4)
    _rect(surface, PALETTE["hair"], 11, 7, 3, 4)
    _rect(surface, PALETTE["skin"], 4, 5, 8, 7)
    _rect(surface, PALETTE["skin_shadow"], 3, 7, 1, 3)
    _rect(surface, PALETTE["skin_shadow"], 12, 7, 1, 3)
    _rect(surface, PALETTE["hair_light"], 3, 3, 4, 1)
    _rect(surface, PALETTE["hair_light"], 9, 4, 3, 1)
    _rect(surface, PALETTE["hair"], 4, 6, 3, 2)
    _rect(surface, PALETTE["hair"], 9, 6, 3, 2)
    _rect(surface, PALETTE["skin"], 5, 7, 6, 4)
    _rect(surface, PALETTE["ink"], 6, 8, 1, 2)
    _rect(surface, PALETTE["ink"], 9, 8, 1, 2)
    _rect(surface, (220, 126, 113), 5, 10, 1, 1)
    _rect(surface, (220, 126, 113), 10, 10, 1, 1)
    _rect(surface, PALETTE["skin_shadow"], 7, 11, 2, 1)

    # A forest-green mantle sits behind a cream tunic and leather belt.
    _rect(surface, (56, 91, 66), 2, 12, 12, 6)
    _rect(surface, (89, 124, 78), 2, 13, 2, 4)
    _rect(surface, (89, 124, 78), 12, 13, 2, 4)
    _rect(surface, (201, 179, 128), 4, 12, 8, 6)
    _rect(surface, (232, 215, 174), 5, 12, 6, 4)
    _rect(surface, (177, 145, 91), 4, 16, 8, 2)
    _rect(surface, PALETTE["gold"], 7, 16, 2, 2)
    _rect(surface, (129, 87, 53), 2, 13, 2, 4)
    _rect(surface, (129, 87, 53), 12, 13, 2, 4)

    # Short trousers, striped leggings, and sturdy boots.
    _rect(surface, (92, 94, 78), 5, 18, 6, 2)
    _rect(surface, (67, 69, 63), 5, 20, 2, 2)
    _rect(surface, (67, 69, 63), 9, 20, 2, 2)
    _rect(surface, (119, 83, 57), 4, 22, 4, 2)
    _rect(surface, (119, 83, 57), 9, 22, 4, 2)
    _rect(surface, (177, 125, 72), 4, 22, 4, 1)
    _rect(surface, (177, 125, 72), 9, 22, 4, 1)

    # The sword sits at the hero's side; its blade changes with the equipped weapon.
    blade = (232, 239, 226) if weapon == "silver_sword" else (177, 193, 189)
    _rect(surface, PALETTE["metal"], 1, 12, 1, 5)
    _rect(surface, blade, 1, 11, 1, 5)
    _rect(surface, PALETTE["gold"], 0, 16, 3, 1)
    _rect(surface, PALETTE["boot"], 1, 17, 1, 3)

    # The torso changes visibly when armor is equipped.
    if armor == "leather_armor":
        _rect(surface, (126, 77, 45), 4, 13, 8, 4)
        _rect(surface, (171, 111, 59), 5, 13, 6, 1)
        _rect(surface, PALETTE["gold"], 7, 15, 2, 1)
        _rect(surface, (83, 55, 39), 4, 17, 8, 1)
    elif armor == "chainmail":
        _rect(surface, (134, 145, 147), 4, 13, 8, 4)
        _rect(surface, (90, 103, 111), 4, 14, 8, 1)
        _rect(surface, (177, 188, 182), 5, 13, 2, 1)
        _rect(surface, (177, 188, 182), 9, 13, 2, 1)
        _rect(surface, PALETTE["gold"], 7, 16, 2, 2)
    return surface
    return surface


def _slime():
    surface = _canvas()
    body = [(2, 10), (2, 7), (3, 4), (5, 2), (11, 2), (13, 4),
            (14, 7), (14, 10), (12, 12), (4, 12)]
    pygame.draw.polygon(surface, PALETTE["slime"], body)
    _rect(surface, PALETTE["slime_light"], 5, 4, 3, 1)
    _rect(surface, PALETTE["slime_light"], 4, 5, 2, 1)
    _rect(surface, PALETTE["slime_dark"], 4, 11, 8, 1)
    _rect(surface, PALETTE["white"], 5, 7, 2, 2)
    _rect(surface, PALETTE["white"], 10, 7, 2, 2)
    _rect(surface, PALETTE["ink"], 6, 8, 1, 1)
    _rect(surface, PALETTE["ink"], 11, 8, 1, 1)
    return surface


def _chest(opened=False):
    surface = _canvas()
    _rect(surface, PALETTE["wood"], 2, 5, 12, 9)
    _rect(surface, PALETTE["wood_light"], 3, 6, 10, 2)
    _rect(surface, PALETTE["wood"], 3, 8, 10, 5)
    _rect(surface, PALETTE["gold"], 2, 8, 12, 1)
    _rect(surface, PALETTE["gold"], 7, 8, 2, 4)
    _rect(surface, PALETTE["stone_dark"], 3, 13, 10, 1)
    if opened:
        _rect(surface, PALETTE["wood"], 2, 3, 12, 3)
        _rect(surface, PALETTE["wood_light"], 3, 3, 10, 1)
        _rect(surface, PALETTE["gold"], 3, 5, 10, 1)
        _rect(surface, PALETTE["ink"], 4, 9, 8, 2)
    else:
        _rect(surface, PALETTE["wood_light"], 3, 4, 10, 2)
        _rect(surface, PALETTE["wood"], 3, 3, 10, 2)
        _rect(surface, PALETTE["gold"], 7, 5, 2, 3)
    return surface


def _grass(variant):
    surface = _canvas()
    base = PALETTE["grass"] if variant % 2 == 0 else PALETTE["grass_dark"]
    surface.fill(base)
    rng = random.Random(variant + 431)
    accents = (PALETTE["grass_dark"], PALETTE["grass_light"], PALETTE["grass_gold"])
    for _ in range(5):
        x, y = rng.randrange(16), rng.randrange(16)
        surface.set_at((x, y), accents[rng.randrange(len(accents))])
    # Short, two pixel blades read as tufts instead of smooth noise.
    for x, y in ((2, 3), (11, 12), (6, 8)):
        if (x + y + variant) % 2 == 0:
            _rect(surface, PALETTE["grass_light"], x, y, 1, 2)
    return surface


def _dirt():
    surface = _canvas()
    surface.fill(PALETTE["dirt"])
    rng = random.Random(820)
    for _ in range(8):
        x, y = rng.randrange(16), rng.randrange(16)
        color = PALETTE["dirt_light"] if (x + y) % 2 else PALETTE["dirt_dark"]
        _rect(surface, color, x, y, rng.choice((1, 2)), 1)
    _rect(surface, PALETTE["dirt_dark"], 0, 15, 16, 1)
    return surface


def _stone():
    surface = _canvas()
    surface.fill(PALETTE["stone_dark"])
    for y, offset in ((1, 0), (6, 3), (11, 0)):
        for x in range(offset, 16, 8):
            _rect(surface, PALETTE["stone"], x, y, 7, 4)
            _rect(surface, PALETTE["stone_light"], x, y, 6, 1)
            _rect(surface, (83, 81, 94), x, y + 3, 7, 1)
    return surface


def _flower(color):
    surface = _canvas()
    _rect(surface, PALETTE["grass_dark"], 7, 8, 2, 4)
    _rect(surface, color, 6, 5, 4, 3)
    _rect(surface, PALETTE["white"], 7, 4, 2, 1)
    _rect(surface, PALETTE["gold"], 7, 6, 2, 1)
    return surface


def _torch():
    surface = _canvas()
    _rect(surface, PALETTE["boot"], 7, 7, 2, 7)
    _rect(surface, PALETTE["gold"], 6, 5, 4, 3)
    _rect(surface, (226, 111, 54), 7, 3, 2, 4)
    _rect(surface, (248, 217, 118), 7, 4, 1, 2)
    return surface


def _roof():
    surface = _canvas()
    surface.fill((76, 41, 38))
    for y in (2, 7, 12):
        _rect(surface, PALETTE["roof"], 0, y, 16, 4)
        for x in (2, 8, 14):
            _rect(surface, PALETTE["roof_light"], x, y, 2, 1)
    return surface


def _dungeon_floor(variant):
    surface = _canvas()
    surface.fill((64 + variant % 2 * 5, 64, 70))
    rng = random.Random(variant + 175)
    for _ in range(6):
        x, y = rng.randrange(16), rng.randrange(16)
        _rect(surface, (83, 82, 84), x, y, rng.choice((1, 2)), 1)
    _rect(surface, (53, 53, 61), 0, 15, 16, 1)
    return surface


def _stairs():
    surface = _canvas()
    surface.fill((53, 53, 61))
    for row in range(5):
        _rect(surface, (100 + row * 5, 99 + row * 4, 101 + row * 3), 2 + row, 3 + row * 2, 12 - row * 2, 2)
        _rect(surface, PALETTE["stone_light"], 2 + row, 3 + row * 2, 12 - row * 2, 1)
    return surface


def _well():
    surface = _canvas()
    _rect(surface, PALETTE["stone_dark"], 2, 5, 12, 9)
    _rect(surface, PALETTE["stone_light"], 2, 5, 12, 2)
    _rect(surface, (37, 68, 80), 4, 8, 8, 4)
    _rect(surface, PALETTE["wood"], 4, 2, 2, 4)
    _rect(surface, PALETTE["wood"], 10, 2, 2, 4)
    _rect(surface, PALETTE["wood_light"], 4, 1, 8, 1)
    _rect(surface, PALETTE["wood"], 7, 2, 2, 4)
    return surface


def _shopkeeper():
    surface = _canvas()
    _rect(surface, (65, 45, 35), 4, 2, 8, 3)
    _rect(surface, (141, 89, 55), 3, 4, 10, 2)
    _rect(surface, PALETTE["skin"], 5, 5, 6, 4)
    _rect(surface, PALETTE["ink"], 6, 6, 1, 1)
    _rect(surface, PALETTE["ink"], 9, 6, 1, 1)
    _rect(surface, (80, 111, 67), 3, 9, 10, 5)
    _rect(surface, PALETTE["gold"], 6, 9, 4, 1)
    _rect(surface, PALETTE["boot"], 4, 14, 3, 2)
    _rect(surface, PALETTE["boot"], 9, 14, 3, 2)
    return surface


def _villager():
    surface = _shopkeeper()
    for y in range(16):
        for x in range(16):
            if tuple(surface.get_at((x, y))[:3]) == (80, 111, 67):
                surface.set_at((x, y), (66, 91, 132))
    _rect(surface, PALETTE["gold"], 6, 11, 4, 1)
    return surface


def _skeleton():
    surface = _canvas()
    _rect(surface, PALETTE["bone"], 5, 2, 6, 5)
    _rect(surface, PALETTE["ink"], 6, 4, 1, 1)
    _rect(surface, PALETTE["ink"], 9, 4, 1, 1)
    _rect(surface, PALETTE["bone"], 7, 7, 2, 5)
    _rect(surface, PALETTE["bone"], 4, 8, 8, 2)
    _rect(surface, PALETTE["bone"], 4, 10, 2, 4)
    _rect(surface, PALETTE["bone"], 10, 10, 2, 4)
    _rect(surface, (143, 66, 54), 3, 6, 1, 6)
    _rect(surface, (143, 66, 54), 2, 5, 3, 2)
    return surface


def sprite(name, size=(32, 32)):
    """Return a cached pixel sprite, enlarged with nearest-neighbor sampling."""
    if name not in _BASE:
        builders = {
            "player": _player,
            "slime": _slime,
            "chest": lambda: _chest(False),
            "chest_open": lambda: _chest(True),
            "grass_0": lambda: _grass(0),
            "grass_1": lambda: _grass(1),
            "grass_2": lambda: _grass(2),
            "grass_3": lambda: _grass(3),
            "dirt": _dirt,
            "stone": _stone,
            "flower_yellow": lambda: _flower(PALETTE["gold"]),
            "flower_red": lambda: _flower((221, 101, 94)),
            "torch": _torch,
            "roof": _roof,
            "dungeon_floor_0": lambda: _dungeon_floor(0),
            "dungeon_floor_1": lambda: _dungeon_floor(1),
            "stairs": _stairs,
            "well": _well,
            "shopkeeper": _shopkeeper,
            "villager": _villager,
            "skeleton": _skeleton,
        }
        _BASE[name] = builders[name]()
    key = (name, tuple(size)) if size else (name, None)
    if key not in _SCALED:
        original = _BASE[name]
        _SCALED[key] = original.copy() if size is None else pygame.transform.scale(original, size)
    return _SCALED[key]


def hero_sprite(weapon="rusty_sword", armor="traveler_clothes", size=(32, 32)):
    """Return the player sprite with the currently equipped gear visible."""
    key = (weapon, armor, tuple(size))
    if key not in _HERO_SCALED:
        _HERO_SCALED[key] = pygame.transform.scale(_player(weapon, armor), size)
    return _HERO_SCALED[key]

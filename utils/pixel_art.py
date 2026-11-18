"""Small hand-drawn pixel sprites rendered from a 16x16 pixel grid."""

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


def _canvas(size=(16, 16)):
    return pygame.Surface(size, pygame.SRCALPHA)


def _rect(surface, color, x, y, width, height=1):
    pygame.draw.rect(surface, color, pygame.Rect(x, y, width, height))


def _player():
    surface = _canvas()
    rows = (
        "....HHHHHHHH....",
        "...HHHHHHHHHH...",
        "..HHHHHHHHHHHH..",
        "..HHSSSSSSSSHH..",
        "..HSSSSSSSSSSH..",
        "..HSSSESSSESSH..",
        "...SSSSSSSSSS...",
        "...SSSWWSSSS....",
        "...BBBBBBBB....",
        "..BBBBBBBBBB..",
        "..BBBBYYBBBB..",
        "...BB....BB...",
        "...PP....PP...",
        "...PP....PP...",
        "...KK....KK...",
        "...KK....KK...",
    )
    colors = {
        "H": PALETTE["hair"], "S": PALETTE["skin"], "E": PALETTE["ink"],
        "B": PALETTE["blue"], "W": PALETTE["white"], "Y": PALETTE["gold"],
        "P": PALETTE["pants"], "K": PALETTE["boot"],
    }
    for y, row in enumerate(rows):
        offset = (16 - len(row)) // 2
        for x, pixel in enumerate(row):
            if pixel in colors:
                surface.set_at((x + offset, y), colors[pixel])
    # Hair shine, cheek, and sleeve details form deliberate pixel clusters.
    _rect(surface, PALETTE["hair_light"], 5, 2, 4)
    _rect(surface, PALETTE["skin_shadow"], 11, 6, 1)
    _rect(surface, PALETTE["blue_light"], 4, 9, 2, 2)
    _rect(surface, PALETTE["blue_dark"], 10, 10, 2, 1)
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
        }
        _BASE[name] = builders[name]()
    key = (name, tuple(size)) if size else (name, None)
    if key not in _SCALED:
        original = _BASE[name]
        _SCALED[key] = original.copy() if size is None else pygame.transform.scale(original, size)
    return _SCALED[key]

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


def _player(weapon="rusty_sword", armor="traveler_clothes", direction="down", frame=0):
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
    if frame % 2:
        surface.fill((0, 0, 0, 0), pygame.Rect(4, 19, 10, 5))
        _rect(surface, (92, 94, 78), 5, 18, 6, 2)
        _rect(surface, (67, 69, 63), 4, 20, 2, 2)
        _rect(surface, (67, 69, 63), 10, 19, 2, 2)
        _rect(surface, (119, 83, 57), 2, 22, 5, 2)
        _rect(surface, (119, 83, 57), 10, 21, 4, 2)
        _rect(surface, (177, 125, 72), 2, 22, 5, 1)
        _rect(surface, (177, 125, 72), 10, 21, 4, 1)
    if direction == "up":
        _rect(surface, PALETTE["hair"], 3, 5, 10, 7)
        _rect(surface, PALETTE["hair_light"], 4, 5, 3, 1)
        _rect(surface, PALETTE["hair"], 2, 8, 2, 3)
        _rect(surface, PALETTE["hair"], 12, 8, 2, 3)
    elif direction in ("left", "right"):
        surface.fill((0, 0, 0, 0), pygame.Rect(2, 2, 13, 10))
        _rect(surface, PALETTE["hair"], 4, 3, 8, 5)
        _rect(surface, PALETTE["hair"], 3, 6, 5, 6)
        _rect(surface, PALETTE["hair_light"], 5, 4, 4, 1)
        _rect(surface, PALETTE["skin"], 8, 7, 5, 5)
        _rect(surface, PALETTE["skin_shadow"], 7, 8, 2, 3)
        _rect(surface, PALETTE["hair"], 9, 6, 4, 2)
        _rect(surface, PALETTE["ink"], 11, 9, 1, 2)
        _rect(surface, PALETTE["skin_shadow"], 13, 9, 1, 2)
        _rect(surface, PALETTE["skin_shadow"], 9, 11, 3, 1)
        if direction == "left":
            surface = pygame.transform.flip(surface, True, False)
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
    for _ in range(28):
        x, y = rng.randrange(16), rng.randrange(16)
        surface.set_at((x, y), accents[rng.randrange(len(accents))])
    # Short, two pixel blades read as tufts instead of smooth noise.
    for x, y in ((2, 3), (11, 12), (6, 8)):
        if (x + y + variant) % 2 == 0:
            _rect(surface, PALETTE["grass_light"], x, y, 1, 2)
    return surface


def _path(variant=0):
    surface = _canvas()
    surface.fill((132, 91, 57))
    rng = random.Random(variant + 944)
    for _ in range(34):
        x, y = rng.randrange(16), rng.randrange(16)
        color = rng.choice(((154, 109, 68), (111, 75, 51), (174, 128, 80), (126, 84, 55)))
        _rect(surface, color, x, y, rng.choice((1, 1, 2)), 1)
    _rect(surface, (100, 69, 48), 0, 15, 16, 1)
    return surface


def _water(variant=0):
    surface = _canvas()
    surface.fill((48, 111, 132))
    rng = random.Random(variant + 325)
    for _ in range(13):
        x, y = rng.randrange(16), rng.randrange(16)
        _rect(surface, rng.choice(((58, 134, 148), (76, 150, 157), (37, 96, 125))), x, y, rng.choice((1, 2, 3)), 1)
    for x, y in ((2, 3), (9, 8), (5, 13)):
        _rect(surface, (129, 187, 178), x, y, 2, 1)
    return surface


def _terrain_overlay(mask, water=False, variant=0):
    """Transparent, connected pixel patch for organic trail and shoreline edges."""
    surface = _canvas()
    if water:
        fill = (48, 111, 132)
        accents = ((58, 134, 148), (76, 150, 157), (37, 96, 125))
    else:
        fill = (132, 91, 57)
        accents = ((154, 109, 68), (111, 75, 51), (174, 128, 80))
    pygame.draw.ellipse(surface, fill, (0, 0, 16, 16))
    if mask & 1:
        _rect(surface, fill, 4, 0, 8, 9)
    if mask & 2:
        _rect(surface, fill, 7, 4, 9, 8)
    if mask & 4:
        _rect(surface, fill, 4, 7, 8, 9)
    if mask & 8:
        _rect(surface, fill, 0, 4, 9, 8)
    if mask & 16:
        pygame.draw.polygon(surface, fill, ((8, 0), (16, 0), (16, 8)))
    if mask & 32:
        pygame.draw.polygon(surface, fill, ((8, 16), (16, 8), (16, 16)))
    if mask & 64:
        pygame.draw.polygon(surface, fill, ((0, 8), (8, 16), (0, 16)))
    if mask & 128:
        pygame.draw.polygon(surface, fill, ((0, 0), (8, 0), (0, 8)))
    rng = random.Random(mask * 101 + variant + (550 if water else 0))
    for _ in range(9):
        x, y = rng.randrange(1, 15), rng.randrange(1, 15)
        if surface.get_at((x, y)).a:
            _rect(surface, rng.choice(accents), x, y, rng.choice((1, 2)), 1)
    if water:
        _rect(surface, (139, 190, 176), 5, 5, 2, 1)
        _rect(surface, (119, 176, 166), 10, 10, 2, 1)
    return surface


def _tree():
    """Layered broadleaf tree, with a transparent shadow and pixel highlights."""
    surface = _canvas((24, 32))
    _rect(surface, (36, 67, 41, 100), 3, 26, 18, 4)
    _rect(surface, (96, 66, 43), 10, 18, 5, 12)
    _rect(surface, (145, 97, 52), 11, 20, 2, 7)
    for x, y, w, h, color in (
        (4, 7, 16, 12, (31, 87, 49)), (2, 10, 20, 11, (43, 113, 58)),
        (5, 4, 14, 14, (56, 136, 66)), (7, 2, 10, 7, (82, 158, 74)),
        (3, 13, 7, 6, (37, 101, 53)), (14, 12, 7, 7, (34, 99, 51)),
    ):
        _rect(surface, color, x, y, w, h)
    for x, y in ((7, 4), (10, 7), (15, 5), (5, 11), (12, 12), (17, 10), (8, 15)):
        _rect(surface, (112, 177, 83), x, y, 2, 2)
    for x, y in ((10, 9), (15, 13), (5, 14)):
        _rect(surface, (220, 192, 94), x, y, 1, 1)
    return surface


def _rock():
    surface = _canvas()
    points = [(2, 12), (3, 7), (6, 5), (7, 2), (12, 3), (14, 7), (14, 12), (11, 14), (4, 14)]
    pygame.draw.polygon(surface, (81, 91, 92), points)
    _rect(surface, (140, 150, 139), 6, 5, 5, 2)
    _rect(surface, (104, 119, 117), 4, 8, 8, 2)
    _rect(surface, (57, 69, 74), 4, 12, 8, 2)
    return surface


def _portal(kind="dungeon", frame=0):
    """Small overgrown stone gateway with a distinct warm or enchanted opening."""
    surface = _canvas((24, 32))
    _rect(surface, (30, 48, 38, 110), 1, 28, 22, 3)
    # Threshold stones and the dark doorway sit behind the arch blocks.
    _rect(surface, (40, 48, 48), 7, 10, 10, 18)
    if kind == "town":
        glow = (133, 96, 52)
        glow_light = (235, 190, 99)
        stone = (112, 112, 91)
    else:
        glow = (44, 104, 119)
        glow_light = (99, 211, 194)
        stone = (96, 110, 107)
    _rect(surface, glow, 9, 15, 6, 13)
    _rect(surface, glow_light, 9 + frame % 2, 15, 1, 9)
    _rect(surface, (142, 146, 126), 3, 27, 18, 2)
    _rect(surface, (110, 115, 106), 2, 23, 5, 5)
    _rect(surface, stone, 3, 11, 4, 15)
    _rect(surface, (136, 146, 131), 3, 12, 2, 10)
    _rect(surface, stone, 17, 11, 4, 15)
    _rect(surface, (65, 80, 76), 19, 13, 2, 10)
    _rect(surface, stone, 5, 7, 14, 5)
    _rect(surface, (137, 145, 129), 7, 5, 10, 4)
    _rect(surface, (152, 157, 133), 9, 3, 6, 3)
    _rect(surface, (42, 79, 48), 2, 15, 2, 8)
    _rect(surface, (54, 101, 56), 19, 17, 2, 7)
    _rect(surface, (104, 161, 76), 2, 16, 2, 2)
    _rect(surface, (115, 168, 82), 19, 19, 2, 2)
    _rect(surface, glow_light, 10 + frame % 2, 10, 2, 1)
    return surface


def _chief():
    surface = _canvas()
    _rect(surface, (225, 217, 189), 4, 2, 8, 4)
    _rect(surface, (237, 220, 177), 5, 5, 6, 5)
    _rect(surface, (250, 235, 201), 6, 5, 4, 2)
    _rect(surface, PALETTE["ink"], 6, 7, 1, 1)
    _rect(surface, PALETTE["ink"], 9, 7, 1, 1)
    _rect(surface, (235, 234, 218), 6, 9, 4, 3)
    _rect(surface, (61, 76, 108), 3, 11, 10, 4)
    _rect(surface, (89, 109, 140), 5, 11, 6, 4)
    _rect(surface, PALETTE["gold"], 7, 11, 2, 4)
    _rect(surface, PALETTE["boot"], 4, 15, 3, 1)
    _rect(surface, PALETTE["boot"], 9, 15, 3, 1)
    return surface


def _old_knight():
    """Retired knight Garen: grey hair and beard, dented cuirass and a faded red cape."""
    surface = _canvas()
    _rect(surface, (122, 36, 38), 3, 8, 10, 7)
    _rect(surface, (186, 184, 176), 4, 1, 8, 3)
    _rect(surface, (160, 158, 150), 3, 3, 2, 4)
    _rect(surface, (160, 158, 150), 11, 3, 2, 4)
    _rect(surface, PALETTE["skin"], 5, 3, 6, 4)
    _rect(surface, PALETTE["skin_shadow"], 5, 6, 6, 1)
    _rect(surface, PALETTE["ink"], 6, 4, 1, 1)
    _rect(surface, PALETTE["ink"], 9, 4, 1, 1)
    _rect(surface, (214, 212, 204), 5, 6, 6, 3)
    _rect(surface, (186, 184, 176), 7, 9, 2, 1)
    _rect(surface, (128, 138, 142), 4, 9, 8, 5)
    _rect(surface, (176, 186, 186), 5, 9, 3, 4)
    _rect(surface, PALETTE["gold"], 7, 11, 2, 1)
    _rect(surface, (92, 64, 44), 4, 13, 8, 1)
    _rect(surface, PALETTE["pants"], 5, 14, 2, 1)
    _rect(surface, PALETTE["pants"], 9, 14, 2, 1)
    _rect(surface, PALETTE["boot"], 4, 15, 3, 1)
    _rect(surface, PALETTE["boot"], 9, 15, 3, 1)
    return surface


def _merchant():
    """Wandering merchant Toby: wide travel hat, green scarf, an overstuffed pack and a walking staff."""
    surface = _canvas()
    # Backpack bulging out behind both shoulders, with a bedroll on top.
    _rect(surface, (112, 74, 46), 1, 6, 14, 7)
    _rect(surface, (146, 100, 60), 2, 7, 12, 5)
    _rect(surface, (176, 160, 120), 2, 4, 12, 2)
    _rect(surface, (138, 122, 88), 2, 5, 12, 1)
    _rect(surface, (204, 72, 60), 2, 4, 1, 2)
    _rect(surface, (204, 72, 60), 13, 4, 1, 2)
    # Wide-brimmed hat with a feather.
    _rect(surface, (98, 64, 40), 3, 2, 10, 1)
    _rect(surface, (122, 82, 50), 5, 0, 6, 2)
    _rect(surface, (176, 58, 50), 5, 1, 6, 1)
    _rect(surface, (238, 220, 150), 11, 0, 2, 1)
    # Face and grin.
    _rect(surface, PALETTE["skin"], 5, 3, 6, 4)
    _rect(surface, PALETTE["ink"], 6, 4, 1, 1)
    _rect(surface, PALETTE["ink"], 9, 4, 1, 1)
    _rect(surface, PALETTE["skin_shadow"], 7, 6, 2, 1)
    # Green scarf, travel coat, belt pouch and walking staff.
    _rect(surface, (70, 140, 86), 4, 7, 8, 2)
    _rect(surface, (108, 92, 64), 4, 9, 8, 5)
    _rect(surface, (138, 118, 82), 5, 9, 2, 4)
    _rect(surface, (64, 44, 34), 4, 12, 8, 1)
    _rect(surface, PALETTE["gold"], 9, 12, 2, 2)
    _rect(surface, (120, 84, 50), 14, 3, 1, 12)
    _rect(surface, (164, 120, 70), 14, 2, 1, 1)
    _rect(surface, PALETTE["pants"], 5, 14, 2, 1)
    _rect(surface, PALETTE["pants"], 9, 14, 2, 1)
    _rect(surface, PALETTE["boot"], 4, 15, 3, 1)
    _rect(surface, PALETTE["boot"], 9, 15, 3, 1)
    return surface


def _fountain():
    surface = _canvas((16, 24))
    _rect(surface, (48, 62, 70), 2, 15, 12, 8)
    _rect(surface, (135, 143, 134), 2, 15, 12, 2)
    _rect(surface, (73, 130, 152), 4, 17, 8, 3)
    _rect(surface, (105, 190, 193), 5, 17, 5, 1)
    _rect(surface, (153, 165, 146), 6, 12, 4, 4)
    _rect(surface, (113, 140, 139), 7, 9, 2, 4)
    _rect(surface, (83, 181, 193), 7, 6, 2, 4)
    _rect(surface, (244, 207, 107), 7, 2, 2, 4)
    _rect(surface, (255, 245, 190), 7, 1, 2, 2)
    _rect(surface, (232, 195, 92), 4, 7, 2, 2)
    _rect(surface, (232, 195, 92), 10, 7, 2, 2)
    return surface


def _altar(kind):
    surface = _canvas()
    colors = {
        "wind": ((119, 150, 157), (179, 226, 214)),
        "earth": ((123, 114, 91), (212, 184, 122)),
        "fire": ((137, 76, 54), (251, 163, 68)),
    }
    stone, seal = colors[kind]
    _rect(surface, (51, 68, 57, 120), 2, 13, 12, 2)
    _rect(surface, stone, 3, 6, 10, 8)
    _rect(surface, (174, 159, 123), 4, 5, 8, 2)
    _rect(surface, stone, 6, 3, 4, 4)
    _rect(surface, seal, 7, 6, 2, 5)
    _rect(surface, (242, 225, 167), 7, 7, 1, 2)
    _rect(surface, seal, 4, 10, 2, 1)
    _rect(surface, seal, 10, 10, 2, 1)
    return surface


def _dark_knight():
    surface = _canvas((16, 24))
    _rect(surface, (40, 36, 48), 2, 5, 12, 14)
    _rect(surface, (77, 67, 76), 4, 3, 8, 6)
    _rect(surface, (28, 30, 39), 5, 5, 6, 4)
    _rect(surface, (221, 96, 75), 6, 7, 2, 1)
    _rect(surface, (221, 96, 75), 9, 7, 2, 1)
    _rect(surface, (103, 32, 41), 1, 9, 4, 11)
    _rect(surface, (72, 28, 42), 11, 10, 4, 10)
    _rect(surface, (109, 116, 119), 5, 10, 6, 7)
    _rect(surface, (65, 74, 83), 4, 11, 2, 5)
    _rect(surface, (65, 74, 83), 10, 11, 2, 5)
    _rect(surface, (167, 52, 45), 7, 11, 2, 4)
    _rect(surface, (106, 119, 128), 2, 12, 2, 5)
    _rect(surface, (106, 119, 128), 12, 12, 2, 5)
    _rect(surface, (184, 191, 184), 3, 12, 1, 4)
    _rect(surface, (184, 191, 184), 12, 11, 1, 5)
    _rect(surface, (62, 67, 72), 5, 18, 2, 4)
    _rect(surface, (62, 67, 72), 9, 18, 2, 4)
    _rect(surface, PALETTE["boot"], 4, 22, 4, 2)
    _rect(surface, PALETTE["boot"], 9, 22, 4, 2)
    _rect(surface, (174, 189, 188), 13, 13, 1, 7)
    _rect(surface, (224, 224, 201), 13, 10, 1, 4)
    _rect(surface, (167, 52, 45), 1, 4, 2, 5)
    _rect(surface, (167, 52, 45), 13, 4, 2, 5)
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
    if name not in _BASE and name.startswith(("trail_", "water_edge_")):
        parts = name.split("_")
        mask, variant = int(parts[-2]), int(parts[-1])
        _BASE[name] = _terrain_overlay(mask, name.startswith("water_edge_"), variant)
    elif name not in _BASE and name.startswith("grass_"):
        _BASE[name] = _grass(int(name.rsplit("_", 1)[1]))
    if name not in _BASE:
        builders = {
            "player": _player,
            "slime": _slime,
            "chest": lambda: _chest(False),
            "chest_open": lambda: _chest(True),
            "path": lambda: _path(0),
            "path_0": lambda: _path(0),
            "path_1": lambda: _path(1),
            "path_2": lambda: _path(2),
            "water": lambda: _water(0),
            "water_0": lambda: _water(0),
            "water_1": lambda: _water(1),
            "tree": _tree,
            "rock": _rock,
            "portal_town": lambda: _portal("town"),
            "portal_dungeon": lambda: _portal("dungeon"),
            "portal_dungeon_0": lambda: _portal("dungeon", 0),
            "portal_dungeon_1": lambda: _portal("dungeon", 1),
            "chief": _chief,
            "old_knight": _old_knight,
            "merchant": _merchant,
            "star_fountain": _fountain,
            "altar_wind": lambda: _altar("wind"),
            "altar_earth": lambda: _altar("earth"),
            "altar_fire": lambda: _altar("fire"),
            "dark_knight": _dark_knight,
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


def hero_sprite(weapon="rusty_sword", armor="traveler_clothes", size=(32, 32), direction="down", frame=0):
    """Return the player sprite with the currently equipped gear visible."""
    key = (weapon, armor, tuple(size), direction, frame % 2)
    if key not in _HERO_SCALED:
        _HERO_SCALED[key] = pygame.transform.scale(_player(weapon, armor, direction, frame), size)
    return _HERO_SCALED[key]

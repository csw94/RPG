"""Hand-drawn pixel sprites, including the taller 16x24 hero sprite."""

import math
import random
import pygame


PALETTE = {
    # Cozy, slightly warm greens (Stardew-like) instead of the older cool forest tones.
    "grass": (110, 168, 82),
    "grass_dark": (84, 140, 68),
    "grass_deep": (66, 116, 62),
    "grass_light": (146, 196, 98),
    "grass_gold": (204, 204, 112),
    "path": (200, 156, 104),
    "path_light": (222, 184, 130),
    "path_dark": (172, 128, 84),
    "path_rim": (138, 100, 70),
    "outline": (54, 40, 46),
    "leaf_dark": (52, 108, 66),
    "leaf": (78, 146, 76),
    "leaf_light": (128, 186, 90),
    "leaf_glint": (186, 220, 120),
    "bark": (110, 72, 50),
    "bark_light": (150, 104, 66),
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

def tile_noise(x, y, seed=0):
    """Deterministic, pattern-free value in [0, 1) for a map tile (no visible stripes)."""
    h = (x * 73856093) ^ (y * 19349663) ^ (seed * 83492791)
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536


NPC_SIZE = (32, 48)  # NPCs share the hero's 16x24 chibi proportions, drawn at 2x.

_BASE = {}
_SCALED = {}
_HERO_SCALED = {}


def _canvas(size=(16, 16)):
    return pygame.Surface(size, pygame.SRCALPHA)


def _rect(surface, color, x, y, width, height=1):
    pygame.draw.rect(surface, color, pygame.Rect(x, y, width, height))


HERO = {
    "mantle": (56, 91, 66), "mantle_light": (89, 124, 78), "mantle_dark": (42, 70, 52),
    "tunic": (201, 179, 128), "tunic_light": (232, 215, 174), "belt": (177, 145, 91),
    "arm": (129, 87, 53), "trousers": (92, 94, 78), "legging": (67, 69, 63),
    "legging_far": (50, 52, 48), "boot": (119, 83, 57), "boot_light": (177, 125, 72),
    "boot_far": (90, 63, 45),
}


def walk_frame(clock):
    """Map a walk clock (steps taken) to a pose: 0 stand, 1 left step, 2 stand, 3 right step."""
    return int(clock) % 4 if clock else 0


def _hero_head(s, direction):
    hair, light, skin, shade, ink = (PALETTE[k] for k in ("hair", "hair_light", "skin", "skin_shadow", "ink"))
    if direction == "down":
        _rect(s, hair, 4, 1, 8, 2)
        _rect(s, hair, 2, 3, 12, 2)
        _rect(s, hair, 1, 5, 14, 3)
        _rect(s, hair, 2, 7, 3, 4)
        _rect(s, hair, 11, 7, 3, 4)
        _rect(s, skin, 4, 5, 8, 7)
        _rect(s, shade, 3, 7, 1, 3)
        _rect(s, shade, 12, 7, 1, 3)
        _rect(s, light, 3, 3, 4, 1)
        _rect(s, light, 9, 4, 3, 1)
        _rect(s, hair, 4, 6, 3, 2)
        _rect(s, hair, 9, 6, 3, 2)
        _rect(s, skin, 5, 7, 6, 4)
        _rect(s, ink, 6, 8, 1, 2)
        _rect(s, ink, 9, 8, 1, 2)
        _rect(s, (220, 126, 113), 5, 10, 1, 1)
        _rect(s, (220, 126, 113), 10, 10, 1, 1)
        _rect(s, shade, 7, 11, 2, 1)
    elif direction == "up":
        _rect(s, hair, 4, 1, 8, 2)
        _rect(s, hair, 2, 3, 12, 2)
        _rect(s, hair, 1, 5, 14, 3)
        _rect(s, hair, 2, 8, 12, 3)
        _rect(s, hair, 4, 11, 8, 1)
        _rect(s, light, 4, 2, 4, 1)
        _rect(s, light, 3, 4, 3, 1)
        _rect(s, light, 9, 5, 3, 1)
        _rect(s, PALETTE["hair"], 7, 9, 2, 2)
        _rect(s, shade, 1, 8, 1, 2)
        _rect(s, shade, 14, 8, 1, 2)
    else:  # drawn facing right; "left" is mirrored afterwards
        _rect(s, hair, 4, 1, 8, 2)
        _rect(s, hair, 3, 3, 10, 4)
        _rect(s, hair, 3, 6, 5, 6)
        _rect(s, light, 5, 4, 4, 1)
        _rect(s, skin, 8, 7, 5, 5)
        _rect(s, shade, 7, 8, 2, 3)
        _rect(s, hair, 9, 6, 4, 2)
        _rect(s, ink, 11, 9, 1, 2)
        _rect(s, shade, 13, 9, 1, 2)
        _rect(s, shade, 9, 11, 3, 1)


def _hero_torso(s, direction, frame, weapon, armor):
    c = HERO
    swing = {1: -1, 3: 1}.get(frame, 0)  # arms swing opposite to the stepping leg
    blade = {"silver_sword": (232, 239, 226), "steel_longsword": (206, 216, 216), "wind_dagger": (168, 226, 196),
             "earth_hammer": (176, 150, 112), "flame_blade": (244, 150, 96),
             "star_sword": (252, 238, 156)}.get(weapon, (177, 193, 189))
    if direction == "down":
        _rect(s, c["mantle"], 2, 12, 12, 6)
        _rect(s, c["tunic"], 4, 12, 8, 6)
        _rect(s, c["tunic_light"], 5, 12, 6, 4)
        _rect(s, c["belt"], 4, 16, 8, 2)
        _rect(s, PALETTE["gold"], 7, 16, 2, 2)
        _rect(s, c["mantle_light"], 2, 13 + swing, 2, 4)
        _rect(s, c["arm"], 2, 13 + swing, 2, 4)
        _rect(s, c["mantle_light"], 12, 13 - swing, 2, 4)
        _rect(s, c["arm"], 12, 13 - swing, 2, 4)
        _rect(s, PALETTE["metal"], 1, 12 + swing, 1, 5)
        _rect(s, blade, 1, 11 + swing, 1, 5)
        _rect(s, PALETTE["gold"], 0, 16 + swing, 3, 1)
        _rect(s, PALETTE["boot"], 1, 17 + swing, 1, 3)
        if armor == "leather_armor":
            _rect(s, (126, 77, 45), 4, 13, 8, 4)
            _rect(s, (171, 111, 59), 5, 13, 6, 1)
            _rect(s, PALETTE["gold"], 7, 15, 2, 1)
            _rect(s, (83, 55, 39), 4, 17, 8, 1)
        elif armor == "chainmail":
            _rect(s, (134, 145, 147), 4, 13, 8, 4)
            _rect(s, (90, 103, 111), 4, 14, 8, 1)
            _rect(s, (177, 188, 182), 5, 13, 2, 1)
            _rect(s, (177, 188, 182), 9, 13, 2, 1)
            _rect(s, PALETTE["gold"], 7, 16, 2, 2)
    elif direction == "up":
        _rect(s, PALETTE["metal"], 13, 9, 1, 3)        # hilt over the shoulder
        _rect(s, PALETTE["gold"], 12, 11, 3, 1)
        _rect(s, c["mantle"], 2, 12, 12, 6)
        _rect(s, c["mantle_light"], 3, 12, 10, 1)
        _rect(s, c["mantle_dark"], 5, 14, 1, 4)
        _rect(s, c["mantle_dark"], 10, 14, 1, 4)
        _rect(s, PALETTE["boot"], 11, 13, 3, 1)       # sword strap
        _rect(s, PALETTE["boot"], 9, 14, 2, 1)
        _rect(s, c["arm"], 1, 13 - swing, 2, 4)
        _rect(s, c["arm"], 13, 13 + swing, 2, 4)
        _rect(s, c["belt"], 3, 17, 10, 1)
    else:
        _rect(s, c["mantle"], 3, 12, 5, 6)             # cape trails behind
        _rect(s, c["mantle_dark"], 3, 15, 2, 3)
        _rect(s, PALETTE["metal"], 4, 15, 1, 4)        # sheathed sword at the far hip
        _rect(s, PALETTE["gold"], 3, 15, 3, 1)
        _rect(s, c["tunic"], 6, 12, 6, 6)
        _rect(s, c["tunic_light"], 7, 12, 4, 3)
        if armor == "leather_armor":
            _rect(s, (126, 77, 45), 6, 13, 6, 4)
        elif armor == "chainmail":
            _rect(s, (134, 145, 147), 6, 13, 6, 4)
            _rect(s, (90, 103, 111), 6, 14, 6, 1)
        _rect(s, c["belt"], 6, 16, 6, 2)
        _rect(s, PALETTE["gold"], 10, 16, 1, 2)
        _rect(s, c["arm"], 8 + swing, 13, 2, 4)
        _rect(s, PALETTE["skin"], 8 + swing, 16, 2, 1)


def _hero_legs(s, direction, frame):
    c = HERO
    _rect(s, c["trousers"], 5, 18, 6, 2)
    if direction in ("down", "up"):
        for side, x, bx in (("left", 5, 4), ("right", 9, 9)):
            lifted = (frame == 1 and side == "left") or (frame == 3 and side == "right")
            top = 21 if lifted else 22
            _rect(s, c["legging"], x, 20, 2, top - 20)
            _rect(s, c["boot"], bx, top, 4, 2)
            if direction == "down":
                _rect(s, c["boot_light"], bx, top, 4, 1)
        return
    if frame in (1, 3):
        near_fwd = frame == 1
        front = ("legging", "boot") if near_fwd else ("legging_far", "boot_far")
        back = ("legging_far", "boot_far") if near_fwd else ("legging", "boot")
        _rect(s, c[back[0]], 5, 20, 2, 1)
        _rect(s, c[back[1]], 3, 21, 4, 2)
        _rect(s, c[front[0]], 9, 20, 2, 2)
        _rect(s, c[front[1]], 9, 22, 5, 2)
        _rect(s, c["boot_light"], 9 + (0 if near_fwd else 4), 22, 1, 1)
    else:
        _rect(s, c["legging"], 7, 20, 3, 2)
        _rect(s, c["boot"], 7, 22, 5, 2)
        _rect(s, c["boot_light"], 7, 22, 5, 1)


def _player(weapon="rusty_sword", armor="traveler_clothes", direction="down", frame=0):
    """Chibi adventurer (16x24) with front, back and side bodies and a 4-pose walk cycle.

    Frames: 0 stand, 1 left step, 2 stand, 3 right step. Steps lower the body by 1px.
    """
    frame %= 4
    side = direction in ("left", "right")
    upper = _canvas((16, 24))
    _hero_torso(upper, "right" if side else direction, frame, weapon, armor)
    _hero_head(upper, "right" if side else direction)
    surface = _canvas((16, 24))
    _hero_legs(surface, "right" if side else direction, frame)
    surface.blit(upper, (0, 1 if frame in (1, 3) else 0), pygame.Rect(0, 0, 16, 18))
    surface = _outline(surface)
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
    return _outline(surface)


def _tuft(surface, x, y, light=True):
    """A tiny 3x2 'v' of grass blades: lit tips over a shaded base."""
    tip = PALETTE["grass_light"] if light else PALETTE["grass_dark"]
    _rect(surface, tip, x, y, 1, 1)
    _rect(surface, tip, x + 2, y, 1, 1)
    _rect(surface, PALETTE["grass_dark"], x, y + 1, 3, 1)
    _rect(surface, PALETTE["grass_deep"], x + 1, y + 1, 1, 1)


def _grass(variant):
    """One shared base color for every variant, so the map never shows a checkerboard grid."""
    surface = _canvas()
    surface.fill(PALETTE["grass"])
    rng = random.Random(variant * 7919 + 431)
    # Soft mottling: small 2-pixel smudges, never single noisy dots.
    for _ in range(6):
        x, y = rng.randrange(15), rng.randrange(16)
        _rect(surface, PALETTE["grass_dark"] if rng.random() < 0.6 else PALETTE["grass_light"], x, y, 2, 1)
    for _ in range(rng.choice((1, 2, 2, 3))):
        _tuft(surface, rng.randrange(1, 13), rng.randrange(1, 14), rng.random() < 0.7)
    if variant % 5 == 0:
        fx, fy = rng.randrange(2, 14), rng.randrange(2, 14)
        surface.set_at((fx, fy), rng.choice(((250, 240, 210), (246, 206, 96), (236, 150, 160))))
    return surface


def _path(variant=0):
    surface = _canvas()
    surface.fill(PALETTE["path"])
    rng = random.Random(variant + 944)
    for _ in range(10):
        x, y = rng.randrange(15), rng.randrange(16)
        _rect(surface, rng.choice((PALETTE["path_light"], PALETTE["path_dark"])), x, y, rng.choice((1, 2)), 1)
    for _ in range(2):
        x, y = rng.randrange(1, 14), rng.randrange(1, 14)
        _rect(surface, PALETTE["path_light"], x, y, 2, 1)
        _rect(surface, PALETTE["path_rim"], x, y + 1, 2, 1)
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


def _terrain_overlay(mask, kind="path", variant=0):
    """Transparent, connected pixel patch for organic trail and shoreline edges."""
    surface = _canvas()
    water = kind == "water"
    if water:
        fill = (72, 140, 180)
        accents = ((96, 164, 200), (60, 124, 166), (112, 180, 210))
        rim = (206, 234, 236)
    elif kind == "lava":
        fill = (212, 88, 48)
        accents = ((240, 148, 64), (184, 64, 42), (248, 188, 92))
        rim = LAVA_RIM
    elif kind == "ice":
        fill = (170, 208, 230)
        accents = ((200, 228, 242), (146, 188, 216), (226, 242, 250))
        rim = (112, 150, 182)
    else:
        fill = PALETTE["path"]
        accents = (PALETTE["path_light"], PALETTE["path_dark"], PALETTE["path_light"])
        rim = PALETTE["path_rim"]
    # Full-width arms with a rounded core keep straight roads even (no "beads").
    pygame.draw.rect(surface, fill, (2, 2, 12, 12), border_radius=4)
    if mask & 1:
        _rect(surface, fill, 2, 0, 12, 9)
    if mask & 2:
        _rect(surface, fill, 7, 2, 9, 12)
    if mask & 4:
        _rect(surface, fill, 2, 7, 12, 9)
    if mask & 8:
        _rect(surface, fill, 0, 2, 9, 12)
    if mask & 16:
        pygame.draw.polygon(surface, fill, ((8, 0), (16, 0), (16, 8)))
    if mask & 32:
        pygame.draw.polygon(surface, fill, ((8, 16), (16, 8), (16, 16)))
    if mask & 64:
        pygame.draw.polygon(surface, fill, ((0, 8), (8, 16), (0, 16)))
    if mask & 128:
        pygame.draw.polygon(surface, fill, ((0, 0), (8, 0), (0, 8)))
    rng = random.Random(mask * 101 + variant + {"path": 0, "water": 550, "lava": 880, "ice": 990}[kind])
    for _ in range(9):
        x, y = rng.randrange(1, 15), rng.randrange(1, 15)
        if surface.get_at((x, y)).a:
            _rect(surface, rng.choice(accents), x, y, rng.choice((1, 2)), 1)
    # A 1px rim wherever the patch meets grass inside this tile (the tile border
    # itself is treated as "continues", so neighbouring patches join seamlessly).
    solid = [[surface.get_at((x, y)).a > 0 for x in range(16)] for y in range(16)]
    for y in range(16):
        for x in range(16):
            if not solid[y][x]:
                continue
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < 16 and 0 <= ny < 16 and not solid[ny][nx]:
                    surface.set_at((x, y), rim)
                    break
    if water:
        _rect(surface, (220, 240, 244), 5, 5, 2, 1)
        _rect(surface, (180, 220, 232), 10, 10, 2, 1)
    elif kind == "ice":
        # Diagonal glints and a hairline crack read as frozen water.
        for x, y in ((4, 9), (5, 8), (6, 7)):
            if solid[y][x]:
                surface.set_at((x, y), (244, 250, 255))
        for x, y in ((9, 5), (10, 6), (10, 7), (11, 8)):
            if solid[y][x]:
                surface.set_at((x, y), (130, 170, 200))
    elif kind == "lava":
        # Cooling crust plates break up the flat orange and tie it to the ash ground.
        for _ in range(2):
            x, y = rng.randrange(2, 11), rng.randrange(2, 12)
            if solid[y][x] and solid[y + 1][x + 3]:
                _rect(surface, (120, 62, 54), x, y, 4, 2)
                _rect(surface, (152, 80, 62), x, y, 4, 1)
                _rect(surface, (252, 206, 110), x - 1, y + 2, 2, 1)
    return surface


def _soft_shadow(surface, rect, alpha=80):
    """Translucent ground ellipse; a darker core makes it read as soft, not a flat blob."""
    pygame.draw.ellipse(surface, (34, 52, 36, alpha), rect)
    inner = pygame.Rect(rect).inflate(-max(2, rect[2] // 3), -2)
    pygame.draw.ellipse(surface, (34, 52, 36, min(255, alpha + 40)), inner)


def _blob(surface, circles, tones):
    """Draw a rounded canopy: dark outline ring, shaded body, lit upper-left, glints."""
    outline, dark, mid, light, glint = tones
    for cx, cy, r in circles:
        pygame.draw.circle(surface, outline, (cx, cy), r + 1)
    for cx, cy, r in circles:
        pygame.draw.circle(surface, dark, (cx, cy), r)
    for cx, cy, r in circles:
        pygame.draw.circle(surface, mid, (cx - 1, cy - 1), max(1, r - 2))
    for cx, cy, r in circles:
        pygame.draw.circle(surface, light, (cx - max(1, r // 3), cy - max(1, r // 3)), max(1, r // 2 - 1))
    for cx, cy, r in circles:
        if r >= 4:
            _rect(surface, glint, cx - r // 2, cy - r // 2, 2, 1)


def _leaf_tones():
    return (PALETTE["outline"], PALETTE["leaf_dark"], PALETTE["leaf"], PALETTE["leaf_light"], PALETTE["leaf_glint"])


def _trunk(surface, x, top, bottom):
    _rect(surface, PALETTE["outline"], x - 1, top, 6, bottom - top + 1)
    _rect(surface, PALETTE["bark"], x, top, 4, bottom - top)
    _rect(surface, PALETTE["bark_light"], x + 1, top, 1, bottom - top - 1)
    # Little roots flare at the base.
    _rect(surface, PALETTE["outline"], x - 2, bottom - 1, 2, 1)
    _rect(surface, PALETTE["outline"], x + 4, bottom - 1, 2, 1)


def _tree(kind="round"):
    """Cozy round-canopy tree (24x32) with outline, three-tone shading and a soft shadow."""
    surface = _canvas((24, 32))
    _soft_shadow(surface, (2, 25, 20, 6))
    if kind == "pine":
        _trunk(surface, 10, 22, 29)
        tiers = ((12, 2, 5, 9), (12, 7, 8, 14), (12, 12, 10, 21))
        for cx, top, half, bottom in tiers:
            pygame.draw.polygon(surface, PALETTE["outline"],
                                ((cx, top - 1), (cx + half + 1, bottom + 1), (cx - half - 1, bottom + 1)))
        for cx, top, half, bottom in tiers:
            pygame.draw.polygon(surface, (46, 100, 72), ((cx, top), (cx + half, bottom), (cx - half, bottom)))
            pygame.draw.polygon(surface, (66, 130, 84), ((cx, top + 1), (cx - 1, bottom - 1), (cx - half + 2, bottom - 1)))
            _rect(surface, (120, 176, 104), cx - 2, top + 3, 1, 2)
        return surface
    _trunk(surface, 10, 18, 29)
    _blob(surface, ((12, 11, 8), (6, 15, 5), (18, 15, 5), (12, 16, 6)), _leaf_tones())
    if kind == "fruit":
        for x, y in ((7, 9), (15, 8), (11, 14), (17, 16), (6, 17)):
            _rect(surface, (204, 64, 60), x, y, 2, 2)
            surface.set_at((x, y), (250, 150, 130))
    return surface


def _bush():
    surface = _canvas()
    _soft_shadow(surface, (1, 11, 14, 5))
    _blob(surface, ((5, 9, 4), (10, 8, 4), (8, 6, 4)), _leaf_tones())
    for x, y in ((5, 7), (10, 6)):
        surface.set_at((x, y), (250, 232, 200))
    return surface


def _flower_patch(variant=0):
    surface = _canvas()
    rng = random.Random(variant + 77)
    petals = ((250, 240, 214), (246, 206, 96), (236, 150, 168), (170, 160, 236))
    for _ in range(4):
        x, y = rng.randrange(2, 13), rng.randrange(3, 13)
        color = rng.choice(petals)
        _rect(surface, PALETTE["grass_deep"], x + 1, y + 2, 1, 2)
        surface.set_at((x + 1, y), color)
        surface.set_at((x, y + 1), color)
        surface.set_at((x + 2, y + 1), color)
        surface.set_at((x + 1, y + 1), (246, 206, 96) if color != (246, 206, 96) else (210, 120, 60))
    return surface


def _pebbles(variant=0):
    surface = _canvas()
    rng = random.Random(variant + 300)
    for _ in range(3):
        x, y = rng.randrange(2, 12), rng.randrange(4, 13)
        w = rng.choice((2, 3))
        _rect(surface, (120, 118, 112), x, y + 1, w, 1)
        _rect(surface, (176, 172, 160), x, y, w, 1)
    return surface


def _shadow():
    surface = _canvas((16, 8))
    _soft_shadow(surface, (1, 1, 14, 6), 70)
    return surface


def _fence(vertical=False):
    surface = _canvas()
    post, post_light, rail = (128, 86, 56), (176, 128, 82), (156, 108, 70)
    if vertical:
        _rect(surface, PALETTE["outline"], 6, 0, 4, 16)
        _rect(surface, rail, 7, 0, 2, 16)
        _rect(surface, post_light, 7, 0, 1, 16)
        _rect(surface, PALETTE["outline"], 5, 2, 6, 7)
        _rect(surface, post, 6, 2, 4, 6)
        _rect(surface, post_light, 6, 2, 4, 1)
        return surface
    for y in (5, 10):
        _rect(surface, PALETTE["outline"], 0, y - 1, 16, 3)
        _rect(surface, post_light if y == 5 else rail, 0, y, 16, 1)
    for x in (2, 10):
        _rect(surface, PALETTE["outline"], x - 1, 2, 5, 12)
        _rect(surface, post, x, 3, 3, 10)
        _rect(surface, post_light, x, 3, 1, 9)
    _rect(surface, (34, 52, 36, 70), 0, 14, 16, 2)
    return surface


def _gate_arch():
    """Village entrance: two timber posts on stone footings under a small shingled cap.

    The middle stays transparent so the road visibly runs through the gate.
    """
    surface = _canvas((24, 32))
    o = PALETTE["outline"]
    post, post_light = (128, 86, 56), (176, 128, 82)
    for x in (3, 17):
        _soft_shadow(surface, (x - 2, 28, 8, 4), 70)
        _rect(surface, o, x - 1, 8, 6, 22)
        _rect(surface, post, x, 9, 4, 18)
        _rect(surface, post_light, x, 9, 1, 17)
        # Stone footing with a mossy lip.
        _rect(surface, o, x - 2, 25, 8, 6)
        _rect(surface, (150, 146, 136), x - 1, 26, 6, 4)
        _rect(surface, (186, 182, 168), x - 1, 26, 6, 1)
        _rect(surface, PALETTE["leaf_light"], x - 1, 25, 3, 1)
    # Cross beam and a little roof cap in the cottage teal.
    _rect(surface, o, 1, 8, 22, 4)
    _rect(surface, post, 2, 9, 20, 2)
    _rect(surface, post_light, 2, 9, 20, 1)
    pygame.draw.polygon(surface, o, ((0, 8), (4, 2), (19, 2), (23, 8)))
    pygame.draw.polygon(surface, (72, 120, 126), ((2, 7), (5, 3), (18, 3), (21, 7)))
    _rect(surface, (100, 152, 150), 5, 4, 14, 1)
    _rect(surface, (140, 190, 176), 3, 6, 18, 1)
    # Hanging lantern gives the entrance a warm focal point.
    _rect(surface, o, 11, 12, 1, 2)
    _rect(surface, o, 10, 14, 4, 4)
    _rect(surface, (248, 210, 120), 11, 15, 2, 2)
    # Climbing vine on the left post.
    for y in (13, 16, 19):
        _rect(surface, PALETTE["leaf"], 2, y, 2, 2)
        surface.set_at((2, y), PALETTE["leaf_light"])
    surface.set_at((3, 17), (236, 150, 168))
    return surface


def _crops():
    """Tilled garden bed with two rows of round cabbages."""
    surface = _canvas()
    surface.fill((150, 104, 70))
    for y in (3, 11):
        _rect(surface, (120, 80, 56), 0, y + 3, 16, 1)
    for y in (2, 10):
        for x in (3, 11):
            pygame.draw.circle(surface, PALETTE["outline"], (x, y + 1), 3)
            pygame.draw.circle(surface, PALETTE["leaf"], (x, y + 1), 2)
            surface.set_at((x - 1, y), PALETTE["leaf_glint"])
    return surface


def _barrel():
    surface = _canvas()
    _soft_shadow(surface, (2, 11, 12, 5))
    _rect(surface, PALETTE["outline"], 3, 2, 10, 12)
    _rect(surface, (150, 98, 60), 4, 3, 8, 10)
    _rect(surface, (186, 132, 82), 5, 3, 2, 10)
    _rect(surface, (110, 112, 118), 4, 5, 8, 1)
    _rect(surface, (110, 112, 118), 4, 10, 8, 1)
    _rect(surface, (100, 66, 44), 4, 3, 8, 1)
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
    return _outline(surface)


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
    return _outline(surface)


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
    return _outline(surface)


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
    return _outline(surface)


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
    return _outline(surface)


LAVA_RIM = (74, 52, 56)


def _outline(surface, color=None):
    """Add a 1px outline around every solid pixel (soft shadows are left alone)."""
    color = color or PALETTE["outline"]
    w, h = surface.get_size()
    solid = [[surface.get_at((x, y)).a >= 200 for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            if solid[y][x]:
                continue
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h and solid[ny][nx]:
                    surface.set_at((x, y), color)
                    break
    return surface


# --- Hero-sized NPCs (16x24, same chibi proportions as the player) -------------------

def _person_head(s, hair, hair_light, style="short"):
    skin, shade = PALETTE["skin"], PALETTE["skin_shadow"]
    if style == "long":
        _rect(s, hair, 2, 7, 3, 9)
        _rect(s, hair, 11, 7, 3, 9)
    _rect(s, hair, 4, 1, 8, 2)
    _rect(s, hair, 2, 3, 12, 2)
    _rect(s, hair, 2, 5, 12, 3)
    _rect(s, hair, 3, 7, 2, 3)
    _rect(s, hair, 11, 7, 2, 3)
    _rect(s, skin, 4, 6, 8, 6)
    _rect(s, shade, 4, 6, 8, 1)
    _rect(s, hair, 4, 5, 8, 1)
    _rect(s, hair, 4, 6, 2, 1)
    _rect(s, hair, 10, 6, 2, 1)
    _rect(s, hair_light, 4, 2, 4, 1)
    _rect(s, hair_light, 9, 3, 3, 1)
    _rect(s, PALETTE["ink"], 6, 8, 1, 2)
    _rect(s, PALETTE["ink"], 9, 8, 1, 2)
    _rect(s, (220, 126, 113), 5, 10, 1, 1)
    _rect(s, (220, 126, 113), 10, 10, 1, 1)
    _rect(s, shade, 7, 11, 2, 1)


def _person_body(s, top, top_light, bottom, kind="pants"):
    skin = PALETTE["skin"]
    _rect(s, top, 2, 12, 2, 5)
    _rect(s, top, 12, 12, 2, 5)
    _rect(s, skin, 2, 17, 2, 1)
    _rect(s, skin, 12, 17, 2, 1)
    _rect(s, top, 4, 12, 8, 6)
    _rect(s, top_light, 5, 12, 6, 1)
    if kind == "robe":
        _rect(s, top, 4, 18, 8, 2)
        _rect(s, top, 3, 20, 10, 2)
        _rect(s, top_light, 4, 20, 2, 2)
        _rect(s, PALETTE["boot"], 4, 22, 3, 2)
        _rect(s, PALETTE["boot"], 9, 22, 3, 2)
    elif kind == "skirt":
        _rect(s, bottom, 4, 17, 8, 2)
        _rect(s, bottom, 3, 19, 10, 2)
        _rect(s, (70, 60, 64), 5, 21, 2, 1)
        _rect(s, (70, 60, 64), 9, 21, 2, 1)
        _rect(s, PALETTE["boot"], 4, 22, 3, 2)
        _rect(s, PALETTE["boot"], 9, 22, 3, 2)
    else:
        _rect(s, bottom, 5, 18, 6, 2)
        _rect(s, bottom, 5, 20, 2, 2)
        _rect(s, bottom, 9, 20, 2, 2)
        _rect(s, PALETTE["boot"], 4, 22, 4, 2)
        _rect(s, PALETTE["boot"], 9, 22, 4, 2)
        _rect(s, (150, 104, 66), 4, 22, 4, 1)
        _rect(s, (150, 104, 66), 9, 22, 4, 1)


def _beard(s, color, long=False):
    _rect(s, color, 4, 10, 8, 2)
    _rect(s, color, 5, 12, 6, 1)
    if long:
        _rect(s, color, 5, 13, 6, 2)
        _rect(s, color, 6, 15, 4, 1)
    _rect(s, PALETTE["skin_shadow"], 7, 10, 2, 1)


def _npc_herbalist():
    """Marta: long auburn hair, sage dress, cream apron and a herb sprig."""
    s = _canvas((16, 24))
    _person_head(s, (156, 84, 62), (200, 124, 86), "long")
    _person_body(s, (104, 148, 96), (140, 182, 122), (86, 126, 82), "skirt")
    _rect(s, (238, 226, 196), 5, 14, 6, 6)
    _rect(s, (214, 198, 164), 5, 19, 6, 1)
    _rect(s, (236, 150, 168), 12, 16, 2, 1)
    _rect(s, PALETTE["leaf_light"], 13, 15, 1, 1)
    return _outline(s)


def _npc_shopkeeper():
    """Logan: short dark hair, trimmed beard, cream shirt under a leather apron."""
    s = _canvas((16, 24))
    _person_head(s, (88, 58, 44), (130, 90, 62))
    _beard(s, (98, 64, 48))
    _person_body(s, (226, 210, 170), (246, 236, 206), (80, 84, 104))
    _rect(s, (150, 98, 62), 5, 14, 6, 6)
    _rect(s, (186, 130, 82), 5, 14, 6, 1)
    _rect(s, PALETTE["gold"], 7, 16, 2, 1)
    return _outline(s)


def _npc_chief():
    """Chief Valen: white hair, a long white beard and a gold-trimmed blue robe."""
    s = _canvas((16, 24))
    _person_head(s, (226, 222, 210), (252, 250, 242))
    _person_body(s, (70, 98, 150), (102, 132, 182), (70, 98, 150), "robe")
    _rect(s, PALETTE["gold"], 7, 16, 2, 6)
    _beard(s, (238, 236, 226), long=True)
    return _outline(s)


def _npc_old_knight():
    """Garen: grey hair and beard, a steel cuirass with pauldrons over a faded red cape."""
    s = _canvas((16, 24))
    _rect(s, (150, 60, 56), 2, 12, 12, 10)
    _person_head(s, (168, 168, 164), (210, 210, 204))
    _person_body(s, (138, 148, 156), (190, 198, 202), (70, 74, 90))
    _rect(s, (190, 198, 202), 2, 12, 3, 2)
    _rect(s, (190, 198, 202), 11, 12, 3, 2)
    _rect(s, PALETTE["gold"], 7, 15, 2, 1)
    _rect(s, (150, 60, 56), 1, 14, 1, 7)
    _rect(s, (150, 60, 56), 14, 14, 1, 7)
    _beard(s, (190, 190, 184))
    return _outline(s)


def _npc_townsfolk():
    """Plaza villager: straw hat over blond hair, sky-blue shirt and a bread basket."""
    s = _canvas((16, 24))
    _person_head(s, (226, 190, 104), (248, 222, 150))
    _person_body(s, (110, 160, 210), (150, 192, 232), (120, 90, 64))
    _rect(s, (120, 90, 64), 5, 14, 1, 4)
    _rect(s, (120, 90, 64), 10, 14, 1, 4)
    _rect(s, (214, 182, 110), 1, 3, 14, 2)
    _rect(s, (232, 204, 130), 4, 0, 8, 3)
    _rect(s, (190, 76, 66), 4, 2, 8, 1)
    _rect(s, (170, 120, 70), 10, 16, 5, 3)
    _rect(s, (214, 160, 96), 11, 15, 3, 1)
    return _outline(s)


def _npc_merchant():
    """Toby: wide travel hat with a feather, green scarf and an overstuffed backpack."""
    s = _canvas((16, 24))
    _rect(s, (146, 100, 60), 1, 10, 14, 9)
    _rect(s, (176, 160, 120), 1, 8, 14, 2)
    _rect(s, (204, 72, 60), 1, 8, 1, 2)
    _rect(s, (204, 72, 60), 14, 8, 1, 2)
    _person_head(s, (110, 76, 52), (150, 106, 70))
    _person_body(s, (108, 92, 64), (140, 120, 84), (80, 84, 104))
    _rect(s, (70, 140, 86), 4, 12, 8, 2)
    _rect(s, (110, 180, 120), 5, 12, 3, 1)
    _rect(s, (98, 64, 40), 1, 4, 14, 2)
    _rect(s, (122, 82, 50), 4, 0, 8, 4)
    _rect(s, (176, 58, 50), 4, 3, 8, 1)
    _rect(s, (238, 220, 150), 12, 0, 2, 2)
    _rect(s, (120, 84, 50), 15, 6, 1, 17)
    return _outline(s)


def _npc_innkeeper():
    """Rosa the innkeeper: auburn bun, cream blouse, green apron and a tankard."""
    s = _canvas((16, 24))
    _person_head(s, (170, 84, 54), (206, 120, 80))
    _person_body(s, (236, 222, 190), (250, 240, 214), (90, 120, 80), kind="skirt")
    _rect(s, (170, 84, 54), 6, 0, 4, 2)          # bun
    _rect(s, (96, 140, 92), 5, 13, 6, 5)         # apron
    _rect(s, (128, 170, 116), 6, 13, 4, 1)
    _rect(s, (196, 160, 96), 12, 14, 3, 3)       # tankard
    _rect(s, (250, 246, 230), 12, 13, 3, 1)
    return _outline(s)


def _npc_blacksmith():
    """Bron the smith: soot-dark hair, broad beard, leather apron and a hammer."""
    s = _canvas((16, 24))
    _person_head(s, (58, 50, 50), (92, 80, 76))
    _person_body(s, (150, 92, 64), (186, 120, 84), (70, 64, 60))
    _beard(s, (70, 56, 50))
    _rect(s, (98, 66, 46), 4, 13, 8, 6)          # leather apron
    _rect(s, (126, 88, 60), 5, 13, 6, 1)
    _rect(s, (120, 90, 62), 13, 11, 1, 7)        # hammer handle
    _rect(s, (150, 156, 160), 12, 10, 3, 2)      # hammer head
    return _outline(s)


def _npc_librarian():
    """Edel the librarian: silver hair, round glasses, a long blue robe and a book."""
    s = _canvas((16, 24))
    _person_head(s, (200, 204, 214), (232, 236, 244), style="long")
    _person_body(s, (70, 92, 150), (104, 128, 186), (70, 92, 150), kind="robe")
    _rect(s, (60, 50, 46), 5, 8, 3, 1)            # glasses frame
    _rect(s, (60, 50, 46), 8, 8, 3, 1)
    _rect(s, (150, 56, 48), 11, 14, 4, 4)         # red book
    _rect(s, (236, 214, 150), 11, 15, 1, 2)
    return _outline(s)


def _npc_apothecary():
    """Mira the apothecary: green hood, purple dress and a glowing flask."""
    s = _canvas((16, 24))
    _person_head(s, (86, 60, 50), (120, 88, 70))
    _person_body(s, (122, 80, 140), (156, 112, 174), (96, 64, 112), kind="skirt")
    _rect(s, (84, 128, 88), 3, 1, 10, 3)          # hood
    _rect(s, (84, 128, 88), 2, 4, 2, 6)
    _rect(s, (84, 128, 88), 12, 4, 2, 6)
    _rect(s, (210, 236, 240), 12, 13, 3, 1)       # flask neck
    _rect(s, (110, 220, 150), 11, 14, 4, 4)       # potion
    _rect(s, (190, 250, 210), 12, 15, 1, 1)
    return _outline(s)


def _npc_child():
    """Tomi, a village kid: messy hair, short and cheerful, with a wooden sword."""
    s = _canvas((16, 24))
    body = _canvas((16, 24))
    _person_head(body, (150, 100, 60), (190, 140, 90))
    _person_body(body, (220, 130, 70), (240, 170, 110), (80, 100, 140))
    _rect(body, (170, 130, 90), 13, 12, 1, 6)     # wooden sword
    _rect(body, (120, 86, 56), 12, 16, 3, 1)
    # Children are drawn smaller: squash the 24px figure into the lower 20px.
    s.blit(pygame.transform.scale(body, (16, 20)), (0, 4))
    return _outline(s)


def _npc_hunter():
    """Harn the highland hunter: fur-lined hood, thick coat, a bow over the shoulder."""
    s = _canvas((16, 24))
    _person_head(s, (92, 70, 56), (124, 96, 74))
    _person_body(s, (96, 112, 128), (130, 150, 168), (70, 62, 58))
    _rect(s, (236, 232, 222), 2, 4, 12, 2)     # fur trim of the hood
    _rect(s, (120, 92, 70), 3, 1, 10, 3)       # hood
    _rect(s, (206, 200, 188), 3, 3, 10, 1)
    _rect(s, (236, 232, 222), 4, 12, 8, 1)     # fur collar
    _rect(s, (150, 104, 66), 14, 6, 1, 13)     # bow stave
    _rect(s, (230, 222, 200), 13, 7, 1, 11)    # bow string
    return _outline(s)


# --- Field terrain ------------------------------------------------------------------

def _ground(base, darker, lighter, variant, seed, extra=None):
    surface = _canvas()
    surface.fill(base)
    rng = random.Random(variant * 7919 + seed)
    for _ in range(3):
        x, y = rng.randrange(15), rng.randrange(16)
        _rect(surface, darker if rng.random() < 0.55 else lighter, x, y, 2, 1)
    if extra:
        extra(surface, rng, variant)
    return surface


def _canyon(variant):
    def strata(surface, rng, v):
        if v % 3 == 0:
            y = rng.randrange(3, 13)
            _rect(surface, (204, 142, 100), rng.randrange(0, 6), y, rng.randrange(5, 9), 1)
        if v % 4 == 1:
            x, y = rng.randrange(2, 13), rng.randrange(2, 13)
            _rect(surface, (214, 190, 160), x, y, 2, 1)
            _rect(surface, (140, 90, 66), x, y + 1, 2, 1)
    return _ground((186, 118, 82), (166, 102, 72), (204, 140, 98), variant, 611, strata)


def _snow(variant):
    def sparkle(surface, rng, v):
        if v % 3 == 0:
            _rect(surface, (255, 255, 255), rng.randrange(1, 15), rng.randrange(1, 15), 1, 1)
        if v % 5 == 2:
            x, y = rng.randrange(1, 12), rng.randrange(2, 14)
            _rect(surface, (206, 218, 232), x, y, 4, 1)
    return _ground((232, 238, 244), (210, 220, 232), (248, 251, 255), variant, 733, sparkle)


def _snowcap(surface):
    """Pile snow on every upward-facing edge of a sprite (pines, rocks)."""
    surface = surface.copy()
    w, h = surface.get_size()
    outline = PALETTE["outline"]
    solid = lambda x, y: 0 <= x < w and 0 <= y < h and surface.get_at((x, y)).a >= 200 \
        and tuple(surface.get_at((x, y)))[:3] != outline
    tops = [(x, y) for y in range(h) for x in range(w) if solid(x, y) and not solid(x, y - 1)]
    for x, y in tops:
        surface.set_at((x, y), (246, 250, 255))
        if solid(x, y + 1) and (x + y) % 3 == 0:
            surface.set_at((x, y + 1), (214, 228, 240))
    return surface


def _frosted(surface, eyes=(130, 236, 255)):
    """Ice-touched recolour: pale blues by brightness, outline kept, vivid head pixels glow."""
    surface = surface.copy()
    outline = PALETTE["outline"]
    w, h = surface.get_size()
    pixels = [(x, y) for y in range(h) for x in range(w) if surface.get_at((x, y)).a >= 200]
    lum = {p: sum(tuple(surface.get_at(p))[:3]) for p in pixels}
    upper = sorted(v for p, v in lum.items() if p[1] < h * 0.5)
    bright = upper[-max(2, len(upper) // 25)] if upper else 999
    for p in pixels:
        r, g, b, a = surface.get_at(p)
        if (r, g, b) == outline:
            continue
        vivid = max(r, g, b) - min(r, g, b) > 70 or lum[p] > 650
        if lum[p] >= bright and lum[p] > 300 and vivid and p[1] < h * 0.5:
            surface.set_at(p, (*eyes, a))
            continue
        k = lum[p] / 765
        surface.set_at(p, (int(96 + 150 * k), int(130 + 120 * k), int(168 + 87 * k), a))
    return surface


def _frost_wisp():
    """Frost wisp (16x16): a floating flame of cold light with two dark eyes."""
    s = _canvas()
    pygame.draw.ellipse(s, (150, 206, 236), (3, 5, 10, 9))
    pygame.draw.polygon(s, (150, 206, 236), ((4, 8), (6, 2), (8, 6), (10, 1), (12, 8)))
    pygame.draw.ellipse(s, (214, 240, 252), (5, 7, 6, 5))
    _rect(s, (250, 254, 255), 7, 8, 2, 2)
    _rect(s, (40, 70, 110), 6, 9, 1, 2)
    _rect(s, (40, 70, 110), 9, 9, 1, 2)
    _rect(s, (150, 206, 236), 5, 14, 2, 1)
    _rect(s, (150, 206, 236), 9, 14, 2, 1)
    _rect(s, (190, 228, 246), 2, 3, 1, 1)
    _rect(s, (190, 228, 246), 13, 4, 1, 1)
    return _outline(s)


def _ash(variant):
    def cracks(surface, rng, v):
        if v % 3 == 0:
            x, y = rng.randrange(2, 10), rng.randrange(3, 13)
            for step in range(4):
                surface.set_at((x + step, y + (step % 2)), (62, 52, 58))
            if v % 2 == 0:
                surface.set_at((x + 1, y), (232, 128, 64))
    return _ground((98, 86, 90), (84, 72, 78), (118, 106, 108), variant, 977, cracks)


ROCK_TONES = {
    "rock": ((176, 126, 100), (214, 168, 134), (136, 90, 74)),     # red canyon sandstone
    "basalt": ((82, 74, 84), (122, 112, 120), (58, 50, 60)),       # volcanic
    "mossrock": ((146, 146, 136), (188, 188, 174), (106, 108, 104)),  # forest / grassland
    "icerock": ((150, 176, 198), (214, 232, 244), (106, 132, 158)),  # frost highlands
}


def _rock(variant=0, tone="rock"):
    base, light, dark = ROCK_TONES[tone]
    basalt = tone == "basalt"
    surface = _canvas()
    pygame.draw.ellipse(surface, (34, 30, 36, 80), (1, 11, 14, 5))
    shapes = (
        ((2, 13), (2, 8), (4, 5), (8, 3), (12, 4), (14, 8), (14, 13)),
        ((1, 13), (2, 9), (5, 7), (8, 9), (8, 13)),
        ((3, 13), (4, 4), (7, 2), (11, 3), (13, 7), (13, 13)),
    )
    shape = shapes[variant % 3]
    pygame.draw.polygon(surface, base, shape)
    if variant % 3 == 1:
        pygame.draw.polygon(surface, base, ((8, 13), (9, 6), (12, 4), (15, 7), (15, 13)))
        _rect(surface, light, 10, 6, 3, 1)
    _rect(surface, light, shape[2][0] + 1, shape[2][1] + 1, 4, 1)
    _rect(surface, light, shape[2][0], shape[2][1] + 2, 2, 2)
    _rect(surface, dark, 3, 11, 10, 2)
    if basalt and variant % 2 == 0:
        _rect(surface, (232, 128, 64), 7, 9, 1, 2)
    if tone == "mossrock":
        _rect(surface, PALETTE["leaf"], shape[2][0], shape[2][1], 4, 1)
        _rect(surface, PALETTE["leaf_light"], shape[2][0] + 1, shape[2][1], 2, 1)
    return _outline(surface)


def _tuft_decal(kind):
    surface = _canvas()
    if kind == "dry":
        blades, base = (214, 184, 120), (160, 120, 80)
    else:
        blades, base = PALETTE["grass_light"], PALETTE["grass_dark"]
    for x, y in ((4, 8), (9, 10)):
        _rect(surface, blades, x, y, 1, 2)
        _rect(surface, blades, x + 2, y - 1, 1, 3)
        _rect(surface, blades, x + 4, y, 1, 2)
        _rect(surface, base, x, y + 2, 5, 1)
    return surface


def _ember():
    surface = _canvas()
    for x, y in ((4, 6), (10, 11)):
        _rect(surface, (62, 52, 58), x, y, 3, 1)
        _rect(surface, (62, 52, 58), x + 2, y + 1, 2, 1)
        surface.set_at((x + 1, y), (240, 140, 70))
    surface.set_at((8, 3), (250, 190, 100))
    return surface


def _slime_v2():
    """Green slime (16x12): glossy dome, darker base, big friendly eyes."""
    s = _canvas((16, 12))
    pygame.draw.ellipse(s, PALETTE["slime_dark"], (1, 2, 14, 10))
    pygame.draw.ellipse(s, PALETTE["slime"], (2, 2, 12, 8))
    _rect(s, PALETTE["slime_light"], 4, 3, 3, 1)
    _rect(s, PALETTE["slime_light"], 3, 4, 1, 2)
    _rect(s, (250, 255, 240), 5, 3, 1, 1)
    _rect(s, PALETTE["ink"], 5, 6, 2, 2)
    _rect(s, PALETTE["ink"], 10, 6, 2, 2)
    _rect(s, (255, 255, 255), 5, 6, 1, 1)
    _rect(s, (255, 255, 255), 10, 6, 1, 1)
    _rect(s, PALETTE["slime_dark"], 7, 9, 2, 1)
    return _outline(s)


def _goblin():
    """Goblin scout (16x16): long ears, red eyes, patched leather tunic and a crude dagger."""
    s = _canvas()
    skin, skin_dark = (124, 170, 84), (88, 130, 64)
    _rect(s, skin, 0, 4, 3, 2)
    _rect(s, skin, 13, 4, 3, 2)
    _rect(s, skin, 3, 2, 10, 7)
    _rect(s, skin_dark, 3, 7, 10, 2)
    _rect(s, (98, 70, 52), 3, 1, 10, 2)
    _rect(s, (232, 70, 54), 5, 5, 2, 1)
    _rect(s, (232, 70, 54), 9, 5, 2, 1)
    _rect(s, (250, 240, 210), 6, 8, 1, 1)
    _rect(s, (250, 240, 210), 9, 8, 1, 1)
    _rect(s, (138, 96, 62), 4, 9, 8, 5)
    _rect(s, (176, 128, 82), 5, 9, 6, 1)
    _rect(s, (204, 72, 60), 7, 11, 2, 2)
    _rect(s, skin, 2, 10, 2, 3)
    _rect(s, skin, 12, 10, 2, 3)
    _rect(s, (190, 200, 206), 14, 6, 1, 6)
    _rect(s, (110, 72, 50), 13, 11, 3, 1)
    _rect(s, (74, 60, 56), 5, 14, 2, 2)
    _rect(s, (74, 60, 56), 9, 14, 2, 2)
    return _outline(s)


def _harpy():
    """Storm harpy (24x24): teal feathered wings, wild white hair and golden talons."""
    s = _canvas((24, 24))
    wing, wing_light, wing_dark = (70, 150, 150), (130, 200, 190), (46, 104, 112)
    for side in (1, -1):
        cx = 12 + side * 2
        pts = [(cx, 8), (cx + side * 11, 2), (cx + side * 11, 8), (cx + side * 9, 13), (cx + side * 4, 15)]
        pygame.draw.polygon(s, wing_dark, pts)
        pygame.draw.polygon(s, wing, [(cx, 9), (cx + side * 10, 4), (cx + side * 9, 9), (cx + side * 4, 13)])
        for i in range(3):
            x = cx + side * (5 + i * 2)
            _rect(s, wing_light, min(x, x + side), 5 + i, 1, 4)
    _rect(s, (236, 236, 226), 8, 1, 8, 4)
    _rect(s, (236, 236, 226), 7, 4, 2, 6)
    _rect(s, (236, 236, 226), 15, 4, 2, 6)
    _rect(s, PALETTE["skin"], 9, 4, 6, 5)
    _rect(s, (40, 120, 140), 10, 6, 1, 1)
    _rect(s, (40, 120, 140), 13, 6, 1, 1)
    _rect(s, PALETTE["skin_shadow"], 11, 8, 2, 1)
    _rect(s, wing, 9, 9, 6, 6)
    _rect(s, wing_light, 10, 9, 4, 2)
    _rect(s, wing_dark, 9, 15, 6, 4)
    for x in (9, 13):
        _rect(s, (226, 182, 80), x, 19, 2, 3)
        _rect(s, (226, 182, 80), x - 1, 22, 4, 1)
    return _outline(s)


def _golem():
    """Rock golem (24x24): stacked mossy boulders around a glowing amber core."""
    s = _canvas((24, 24))
    stone, light, dark = (150, 140, 124), (190, 180, 160), (104, 96, 88)
    _rect(s, dark, 1, 8, 6, 10)
    _rect(s, dark, 17, 8, 6, 10)
    _rect(s, stone, 2, 8, 4, 8)
    _rect(s, stone, 18, 8, 4, 8)
    _rect(s, dark, 1, 17, 6, 4)
    _rect(s, dark, 17, 17, 6, 4)
    _rect(s, stone, 6, 6, 12, 12)
    _rect(s, light, 7, 6, 10, 2)
    _rect(s, dark, 6, 16, 12, 2)
    _rect(s, stone, 8, 1, 8, 6)
    _rect(s, light, 9, 1, 6, 1)
    _rect(s, (250, 196, 90), 9, 3, 2, 2)
    _rect(s, (250, 196, 90), 13, 3, 2, 2)
    pygame.draw.circle(s, (232, 150, 60), (12, 11), 3)
    pygame.draw.circle(s, (255, 226, 140), (12, 11), 1)
    _rect(s, dark, 7, 18, 4, 5)
    _rect(s, dark, 13, 18, 4, 5)
    _rect(s, stone, 8, 18, 2, 4)
    _rect(s, stone, 14, 18, 2, 4)
    for x, y in ((8, 6), (14, 7), (3, 8), (19, 8), (10, 1)):
        _rect(s, PALETTE["leaf"], x, y, 3, 1)
        s.set_at((x + 1, y), PALETTE["leaf_light"])
    _rect(s, dark, 9, 13, 1, 3)
    _rect(s, dark, 16, 9, 1, 3)
    return _outline(s)


def _lizardman():
    """Fire lizardman (24x24): crimson scales, cream belly, flaming tail and a curved blade."""
    s = _canvas((24, 24))
    scale, scale_light, scale_dark = (196, 70, 52), (230, 112, 72), (140, 44, 40)
    pygame.draw.polygon(s, scale_dark, ((4, 20), (1, 16), (2, 13), (6, 18)))
    _rect(s, (250, 170, 60), 1, 11, 2, 3)
    _rect(s, (255, 226, 120), 1, 12, 1, 1)
    _rect(s, scale, 8, 2, 9, 6)
    _rect(s, scale, 15, 5, 5, 3)
    _rect(s, scale_light, 9, 2, 6, 1)
    _rect(s, (250, 210, 80), 13, 4, 2, 1)
    _rect(s, PALETTE["ink"], 14, 4, 1, 1)
    _rect(s, scale_dark, 16, 7, 4, 1)
    for x in (9, 11, 13):
        _rect(s, (250, 170, 60), x, 1, 1, 1)
    _rect(s, scale, 7, 8, 9, 9)
    _rect(s, (238, 208, 150), 9, 9, 5, 7)
    _rect(s, (214, 180, 124), 9, 11, 5, 1)
    _rect(s, (214, 180, 124), 9, 13, 5, 1)
    _rect(s, scale, 5, 9, 2, 6)
    _rect(s, scale, 16, 9, 2, 5)
    _rect(s, scale_dark, 7, 17, 3, 5)
    _rect(s, scale_dark, 13, 17, 3, 5)
    _rect(s, scale, 6, 21, 4, 2)
    _rect(s, scale, 13, 21, 4, 2)
    pygame.draw.line(s, (214, 220, 226), (19, 13), (22, 3))
    pygame.draw.line(s, (240, 244, 246), (20, 12), (23, 4))
    _rect(s, (150, 104, 66), 17, 13, 3, 2)
    return _outline(s)



DUNGEON_TONES = {
    # floor, floor seam, wall, wall light, wall top, accent
    "wind": ((150, 166, 164), (124, 140, 140), (118, 140, 142), (160, 180, 178), (70, 84, 90), (120, 206, 220)),
    "earth": ((146, 108, 78), (118, 86, 62), (112, 84, 64), (150, 116, 86), (64, 48, 42), (250, 200, 110)),
    "fire": ((76, 64, 70), (58, 50, 56), (120, 54, 48), (156, 76, 62), (52, 34, 36), (250, 150, 64)),
    "abyss": ((54, 46, 72), (40, 34, 56), (66, 50, 98), (96, 78, 136), (28, 22, 40), (186, 140, 255)),
    "ice": ((190, 214, 230), (162, 190, 212), (120, 160, 190), (170, 204, 226), (70, 98, 126), (140, 230, 255)),
}



# --- Regional enemies (v0.8.0) -----------------------------------------------------

def _wolf():
    """Forest wolf (16x12): grey coat, pale belly, amber eye, bushy tail."""
    s = _canvas((16, 12))
    fur, dark, light = (128, 134, 146), (88, 94, 108), (196, 200, 206)
    _rect(s, dark, 0, 3, 3, 2)          # tail
    _rect(s, fur, 1, 2, 2, 1)
    _rect(s, fur, 3, 4, 8, 4)           # body
    _rect(s, light, 4, 7, 6, 1)
    _rect(s, dark, 3, 4, 8, 1)
    _rect(s, fur, 10, 2, 4, 4)          # head
    _rect(s, fur, 14, 4, 2, 2)          # snout
    _rect(s, PALETTE["ink"], 15, 4, 1, 1)
    _rect(s, dark, 10, 1, 1, 1)
    _rect(s, dark, 12, 1, 1, 1)
    _rect(s, (238, 176, 64), 12, 3, 1, 1)
    for x in (3, 5, 8, 10):
        _rect(s, dark, x, 8, 1, 3)
    return _outline(s)


def _mushroom():
    """Poison mushroom sprite (16x16): spotted purple cap, sleepy face, stubby feet."""
    s = _canvas()
    cap, cap_dark, spot = (150, 82, 168), (108, 56, 128), (236, 222, 240)
    pygame.draw.ellipse(s, cap_dark, (1, 1, 14, 9))
    pygame.draw.ellipse(s, cap, (1, 1, 14, 7))
    for x, y in ((4, 3), (9, 2), (11, 5), (6, 5)):
        _rect(s, spot, x, y, 2, 1)
    _rect(s, (236, 220, 186), 4, 9, 8, 5)
    _rect(s, (204, 186, 150), 4, 13, 8, 1)
    _rect(s, PALETTE["ink"], 6, 10, 1, 1)
    _rect(s, PALETTE["ink"], 9, 10, 1, 1)
    _rect(s, (190, 96, 120), 7, 12, 2, 1)
    _rect(s, (120, 96, 80), 4, 14, 3, 2)
    _rect(s, (120, 96, 80), 9, 14, 3, 2)
    return _outline(s)


def _scorpion():
    """Red canyon scorpion (16x12): curled stinger tail and two pincers."""
    s = _canvas((16, 12))
    shell, dark, light = (190, 72, 52), (132, 46, 38), (230, 120, 84)
    _rect(s, shell, 4, 6, 8, 3)         # body
    _rect(s, light, 5, 6, 6, 1)
    _rect(s, shell, 11, 2, 2, 5)        # tail rising
    _rect(s, shell, 8, 1, 4, 2)
    _rect(s, (246, 214, 120), 7, 2, 1, 2)  # stinger
    _rect(s, shell, 0, 5, 3, 2)         # pincers
    _rect(s, dark, 0, 7, 2, 1)
    _rect(s, shell, 1, 9, 3, 1)
    _rect(s, PALETTE["ink"], 4, 7, 1, 1)
    for x in (5, 7, 9, 11):
        _rect(s, dark, x, 9, 1, 2)
    return _outline(s)


def _bandit():
    """Canyon bandit (16x20): hood, mask, short blade."""
    s = _canvas((16, 20))
    hood, hood_dark = (110, 78, 58), (78, 54, 42)
    _rect(s, hood, 4, 1, 8, 7)
    _rect(s, (226, 184, 142), 5, 4, 6, 3)
    _rect(s, (60, 54, 62), 5, 6, 6, 2)  # mask
    _rect(s, PALETTE["ink"], 6, 4, 1, 1)
    _rect(s, PALETTE["ink"], 9, 4, 1, 1)
    _rect(s, hood_dark, 3, 8, 10, 7)    # cloak
    _rect(s, (156, 62, 52), 4, 9, 8, 1) # scarf
    _rect(s, (90, 74, 60), 4, 15, 3, 4)
    _rect(s, (90, 74, 60), 9, 15, 3, 4)
    _rect(s, (190, 200, 206), 14, 8, 1, 6)
    _rect(s, (120, 84, 56), 13, 13, 3, 1)
    return _outline(s)


def _salamander():
    """Fire salamander (16x12): orange body, flame crest along the back."""
    s = _canvas((16, 12))
    body, dark, belly = (226, 110, 46), (166, 70, 36), (246, 196, 96)
    _rect(s, body, 0, 7, 3, 2)          # tail
    _rect(s, body, 3, 5, 9, 4)
    _rect(s, belly, 4, 8, 7, 1)
    _rect(s, body, 11, 4, 5, 3)         # head
    _rect(s, PALETTE["ink"], 14, 5, 1, 1)
    for x in (4, 6, 8, 10):
        _rect(s, (250, 210, 80), x, 3, 1, 2)
        _rect(s, (238, 92, 54), x + 1, 4, 1, 1)
    _rect(s, dark, 4, 9, 2, 2)
    _rect(s, dark, 9, 9, 2, 2)
    return _outline(s)


def _magma_slime():
    """Magma slime (16x12): dark crust over glowing lava cracks."""
    s = _canvas((16, 12))
    pygame.draw.ellipse(s, (74, 52, 56), (1, 2, 14, 10))
    pygame.draw.ellipse(s, (120, 70, 60), (2, 2, 12, 8))
    for x, y, w in ((3, 5, 3), (9, 4, 3), (6, 8, 4)):
        _rect(s, (246, 126, 52), x, y, w, 1)
    _rect(s, (255, 214, 96), 4, 3, 2, 1)
    _rect(s, (255, 230, 120), 5, 6, 2, 2)
    _rect(s, (255, 230, 120), 10, 6, 2, 2)
    _rect(s, PALETTE["ink"], 6, 7, 1, 1)
    _rect(s, PALETTE["ink"], 11, 7, 1, 1)
    return _outline(s)


def _bat():
    """Cave bat (16x12): wide wings, small furry body, red eyes."""
    s = _canvas((16, 12))
    wing, wing_light = (76, 62, 96), (112, 92, 138)
    _rect(s, wing, 0, 3, 6, 3)
    _rect(s, wing, 10, 3, 6, 3)
    _rect(s, wing, 1, 6, 2, 1)
    _rect(s, wing, 4, 6, 2, 2)
    _rect(s, wing, 10, 6, 2, 2)
    _rect(s, wing, 13, 6, 2, 1)
    _rect(s, wing_light, 1, 3, 4, 1)
    _rect(s, wing_light, 11, 3, 4, 1)
    _rect(s, (96, 80, 110), 6, 2, 4, 6)  # body
    _rect(s, (96, 80, 110), 6, 1, 1, 1)
    _rect(s, (96, 80, 110), 9, 1, 1, 1)
    _rect(s, (232, 70, 54), 7, 3, 1, 1)
    _rect(s, (232, 70, 54), 8, 3, 1, 1)
    _rect(s, (250, 240, 210), 7, 5, 1, 1)
    return _outline(s)


def _skeleton_warrior():
    """Skeleton soldier (16x20): skull, rib cage, rusty sword and round shield."""
    s = _canvas((16, 20))
    bone, shade = PALETTE["bone"], (178, 170, 148)
    _rect(s, bone, 5, 1, 6, 5)
    _rect(s, shade, 5, 5, 6, 1)
    _rect(s, PALETTE["ink"], 6, 3, 2, 1)
    _rect(s, PALETTE["ink"], 9, 3, 2, 1)
    _rect(s, bone, 7, 6, 2, 1)
    for y in (8, 10, 12):
        _rect(s, bone, 5, y, 6, 1)
    _rect(s, bone, 7, 7, 2, 7)
    _rect(s, bone, 6, 14, 1, 5)
    _rect(s, bone, 9, 14, 1, 5)
    _rect(s, bone, 4, 8, 1, 5)
    _rect(s, bone, 11, 8, 1, 4)
    _rect(s, (150, 120, 100), 12, 4, 1, 8)   # rusty blade
    _rect(s, (110, 80, 60), 11, 11, 3, 1)
    pygame.draw.ellipse(s, (104, 82, 62), (0, 9, 5, 6))
    _rect(s, (160, 130, 90), 2, 11, 1, 2)
    return _outline(s)


def _abyssal(surface, tint=(110, 70, 170), eyes=(255, 190, 120)):
    """Abyss-touched recolour: darken toward ``tint``, keep the outline, light up the eyes.

    The brightest few pixels (eyes, gems, highlights) become glowing ``eyes`` colour."""
    surface = surface.copy()
    outline = PALETTE["outline"]
    w, h = surface.get_size()
    pixels = [(x, y) for y in range(h) for x in range(w) if surface.get_at((x, y)).a >= 200]
    lum = {p: sum(tuple(surface.get_at(p))[:3]) for p in pixels}
    upper = sorted(v for p, v in lum.items() if p[1] < h * 0.5)
    bright = upper[-max(2, len(upper) // 25)] if upper else 999
    for p in pixels:
        r, g, b, a = surface.get_at(p)
        if (r, g, b) == outline:
            continue
        vivid = max(r, g, b) - min(r, g, b) > 70 or lum[p] > 650  # eyes/gems, not grey fur
        if lum[p] >= bright and lum[p] > 300 and vivid and p[1] < h * 0.5:  # glow only on the head
            surface.set_at(p, (*eyes, a))
            continue
        k = lum[p] / 765
        surface.set_at(p, (int(tint[0] * (0.25 + 0.6 * k)), int(tint[1] * (0.25 + 0.6 * k)),
                           int(tint[2] * (0.3 + 0.7 * k)), a))
    return surface


def _dfloor(style, variant):
    floor, seam, *_rest = DUNGEON_TONES[style]
    surface = _canvas()
    surface.fill(floor)
    offset = 4 if variant % 2 else 0
    _rect(surface, seam, 0, 7, 16, 1)
    _rect(surface, seam, 0, 15, 16, 1)
    _rect(surface, seam, (7 + offset) % 16, 0, 1, 7)
    _rect(surface, seam, (11 + offset) % 16, 8, 1, 7)
    light = tuple(min(255, v + 14) for v in floor)
    _rect(surface, light, 1, 1, 4, 1)
    _rect(surface, light, 9, 9, 3, 1)
    rng = random.Random(variant * 31 + len(style))
    if style == "wind" and variant == 1:
        _rect(surface, PALETTE["leaf"], rng.randrange(2, 12), 6, 3, 1)
    elif style == "earth":
        x, y = rng.randrange(2, 12), rng.randrange(2, 12)
        _rect(surface, (176, 140, 104), x, y, 2, 1)
    elif style == "fire" and variant == 2:
        _rect(surface, (40, 32, 38), 3, 11, 5, 1)
        surface.set_at((5, 11), (240, 140, 70))
    return surface


def _dwall(style, face):
    _floor, _seam, wall, light, top, _accent = DUNGEON_TONES[style]
    surface = _canvas()
    if not face:
        surface.fill(top)
        _rect(surface, tuple(min(255, v + 12) for v in top), 0, 0, 16, 1)
        _rect(surface, tuple(min(255, v + 8) for v in top), 3, 6, 4, 1)
        _rect(surface, tuple(min(255, v + 8) for v in top), 10, 11, 3, 1)
        return surface
    surface.fill(PALETTE["outline"])
    _rect(surface, top, 0, 0, 16, 3)
    _rect(surface, light, 0, 3, 16, 1)
    for row, y in enumerate((4, 8, 12)):
        off = 4 if row % 2 else 0
        for x in range(-off, 16, 8):
            _rect(surface, wall, x + 1, y, 7, 3)
            _rect(surface, light, x + 1, y, 6, 1)
    if style == "earth":
        _rect(surface, PALETTE["outline"], 6, 3, 4, 13)
        _rect(surface, (150, 104, 66), 7, 3, 2, 13)
    _rect(surface, (30, 22, 26), 0, 15, 16, 1)
    return surface


def _wall_torch(style):
    accent = DUNGEON_TONES[style][5]
    surface = _canvas()
    _rect(surface, PALETTE["outline"], 6, 7, 4, 6)
    _rect(surface, (120, 84, 60), 7, 7, 2, 5)
    _rect(surface, PALETTE["outline"], 5, 6, 6, 2)
    pygame.draw.polygon(surface, accent, ((5, 6), (8, 0), (11, 6)))
    pygame.draw.polygon(surface, (255, 236, 180), ((7, 6), (8, 3), (9, 6)))
    return surface


def _dstairs():
    surface = _canvas()
    surface.fill(PALETTE["outline"])
    for step in range(4):
        y = 2 + step * 3
        shade = 150 - step * 22
        _rect(surface, (shade, shade - 6, shade - 10), 2 + step, y, 12 - step * 2, 2)
        _rect(surface, (shade + 30, shade + 24, shade + 18), 2 + step, y, 12 - step * 2, 1)
    _rect(surface, (20, 16, 20), 6, 14, 4, 2)
    return surface


def sprite(name, size=(32, 32)):
    """Return a cached pixel sprite, enlarged with nearest-neighbor sampling."""
    if name not in _BASE and name.startswith(("trail_", "water_edge_")):
        parts = name.split("_")
        mask, variant = int(parts[-2]), int(parts[-1])
        kind = "water" if name.startswith("water_edge_") else "path"
        _BASE[name] = _terrain_overlay(mask, kind, variant)
    elif name not in _BASE and name.startswith(("lava_edge_", "ice_edge_")):
        parts = name.split("_")
        _BASE[name] = _terrain_overlay(int(parts[-2]), parts[0], int(parts[-1]))
    elif name not in _BASE and name.startswith(("grass_", "canyon_", "ash_", "snow_", "rock_", "basalt_", "mossrock_",
                                                 "icerock_")):
        prefix, number = name.rsplit("_", 1)
        builder = {"grass": _grass, "canyon": _canyon, "ash": _ash, "snow": _snow, "rock": _rock,
                   "basalt": lambda v: _rock(v, "basalt"), "mossrock": lambda v: _rock(v, "mossrock"),
                   "icerock": lambda v: _rock(v, "icerock")}[prefix]
        _BASE[name] = builder(int(number))
    if name not in _BASE and name.startswith(("dfloor_", "dwall_", "wall_torch_")):
        parts = name.split("_")
        if parts[0] == "dfloor":
            _BASE[name] = _dfloor(parts[1], int(parts[2]))
        elif parts[0] == "dwall":
            _BASE[name] = _dwall(parts[2], parts[1] == "face")
        else:
            _BASE[name] = _wall_torch(parts[2])
    if name not in _BASE:
        builders = {
            "player": _player,
            "slime": _slime_v2,
            "goblin": _goblin,
            "harpy": _harpy,
            "golem": _golem,
            "lizardman": _lizardman,
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
            "tree_round": _tree,
            "tree_fruit": lambda: _tree("fruit"),
            "tree_pine": lambda: _tree("pine"),
            "bush": _bush,
            "flower_patch": _flower_patch,
            "flower_patch_1": lambda: _flower_patch(1),
            "pebbles": _pebbles,
            "shadow": _shadow,
            "fence": _fence,
            "fence_v": lambda: _fence(True),
            "barrel": _barrel,
            "gate_arch": _gate_arch,
            "crops": _crops,
            "dstairs": _dstairs,
            "rock": _rock,
            "tuft": lambda: _tuft_decal("green"),
            "dry_tuft": lambda: _tuft_decal("dry"),
            "ember": _ember,
            "portal_town": lambda: _portal("town"),
            "portal_dungeon": lambda: _portal("dungeon"),
            "portal_dungeon_0": lambda: _portal("dungeon", 0),
            "portal_dungeon_1": lambda: _portal("dungeon", 1),
            "chief": _npc_chief,
            "old_knight": _npc_old_knight,
            "merchant": _npc_merchant,
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
            "shopkeeper": _npc_shopkeeper,
            "villager": _npc_herbalist,
            "townsfolk": _npc_townsfolk,
            "skeleton": _skeleton,
            "shadow_wolf": lambda: _abyssal(pygame.transform.flip(_wolf(), True, False)),
            "void_slime": lambda: _abyssal(_slime_v2(), (60, 150, 170)),
            "abyss_knight": lambda: _abyssal(_dark_knight(), (120, 70, 190)),
            "abyss_lord": lambda: _abyssal(_golem(), (150, 60, 210), eyes=(255, 120, 230)),
            "frost_wolf": lambda: _frosted(pygame.transform.flip(_wolf(), True, False)),
            "hunter": _npc_hunter,
            "innkeeper": _npc_innkeeper,
            "blacksmith": _npc_blacksmith,
            "librarian": _npc_librarian,
            "apothecary": _npc_apothecary,
            "child": _npc_child,
            "ice_slime": lambda: _frosted(_slime_v2()),
            "frost_wisp": _frost_wisp,
            "frost_lizard": lambda: _frosted(_lizardman(), eyes=(90, 210, 255)),
            "tree_snowpine": lambda: _snowcap(_tree("pine")),
            "wolf": lambda: pygame.transform.flip(_wolf(), True, False),
            "mushroom": _mushroom,
            "scorpion": _scorpion,
            "bandit": _bandit,
            "salamander": lambda: pygame.transform.flip(_salamander(), True, False),
            "magma_slime": _magma_slime,
            "bat": _bat,
            "skeleton_warrior": _skeleton_warrior,
        }
        _BASE[name] = builders[name]()
    key = (name, tuple(size)) if size else (name, None)
    if key not in _SCALED:
        original = _BASE[name]
        _SCALED[key] = original.copy() if size is None else pygame.transform.scale(original, size)
    return _SCALED[key]


def hero_sprite(weapon="rusty_sword", armor="traveler_clothes", size=(32, 32), direction="down", frame=0):
    """Return the player sprite with the currently equipped gear visible."""
    key = (weapon, armor, tuple(size), direction, frame % 4)
    if key not in _HERO_SCALED:
        _HERO_SCALED[key] = pygame.transform.scale(_player(weapon, armor, direction, frame), size)
    return _HERO_SCALED[key]


def fit_sprite(name, box):
    """Scale a sprite by the largest integer factor that fits ``box``, keeping proportions."""
    base = sprite(name, None)
    w, h = base.get_size()
    factor = max(1, min(box[0] // w, box[1] // h))
    return sprite(name, (w * factor, h * factor))


# --- Idle animation for standing NPCs -------------------------------------------------
_POSES = {}


def idle_pose(clock, seed=0):
    """Which idle pose to show: a slow breath every 2.4s and a quick blink every 3.7s."""
    phase = clock + seed * 0.73
    if phase % 3.7 < 0.15:
        return "blink"
    return "breath" if phase % 2.4 >= 1.2 else "rest"


def npc_pose(name, pose):
    """Unscaled NPC sprite in an idle pose: rest, breath (head dips 1px) or blink."""
    key = (name, pose)
    if key not in _POSES:
        base = sprite(name, None)
        image = base.copy()
        if pose == "breath":
            image.fill((0, 0, 0, 0), pygame.Rect(0, 0, image.get_width(), 12))
            image.blit(base, (0, 1), pygame.Rect(0, 0, image.get_width(), 12))
        elif pose == "blink":
            lid = base.get_at((7, 8))
            for x in (6, 9):
                if tuple(base.get_at((x, 8)))[:3] == PALETTE["ink"]:
                    image.set_at((x, 8), lid)
        _POSES[key] = image
    return _POSES[key]


def npc_sprite(name, size, clock=0.0, seed=0):
    """NPC sprite scaled to ``size`` in the idle pose for ``clock``."""
    pose = idle_pose(clock, seed)
    key = (name, pose, tuple(size))
    if key not in _POSES:
        _POSES[key] = pygame.transform.scale(npc_pose(name, pose), size)
    return _POSES[key]


# --- Idle animation for enemies (battle screen, dungeon bosses) -----------------------
IDLE_STYLES = {"slime": "squash", "magma_slime": "squash", "mushroom": "squash",
               "bat": "hover", "harpy": "hover"}  # everyone else breathes


def _enemy_pose(name, pose):
    """Unscaled enemy sprite: rest, squash (1px shorter, 2px wider) or breath (top dips 1px)."""
    key = ("enemy", name, pose)
    if key not in _POSES:
        base = sprite(name, None)
        w, h = base.get_size()
        if pose == "squash":
            image = pygame.transform.scale(base, (w + 2, h - 1))
        elif pose == "breath":
            cut = int(h * 0.6)
            image = base.copy()
            image.fill((0, 0, 0, 0), pygame.Rect(0, 0, w, cut))
            image.blit(base, (0, 1), pygame.Rect(0, 0, w, cut))
        else:
            image = base
        _POSES[key] = image
    return _POSES[key]


def enemy_idle(name, box, clock):
    """Return ``(surface, dy)`` for an idle enemy; blit the surface with its feet at the
    same baseline (``feet - height``) and add ``dy`` (hovering creatures bob)."""
    base = fit_sprite(name, box)
    factor = base.get_width() // sprite(name, None).get_width()
    style = IDLE_STYLES.get(name, "breathe")
    if style == "hover":
        return base, factor * round(1.5 * math.sin(clock * 4))
    on = (clock % 0.8 >= 0.4) if style == "squash" else (clock % 1.2 >= 0.6)
    if not on:
        return base, 0
    pose = "squash" if style == "squash" else "breath"
    key = ("enemy_scaled", name, pose, factor)
    if key not in _POSES:
        raw = _enemy_pose(name, pose)
        _POSES[key] = pygame.transform.scale(raw, (raw.get_width() * factor, raw.get_height() * factor))
    return _POSES[key], 0

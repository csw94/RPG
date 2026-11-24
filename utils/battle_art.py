"""Painted battle backdrops (800x374) that match where the fight happens.

Each scene is painted on a 400x187 canvas and doubled, so it shares the chunky
2x pixel look of the overworld. Both fighters stand on soft ground platforms.
"""

import math
import random

import pygame

from utils.pixel_art import PALETTE

KINDS = ("forest", "canyon", "volcanic", "village", "snow", "dungeon_wind", "dungeon_earth", "dungeon_fire",
         "dungeon_ice", "dungeon_abyss")
W, H = 400, 187
HERO_SPOT, ENEMY_SPOT, FEET_Y = 119, 299, 152
_CACHE = {}

OUTDOOR = {
    # sky bands (top->horizon), far layer, near layer, ground, ground accent, platform
    "forest": (((146, 204, 228), (166, 214, 232), (190, 226, 234)), (126, 176, 134), (78, 140, 92),
               (110, 168, 82), (146, 196, 98), (88, 142, 70)),
    "canyon": (((232, 178, 132), (240, 198, 152), (246, 218, 178)), (204, 146, 108), (170, 104, 80),
               (186, 118, 82), (204, 140, 98), (162, 98, 70)),
    "volcanic": (((70, 52, 66), (100, 66, 74), (146, 86, 76)), (88, 70, 80), (60, 50, 60),
                 (98, 86, 90), (118, 106, 108), (80, 70, 76)),
    "village": (((64, 66, 118), (122, 92, 140), (222, 144, 120)), (92, 74, 104), (58, 48, 72),
                (92, 144, 76), (124, 176, 90), (74, 120, 64)),
    "snow": (((168, 196, 222), (196, 216, 234), (224, 234, 244)), (176, 194, 214), (132, 156, 180),
             (226, 234, 242), (246, 250, 254), (196, 210, 226)),
}
DUNGEON = {
    # wall, wall light, mortar, floor, floor line, accent
    "dungeon_wind": ((118, 140, 142), (154, 176, 174), (86, 104, 108), (150, 166, 164), (124, 140, 140), (120, 206, 220)),
    "dungeon_earth": ((112, 84, 64), (146, 112, 84), (80, 58, 46), (140, 104, 76), (116, 84, 62), (250, 200, 110)),
    "dungeon_fire": ((112, 50, 46), (146, 70, 58), (76, 34, 34), (72, 62, 68), (56, 48, 54), (250, 150, 64)),
    "dungeon_abyss": ((58, 44, 86), (84, 66, 120), (38, 28, 58), (46, 38, 66), (34, 28, 50), (186, 140, 255)),
    "dungeon_ice": ((132, 170, 198), (176, 206, 226), (96, 130, 160), (184, 208, 226), (156, 186, 210), (140, 230, 255)),
}


def _bands(c, colors, bottom):
    step = bottom / len(colors)
    for i, color in enumerate(colors):
        pygame.draw.rect(c, color, (0, round(i * step), W, math.ceil(step) + 1))


def _ridge(c, color, base_y, amplitude, period, phase, top_flat=False):
    points = [(0, H)]
    for x in range(0, W + 8, 8):
        y = base_y - amplitude * (0.5 + 0.5 * math.sin(x / period + phase))
        if top_flat:
            y = base_y - amplitude * (1 if math.sin(x / period + phase) > 0.2 else 0.25)
        points.append((x, round(y)))
    points.append((W, H))
    pygame.draw.polygon(c, color, points)


def _platform(c, x, fill):
    rim = tuple(max(0, v - 28) for v in fill)
    light = tuple(min(255, v + 22) for v in fill)
    pygame.draw.ellipse(c, rim, (x - 38, FEET_Y - 8, 76, 18))
    pygame.draw.ellipse(c, fill, (x - 36, FEET_Y - 8, 72, 15))
    pygame.draw.line(c, light, (x - 22, FEET_Y - 6), (x + 18, FEET_Y - 6))


def _outdoor(kind):
    sky, far, near, ground, accent, platform = OUTDOOR[kind]
    c = pygame.Surface((W, H))
    horizon = 112
    _bands(c, sky, horizon)
    rng = random.Random(kind)
    if kind == "village":
        for _ in range(26):
            c.set_at((rng.randrange(W), rng.randrange(60)), (250, 240, 210))
        pygame.draw.circle(c, (248, 236, 200), (330, 30), 10)
        pygame.draw.circle(c, sky[0], (334, 27), 9)
    elif kind == "volcanic":
        pygame.draw.polygon(c, far, ((150, horizon), (230, 34), (262, 34), (350, horizon)))
        pygame.draw.polygon(c, (226, 110, 54), ((230, 34), (262, 34), (252, 46), (238, 46)))
        for i, (x, y, r) in enumerate(((246, 22, 9), (258, 12, 7), (236, 8, 6))):
            pygame.draw.circle(c, (110, 96, 104), (x, y), r)
    else:
        pygame.draw.circle(c, (255, 244, 200), (64, 30), 12)
        for x, y, w in ((110, 26, 46), (270, 44, 56), (196, 18, 30)):
            pygame.draw.rect(c, (250, 250, 244), (x, y, w, 6))
            pygame.draw.rect(c, (250, 250, 244), (x + 6, y - 4, w - 12, 4))
            pygame.draw.rect(c, tuple(min(255, v + 10) for v in sky[1]), (x + 4, y + 6, w - 8, 2))
    _ridge(c, far, horizon - 6, 26, 37, 1.3, top_flat=(kind == "canyon"))
    if kind == "forest":
        for x in range(-6, W + 12, 14):
            r = 9 + (x * 7) % 5
            pygame.draw.circle(c, PALETTE["outline"], (x, horizon - 2), r + 1)
            pygame.draw.circle(c, near, (x, horizon - 2), r)
            pygame.draw.circle(c, (98, 160, 100), (x - 3, horizon - 5), r // 2)
    elif kind == "village":
        x = 8
        while x < W:
            w, h = 34 + (x * 13) % 18, 20 + (x * 7) % 12
            pygame.draw.rect(c, near, (x, horizon - h, w, h + 4))
            pygame.draw.polygon(c, near, ((x - 4, horizon - h), (x + w // 2, horizon - h - 14), (x + w + 4, horizon - h)))
            pygame.draw.rect(c, (250, 210, 120), (x + 8, horizon - h + 6, 5, 5))
            pygame.draw.rect(c, (250, 210, 120), (x + w - 14, horizon - h + 6, 5, 5))
            x += w + 14
    else:
        _ridge(c, near, horizon + 2, 14, 23, 0.4, top_flat=(kind == "canyon"))
    pygame.draw.rect(c, ground, (0, horizon, W, H - horizon))
    pygame.draw.line(c, accent, (0, horizon), (W, horizon))
    for _ in range(70):
        x, y = rng.randrange(W), rng.randrange(horizon + 4, H)
        pygame.draw.line(c, accent if rng.random() < 0.6 else platform, (x, y), (x + 2, y))
    if kind == "volcanic":
        for _ in range(6):
            x, y = rng.randrange(W), rng.randrange(horizon + 10, H - 6)
            pygame.draw.line(c, (40, 34, 40), (x, y), (x + 9, y + 2))
            c.set_at((x + 4, y + 1), (240, 140, 70))
    _platform(c, HERO_SPOT, platform)
    _platform(c, ENEMY_SPOT, platform)
    return c


def _dungeon(kind):
    wall, wall_light, mortar, floor, floor_line, accent = DUNGEON[kind]
    c = pygame.Surface((W, H))
    horizon = 118
    c.fill(mortar, (0, 0, W, horizon))
    for row, y in enumerate(range(0, horizon, 10)):
        offset = 10 if row % 2 else 0
        for x in range(-offset, W, 20):
            pygame.draw.rect(c, wall, (x + 1, y + 1, 18, 8))
            pygame.draw.line(c, wall_light, (x + 1, y + 1), (x + 17, y + 1))
    if kind == "dungeon_earth":
        for x in (40, 200, 360):
            pygame.draw.rect(c, PALETTE["outline"], (x - 6, 0, 12, horizon))
            pygame.draw.rect(c, (150, 104, 66), (x - 5, 0, 10, horizon))
            pygame.draw.line(c, (190, 140, 90), (x - 4, 0), (x - 4, horizon))
        pygame.draw.rect(c, PALETTE["outline"], (0, 14, W, 9))
        pygame.draw.rect(c, (150, 104, 66), (0, 15, W, 7))
    else:
        for x in (60, 340):
            pygame.draw.rect(c, PALETTE["outline"], (x - 13, 0, 26, horizon))
            pygame.draw.rect(c, wall_light, (x - 12, 0, 24, horizon))
            pygame.draw.rect(c, wall, (x - 4, 0, 14, horizon))
    if kind == "dungeon_wind":
        for x in (150, 250):
            pygame.draw.rect(c, PALETTE["outline"], (x - 9, 8, 18, 46))
            pygame.draw.rect(c, (70, 130, 140), (x - 8, 9, 16, 40))
            pygame.draw.polygon(c, (70, 130, 140), ((x - 8, 49), (x + 8, 49), (x, 56)))
            pygame.draw.circle(c, (226, 190, 100), (x, 26), 4, 1)
    glow = pygame.Surface((W, H), pygame.SRCALPHA)
    lights = (110, 290) if kind != "dungeon_earth" else (120, 280)
    for x in lights:
        for r, a in ((34, 30), (20, 50), (10, 90)):
            pygame.draw.circle(glow, (*accent, a), (x, 54), r)
        pygame.draw.rect(c, PALETTE["outline"], (x - 3, 58, 6, 14))
        pygame.draw.rect(c, (120, 84, 60), (x - 2, 58, 4, 13))
        pygame.draw.polygon(c, accent, ((x - 4, 58), (x, 46), (x + 4, 58)))
        pygame.draw.polygon(c, (255, 236, 180), ((x - 2, 58), (x, 51), (x + 2, 58)))
    c.blit(glow, (0, 0))
    pygame.draw.rect(c, floor, (0, horizon, W, H - horizon))
    pygame.draw.line(c, PALETTE["outline"], (0, horizon), (W, horizon), 2)
    for y in range(horizon + 12, H, 14):
        pygame.draw.line(c, floor_line, (0, y), (W, y))
    for x in range(-200, W + 200, 40):
        pygame.draw.line(c, floor_line, (W // 2 + (x - W // 2) * 0.5, horizon), (x, H))
    if kind == "dungeon_fire":
        rng = random.Random(kind)
        for _ in range(7):
            x, y = rng.randrange(W), rng.randrange(horizon + 8, H - 4)
            pygame.draw.line(c, (230, 110, 50), (x, y), (x + 8, y + 1))
    _platform(c, HERO_SPOT, tuple(min(255, v + 10) for v in floor))
    _platform(c, ENEMY_SPOT, tuple(min(255, v + 10) for v in floor))
    return c


def backdrop(kind):
    if kind not in KINDS:
        kind = "forest"
    if kind not in _CACHE:
        canvas = _dungeon(kind) if kind.startswith("dungeon_") else _outdoor(kind)
        _CACHE[kind] = pygame.transform.scale(canvas, (W * 2, H * 2))
    return _CACHE[kind]

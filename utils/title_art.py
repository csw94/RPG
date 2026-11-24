"""Title screen backdrop: Oak Valley at night, painted at 400x300 and doubled.

The hero stands on a hilltop in front of the star fountain's light beam; the
village glows below and the meadow fills the lower half where the menu sits.
``draw_overlay`` adds the animated bits (twinkling stars, drifting fireflies).
"""

import math
import random

import pygame

from utils.pixel_art import PALETTE

W, H = 400, 300
HORIZON = 150          # canvas y of the far horizon (screen y = 300)
HILL_TOP = 135         # canvas y where the hero's feet rest (screen y = 270)
_CACHE = {}

SKY = ((18, 20, 50), (30, 30, 72), (48, 42, 94), (78, 58, 112), (122, 80, 126), (176, 110, 126))
OUTLINE = PALETTE["outline"]


def _sky(c):
    step = HORIZON / len(SKY)
    for i, color in enumerate(SKY):
        pygame.draw.rect(c, color, (0, round(i * step), W, math.ceil(step) + 1))
    rng = random.Random(7)
    for _ in range(70):
        x, y = rng.randrange(W), rng.randrange(int(HORIZON * 0.7))
        c.set_at((x, y), (150, 150, 190) if rng.random() < 0.7 else (220, 220, 240))
    # Crescent moon with a soft halo.
    halo = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.circle(halo, (240, 230, 200, 26), (30, 30), 21)
    pygame.draw.circle(halo, (240, 230, 200, 44), (30, 30), 16)
    c.blit(halo, (318, 14))
    pygame.draw.circle(c, (246, 236, 204), (348, 44), 12)
    pygame.draw.circle(c, SKY[1], (353, 40), 10)


def _ridge(c, color, base, amplitude, period, phase):
    points = [(0, H)]
    for x in range(0, W + 8, 8):
        points.append((x, round(base - amplitude * (0.5 + 0.5 * math.sin(x / period + phase)))))
    points.append((W, H))
    pygame.draw.polygon(c, color, points)


def _village(c):
    roof, wall, window = (40, 34, 62), (52, 44, 74), (252, 206, 120)
    houses = ((22, 22, 16), (52, 30, 22), (92, 24, 18), (122, 20, 14), (268, 22, 16), (298, 28, 22),
              (336, 24, 18), (366, 20, 14))
    for x, w, h in houses:
        top = HORIZON - h
        pygame.draw.rect(c, wall, (x, top, w, h + 4))
        pygame.draw.polygon(c, roof, ((x - 3, top), (x + w // 2, top - 10), (x + w + 3, top)))
        for wx in range(x + 4, x + w - 4, 9):
            pygame.draw.rect(c, window, (wx, top + 5, 3, 3))
        if w > 20:
            pygame.draw.rect(c, roof, (x + w - 7, top - 12, 4, 8))


def _beam(c):
    beam = pygame.Surface((W, H), pygame.SRCALPHA)
    for width, alpha in ((44, 26), (26, 40), (10, 70)):
        pygame.draw.rect(beam, (210, 232, 255, alpha), (200 - width // 2, 0, width, HILL_TOP))
    pygame.draw.circle(beam, (230, 242, 255, 50), (200, HILL_TOP - 30), 34)
    c.blit(beam, (0, 0))


def _meadow(c):
    bands = ((52, 92, 70), (60, 104, 72), (70, 118, 76), (80, 130, 80))
    step = (H - HORIZON) / len(bands)
    for i, color in enumerate(bands):
        pygame.draw.rect(c, color, (0, HORIZON + round(i * step), W, math.ceil(step) + 1))
    # The hill the hero stands on.
    pygame.draw.ellipse(c, (40, 74, 58), (120, HILL_TOP - 2, 160, 46))
    pygame.draw.ellipse(c, (62, 110, 74), (122, HILL_TOP, 156, 44))
    pygame.draw.line(c, (96, 150, 92), (160, HILL_TOP + 3), (238, HILL_TOP + 3))
    # A moonlit path winding down to the bottom right.
    path = (150, 124, 96)
    points = [(212, HILL_TOP + 14), (226, 190), (250, 240), (262, H)]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        for s in range(0, 21):
            k = s / 20
            x, y = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
            r = 3 + (y - HILL_TOP) / 40
            pygame.draw.circle(c, path, (round(x), round(y)), round(r))
    rng = random.Random(11)
    tones = ((96, 150, 92), (46, 84, 62))
    for _ in range(160):
        x, y = rng.randrange(W), rng.randrange(HORIZON + 4, H)
        pygame.draw.line(c, rng.choice(tones), (x, y), (x + 1, y))
    for _ in range(46):
        x, y = rng.randrange(W), rng.randrange(HORIZON + 20, H)
        if abs(x - 200) < 6 and abs(y - 235) < 6:
            continue
        c.set_at((x, y), rng.choice(((236, 214, 232), (246, 216, 120), (200, 200, 250))))


def _trees(c):
    for cx, base, scale in ((14, 214, 1.3), (46, 190, 1.0), (386, 210, 1.3), (356, 186, 1.0), (82, 176, 0.8),
                            (322, 172, 0.8)):
        r = round(18 * scale)
        pygame.draw.rect(c, (30, 24, 30), (cx - 3, base - 4, 6, round(20 * scale)))
        for dx, dy, rr in ((0, -r, r), (-r // 2, -r // 3, r * 3 // 4), (r // 2, -r // 3, r * 3 // 4)):
            pygame.draw.circle(c, OUTLINE, (cx + dx, base + dy), rr + 1)
            pygame.draw.circle(c, (34, 66, 58), (cx + dx, base + dy), rr)
            pygame.draw.circle(c, (46, 86, 68), (cx + dx - rr // 3, base + dy - rr // 3), rr // 2)


def backdrop():
    if "title" not in _CACHE:
        c = pygame.Surface((W, H))
        _sky(c)
        _ridge(c, (60, 50, 92), HORIZON - 8, 22, 41, 0.7)
        _ridge(c, (48, 44, 78), HORIZON - 2, 12, 23, 2.1)
        _village(c)
        _beam(c)
        _meadow(c)
        _trees(c)
        _CACHE["title"] = pygame.transform.scale(c, (W * 2, H * 2))
    return _CACHE["title"]


_TWINKLES = [(random.Random(n).randrange(4, 796), random.Random(n * 7 + 1).randrange(4, 200), n) for n in range(24)]


def draw_overlay(surface, clock):
    """Animated layer drawn over the cached backdrop each frame."""
    for x, y, n in _TWINKLES:
        glow = 0.5 + 0.5 * math.sin(clock * (1.4 + n % 5 * 0.3) + n)
        if glow > 0.35:
            color = (220 + round(35 * glow), 220 + round(30 * glow), 255)
            pygame.draw.rect(surface, color, (x, y, 2, 2))
            if glow > 0.85:
                pygame.draw.rect(surface, (190, 196, 240), (x - 2, y, 6, 2))
                pygame.draw.rect(surface, (190, 196, 240), (x, y - 2, 2, 6))
    layer = pygame.Surface((800, 600), pygame.SRCALPHA)
    for n in range(14):
        fx = (n * 131 + math.sin(clock * 0.6 + n) * 40 + clock * 9 * (1 if n % 2 else -1)) % 800
        fy = 330 + (n * 53) % 200 + math.sin(clock * 1.1 + n * 1.7) * 14
        pulse = 0.5 + 0.5 * math.sin(clock * 3 + n * 2.1)
        pygame.draw.circle(layer, (230, 250, 140, round(60 * pulse)), (round(fx), round(fy)), 7)
        pygame.draw.rect(layer, (250, 255, 190, round(140 + 115 * pulse)), (round(fx) - 1, round(fy) - 1, 3, 3))
    surface.blit(layer, (0, 0))

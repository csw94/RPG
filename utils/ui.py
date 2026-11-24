"""Shared cozy UI: wood-framed panels with parchment or walnut bodies, bars and buttons.

Parchment bodies hold dark ink text (HUD, dialogue); walnut bodies keep the light cream
text the menus already use (title, shop, battle).
"""

import pygame

from utils.pixel_art import PALETTE

OUTLINE = PALETTE["outline"]
WOOD, WOOD_LIGHT, WOOD_DARK = (150, 104, 66), (196, 146, 94), (108, 70, 48)
PARCHMENT, PARCHMENT_SHADE = (240, 226, 190), (220, 200, 158)
WALNUT, WALNUT_SHADE = (72, 52, 44), (58, 42, 38)
BRASS, BRASS_LIGHT = (214, 172, 88), (246, 214, 140)
INK, INK_SOFT = (62, 44, 40), (122, 92, 70)
GOLD_TRIM = (226, 190, 100)
BORDER = 5


def frame(surface, rect, kind="parchment", active=False, border=BORDER):
    """Draw a wooden frame filling ``rect``; return the inner body rect."""
    rect = pygame.Rect(rect)
    pygame.draw.rect(surface, OUTLINE, rect, border_radius=4)
    wood = rect.inflate(-2, -2)
    pygame.draw.rect(surface, WOOD, wood, border_radius=3)
    pygame.draw.line(surface, WOOD_LIGHT, (wood.left + 3, wood.top + 1), (wood.right - 4, wood.top + 1))
    pygame.draw.line(surface, WOOD_DARK, (wood.left + 3, wood.bottom - 2), (wood.right - 4, wood.bottom - 2))
    if active:
        pygame.draw.rect(surface, GOLD_TRIM, wood, 1, border_radius=3)
    body = rect.inflate(-2 * border, -2 * border)
    pygame.draw.rect(surface, OUTLINE, body.inflate(2, 2))
    fill, shade = (PARCHMENT, PARCHMENT_SHADE) if kind == "parchment" else (WALNUT, WALNUT_SHADE)
    pygame.draw.rect(surface, fill, body)
    pygame.draw.line(surface, shade, (body.left, body.top), (body.right - 1, body.top))
    pygame.draw.line(surface, shade, (body.left, body.top), (body.left, body.bottom - 1))
    # Brass nails in the four corners of the wooden border.
    if rect.width > 40 and rect.height > 24:
        for x, y in ((rect.left + 2, rect.top + 2), (rect.right - 4, rect.top + 2),
                     (rect.left + 2, rect.bottom - 4), (rect.right - 4, rect.bottom - 4)):
            pygame.draw.rect(surface, BRASS, (x, y, 2, 2))
            surface.set_at((x, y), BRASS_LIGHT)
    return body


def frame_around(surface, content, kind="walnut", active=False, border=BORDER):
    """Frame drawn just outside ``content`` so existing layouts keep their space."""
    return frame(surface, pygame.Rect(content).inflate(2 * border + 2, 2 * border + 2), kind, active, border)


def bar(surface, rect, value, maximum, color):
    rect = pygame.Rect(rect)
    pygame.draw.rect(surface, OUTLINE, rect)
    inner = rect.inflate(-2, -2)
    pygame.draw.rect(surface, (92, 70, 62), inner)
    fill = round(inner.width * max(0, value) / maximum) if maximum else 0
    if fill:
        pygame.draw.rect(surface, color, (inner.x, inner.y, fill, inner.height))
        light = tuple(min(255, c + 50) for c in color)
        pygame.draw.line(surface, light, (inner.x, inner.y), (inner.x + fill - 1, inner.y))


def coin(surface, center):
    x, y = center
    pygame.draw.circle(surface, OUTLINE, (x, y), 7)
    pygame.draw.circle(surface, BRASS, (x, y), 6)
    pygame.draw.circle(surface, BRASS_LIGHT, (x - 1, y - 1), 3)
    pygame.draw.line(surface, WOOD_DARK, (x, y - 3), (x, y + 3))


def plank_strip(surface, rect):
    """Dark wooden boards behind the bottom HUD."""
    rect = pygame.Rect(rect)
    pygame.draw.rect(surface, (52, 38, 38), rect)
    for y in range(rect.top + 10, rect.bottom, 11):
        pygame.draw.line(surface, (40, 29, 30), (rect.left, y), (rect.right, y))
    pygame.draw.line(surface, (96, 70, 58), rect.topleft, rect.topright, 2)


def button(surface, font, rect, label, selected=False, size=22):
    rect = pygame.Rect(rect)
    body = frame(surface, rect.inflate(6, 6), "walnut", selected, border=4)
    if selected:
        pygame.draw.rect(surface, BRASS, body)
        pygame.draw.line(surface, BRASS_LIGHT, body.topleft, (body.right - 1, body.top))
    image = font(size).render(str(label), True, INK if selected else (242, 222, 177))
    surface.blit(image, image.get_rect(center=rect.center))

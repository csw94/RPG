"""Village houses built from parts: wall material, roof shape, windows, door and props.

``paint_house(surface, x, y, style)`` paints one building whose canvas origin is the pixel
(x, y). Everything stays inside (x - 10, y - 10, width + 24, 214); the village crops that box
and scales it down to 80%. The front door is always centred so the door tiles line up.
"""

import math
import pygame

OUTLINE = (54, 40, 46)
GLASS = (93, 151, 163)
GLASS_LIGHT = (156, 204, 206)
WOOD_DARK = (77, 48, 39)
GOLD = (245, 194, 74)

WALLS = ("plank", "log", "plaster", "timber", "stone", "brick")
ROOF_SHAPES = ("gable", "hip", "gambrel", "thatch")

# Roof colours: (base, row line, seam, bright eave). Wall colours: (base, light, dark).
HOUSE_STYLES = {
    # Marta's herb cottage: a round straw roof over cream plaster, shutters and drying herbs.
    "herb_cottage": {
        "width": 5, "roof": "thatch", "roof_colors": ((198, 158, 84), (228, 192, 112), (146, 108, 58), (238, 210, 136)),
        "wall": "plaster", "wall_colors": ((236, 220, 184), (248, 238, 212), (196, 172, 136)),
        "chimney": ("left", "stone"), "smoke": True, "windows": "shuttered", "trim": (84, 132, 92),
        "door": "arched", "props": ("planters", "herbs"),
    },
    # Old knight Garen's quarters: a lopsided gable over sturdy planks, his shield above the door.
    "knight_quarters": {
        "width": 7, "roof": "gable", "apex": 0.62,
        "roof_colors": ((166, 98, 62), (200, 130, 84), (128, 72, 50), (226, 164, 106)),
        "wall": "plank", "wall_colors": ((180, 130, 84), (204, 152, 98), (96, 64, 46)),
        "chimney": ("right", "brick"), "windows": "square", "trim": (211, 177, 115),
        "door": "double", "props": ("shield", "weapon_rack", "barrel"),
    },
    # The Sleepy Bear inn: two storeys, a timber-framed upper floor with a balcony.
    "inn": {
        "width": 7, "stories": 2, "roof": "gable", "apex": 0.5,
        "roof_colors": ((96, 128, 74), (128, 160, 98), (72, 100, 58), (170, 200, 128)),
        "wall": "log", "wall_colors": ((150, 100, 62), (186, 132, 82), (100, 64, 44)),
        "upper_wall": "timber", "upper_colors": ((238, 224, 192), (250, 242, 220), (92, 58, 42)),
        "chimney": ("right", "brick"), "smoke": True, "windows": "square", "trim": (211, 177, 115),
        "door": "plank", "props": ("balcony", "lantern", "barrel"),
    },
    # Bron's smithy: squat stone walls under a slate hip roof, a forge glowing in the window.
    "smithy": {
        "width": 5, "roof": "hip",
        "roof_colors": ((86, 90, 104), (118, 122, 136), (62, 64, 78), (150, 154, 168)),
        "wall": "stone", "wall_colors": ((132, 128, 126), (168, 164, 158), (92, 88, 90)),
        "chimney": ("right", "stone_big"), "smoke": True, "windows": "forge", "trim": (82, 70, 64),
        "door": "double", "props": ("anvil", "firewood"),
    },
    # The Starlight library: brick under a blue mansard roof, arched windows and a round oculus.
    "library": {
        "width": 7, "roof": "gambrel",
        "roof_colors": ((64, 82, 140), (92, 112, 172), (48, 60, 108), (136, 156, 210)),
        "wall": "brick", "wall_colors": ((168, 92, 70), (204, 130, 98), (120, 66, 54)),
        "chimney": None, "windows": "arched", "trim": (226, 214, 182),
        "door": "arched_double", "props": ("banners", "oculus"),
    },
    # Mira's apothecary: white half-timbering, a steep purple clay roof and potted flowers.
    "apothecary": {
        "width": 5, "roof": "gable", "apex": 0.5, "steep": True, "tiles": "clay",
        "roof_colors": ((128, 84, 144), (160, 112, 176), (98, 62, 112), (196, 150, 210)),
        "wall": "timber", "wall_colors": ((240, 234, 222), (252, 248, 240), (88, 60, 52)),
        "chimney": ("left", "brick"), "windows": "round", "trim": (120, 84, 60),
        "door": "plank", "props": ("planters", "herbs", "lantern_green"),
    },
}


# --- geometry ---------------------------------------------------------------------------

def _frame(x, y, style):
    """Key heights of the building: wall top, ground line and the roof's eave line."""
    width = style["width"] * 32
    stories = style.get("stories", 1)
    wall_top = y + (56 if stories == 2 else 81)
    if style["roof"] == "hip":
        wall_top += 10  # a hip roof is lower, so the squat walls show more
    ground = y + 190
    return width, wall_top, ground, wall_top + 25


def _roof_points(x, y, width, eave, style):
    x0, x1 = x - 7, x + width + 7
    shape = style["roof"]
    if shape == "gable":
        apex_x = x + int(width * style.get("apex", 0.5))
        top = y - 4 if style.get("steep") or style.get("stories", 1) == 2 else y + 4
        return [(x0, eave), (apex_x, top), (x1, eave)]
    if shape == "hip":
        return [(x0, eave), (x + 40, y + 26), (x + width - 40, y + 26), (x1, eave)]
    if shape == "gambrel":
        knee = y + 44
        return [(x0, eave), (x + 4, knee), (x + 36, y + 4), (x + width - 36, y + 4), (x + width - 4, knee), (x1, eave)]
    # thatch: a soft rounded hump
    cx, half, height = x + width / 2, (x1 - x0) / 2, eave - (y + 2)
    points = []
    for step in range(25):
        t = math.pi * step / 24
        points.append((round(cx - half * math.cos(t)), round(eave - height * math.sin(t) ** 0.55)))
    return points


def _clipped(surface, points, painter):
    """Run painter(tmp, dx, dy) on a scratch layer and keep only what falls inside the polygon."""
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    box = pygame.Rect(min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)
    tmp = pygame.Surface(box.size, pygame.SRCALPHA)
    local = [(px - box.x, py - box.y) for px, py in points]
    painter(tmp, box.x, box.y)
    mask = pygame.Surface(box.size, pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), local)
    tmp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surface.blit(tmp, box.topleft)


# --- walls ------------------------------------------------------------------------------

def _paint_wall(surface, rect, material, colors):
    base, light, dark = colors
    pygame.draw.rect(surface, base, rect)
    if material == "plank":
        for px in range(rect.x + 3, rect.right - 2, 12):
            pygame.draw.line(surface, dark, (px, rect.y + 4), (px, rect.bottom - 2), 2)
            pygame.draw.line(surface, light, (px + 3, rect.y + 6), (px + 3, rect.bottom - 5), 1)
    elif material == "log":
        for row, py in enumerate(range(rect.y, rect.bottom, 11)):
            pygame.draw.line(surface, light, (rect.x, py + 2), (rect.right - 1, py + 2), 2)
            pygame.draw.line(surface, dark, (rect.x, py + 10), (rect.right - 1, py + 10), 2)
            if py + 6 < rect.bottom:
                for end_x in (rect.x - 3, rect.right + 2):
                    pygame.draw.circle(surface, OUTLINE, (end_x, py + 6), 5)
                    pygame.draw.circle(surface, light, (end_x, py + 6), 4)
                    pygame.draw.circle(surface, dark, (end_x, py + 6), 1)
    elif material in ("plaster", "timber"):
        for i in range(7):  # a few worn patches in the plaster
            px = rect.x + 6 + (i * 37) % max(1, rect.width - 20)
            py = rect.y + 8 + (i * 23) % max(1, rect.height - 16)
            pygame.draw.rect(surface, light if i % 2 else dark, (px, py, 8 - i % 3 * 2, 3))
        if material == "timber":
            beam = dark
            third = rect.width // 3
            for bx in (rect.x, rect.x + third, rect.right - third, rect.right - 5):
                pygame.draw.rect(surface, beam, (bx, rect.y, 5, rect.height))
            pygame.draw.rect(surface, beam, (rect.x, rect.y + rect.height // 2 - 2, rect.width, 5))
            for left, right in ((rect.x + 5, rect.x + third), (rect.right - third + 5, rect.right - 5)):
                pygame.draw.line(surface, beam, (left, rect.bottom - 2), (right, rect.y + rect.height // 2 + 2), 4)
        else:
            for bx in (rect.x, rect.right - 5):
                pygame.draw.rect(surface, (122, 84, 56), (bx, rect.y, 5, rect.height))
    elif material == "stone":
        pygame.draw.rect(surface, dark, rect)
        for row, py in enumerate(range(rect.y + 1, rect.bottom, 13)):
            offset = 0 if row % 2 else -11
            for i, px in enumerate(range(rect.x + offset, rect.right, 22)):
                block = pygame.Rect(px + 1, py, 20, 11).clip(rect)
                if block.width > 2:
                    shade = base if (row + i) % 3 else tuple(max(0, v - 14) for v in base)
                    pygame.draw.rect(surface, shade, block)
                    pygame.draw.line(surface, light, block.topleft, (block.right - 2, block.top), 1)
    elif material == "brick":
        pygame.draw.rect(surface, light, rect)
        for row, py in enumerate(range(rect.y + 1, rect.bottom, 7)):
            offset = 0 if row % 2 else -7
            for i, px in enumerate(range(rect.x + offset, rect.right, 14)):
                brick = pygame.Rect(px + 1, py, 12, 5).clip(rect)
                if brick.width > 1:
                    pygame.draw.rect(surface, base if (row * 3 + i) % 5 else dark, brick)


def _paint_body(surface, x, width, wall_top, ground, style):
    pygame.draw.rect(surface, (54, 43, 38), (x + 10, wall_top + 10, width - 20, ground - wall_top))
    pygame.draw.rect(surface, (90, 66, 50), (x + 14, wall_top, width - 28, ground - wall_top))
    inner = pygame.Rect(x + 20, wall_top, width - 40, ground - wall_top - 12)
    if style.get("stories", 1) == 2:
        split = wall_top + (ground - wall_top) // 2 - 10
        _paint_wall(surface, pygame.Rect(inner.x, split, inner.width, inner.bottom - split),
                    style["wall"], style["wall_colors"])
        _paint_wall(surface, pygame.Rect(inner.x, inner.y, inner.width, split - inner.y),
                    style["upper_wall"], style["upper_colors"])
        pygame.draw.rect(surface, OUTLINE, (x + 12, split - 3, width - 24, 7))
        pygame.draw.rect(surface, (122, 84, 56), (x + 13, split - 2, width - 26, 4))
    else:
        _paint_wall(surface, inner, style["wall"], style["wall_colors"])
    # Stone foundation.
    pygame.draw.rect(surface, (75, 62, 54), (x + 10, ground - 12, width - 20, 15))
    for stone_x in range(x + 12, x + width - 12, 18):
        pygame.draw.rect(surface, (135, 119, 103), (stone_x, ground - 10, 14, 6))
        pygame.draw.line(surface, (81, 72, 65), (stone_x + 7, ground - 10), (stone_x + 7, ground - 4), 1)
    # Wall plate under the eaves.
    pygame.draw.rect(surface, (70, 52, 42), (x + 15, wall_top - 4, width - 30, 10))
    pygame.draw.line(surface, (207, 166, 109), (x + 19, wall_top + 3), (x + width - 19, wall_top + 3), 2)


# --- roof -------------------------------------------------------------------------------

def _paint_roof(surface, x, y, width, eave, style):
    points = _roof_points(x, y, width, eave, style)
    base, line, seam, bright = style["roof_colors"]
    shape, tiles = style["roof"], style.get("tiles")

    def texture(tmp, ox, oy):
        tmp.fill(base)
        w, h = tmp.get_size()
        if shape == "thatch":
            for row, py in enumerate(range(-4, h, 7)):
                for i, px in enumerate(range((row % 2) * 2, w, 4)):
                    color = line if (i + row) % 3 == 0 else seam if (i * 7 + row) % 5 == 0 else base
                    pygame.draw.line(tmp, color, (px, py), (px - 2, py + 7), 2)
                if row % 3 == 2:
                    pygame.draw.line(tmp, seam, (0, py + 6), (w, py + 6), 2)
        elif tiles == "clay":
            for row, py in enumerate(range(6, h, 9)):
                offset = 5 if row % 2 else 0
                for px in range(-10 + offset, w, 10):
                    pygame.draw.arc(tmp, seam, (px, py - 8, 10, 12), math.pi, 2 * math.pi, 2)
                    pygame.draw.line(tmp, line, (px + 3, py - 5), (px + 6, py - 5), 1)
        else:
            step_y, step_x = (8, 9) if shape in ("hip", "gambrel") else (10, 11)
            for row, py in enumerate(range(step_y - 1, h, step_y)):
                pygame.draw.line(tmp, line, (0, py), (w, py), 2)
                offset = 5 if row % 2 else 0
                for px in range(offset, w, step_x):
                    pygame.draw.line(tmp, seam, (px, py - step_y + 2), (px, py - 1), 1)

    _clipped(surface, points, texture)
    pygame.draw.polygon(surface, OUTLINE, points, 3)
    if shape == "thatch":
        # Thick, rolled straw eave.
        pygame.draw.rect(surface, OUTLINE, (x - 8, eave - 7, width + 16, 13), border_radius=6)
        pygame.draw.rect(surface, bright, (x - 6, eave - 5, width + 12, 8), border_radius=4)
        for px in range(x - 2, x + width + 4, 6):
            pygame.draw.line(surface, seam, (px, eave - 4), (px - 1, eave + 2), 1)
        return
    pygame.draw.line(surface, bright, (x + 8, eave - 2), (x + width - 8, eave - 2), 4)
    pygame.draw.line(surface, OUTLINE, (x + 8, eave + 5), (x + width - 8, eave + 5), 3)
    if shape == "gable":
        apex = points[1]
        pygame.draw.line(surface, WOOD_DARK, (x + 25, eave - 14), (apex[0], apex[1] + 21), 5)
        pygame.draw.line(surface, WOOD_DARK, (apex[0], apex[1] + 21), (x + width - 25, eave - 14), 5)
        if not style.get("stories", 1) == 2:
            vent = pygame.Rect(apex[0] - 9, apex[1] + 48, 18, 16)
            pygame.draw.rect(surface, (68, 49, 39), vent)
            pygame.draw.rect(surface, (194, 152, 94), vent.inflate(-6, -6), 2)
    elif shape == "hip":
        pygame.draw.line(surface, bright, points[1], points[2], 3)
    elif shape == "gambrel":
        pygame.draw.line(surface, bright, points[1], points[4], 3)
        pygame.draw.line(surface, OUTLINE, points[1], points[4], 1)


def _paint_chimney(surface, x, y, width, style):
    chimney = style.get("chimney")
    if not chimney:
        return None
    side, material = chimney
    big = material == "stone_big"
    w = 32 if big else 25
    cx = x + width - 53 - (6 if big else 0) if side == "right" else x + 31
    top = y + (12 if big else 7)
    pygame.draw.rect(surface, OUTLINE, (cx, top, w, 66 - top + y))
    inner = pygame.Rect(cx + 4, top + 5, w - 8, 56 - top + y)
    if material == "brick":
        _paint_wall(surface, inner, "brick", ((156, 84, 64), (196, 122, 92), (116, 62, 50)))
    else:
        _paint_wall(surface, inner, "stone", ((138, 128, 118), (172, 164, 152), (94, 86, 82)))
    pygame.draw.rect(surface, OUTLINE, (cx - 2, top - 2, w + 4, 6))
    return cx + w // 2, top


def _paint_smoke(surface, chimney_top, big=False):
    if not chimney_top:
        return
    cx, top = chimney_top
    puffs = ((0, -4, 6), (5, -10, 7), (12, -13, 6), (19, -14, 5)) if big else ((0, -4, 5), (6, -9, 5), (13, -11, 4))
    for dx, dy, r in puffs:
        pygame.draw.circle(surface, (214, 214, 220, 200), (cx + dx, top + dy), r)
        pygame.draw.circle(surface, (240, 240, 244, 220), (cx + dx - 1, top + dy - 1), max(1, r - 3))


# --- windows and doors ------------------------------------------------------------------

def _window(surface, rect, kind, trim, flower_box=False, side=None):
    if kind == "round":
        center, r = rect.center, min(rect.width, rect.height) // 2 + 1
        pygame.draw.circle(surface, OUTLINE, center, r + 3)
        pygame.draw.circle(surface, trim, center, r + 1)
        pygame.draw.circle(surface, GLASS, center, r - 2)
        pygame.draw.line(surface, trim, (center[0] - r + 2, center[1]), (center[0] + r - 2, center[1]), 2)
        pygame.draw.line(surface, trim, (center[0], center[1] - r + 2), (center[0], center[1] + r - 2), 2)
        pygame.draw.circle(surface, GLASS_LIGHT, (center[0] - 4, center[1] - 4), 2)
    elif kind == "arched":
        tall = pygame.Rect(rect.x + 2, rect.y - 6, rect.width - 4, rect.height + 10)
        arch_r = tall.width // 2
        pygame.draw.rect(surface, OUTLINE, (tall.x - 3, tall.y + arch_r, tall.width + 6, tall.height - arch_r + 3))
        pygame.draw.circle(surface, OUTLINE, (tall.centerx, tall.y + arch_r), arch_r + 3)
        pygame.draw.rect(surface, trim, (tall.x - 1, tall.y + arch_r, tall.width + 2, tall.height - arch_r + 1))
        pygame.draw.circle(surface, trim, (tall.centerx, tall.y + arch_r), arch_r + 1)
        pygame.draw.rect(surface, GLASS, (tall.x + 2, tall.y + arch_r, tall.width - 4, tall.height - arch_r - 2))
        pygame.draw.circle(surface, GLASS, (tall.centerx, tall.y + arch_r), arch_r - 2)
        pygame.draw.line(surface, trim, (tall.centerx, tall.y + 2), (tall.centerx, tall.bottom - 2), 2)
        pygame.draw.line(surface, GLASS_LIGHT, (tall.x + 4, tall.y + arch_r), (tall.x + 4, tall.y + arch_r + 6), 2)
        pygame.draw.rect(surface, trim, (tall.x - 4, tall.bottom - 1, tall.width + 8, 4))
    else:
        pygame.draw.rect(surface, OUTLINE, rect.inflate(6, 6))
        glass = (236, 142, 62) if kind == "forge" else GLASS
        pygame.draw.rect(surface, glass, rect)
        if kind == "forge":
            pygame.draw.rect(surface, (252, 206, 112), rect.inflate(-10, -10))
            for bx in range(rect.x + 5, rect.right - 2, 6):
                pygame.draw.line(surface, (52, 46, 48), (bx, rect.y), (bx, rect.bottom - 1), 2)
        else:
            pygame.draw.rect(surface, trim if kind != "shuttered" else (211, 177, 115), rect, 3)
            pygame.draw.line(surface, (235, 205, 150), rect.midtop, rect.midbottom, 2)
            pygame.draw.line(surface, (235, 205, 150), rect.midleft, rect.midright, 2)
            pygame.draw.rect(surface, GLASS_LIGHT, (rect.x + 4, rect.y + 4, 3, 3))
        if kind == "shuttered":
            spots = {"left": (rect.x - 13,), "right": (rect.right + 3,)}.get(side, (rect.x - 13, rect.right + 3))
            for sx in spots:
                shutter = pygame.Rect(sx, rect.y - 2, 10, rect.height + 4)
                pygame.draw.rect(surface, OUTLINE, shutter.inflate(2, 2))
                pygame.draw.rect(surface, trim, shutter)
                for sy in range(shutter.y + 4, shutter.bottom - 2, 5):
                    pygame.draw.line(surface, tuple(max(0, v - 30) for v in trim), (sx + 1, sy), (sx + 8, sy), 1)
    if flower_box:
        box = pygame.Rect(rect.x - 2, rect.bottom + 4, rect.width + 4, 6)
        pygame.draw.rect(surface, OUTLINE, box.inflate(2, 2))
        pygame.draw.rect(surface, (105, 60, 39), box)
        for i, color in enumerate(((228, 96, 110), (246, 206, 92), (236, 236, 244), (190, 120, 220))):
            fx = box.x + 4 + i * (box.width - 8) // 3
            pygame.draw.line(surface, (74, 122, 60), (fx, box.y), (fx, box.y - 4), 2)
            pygame.draw.circle(surface, color, (fx, box.y - 5), 3)


def _door(surface, x, width, ground, kind):
    double = kind in ("double", "arched_double")
    arched = kind in ("arched", "arched_double")
    door_w = 42 if double else 30
    door_x = x + (width - door_w) // 2
    door_y = ground - 51
    frame = pygame.Rect(door_x - 4, door_y - 5, door_w + 8, 55)
    leaf = pygame.Rect(door_x, door_y, door_w, 50)
    if arched:
        r = frame.width // 2
        pygame.draw.circle(surface, (48, 38, 34), (frame.centerx, frame.y + r - 6), r)
        pygame.draw.circle(surface, (91, 54, 38), (leaf.centerx, frame.y + r - 6), r - 4)
    pygame.draw.rect(surface, (48, 38, 34), frame)
    pygame.draw.rect(surface, (91, 54, 38), leaf)
    inner = leaf.inflate(-8, -8)
    pygame.draw.rect(surface, (161, 101, 59), inner)
    if arched:
        pygame.draw.circle(surface, (161, 101, 59), (leaf.centerx, frame.y + frame.width // 2 - 6), frame.width // 2 - 8)
    for px in range(inner.x + 5, inner.right - 2, 6):
        pygame.draw.line(surface, (132, 80, 48), (px, inner.y), (px, inner.bottom - 1), 1)
    if double:
        pygame.draw.line(surface, (91, 54, 38), (leaf.centerx, leaf.y - 4), (leaf.centerx, leaf.bottom), 3)
        for hx in (leaf.centerx - 5, leaf.centerx + 4):
            pygame.draw.circle(surface, GOLD, (hx, door_y + 27), 2)
    else:
        for hy in (door_y + 10, door_y + 38):
            pygame.draw.line(surface, (60, 52, 52), (inner.x, hy), (inner.x + 12, hy), 2)
        pygame.draw.circle(surface, GOLD, (door_x + door_w - 7, door_y + 27), 2)
    pygame.draw.rect(surface, (191, 163, 111), (door_x - 6, ground - 5, door_w + 12, 7))
    return frame


# --- props ------------------------------------------------------------------------------

def _crate(surface, rect):
    pygame.draw.rect(surface, OUTLINE, rect.inflate(4, 4))
    pygame.draw.rect(surface, (176, 120, 70), rect)
    pygame.draw.rect(surface, (128, 82, 50), rect, 3)
    pygame.draw.line(surface, (128, 82, 50), rect.topleft, (rect.right - 1, rect.bottom - 1), 3)


def _barrel(surface, cx, bottom):
    body = pygame.Rect(cx - 9, bottom - 24, 18, 24)
    pygame.draw.ellipse(surface, OUTLINE, body.inflate(4, 2))
    pygame.draw.rect(surface, OUTLINE, (body.x - 2, body.y + 3, body.width + 4, body.height - 6))
    pygame.draw.rect(surface, (150, 96, 56), (body.x, body.y + 2, body.width, body.height - 4), border_radius=5)
    for hy in (body.y + 6, body.bottom - 7):
        pygame.draw.line(surface, (96, 96, 104), (body.x, hy), (body.right - 1, hy), 2)
    pygame.draw.line(surface, (190, 132, 80), (body.x + 4, body.y + 4), (body.x + 4, body.bottom - 5), 2)


def _lantern(surface, x, y, glow):
    pygame.draw.line(surface, OUTLINE, (x - 6, y - 4), (x, y - 4), 2)
    pygame.draw.line(surface, OUTLINE, (x, y - 4), (x, y), 1)
    pygame.draw.rect(surface, OUTLINE, (x - 5, y, 10, 13))
    pygame.draw.rect(surface, glow, (x - 3, y + 2, 6, 9))
    pygame.draw.rect(surface, (255, 248, 210), (x - 1, y + 4, 2, 4))


def _paint_props(surface, x, width, wall_top, ground, style, door):
    props, trim = style.get("props", ()), style.get("trim", (211, 177, 115))
    if "awning" in props:
        stripe_a, stripe_b = style["awning"]
        top = wall_top + 14
        left, right = x + 18, x + width - 18
        pygame.draw.rect(surface, OUTLINE, (left - 2, top - 2, right - left + 4, 18))
        for i, sx in enumerate(range(left, right, 12)):
            color = stripe_a if i % 2 == 0 else stripe_b
            w = min(12, right - sx)
            pygame.draw.rect(surface, color, (sx, top, w, 14))
            pygame.draw.polygon(surface, OUTLINE, [(sx - 1, top + 14), (sx + w, top + 14), (sx + w // 2, top + 21)])
            pygame.draw.polygon(surface, color, [(sx + 1, top + 14), (sx + w - 2, top + 14), (sx + w // 2, top + 18)])
        pygame.draw.rect(surface, (255, 255, 255), (left, top + 1, right - left, 2))
    if "balcony" in props:
        floor_y = wall_top + (ground - wall_top) // 2 - 12
        left, right = x + 30, x + width - 30
        pygame.draw.rect(surface, OUTLINE, (left - 2, floor_y - 18, right - left + 4, 24))
        pygame.draw.rect(surface, (156, 104, 62), (left, floor_y, right - left, 4))
        pygame.draw.rect(surface, (186, 132, 82), (left, floor_y - 16, right - left, 3))
        for px in range(left + 2, right, 7):
            pygame.draw.rect(surface, (156, 104, 62), (px, floor_y - 13, 3, 13))
        for px in range(left + 10, right - 6, 22):  # flower pots on the rail
            pygame.draw.rect(surface, (176, 92, 64), (px, floor_y - 23, 8, 6))
            pygame.draw.circle(surface, (228, 96, 110), (px + 4, floor_y - 25), 3)
    if "crates" in props:
        _crate(surface, pygame.Rect(x - 4, ground - 22, 20, 20))
        _crate(surface, pygame.Rect(x + 4, ground - 38, 15, 15))
        _barrel(surface, x + width + 2, ground + 2)
    if "barrel" in props:
        _barrel(surface, x + 2, ground + 2)
    if "lantern" in props:
        _lantern(surface, door.right + 9, door.y + 6, (255, 206, 96))
    if "lantern_green" in props:
        _lantern(surface, door.x - 9, door.y + 6, (150, 236, 170))
    if "planters" in props:
        for px in (door.x - 18, door.right + 4):
            pot = pygame.Rect(px, ground - 15, 14, 12)
            pygame.draw.rect(surface, OUTLINE, pot.inflate(2, 2))
            pygame.draw.rect(surface, (184, 96, 64), pot)
            pygame.draw.circle(surface, (74, 132, 66), (pot.centerx, pot.y - 3), 7)
            pygame.draw.circle(surface, (238, 120, 140), (pot.centerx - 3, pot.y - 5), 2)
            pygame.draw.circle(surface, (250, 220, 110), (pot.centerx + 3, pot.y - 2), 2)
    if "herbs" in props:
        hang = wall_top + 28  # just under the eave, between the windows and the door
        for i, hx in enumerate((x + 22, x + 60, x + width - 60, x + width - 22)):
            length = 10 + (i % 2) * 4
            color = ((96, 150, 80), (150, 110, 180), (186, 170, 86), (96, 150, 80))[i]
            pygame.draw.line(surface, OUTLINE, (hx, hang - 3), (hx, hang + length - 8), 1)
            tip = hang + length
            pygame.draw.polygon(surface, OUTLINE, [(hx - 4, tip - 9), (hx + 4, tip - 9), (hx, tip + 1)])
            pygame.draw.polygon(surface, color, [(hx - 2, tip - 8), (hx + 2, tip - 8), (hx, tip - 2)])
    if "shield" in props:
        cx, top = door.centerx, door.y - 26
        points = [(cx - 9, top), (cx + 9, top), (cx + 9, top + 10), (cx, top + 20), (cx - 9, top + 10)]
        pygame.draw.polygon(surface, OUTLINE, points)
        inner = [(cx - 7, top + 2), (cx + 7, top + 2), (cx + 7, top + 10), (cx, top + 17), (cx - 7, top + 10)]
        pygame.draw.polygon(surface, (58, 84, 150), inner)
        pygame.draw.line(surface, GOLD, (cx, top + 3), (cx, top + 15), 2)
        pygame.draw.line(surface, GOLD, (cx - 5, top + 7), (cx + 5, top + 7), 2)
    if "weapon_rack" in props:
        rx, base = x - 2, ground - 2
        pygame.draw.rect(surface, OUTLINE, (rx - 2, base - 34, 26, 36))
        pygame.draw.rect(surface, (126, 84, 54), (rx, base - 6, 22, 6))
        pygame.draw.rect(surface, (126, 84, 54), (rx, base - 26, 22, 4))
        for i, px in enumerate((rx + 4, rx + 11, rx + 18)):
            pygame.draw.line(surface, (196, 204, 210), (px, base - 32), (px, base - 6), 2)
            tip = (236, 240, 240) if i != 1 else GOLD
            pygame.draw.polygon(surface, tip, [(px - 2, base - 31), (px + 2, base - 31), (px, base - 36)])
    if "anvil" in props:
        ax, ay = x + 4, ground - 12
        pygame.draw.rect(surface, OUTLINE, (ax - 2, ay - 14, 26, 18))
        pygame.draw.rect(surface, (78, 80, 92), (ax, ay - 12, 22, 6))
        pygame.draw.rect(surface, (78, 80, 92), (ax + 7, ay - 6, 8, 6))
        pygame.draw.rect(surface, (126, 128, 140), (ax, ay - 12, 22, 2))
        pygame.draw.rect(surface, (78, 80, 92), (ax + 2, ay, 18, 4))
    if "firewood" in props:
        for row in range(3):
            for i in range(3 - row):
                cx, cy = x + width - 14 + i * 11 + row * 5, ground - 6 - row * 9
                pygame.draw.circle(surface, OUTLINE, (cx, cy), 6)
                pygame.draw.circle(surface, (176, 122, 72), (cx, cy), 4)
                pygame.draw.circle(surface, (126, 84, 52), (cx, cy), 1)
    if "banners" in props:
        for bx in (door.x - 16, door.right + 6):
            top = door.y - 8
            pygame.draw.rect(surface, OUTLINE, (bx - 1, top - 1, 12, 34))
            pygame.draw.polygon(surface, (58, 76, 150), [(bx, top), (bx + 10, top), (bx + 10, top + 30), (bx + 5, top + 25), (bx, top + 30)])
            pygame.draw.circle(surface, GOLD, (bx + 5, top + 10), 3)
            pygame.draw.rect(surface, trim, (bx - 2, top - 3, 14, 3))
    if "oculus" in props:
        _window(surface, pygame.Rect(x + width // 2 - 11, wall_top - 36, 22, 22), "round", trim)


# --- the whole house --------------------------------------------------------------------

def paint_house(surface, x, y, style):
    width, wall_top, ground, eave = _frame(x, y, style)
    chimney_top = _paint_chimney(surface, x, y, width, style)
    _paint_body(surface, x, width, wall_top, ground, style)
    _paint_roof(surface, x, y, width, eave, style)
    trim = style.get("trim", (211, 177, 115))
    kind = style.get("windows", "square")
    if style.get("stories", 1) == 2:
        split = wall_top + (ground - wall_top) // 2 - 10
        for wx in (x + 29, x + width - 56):
            _window(surface, pygame.Rect(wx, wall_top + 12, 27, 22), kind, trim)
        ground_y = split + 14
    else:
        ground_y = wall_top + 32
    planters = "planters" in style.get("props", ()) and kind != "round"
    _window(surface, pygame.Rect(x + 29, ground_y, 27, 24), kind, trim,
            flower_box=kind == "square" or planters, side="left")
    _window(surface, pygame.Rect(x + width - 56, ground_y, 27, 24), kind, trim, flower_box=planters, side="right")
    door = _door(surface, x, width, ground, style.get("door", "plank"))
    _paint_props(surface, x, width, wall_top, ground, style, door)
    if style.get("smoke"):
        _paint_smoke(surface, chimney_top, big=style["chimney"][1] == "stone_big")

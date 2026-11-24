"""Cozy interior pixel art: floors, wall faces, furniture and wall decorations.

Every sprite is drawn on a 16px-per-tile grid, so a w x h tile item is (w*16, h*16).
Furniture that stands against the back wall is two tiles tall: the top half overlaps
the wall face and only the floor half is solid (see HouseInteriorScene.solid_tiles).
"""

import random

import pygame

from utils.pixel_art import PALETTE

O = PALETTE["outline"]
WOOD_DARK, WOOD, WOOD_LIGHT, WOOD_HI = (110, 72, 50), (150, 104, 66), (190, 140, 90), (214, 172, 116)
CREAM = (246, 234, 206)
SHADOW = (34, 24, 30, 70)

RUG_COLORS = {
    "green": ((96, 140, 100), (132, 172, 120), (230, 214, 160)),
    "blue": ((70, 98, 150), (102, 132, 182), (226, 196, 120)),
    "red": ((156, 74, 66), (190, 108, 88), (230, 196, 128)),
}
WALL_THEMES = {
    # (paper, paper accent, wainscot, wainscot light)
    "cottage": ((214, 204, 160), (190, 196, 146), WOOD, WOOD_LIGHT),
    "stone": ((140, 138, 136), (116, 114, 114), WOOD_DARK, WOOD),
    "plaster": ((232, 216, 184), (204, 132, 114), WOOD, WOOD_LIGHT),
}

_BASE = {}
_SCALED = {}


def _c(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def _r(s, color, x, y, w, h=1):
    pygame.draw.rect(s, color, (x, y, w, h))


def _box(s, x, y, w, h, fill, light=None):
    """Outlined box with an optional lit top edge: the basic furniture building block."""
    _r(s, O, x, y, w, h)
    _r(s, fill, x + 1, y + 1, w - 2, h - 2)
    if light:
        _r(s, light, x + 1, y + 1, w - 2, 1)


def _floor(variant):
    s = _c(16, 16)
    s.fill((182, 132, 88))
    rng = random.Random(variant * 31 + 5)
    for row in range(4):
        y = row * 4
        _r(s, (198, 150, 102), 0, y + 1, 16, 1)
        _r(s, (150, 104, 70), 0, y + 3, 16, 1)
        seam = 1 + (variant * 5 + row * 7) % 14
        _r(s, (140, 96, 64), seam, y, 1, 3)
        if rng.random() < 0.35:
            _r(s, (164, 116, 78), rng.randrange(2, 13), y + 2, 2, 1)
    return s


def _wall(theme):
    paper, accent, panel, panel_light = WALL_THEMES[theme]
    s = _c(16, 32)
    _r(s, O, 0, 0, 16, 2)
    _r(s, paper, 0, 2, 16, 20)
    if theme == "stone":
        for row, y in enumerate(range(2, 22, 5)):
            off = 4 if row % 2 else 0
            _r(s, accent, 0, y + 4, 16, 1)
            for x in range(off, 16, 8):
                _r(s, accent, x, y, 1, 4)
            _r(s, (160, 158, 154), 0, y, 16, 1)
    elif theme == "cottage":
        for x in (3, 11):
            _r(s, accent, x, 2, 2, 20)
    else:
        for y in (6, 14):
            for x in (3, 11):
                s.set_at((x, y), accent)
                s.set_at((x + 1, y), accent)
    _r(s, O, 0, 22, 16, 1)
    _r(s, panel_light, 0, 23, 16, 1)
    _r(s, panel, 0, 24, 16, 7)
    _r(s, O, 7, 24, 1, 7)
    _r(s, panel_light, 1, 25, 5, 1)
    _r(s, panel_light, 9, 25, 5, 1)
    _r(s, O, 0, 31, 16, 1)
    return s


def _window():
    s = _c(16, 32)
    _r(s, O, 2, 5, 12, 14)
    _r(s, WOOD_LIGHT, 3, 6, 10, 12)
    _r(s, (164, 208, 220), 4, 7, 8, 10)
    _r(s, (214, 238, 236), 5, 8, 2, 3)
    _r(s, WOOD_LIGHT, 7, 7, 2, 10)
    _r(s, WOOD_LIGHT, 4, 11, 8, 1)
    # Curtains and a sill with a tiny potted sprout.
    _r(s, (226, 176, 160), 2, 5, 2, 10)
    _r(s, (226, 176, 160), 12, 5, 2, 10)
    _r(s, O, 1, 18, 14, 2)
    _r(s, WOOD_HI, 2, 18, 12, 1)
    _r(s, (180, 104, 70), 10, 16, 3, 2)
    _r(s, PALETTE["leaf"], 10, 14, 3, 2)
    return s


def _bed(color):
    blanket, blanket_light = {"green": ((116, 156, 104), (150, 188, 128)),
                              "red": ((164, 76, 68), (198, 108, 92))}[color]
    s = _c(32, 48)
    _r(s, SHADOW, 2, 44, 30, 4)
    _box(s, 1, 4, 30, 14, WOOD, WOOD_LIGHT)          # headboard on the wall
    _r(s, WOOD_DARK, 4, 8, 24, 1)
    _box(s, 2, 14, 28, 32, CREAM)                     # mattress
    _box(s, 4, 16, 11, 7, (252, 246, 230))           # pillows
    _box(s, 17, 16, 11, 7, (252, 246, 230))
    _box(s, 2, 24, 28, 21, blanket, blanket_light)
    for y in (29, 35, 41):                            # quilt stitching
        for x in range(5, 28, 6):
            _r(s, blanket_light, x, y, 3, 1)
    _r(s, CREAM, 3, 25, 26, 2)                        # folded sheet edge
    _box(s, 1, 43, 30, 4, WOOD_DARK, WOOD)           # footboard
    return s


def _bookshelf(kind="books"):
    s = _c(32, 32)
    _r(s, SHADOW, 1, 29, 31, 3)
    _box(s, 1, 0, 30, 31, WOOD_DARK)
    _r(s, WOOD, 2, 1, 28, 2)
    rng = random.Random(9 if kind == "books" else 17)
    book_colors = ((176, 80, 70), (88, 120, 168), (214, 176, 92), (106, 150, 104), (150, 102, 160), CREAM)
    for shelf_y in (3, 12, 21):
        _r(s, (70, 48, 38), 3, shelf_y, 26, 8)
        _r(s, WOOD_LIGHT, 2, shelf_y + 8, 28, 1)
        x = 3
        while x < 28:
            if kind == "herbs":
                jar = rng.choice(((150, 190, 200), (196, 160, 110), (170, 200, 150)))
                _r(s, O, x, shelf_y + 2, 4, 6)
                _r(s, jar, x + 1, shelf_y + 3, 2, 4)
                _r(s, (230, 230, 220), x + 1, shelf_y + 3, 1, 1)
                _r(s, (150, 104, 66), x + 1, shelf_y + 1, 2, 1)
                x += 5
            else:
                w = rng.choice((2, 2, 3))
                h = rng.choice((6, 7, 8))
                _r(s, rng.choice(book_colors), x, shelf_y + 8 - h, w, h)
                _r(s, O, x + w, shelf_y + 8 - h, 1, h)
                x += w + 1
    if kind == "herbs":  # dried bundles hanging from the top board
        for x in (6, 14, 22):
            _r(s, O, x + 1, 1, 1, 2)
            _r(s, PALETTE["leaf"], x, 3, 3, 3)
            _r(s, PALETTE["leaf_light"], x, 3, 1, 2)
    return s


def _cabinet():
    s = _c(32, 32)
    _r(s, SHADOW, 1, 29, 31, 3)
    _box(s, 1, 2, 30, 28, WOOD, WOOD_LIGHT)
    _box(s, 3, 4, 12, 12, (150, 196, 208))
    _box(s, 17, 4, 12, 12, (150, 196, 208))
    for x, color in ((5, (214, 176, 92)), (9, CREAM), (19, (176, 80, 70)), (24, (106, 150, 104))):
        _r(s, color, x, 10, 3, 5)
    _box(s, 3, 18, 12, 10, WOOD_DARK, WOOD)
    _box(s, 17, 18, 12, 10, WOOD_DARK, WOOD)
    _r(s, (226, 190, 100), 14, 22, 1, 2)
    _r(s, (226, 190, 100), 17, 22, 1, 2)
    return s


def _worktable():
    s = _c(32, 32)
    _r(s, SHADOW, 2, 28, 30, 4)
    _box(s, 1, 6, 30, 16, WOOD_LIGHT, WOOD_HI)
    _box(s, 2, 21, 4, 9, WOOD_DARK)
    _box(s, 26, 21, 4, 9, WOOD_DARK)
    # Mortar, herb bundles and an open recipe book.
    _box(s, 4, 9, 7, 6, (150, 146, 140), (186, 182, 174))
    _r(s, WOOD_DARK, 8, 6, 1, 5)
    _box(s, 13, 9, 9, 7, CREAM)
    _r(s, (176, 164, 140), 17, 10, 1, 5)
    for x, color in ((24, PALETTE["leaf"]), (26, PALETTE["leaf_light"]), (25, (236, 150, 168))):
        _r(s, color, x, 10, 2, 4)
    return s


def _table():
    s = _c(32, 32)
    _r(s, SHADOW, 3, 27, 28, 5)
    _box(s, 2, 6, 28, 16, WOOD_LIGHT, WOOD_HI)
    _r(s, CREAM, 10, 7, 12, 14)                # table runner
    _r(s, (226, 196, 150), 10, 12, 12, 1)
    _box(s, 3, 21, 4, 9, WOOD_DARK)
    _box(s, 25, 21, 4, 9, WOOD_DARK)
    _box(s, 13, 9, 6, 5, (226, 120, 96))      # teapot / fruit bowl
    _r(s, (250, 170, 140), 14, 10, 2, 1)
    _box(s, 4, 10, 5, 4, (240, 240, 232))
    return s


def _chair(side):
    s = _c(16, 16)
    _r(s, SHADOW, 3, 13, 11, 3)
    back_x = 3 if side == "right" else 10
    _box(s, back_x, 1, 4, 13, WOOD_DARK, WOOD)
    _box(s, 3, 7, 10, 5, WOOD, WOOD_LIGHT)
    _r(s, (196, 120, 96), 4, 8, 8, 2)
    _r(s, O, 4, 12, 1, 3)
    _r(s, O, 11, 12, 1, 3)
    return s


def _bench():
    s = _c(32, 16)
    _r(s, SHADOW, 2, 13, 30, 3)
    _box(s, 1, 1, 30, 7, (146, 72, 66), (186, 104, 88))
    _box(s, 1, 6, 30, 6, (164, 82, 72), (200, 120, 100))
    _r(s, O, 3, 12, 2, 3)
    _r(s, O, 27, 12, 2, 3)
    return s


def _rug(color, w, h):
    base, mid, trim = RUG_COLORS[color]
    s = _c(w * 16, h * 16)
    rect = pygame.Rect(1, 2, w * 16 - 2, h * 16 - 4)
    pygame.draw.rect(s, O, rect, border_radius=3)
    pygame.draw.rect(s, base, rect.inflate(-2, -2), border_radius=3)
    pygame.draw.rect(s, trim, rect.inflate(-6, -6), 1, border_radius=2)
    inner = rect.inflate(-12, -12)
    pygame.draw.rect(s, mid, inner, border_radius=2)
    cx, cy = rect.center
    pygame.draw.polygon(s, trim, ((cx, cy - 4), (cx + 6, cy), (cx, cy + 4), (cx - 6, cy)))
    pygame.draw.polygon(s, base, ((cx, cy - 2), (cx + 3, cy), (cx, cy + 2), (cx - 3, cy)))
    for x in range(3, w * 16 - 3, 3):  # fringe
        s.set_at((x, 1), trim)
        s.set_at((x, h * 16 - 2), trim)
    return s


def _plant_pot():
    s = _c(16, 16)
    _r(s, SHADOW, 3, 13, 11, 3)
    _box(s, 4, 9, 8, 6, (184, 104, 70), (214, 136, 96))
    for cx, cy, r in ((8, 6, 4), (5, 7, 3), (11, 7, 3)):
        pygame.draw.circle(s, O, (cx, cy), r + 1)
    for cx, cy, r in ((8, 6, 4), (5, 7, 3), (11, 7, 3)):
        pygame.draw.circle(s, PALETTE["leaf"], (cx, cy), r)
    _r(s, PALETTE["leaf_light"], 6, 4, 2, 2)
    _r(s, PALETTE["leaf_glint"], 7, 4, 1, 1)
    return s


def _jars():
    s = _c(16, 16)
    _r(s, SHADOW, 1, 13, 15, 3)
    for x, h, color in ((1, 9, (150, 190, 200)), (6, 11, (196, 160, 110)), (11, 8, (170, 200, 150))):
        _box(s, x, 14 - h, 4, h, color)
        _r(s, (240, 240, 232), x + 1, 15 - h, 1, 2)
        _r(s, WOOD, x + 1, 13 - h, 2, 1)
    return s


def _crate():
    s = _c(16, 16)
    _r(s, SHADOW, 1, 13, 15, 3)
    _box(s, 1, 3, 14, 12, WOOD, WOOD_LIGHT)
    _r(s, WOOD_DARK, 2, 8, 12, 1)
    pygame.draw.line(s, WOOD_DARK, (2, 4), (13, 13))
    _r(s, (236, 150, 80), 4, 1, 3, 3)  # a few carrots poking out
    _r(s, PALETTE["leaf"], 4, 0, 3, 1)
    return s


def _barrel():
    s = _c(16, 16)
    _r(s, SHADOW, 2, 13, 13, 3)
    _box(s, 3, 1, 10, 14, (150, 98, 60))
    _r(s, (186, 132, 82), 5, 2, 2, 12)
    _r(s, (110, 112, 118), 4, 4, 8, 1)
    _r(s, (110, 112, 118), 4, 11, 8, 1)
    return s


def _cauldron():
    s = _c(16, 16)
    _r(s, SHADOW, 1, 13, 15, 3)
    pygame.draw.circle(s, O, (8, 9), 7)
    pygame.draw.circle(s, (70, 70, 80), (8, 9), 6)
    _r(s, O, 2, 4, 12, 3)
    _r(s, (120, 190, 120), 3, 5, 10, 1)
    _r(s, (190, 236, 160), 5, 3, 2, 2)
    _r(s, (110, 110, 120), 4, 9, 2, 3)
    return s


def _chest():
    s = _c(16, 16)
    _r(s, SHADOW, 1, 13, 15, 3)
    _box(s, 1, 3, 14, 12, (150, 98, 60), (186, 132, 82))
    _r(s, O, 1, 7, 14, 1)
    _r(s, (226, 190, 100), 1, 8, 14, 1)
    _box(s, 6, 7, 4, 4, (226, 190, 100))
    return s


def _globe():
    s = _c(16, 16)
    _r(s, SHADOW, 3, 13, 11, 3)
    _box(s, 5, 12, 6, 3, WOOD_DARK)
    _r(s, O, 7, 9, 2, 3)
    pygame.draw.circle(s, O, (8, 6), 6)
    pygame.draw.circle(s, (100, 150, 196), (8, 6), 5)
    _r(s, (120, 176, 104), 5, 4, 3, 3)
    _r(s, (120, 176, 104), 9, 6, 3, 2)
    _r(s, (220, 236, 240), 6, 3, 1, 1)
    return s


def _fireplace():
    s = _c(48, 32)
    _r(s, SHADOW, 0, 29, 48, 3)
    _box(s, 1, 2, 46, 29, (150, 146, 140), (186, 182, 174))
    for row, y in enumerate(range(6, 28, 5)):
        _r(s, (124, 120, 116), 2, y, 44, 1)
        for x in range(4 + (row % 2) * 5, 46, 10):
            _r(s, (124, 120, 116), x, y - 4, 1, 4)
    _box(s, 1, 0, 46, 5, WOOD, WOOD_LIGHT)            # mantel
    _r(s, (226, 190, 100), 8, 0, 3, 2)                 # candles on the mantel
    _r(s, (226, 190, 100), 37, 0, 3, 2)
    _box(s, 12, 11, 24, 20, (40, 30, 34))              # firebox
    pygame.draw.polygon(s, (226, 112, 56), ((15, 30), (24, 13), (33, 30)))
    pygame.draw.polygon(s, (250, 196, 90), ((19, 30), (24, 19), (29, 30)))
    _r(s, (255, 240, 190), 23, 25, 2, 4)
    _r(s, WOOD_DARK, 14, 29, 20, 2)
    return s


def _weapon_rack():
    s = _c(32, 32)
    _r(s, SHADOW, 1, 29, 31, 3)
    _box(s, 1, 4, 30, 4, WOOD, WOOD_LIGHT)
    _box(s, 1, 26, 30, 4, WOOD, WOOD_LIGHT)
    _r(s, O, 2, 4, 2, 26)
    _r(s, O, 28, 4, 2, 26)
    for x in (7, 14, 21):
        _r(s, O, x - 1, 1, 4, 26)
        _r(s, (196, 204, 210), x, 2, 2, 20)
        _r(s, (240, 244, 246), x, 2, 1, 16)
        _r(s, (150, 108, 60), x - 2, 21, 6, 2)
        _r(s, WOOD_DARK, x, 23, 2, 3)
    _box(s, 25, 10, 6, 12, (120, 126, 136), (170, 178, 186))  # shield
    _r(s, (176, 80, 70), 27, 13, 2, 6)
    return s


def _armor_stand():
    s = _c(16, 32)
    _r(s, SHADOW, 2, 29, 13, 3)
    _box(s, 4, 28, 8, 3, WOOD_DARK)
    _r(s, O, 7, 20, 2, 9)
    _box(s, 3, 9, 10, 12, (128, 138, 146), (176, 186, 190))   # cuirass
    _r(s, (176, 186, 190), 5, 11, 2, 7)
    _r(s, (226, 190, 100), 7, 14, 2, 2)
    _box(s, 4, 1, 8, 9, (120, 128, 136), (170, 178, 186))     # helm
    _r(s, O, 5, 5, 6, 1)
    _r(s, (176, 80, 70), 7, 0, 2, 2)                          # plume
    return s


def _map_table():
    s = _c(48, 32)
    _r(s, SHADOW, 2, 28, 46, 4)
    _box(s, 1, 5, 46, 18, WOOD, WOOD_LIGHT)
    _box(s, 2, 22, 4, 8, WOOD_DARK)
    _box(s, 42, 22, 4, 8, WOOD_DARK)
    _box(s, 7, 7, 26, 14, (232, 214, 168))                    # unrolled map
    pygame.draw.line(s, (120, 168, 190), (10, 16), (20, 10))
    pygame.draw.line(s, (150, 104, 66), (14, 18), (28, 12))
    _r(s, (176, 80, 70), 24, 11, 2, 2)
    _box(s, 36, 8, 6, 6, (196, 204, 210))                     # helmet / candle
    _r(s, (250, 210, 120), 38, 6, 2, 2)
    return s


def _desk():
    s = _c(48, 32)
    _r(s, SHADOW, 2, 28, 46, 4)
    _box(s, 1, 6, 46, 22, WOOD, WOOD_LIGHT)
    _box(s, 3, 15, 13, 12, WOOD_DARK, WOOD)
    _box(s, 32, 15, 13, 12, WOOD_DARK, WOOD)
    _r(s, (226, 190, 100), 9, 20, 2, 1)
    _r(s, (226, 190, 100), 38, 20, 2, 1)
    _box(s, 17, 8, 12, 7, CREAM)                              # ledger
    _r(s, (176, 164, 140), 22, 9, 1, 5)
    _box(s, 4, 3, 4, 8, (176, 80, 70))                        # book stack
    _box(s, 8, 5, 4, 6, (88, 120, 168))
    _r(s, O, 38, 2, 2, 7)                                     # quill + candle
    _r(s, (240, 240, 232), 39, 1, 1, 6)
    _box(s, 42, 6, 3, 4, CREAM)
    _r(s, (250, 196, 90), 43, 4, 1, 2)
    return s


def _banner(color=(70, 98, 150)):
    s = _c(16, 32)
    _r(s, O, 1, 3, 14, 2)
    _r(s, WOOD_LIGHT, 2, 3, 12, 1)
    _r(s, O, 2, 5, 12, 15)
    _r(s, color, 3, 5, 10, 14)
    pygame.draw.polygon(s, O, ((2, 19), (14, 19), (8, 24)))
    pygame.draw.polygon(s, color, ((3, 19), (13, 19), (8, 23)))
    pygame.draw.circle(s, (226, 190, 100), (8, 11), 3, 1)
    _r(s, (226, 190, 100), 8, 10, 1, 3)
    return s


def _wall_map():
    s = _c(48, 32)
    _box(s, 2, 4, 44, 18, WOOD_DARK)
    _r(s, (232, 214, 168), 4, 6, 40, 14)
    pygame.draw.polygon(s, (150, 190, 120), ((8, 16), (14, 8), (24, 10), (30, 16), (18, 18)))
    pygame.draw.line(s, (120, 168, 200), (30, 7), (36, 18))
    _r(s, (176, 80, 70), 18, 12, 2, 2)
    for x, y in ((10, 9), (34, 12), (26, 15)):
        _r(s, (90, 70, 60), x, y, 1, 1)
    return s


def _painting():
    s = _c(32, 32)
    _box(s, 4, 5, 24, 16, (196, 160, 90))
    _r(s, (164, 208, 220), 6, 7, 20, 7)
    _r(s, (120, 176, 104), 6, 14, 20, 5)
    pygame.draw.circle(s, (250, 220, 140), (21, 10), 2)
    return s


def _doorway():
    s = _c(16, 16)
    _r(s, (120, 84, 60), 1, 0, 14, 16)
    _r(s, (196, 150, 100), 3, 2, 10, 12)
    for y in range(3, 13, 2):
        _r(s, (170, 120, 80), 4, y, 8, 1)
    return s


_BUILDERS = {
    "floor_0": lambda: _floor(0),
    "floor_1": lambda: _floor(1),
    "floor_2": lambda: _floor(2),
    "wall_cottage": lambda: _wall("cottage"),
    "wall_stone": lambda: _wall("stone"),
    "wall_plaster": lambda: _wall("plaster"),
    "window": _window,
    "bed_green": lambda: _bed("green"),
    "bed_red": lambda: _bed("red"),
    "bookshelf": _bookshelf,
    "herb_shelf": lambda: _bookshelf("herbs"),
    "cabinet": _cabinet,
    "worktable": _worktable,
    "table": _table,
    "chair_left": lambda: _chair("left"),
    "chair_right": lambda: _chair("right"),
    "bench": _bench,
    "plant_pot": _plant_pot,
    "jars": _jars,
    "crate": _crate,
    "barrel": _barrel,
    "cauldron": _cauldron,
    "chest": _chest,
    "globe": _globe,
    "fireplace": _fireplace,
    "weapon_rack": _weapon_rack,
    "armor_stand": _armor_stand,
    "map_table": _map_table,
    "desk": _desk,
    "banner": _banner,
    "wall_map": _wall_map,
    "painting": _painting,
    "doorway": _doorway,
}


def interior_sprite(name, scale=2):
    """Cached interior sprite. ``scale=None`` returns the 16px-grid original."""
    if name not in _BASE:
        if name.startswith("rug_"):
            _, color, dims = name.split("_")
            w, h = (int(v) for v in dims.split("x"))
            _BASE[name] = _rug(color, w, h)
        else:
            _BASE[name] = _BUILDERS[name]()
    if scale is None:
        return _BASE[name]
    key = (name, scale)
    if key not in _SCALED:
        base = _BASE[name]
        _SCALED[key] = pygame.transform.scale(base, (base.get_width() * scale, base.get_height() * scale))
    return _SCALED[key]

"""Generate the game icon (assets/icon.png and assets/icon.ico) as 32x32 pixel art.

Run from the project root:  python tools/make_icon.py
The .ico embeds PNG images, so no Pillow dependency is needed.
"""

import io
import os
import struct
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

NAVY = (24, 28, 58)
GOLD = (232, 182, 72)
GOLD_DARK = (150, 104, 44)
CREAM = (255, 240, 200)
BLADE = (206, 228, 255)
BLADE_EDGE = (120, 150, 196)
GRIP = (110, 70, 44)
GEM = (96, 178, 240)


def draw_icon():
    s = pygame.Surface((32, 32), pygame.SRCALPHA)
    px = lambda x, y, c: s.set_at((x, y), c)

    # Rounded night-sky badge with a gold rim.
    pygame.draw.rect(s, GOLD_DARK, (1, 1, 30, 30), border_radius=6)
    pygame.draw.rect(s, GOLD, (2, 2, 28, 28), border_radius=5)
    pygame.draw.rect(s, NAVY, (3, 3, 26, 26), border_radius=4)
    for x, y in ((6, 6), (13, 5), (5, 12), (26, 17), (20, 25), (11, 9), (25, 23)):
        px(x, y, CREAM)

    # Four-point star sparkle in the upper right.
    cx, cy = 22, 9
    for d in range(1, 5):
        px(cx + d, cy, GOLD if d < 3 else CREAM)
        px(cx - d, cy, GOLD if d < 3 else CREAM)
        px(cx, cy + d, GOLD if d < 3 else CREAM)
        px(cx, cy - d, GOLD if d < 3 else CREAM)
    for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        px(cx + dx, cy + dy, GOLD)
    px(cx, cy, (255, 255, 255))

    # Star sword on a diagonal from the lower left toward the sparkle.
    for i in range(11):
        x, y = 11 + i, 20 - i
        px(x, y, BLADE)
        px(x + 1, y, BLADE)
        px(x, y - 1, (255, 255, 255) if i % 3 else BLADE)
        px(x + 1, y + 1, BLADE_EDGE)
    px(21, 10, (255, 255, 255))
    # Cross-guard perpendicular to the blade.
    for i in range(-3, 4):
        px(10 + i, 19 + i, GOLD)
        px(11 + i, 19 + i, GOLD_DARK if abs(i) == 3 else GOLD)
    # Grip and pommel gem.
    for i in range(3):
        px(9 - i, 22 + i, GRIP)
        px(8 - i, 22 + i, GRIP)
    pygame.draw.rect(s, GOLD, (4, 24, 3, 3))
    px(5, 25, GEM)
    return s


def png_bytes(surface):
    buffer = io.BytesIO()
    pygame.image.save(surface, buffer, "icon.png")
    return buffer.getvalue()


def write_ico(path, images):
    header = struct.pack("<HHH", 0, 1, len(images))
    entries, blobs = b"", b""
    offset = 6 + 16 * len(images)
    for size, data in images:
        dim = 0 if size >= 256 else size
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(data), offset)
        blobs += data
        offset += len(data)
    with open(path, "wb") as handle:
        handle.write(header + entries + blobs)


def main():
    pygame.init()
    base = draw_icon()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pygame.image.save(base, os.path.join(root, "assets", "icon.png"))
    images = []
    for size in (16, 24, 32, 48, 64, 128, 256):
        scaled = pygame.transform.smoothscale(base, (size, size)) if size < 32 else pygame.transform.scale(base, (size, size))
        images.append((size, png_bytes(scaled)))
    write_ico(os.path.join(root, "assets", "icon.ico"), images)
    if len(sys.argv) > 1:
        pygame.image.save(pygame.transform.scale(base, (256, 256)), sys.argv[1])
    print("icon written")


if __name__ == "__main__":
    main()

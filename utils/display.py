"""Window scaling: the game draws on an 800x600 canvas that is enlarged to the window.

Pixel art is scaled with nearest-neighbour sampling. Fullscreen keeps the 4:3 picture
centred with black bars, and mouse positions are mapped back to canvas coordinates.
"""

import pygame

from settings import HEIGHT, WIDTH

SCALES = {"1x": 1.0, "1.5x": 1.5, "2x": 2.0}
TASKBAR_MARGIN = 80  # keep windowed modes clear of the taskbar and title bar


def available_modes(desktop_size):
    """Window modes that fit on this desktop, plus fullscreen."""
    width, height = desktop_size
    fitting = [mode for mode, scale in SCALES.items()
               if scale == 1.0 or (WIDTH * scale <= width and HEIGHT * scale + TASKBAR_MARGIN <= height)]
    return (*fitting, "fullscreen")


def window_size(mode, desktop_size):
    if mode == "fullscreen":
        return tuple(desktop_size)
    scale = SCALES.get(mode, 1.0)
    return (round(WIDTH * scale), round(HEIGHT * scale))


def view_rect(window):
    """Largest 4:3 rectangle centred in the window."""
    width, height = window
    scale = min(width / WIDTH, height / HEIGHT)
    size = (round(WIDTH * scale), round(HEIGHT * scale))
    return pygame.Rect((width - size[0]) // 2, (height - size[1]) // 2, *size)


def to_canvas(pos, view):
    x = (pos[0] - view.x) * WIDTH / view.width
    y = (pos[1] - view.y) * HEIGHT / view.height
    return (max(0, min(WIDTH - 1, int(x))), max(0, min(HEIGHT - 1, int(y))))


def map_events(events, view):
    """Rewrite mouse positions from window to canvas coordinates (other events untouched)."""
    if view.size == (WIDTH, HEIGHT) and view.topleft == (0, 0):
        return list(events)
    mapped = []
    for event in events:
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            data = dict(event.dict)
            data["pos"] = to_canvas(event.pos, view)
            event = pygame.event.Event(event.type, data)
        mapped.append(event)
    return mapped

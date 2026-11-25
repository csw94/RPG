"""Move positions in old saves onto the current map layout.

Layout versions:
  1  up to v0.6.x  - fields 40x24, village and north shrine clearing 25x16
  2  v0.7.0-v0.9.0 - fields 52x31 (x1.3), village/clearing 32x21 (old core shifted by (3, 2))
  3  v0.9.1-       - the volcanic field_south is mirrored top to bottom (enter at the top)
  4  v0.24.0-      - village houses moved off-grid; a hero saved at an old door moves to the new one

Saves only started recording ``layout_version`` with layout 3, so older saves are dated by
the slot's ``updated_at`` (SQLite CURRENT_TIMESTAMP, UTC) against the release times below.
Dungeons and house interiors kept their coordinates in every version.
"""

import math

LAYOUT_VERSION = 4
# UTC times of the release commits that introduced each layout.
LAYOUT_SINCE = ((3, "2026-11-24 06:53:37"), (2, "2026-11-24 02:32:18"))

FIELD_SCALE = 1.3
CORE_OFFSET = (3, 2)
FIELD_ROWS = 31
# Layout 4: old village door/exit tiles -> the same building's new door/exit tiles.
VILLAGE_DOORS_V4 = {
    (6, 9): (5, 8), (6, 10): (5, 9),          # Marta's cottage
    (24, 9): (25, 10), (24, 10): (25, 11),    # Garen's quarters
    (37, 8): (34, 7), (37, 9): (34, 8),       # inn
    (37, 17): (39, 17), (37, 18): (39, 18),   # smithy
    (7, 26): (6, 24),                         # library
    (25, 26): (29, 26),                       # apothecary
}


def guess_layout(saved_at):
    """Layout an unversioned save was written with; unknown times count as current."""
    if not saved_at:
        return LAYOUT_VERSION
    for version, since in LAYOUT_SINCE:
        if str(saved_at) >= since:
            return version
    return 1


def _scale(value):
    return math.floor(value * FIELD_SCALE + 0.5)


def _point_mover(world, version):
    """Return a function mapping an (x, y) tile in ``world`` from ``version`` to the current layout."""
    steps = []
    if version < 2:
        if world.startswith("field_"):
            steps.append(lambda x, y: (_scale(x), _scale(y)))
        elif world in ("village", "village_north_shrine"):
            steps.append(lambda x, y: (x + CORE_OFFSET[0], y + CORE_OFFSET[1]))
    if version < 3 and world == "field_south":
        steps.append(lambda x, y: (x, FIELD_ROWS - 1 - y))
    if version < 4 and world == "village":
        steps.append(lambda x, y: VILLAGE_DOORS_V4.get((round(x), round(y)), (x, y)))
    if not steps:
        return None

    def move(x, y):
        for step in steps:
            x, y = step(x, y)
        return x, y
    return move


def migrate(state, saved_at=None):
    """Return a copy of ``state`` with positions converted to the current layout."""
    state = dict(state)
    version = state.get("layout_version") or guess_layout(saved_at)
    if version < LAYOUT_VERSION:
        world = state.get("world", "")
        move = _point_mover(world, version)
        if move and "x" in state and "y" in state:
            x, y = move(float(state["x"]), float(state["y"]))
            state["x"], state["y"] = float(x), float(y)
        opened = state.get("opened_by_world")
        if isinstance(opened, dict):
            state["opened_by_world"] = {
                key: [list(move_key(*point)) for point in points] if (move_key := _point_mover(key, version)) else points
                for key, points in opened.items()
            }
        herb_mover = _point_mover("field_east", version)  # moon herbs only grow on the forest path
        if herb_mover and state.get("collected_herbs"):
            state["collected_herbs"] = [list(herb_mover(*point)) for point in state["collected_herbs"]]
    state["layout_version"] = LAYOUT_VERSION
    return state

"""Player preferences (volumes, window size) kept in settings.json next to the save file."""

import json
import os
from pathlib import Path

DISPLAY_MODES = ("1x", "1.5x", "2x", "fullscreen")
DEFAULTS = {"music": 7, "sfx": 7, "display": "1x"}


def default_path():
    if os.name == "nt":
        root = Path(os.environ.get("APPDATA", Path.home()))
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return root / "ChroniclesOfPixel" / "settings.json"


def _clean(raw):
    settings = dict(DEFAULTS)
    if not isinstance(raw, dict):
        return settings
    for key in ("music", "sfx"):
        try:
            settings[key] = max(0, min(10, int(raw.get(key, DEFAULTS[key]))))
        except (TypeError, ValueError):
            pass
    if raw.get("display") in DISPLAY_MODES:
        settings["display"] = raw["display"]
    return settings


def load(path=None):
    path = Path(path) if path else default_path()
    try:
        return _clean(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return dict(DEFAULTS)


def save(settings, path=None):
    path = Path(path) if path else default_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(_clean(settings), ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass  # preferences are a convenience; never crash the game over them

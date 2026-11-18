"""SQLite save storage, kept in the user's writable data directory."""

import json
import os
from pathlib import Path
import sqlite3
from typing import Any


def _default_save_path() -> Path:
    if os.name == "nt":
        root = Path(os.environ.get("APPDATA", Path.home()))
    elif os.name == "darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return root / "ChroniclesOfPixel" / "save.db"


class SaveManager:
    """SQLite-backed JSON player save with a small adapter-friendly boundary."""

    def __init__(self, database_path: str | Path | None = None):
        self.database_path = Path(database_path) if database_path else _default_save_path()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS saves ("
                "slot INTEGER PRIMARY KEY CHECK(slot = 1), payload TEXT NOT NULL, "
                "updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
            )

    def has_save(self) -> bool:
        with self._connect() as connection:
            return connection.execute("SELECT 1 FROM saves WHERE slot = 1").fetchone() is not None

    def save(self, state: dict[str, Any]) -> None:
        payload = json.dumps(state, ensure_ascii=False)
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO saves(slot, payload) VALUES(1, ?) "
                "ON CONFLICT(slot) DO UPDATE SET payload=excluded.payload, "
                "updated_at=CURRENT_TIMESTAMP",
                (payload,),
            )

    def load(self) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT payload FROM saves WHERE slot = 1").fetchone()
        return json.loads(row[0]) if row else None

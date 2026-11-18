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
    """SQLite-backed saves for three selectable player slots."""

    SLOT_COUNT = 3

    def __init__(self, database_path: str | Path | None = None):
        self.database_path = Path(database_path) if database_path else _default_save_path()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='saves'"
            ).fetchone()
            old_schema = "".join((row[0] or "").lower().split()) if row else ""
            if row and "check(slot=1)" in old_schema:
                connection.execute("ALTER TABLE saves RENAME TO saves_legacy")
                self._create_table(connection)
                connection.execute(
                    "INSERT INTO saves(slot, payload, updated_at) "
                    "SELECT slot, payload, updated_at FROM saves_legacy"
                )
                connection.execute("DROP TABLE saves_legacy")
            else:
                self._create_table(connection)

    @staticmethod
    def _create_table(connection: sqlite3.Connection) -> None:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS saves ("
            "slot INTEGER PRIMARY KEY CHECK(slot BETWEEN 1 AND 3), payload TEXT NOT NULL, "
            "updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )

    @classmethod
    def _validate_slot(cls, slot: int) -> int:
        if isinstance(slot, bool) or not isinstance(slot, int) or not 1 <= slot <= cls.SLOT_COUNT:
            raise ValueError(f"slot must be an integer from 1 to {cls.SLOT_COUNT}")
        return slot

    def has_save(self, slot: int) -> bool:
        slot = self._validate_slot(slot)
        with self._connect() as connection:
            return connection.execute("SELECT 1 FROM saves WHERE slot = ?", (slot,)).fetchone() is not None

    def list_saves(self) -> dict[int, dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT slot, payload FROM saves ORDER BY slot").fetchall()
        return {slot: json.loads(payload) for slot, payload in rows}

    def save(self, state: dict[str, Any], slot: int = 1) -> None:
        slot = self._validate_slot(slot)
        payload = json.dumps(state, ensure_ascii=False)
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO saves(slot, payload) VALUES(?, ?) "
                "ON CONFLICT(slot) DO UPDATE SET payload=excluded.payload, "
                "updated_at=CURRENT_TIMESTAMP",
                (slot, payload),
            )

    def load(self, slot: int = 1) -> dict[str, Any] | None:
        slot = self._validate_slot(slot)
        with self._connect() as connection:
            row = connection.execute("SELECT payload FROM saves WHERE slot = ?", (slot,)).fetchone()
        return json.loads(row[0]) if row else None

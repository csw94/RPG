"""SQLite save storage, kept in the user's writable data directory."""

import json
import os
from pathlib import Path
import sqlite3
from dataclasses import dataclass
from typing import Any

from gameplay.world_data import MAP_GRAPH


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


@dataclass(frozen=True)
class BattleResult:
    victory: bool
    turns: int
    player_hp: int
    monster_hp: int


class StoryProgressionManager:
    """SQLite-backed story save and progression rules for the single-player campaign."""

    FLAGS = (
        "prologue_done", "shrine_wind", "shrine_earth", "shrine_fire",
        "star_sword_awakened", "final_boss",
    )
    SHRINES = ("shrine_wind", "shrine_earth", "shrine_fire")
    MAP_GRAPH = MAP_GRAPH
    SUB_QUEST_TARGETS = {"sq_moon_herb": 3, "sq_old_sword": 1, "sq_goblin_hunt": 5}
    MONSTERS = {
        "slime": (35, 10, 2),
        "shrine_wind": (140, 22, 6),
        "shrine_earth": (200, 20, 12),
        "shrine_fire": (160, 28, 8),
        "final_boss": (320, 35, 15),
    }

    def __init__(self, database_path: str | Path = "game_save.db"):
        self.database_path = str(database_path)
        if self.database_path != ":memory:":
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.database_path)
        self._connection.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        with self._connection:
            self._connection.execute(
                "CREATE TABLE IF NOT EXISTS player_save ("
                "id INTEGER PRIMARY KEY CHECK (id = 1), player_name TEXT NOT NULL, "
                "level INTEGER DEFAULT 1, hp INTEGER DEFAULT 100, max_hp INTEGER DEFAULT 100, "
                "atk INTEGER DEFAULT 15, def INTEGER DEFAULT 5, gold INTEGER DEFAULT 0, "
                "weapon TEXT DEFAULT '녹슨 철검', current_map TEXT DEFAULT 'village_square', "
                "pos_x INTEGER DEFAULT 10, pos_y INTEGER DEFAULT 10, "
                "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, evasion_bonus INTEGER DEFAULT 0)"
            )
            self._connection.execute(
                "CREATE TABLE IF NOT EXISTS quest_flags ("
                "flag_key TEXT PRIMARY KEY, is_cleared INTEGER DEFAULT 0, cleared_at DATETIME)"
            )
            self._connection.execute(
                "CREATE TABLE IF NOT EXISTS sub_quests ("
                "quest_id TEXT PRIMARY KEY, status TEXT NOT NULL DEFAULT 'NOT_STARTED', "
                "progress INTEGER NOT NULL DEFAULT 0, target INTEGER NOT NULL, "
                "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
            )
            self._connection.execute(
                "CREATE TABLE IF NOT EXISTS player_inventory ("
                "id INTEGER PRIMARY KEY CHECK(id=1), potions INTEGER NOT NULL DEFAULT 0, "
                "high_potions INTEGER NOT NULL DEFAULT 0, broken_old_sword INTEGER NOT NULL DEFAULT 0, "
                "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
            )
            # Existing saves created from the specified schema gain the wind seal field safely.
            columns = {row[1] for row in self._connection.execute("PRAGMA table_info(player_save)")}
            if "evasion_bonus" not in columns:
                self._connection.execute(
                    "ALTER TABLE player_save ADD COLUMN evasion_bonus INTEGER DEFAULT 0"
                )

    def init_new_game(self, player_name: str) -> None:
        name = player_name.strip() if isinstance(player_name, str) else ""
        if not name:
            raise ValueError("player_name must not be empty")
        with self._connection:
            self._connection.execute(
                "INSERT INTO player_save (id, player_name, level, hp, max_hp, atk, def, gold, "
                "weapon, current_map, pos_x, pos_y, evasion_bonus, updated_at) "
                "VALUES (1, ?, 1, 100, 100, 15, 5, 0, '녹슨 철검', 'village_square', 10, 10, 0, CURRENT_TIMESTAMP) "
                "ON CONFLICT(id) DO UPDATE SET player_name=excluded.player_name, level=1, hp=100, "
                "max_hp=100, atk=15, def=5, gold=0, weapon='녹슨 철검', current_map='village_square', "
                "pos_x=10, pos_y=10, evasion_bonus=0, updated_at=CURRENT_TIMESTAMP",
                (name,),
            )
            self._connection.execute("DELETE FROM quest_flags")
            self._connection.executemany(
                "INSERT INTO quest_flags(flag_key, is_cleared, cleared_at) VALUES (?, 0, NULL)",
                ((flag,) for flag in self.FLAGS),
            )
            self._connection.execute("DELETE FROM sub_quests")
            self._connection.executemany(
                "INSERT INTO sub_quests(quest_id, status, progress, target) VALUES (?, 'NOT_STARTED', 0, ?)",
                self.SUB_QUEST_TARGETS.items(),
            )
            self._connection.execute(
                "INSERT INTO player_inventory(id, potions, high_potions, broken_old_sword) "
                "VALUES (1, 0, 0, 0) ON CONFLICT(id) DO UPDATE SET potions=0, high_potions=0, "
                "broken_old_sword=0, updated_at=CURRENT_TIMESTAMP"
            )

    def load_game(self) -> dict[str, Any] | None:
        player = self._connection.execute("SELECT * FROM player_save WHERE id=1").fetchone()
        if player is None:
            return None
        flags = {key: 0 for key in self.FLAGS}
        flags.update({row[0]: row[1] for row in self._connection.execute(
            "SELECT flag_key, is_cleared FROM quest_flags"
        )})
        player_data = dict(player)
        # Keep the storage timestamp internal; it is metadata rather than game state.
        player_data.pop("updated_at", None)
        quests = {row["quest_id"]: dict(row) for row in self._connection.execute(
            "SELECT quest_id, status, progress, target, updated_at FROM sub_quests ORDER BY quest_id"
        )}
        inventory_row = self._connection.execute(
            "SELECT potions, high_potions, broken_old_sword FROM player_inventory WHERE id=1"
        ).fetchone()
        inventory = dict(inventory_row) if inventory_row else {"potions": 0, "high_potions": 0, "broken_old_sword": 0}
        return {"player": player_data, "flags": flags, "sub_quests": quests, "inventory": inventory}

    def move_player(self, target_map: str) -> bool:
        """Move to a directly connected map, refusing unknown or unreachable destinations."""
        with self._connection:
            row = self._connection.execute("SELECT current_map FROM player_save WHERE id=1").fetchone()
            if row is None:
                raise RuntimeError("start a new game before moving")
            current_map = row[0]
            if target_map not in self.MAP_GRAPH.get(current_map, ()):
                return False
            self._connection.execute(
                "UPDATE player_save SET current_map=?, updated_at=CURRENT_TIMESTAMP WHERE id=1",
                (target_map,),
            )
            return True

    def get_sub_quest(self, quest_id: str) -> dict[str, Any]:
        if quest_id not in self.SUB_QUEST_TARGETS:
            raise ValueError(f"unknown sub quest: {quest_id}")
        row = self._connection.execute(
            "SELECT quest_id, status, progress, target, updated_at FROM sub_quests WHERE quest_id=?",
            (quest_id,),
        ).fetchone()
        if row is None:
            raise RuntimeError("start a new game before reading sub quests")
        return dict(row)

    def accept_sub_quest(self, quest_id: str) -> bool:
        self.get_sub_quest(quest_id)
        with self._connection:
            cursor = self._connection.execute(
                "UPDATE sub_quests SET status='IN_PROGRESS', updated_at=CURRENT_TIMESTAMP "
                "WHERE quest_id=? AND status='NOT_STARTED'", (quest_id,)
            )
            return cursor.rowcount == 1

    def advance_sub_quest(self, quest_id: str, amount: int = 1) -> int:
        self.get_sub_quest(quest_id)
        if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
            raise ValueError("amount must be a non-negative integer")
        with self._connection:
            self._connection.execute(
                "UPDATE sub_quests SET progress=MIN(target, progress + ?), updated_at=CURRENT_TIMESTAMP "
                "WHERE quest_id=? AND status='IN_PROGRESS'", (amount, quest_id)
            )
        return self.get_sub_quest(quest_id)["progress"]

    def record_goblin_scout_kill(self, amount: int = 1) -> int:
        return self.advance_sub_quest("sq_goblin_hunt", amount)

    def complete_sub_quest(self, quest_id: str) -> bool:
        quest = self.get_sub_quest(quest_id)
        if quest["status"] != "IN_PROGRESS" or quest["progress"] < quest["target"]:
            return False
        with self._connection:
            cursor = self._connection.execute(
                "UPDATE sub_quests SET status='COMPLETED', updated_at=CURRENT_TIMESTAMP "
                "WHERE quest_id=? AND status='IN_PROGRESS' AND progress>=target", (quest_id,)
            )
            if cursor.rowcount != 1:
                return False
            if quest_id == "sq_moon_herb":
                self._connection.execute(
                    "UPDATE player_save SET gold=gold+100, updated_at=CURRENT_TIMESTAMP WHERE id=1"
                )
                self._connection.execute(
                    "UPDATE player_inventory SET high_potions=high_potions+2, updated_at=CURRENT_TIMESTAMP WHERE id=1"
                )
            elif quest_id == "sq_old_sword":
                self._connection.execute(
                    "UPDATE player_save SET atk=atk+4, def=def+4, updated_at=CURRENT_TIMESTAMP WHERE id=1"
                )
            elif quest_id == "sq_goblin_hunt":
                self._connection.execute(
                    "UPDATE player_save SET gold=gold+180, updated_at=CURRENT_TIMESTAMP WHERE id=1"
                )
                self._connection.execute(
                    "UPDATE player_inventory SET potions=potions+3, updated_at=CURRENT_TIMESTAMP WHERE id=1"
                )
            return True

    def recover_old_sword(self) -> bool:
        """Mark the 폐광 chest objective and persist the recovered quest item."""
        quest = self.get_sub_quest("sq_old_sword")
        if quest["status"] != "IN_PROGRESS" or quest["progress"] >= quest["target"]:
            return False
        with self._connection:
            self._connection.execute(
                "UPDATE player_inventory SET broken_old_sword=1, updated_at=CURRENT_TIMESTAMP WHERE id=1"
            )
        self.advance_sub_quest("sq_old_sword")
        return True

    def _flag(self, key: str) -> int:
        row = self._connection.execute(
            "SELECT is_cleared FROM quest_flags WHERE flag_key=?", (key,)
        ).fetchone()
        return int(row[0]) if row else 0

    def clear_shrine(self, shrine_key: str) -> bool:
        if shrine_key not in self.SHRINES:
            raise ValueError(f"unknown shrine: {shrine_key}")
        with self._connection:
            if self._connection.execute("SELECT 1 FROM player_save WHERE id=1").fetchone() is None:
                raise RuntimeError("start a new game before clearing a shrine")
            if self._flag(shrine_key):
                return False
            self._connection.execute(
                "UPDATE player_save SET level=level+1, max_hp=max_hp+30, hp=max_hp+30, "
                "atk=atk+5, def=def+3, updated_at=CURRENT_TIMESTAMP WHERE id=1"
            )
            if shrine_key == "shrine_wind":
                self._connection.execute("UPDATE player_save SET evasion_bonus=1 WHERE id=1")
            elif shrine_key == "shrine_earth":
                self._connection.execute(
                    "UPDATE player_save SET max_hp=max_hp+50, hp=max_hp, def=def+5 WHERE id=1"
                )
            elif shrine_key == "shrine_fire":
                self._connection.execute("UPDATE player_save SET atk=atk+10 WHERE id=1")
            self._connection.execute(
                "UPDATE quest_flags SET is_cleared=1, cleared_at=CURRENT_TIMESTAMP WHERE flag_key=?",
                (shrine_key,),
            )
            return True

    def check_fountain_awakening(self) -> bool:
        with self._connection:
            if not all(self._flag(shrine) for shrine in self.SHRINES):
                return False
            if not self._flag("star_sword_awakened"):
                self._connection.execute(
                    "UPDATE player_save SET weapon='별빛의 검', atk=atk+25, updated_at=CURRENT_TIMESTAMP WHERE id=1"
                )
                self._connection.execute(
                    "UPDATE quest_flags SET is_cleared=1, cleared_at=CURRENT_TIMESTAMP "
                    "WHERE flag_key='star_sword_awakened'"
                )
            return True

    def simulate_battle(self, monster_id: str) -> BattleResult:
        if monster_id not in self.MONSTERS:
            raise ValueError(f"unknown monster: {monster_id}")
        with self._connection:
            player_row = self._connection.execute("SELECT * FROM player_save WHERE id=1").fetchone()
            if player_row is None:
                raise RuntimeError("start a new game before battling")
            if monster_id == "final_boss" and not self._flag("star_sword_awakened"):
                raise PermissionError("the final boss is locked until the star sword awakens")
            monster_hp, monster_atk, monster_def = self.MONSTERS[monster_id]
            player_hp = int(player_row["hp"])
            player_atk = int(player_row["atk"])
            player_def = int(player_row["def"])
            if player_hp <= 0:
                return BattleResult(False, 0, 0, monster_hp)
            turns = 0
            while player_hp > 0 and monster_hp > 0:
                turns += 1
                monster_hp = max(0, monster_hp - max(1, player_atk - monster_def))
                if monster_hp:
                    player_hp = max(0, player_hp - max(1, monster_atk - player_def))
            victory = monster_hp == 0
            self._connection.execute(
                "UPDATE player_save SET hp=?, updated_at=CURRENT_TIMESTAMP WHERE id=1", (player_hp,)
            )
            if victory and monster_id in self.SHRINES:
                # Winning a shrine guardian encounter is the canonical way to clear its shrine.
                self.clear_shrine(monster_id)
            if victory and monster_id == "final_boss":
                self._connection.execute(
                    "UPDATE quest_flags SET is_cleared=1, cleared_at=CURRENT_TIMESTAMP WHERE flag_key='final_boss'"
                )
            return BattleResult(victory, turns, player_hp, monster_hp)

    def is_ending_unlocked(self) -> bool:
        return bool(self._flag("final_boss"))

    def close(self) -> None:
        self._connection.close()

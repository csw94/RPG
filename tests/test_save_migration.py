"""Old saves keep their place after the map layout changes (v0.7.0 enlargement, v0.9.1 flip)."""

import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from db.save_manager import SaveManager
from gameplay.save_migration import LAYOUT_VERSION, guess_layout, migrate
from scenes.field_scene import FieldScene

V06 = "2026-11-23 10:00:00"      # before v0.7.0: 40x24 fields, 25x16 village
V090 = "2026-11-24 05:00:00"     # v0.7.0 .. v0.9.0: 52x31 fields, south field runs uphill
V091 = "2026-11-24 07:30:00"     # v0.9.1: south field runs downhill, still unversioned


class FakeGame:
    active_slot = 1

    def save_game(self):
        pass


class GuessTests(unittest.TestCase):
    def test_layout_is_guessed_from_the_save_time(self):
        self.assertEqual(guess_layout(V06), 1)
        self.assertEqual(guess_layout(V090), 2)
        self.assertEqual(guess_layout(V091), 3)
        self.assertEqual(guess_layout(None), LAYOUT_VERSION)


class MigrationTests(unittest.TestCase):
    def test_v06_field_positions_scale_with_the_map(self):
        state = {"world": "field_east", "x": 17.0, "y": 12.0,
                 "opened_by_world": {"field_east": [[17, 11]]}, "collected_herbs": [[13, 10], [22, 8]]}
        new = migrate(state, V06)
        self.assertEqual((new["x"], new["y"]), (22.0, 16.0))
        self.assertEqual(new["opened_by_world"]["field_east"], [[22, 14]])
        self.assertEqual(sorted(new["collected_herbs"]), [[17, 13], [29, 10]])
        self.assertEqual(new["layout_version"], LAYOUT_VERSION)

    def test_v06_village_and_shrine_clearing_shift_by_the_core_offset(self):
        self.assertEqual(self._pos(migrate({"world": "village", "x": 12.0, "y": 11.0}, V06)), (15.0, 13.0))
        self.assertEqual(self._pos(migrate({"world": "village_north_shrine", "x": 12.0, "y": 10.0}, V06)),
                         (15.0, 12.0))

    def test_v06_south_field_is_scaled_then_flipped(self):
        new = migrate({"world": "field_south", "x": 22.0, "y": 3.0}, V06)
        self.assertEqual(self._pos(new), (29.0, 26.0))

    def test_v090_south_field_is_flipped(self):
        state = {"world": "field_south", "x": 29.0, "y": 4.0,
                 "opened_by_world": {"field_south": [[23, 16], [9, 20]], "field_east": [[22, 14]]}}
        new = migrate(state, V090)
        self.assertEqual(self._pos(new), (29.0, 26.0))
        self.assertEqual(sorted(new["opened_by_world"]["field_south"]), [[9, 10], [23, 14]])
        self.assertEqual(new["opened_by_world"]["field_east"], [[22, 14]])

    def test_current_and_versioned_saves_are_untouched(self):
        for state, when in (({"world": "field_south", "x": 16.0, "y": 3.0}, V091),
                            ({"world": "field_south", "x": 16.0, "y": 3.0, "layout_version": 3}, V06)):
            self.assertEqual(self._pos(migrate(state, when)), (16.0, 3.0))

    def test_dungeons_and_houses_keep_their_coordinates(self):
        for world in ("shrine_fire_1f", "village_house_1"):
            self.assertEqual(self._pos(migrate({"world": world, "x": 5.0, "y": 7.0}, V06)), (5.0, 7.0))

    def test_migrated_old_chest_stays_opened_in_game(self):
        state = migrate({"world": "field_south", "x": 29.0, "y": 4.0,
                         "opened_by_world": {"field_south": [[23, 16]]}}, V090)
        field = FieldScene(FakeGame(), state)
        self.assertFalse(field.position_recovered)
        self.assertIn((23, 14), field.opened)

    def test_new_saves_record_the_layout_version(self):
        field = FieldScene(FakeGame(), {"world": "field_east", "x": 2, "y": 16})
        self.assertEqual(field.serialize()["layout_version"], LAYOUT_VERSION)

    @staticmethod
    def _pos(state):
        return (state["x"], state["y"])


class SaveManagerTests(unittest.TestCase):
    def test_loading_an_old_save_migrates_it(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            path = Path(folder) / "save.db"
            manager = SaveManager(path)
            manager.save({"world": "field_south", "x": 29.0, "y": 4.0}, 2)
            with sqlite3.connect(path) as connection:
                connection.execute("UPDATE saves SET updated_at=? WHERE slot=2", (V090,))
            loaded = manager.load(2)
            self.assertEqual((loaded["x"], loaded["y"]), (29.0, 26.0))
            with sqlite3.connect(path) as connection:
                raw = json.loads(connection.execute("SELECT payload FROM saves WHERE slot=2").fetchone()[0])
            self.assertNotIn("layout_version", raw)  # loading never rewrites the slot by itself



class LegacyFieldTests(unittest.TestCase):
    def test_single_field_saves_resume_at_the_forest_entrance(self):
        import main
        from gameplay.world_data import FIELD_ROUTES

        game = main.Game.__new__(main.Game)  # no window or save file needed
        field = game._create_world({"world": "field", "x": 22.0, "y": 12.0})
        self.assertEqual(field.world, "field_east")
        self.assertEqual((field.player["x"], field.player["y"]), FIELD_ROUTES["field_east"]["village_spawn"])
        self.assertFalse(field.position_recovered)


if __name__ == "__main__":
    unittest.main()

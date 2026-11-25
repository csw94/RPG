"""Oak Valley layout v4: buildings of different sizes placed off-grid instead of mirrored."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay import save_migration
from scenes.village_scene import PLACES, VillageScene, house_plot
from utils.house_art import HOUSE_STYLES


class FakeGame:
    active_slot = 1
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}

    def save_game(self):
        pass

    def font(self, size):
        return pygame.font.Font(None, size)


def house_rect(key):
    """Pixel rectangle the village blits the (scaled) house into."""
    tx, ty = PLACES[key]
    width = HOUSE_STYLES[key]["width"] * 32
    w, h = round((width + 24) * 0.8), round(214 * 0.8)
    cx, cy = tx * 32 - 10 + (width + 24) / 2, ty * 32 - 10 + 107
    return pygame.Rect(round(cx - w / 2), round(cy - h / 2), w, h)


class VillageLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))
        cls.village = VillageScene(FakeGame(), {"world": "village", "x": 15, "y": 15})

    def test_every_house_has_a_place(self):
        self.assertEqual(set(PLACES), set(HOUSE_STYLES))

    def test_houses_come_in_different_sizes(self):
        widths = {HOUSE_STYLES[key]["width"] for key in PLACES}
        self.assertGreaterEqual(len(widths), 2)
        for key in PLACES:
            self.assertEqual(HOUSE_STYLES[key]["width"] % 2, 1, f"{key}: odd widths centre the door on a tile")

    def test_layout_is_not_mirrored(self):
        rows = [PLACES[key][1] for key in PLACES]
        self.assertGreaterEqual(len(set(rows)), 5, "houses should not line up in rows")
        cols = [PLACES[key][0] for key in PLACES]
        self.assertGreaterEqual(len(set(cols)), 5, "houses should not line up in columns")
        # No house is the mirror image of another across the plaza's centre line (x = 15.5).
        spots = {(tx + HOUSE_STYLES[key]["width"] / 2, ty) for key, (tx, ty) in PLACES.items()}
        for cx, ty in spots:
            self.assertNotIn((31 - cx, ty), spots - {(cx, ty)})

    def test_door_sits_under_the_middle_of_the_drawn_house(self):
        for key in PLACES:
            footprint, door = house_plot(key)
            bx, by, bw, bh = footprint
            self.assertEqual(door, (bx + bw // 2, by + bh), key)
            self.assertLessEqual(abs(house_rect(key).centerx - (door[0] * 32 + 16)), 4, key)

    def test_village_uses_the_derived_plots(self):
        v = self.village
        self.assertEqual(v.BUILDINGS["herb_cottage"], house_plot("herb_cottage")[0])
        self.assertEqual(v.BUILDINGS["knight_quarters"], house_plot("knight_quarters")[0])
        self.assertEqual(v.QUEST_HOUSE_DOOR, house_plot("herb_cottage")[1])
        self.assertEqual(v.KNIGHT_HOUSE_DOOR, house_plot("knight_quarters")[1])
        for key, place in v.DISTRICT.items():
            self.assertEqual((place["footprint"], place["door"]), house_plot(key), key)

    def test_no_tree_is_drawn_over_a_house(self):
        v = self.village
        for tx, ty in v.trees:
            tree = pygame.Rect(tx * 32 - 8, ty * 32 - 32, 48, 64)
            for key in PLACES:
                self.assertFalse(tree.colliderect(house_rect(key)), (key, (tx, ty)))

    def test_doors_and_exits_are_on_or_next_to_a_road(self):
        v = self.village
        road = v.road_tiles()
        for door in [v.QUEST_HOUSE_DOOR, v.KNIGHT_HOUSE_DOOR, *(p["door"] for p in v.DISTRICT.values())]:
            x, y = door
            near = {(x, y), (x, y + 1), (x - 1, y + 1), (x + 1, y + 1)}
            self.assertTrue(near & road, door)

    def test_garens_house_looks_like_a_knights_home(self):
        props = HOUSE_STYLES["knight_quarters"]["props"]
        self.assertIn("shield", props)
        self.assertNotIn("awning", props)


class LayoutFourMigrationTests(unittest.TestCase):
    def test_layout_version_went_up(self):
        self.assertEqual(save_migration.LAYOUT_VERSION, 4)

    def test_old_door_spots_follow_their_buildings(self):
        moves = {(24, 10): VillageScene.HOUSE_EXITS["village_house_2"],
                 (6, 10): VillageScene.HOUSE_EXITS["village_house_1"],
                 (37, 8): VillageScene.DISTRICT["inn"]["door"],
                 (25, 26): VillageScene.DISTRICT["apothecary"]["door"]}
        for old, new in moves.items():
            state = save_migration.migrate({"world": "village", "x": old[0], "y": old[1], "layout_version": 3})
            self.assertEqual((state["x"], state["y"]), (float(new[0]), float(new[1])), old)
            self.assertEqual(state["layout_version"], 4)

    def test_other_village_spots_and_other_maps_stay_put(self):
        state = save_migration.migrate({"world": "village", "x": 15, "y": 15, "layout_version": 3})
        self.assertEqual((state["x"], state["y"]), (15.0, 15.0))
        state = save_migration.migrate({"world": "field_east", "x": 24, "y": 10, "layout_version": 3})
        self.assertEqual((state["x"], state["y"]), (24.0, 10.0))


if __name__ == "__main__":
    unittest.main()

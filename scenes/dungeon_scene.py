"""Reusable two-floor shrine dungeon. Each shrine has its own saved floors and boss."""

import pygame

from gameplay.enemies import ENEMIES
from gameplay.world_data import FIELD_ROUTES
from scenes.field_scene import FieldScene
from settings import TILE_SIZE
from utils.pixel_art import fit_sprite, hero_sprite, sprite, tile_noise


SHRINE_DUNGEONS = {
    "shrine_wind": {
        "boss": "shrine_wind", "name": "바람의 제단", "chest": "potion",
        "field": "field_east",
        "chest_pos": (4, 3), "stairs": (22, 2), "boss_pos": (12, 7), "exit": (2, 14),
        "style": "wind",
    },
    "shrine_earth": {
        "boss": "shrine_earth", "name": "대지의 폐광", "chest": "broken_sword",
        "field": "field_west",
        "chest_pos": (20, 12), "stairs": (22, 13), "boss_pos": (12, 3), "exit": (12, 14),
        "style": "earth",
    },
    "shrine_fire": {
        "boss": "shrine_fire", "name": "불꽃의 신전", "chest": "high_potion",
        "field": "field_south",
        "chest_pos": (12, 12), "stairs": (12, 2), "boss_pos": (12, 7), "exit": (22, 14),
        "style": "fire",
    },
}


class DungeonScene(FieldScene):
    COLS, ROWS = 25, 16
    ENTRY = (2, 13)

    def __init__(self, game, state=None):
        state = dict(state or {})
        map_id = state.get("map_id", state.get("world", "dungeon"))
        if map_id == "dungeon":
            map_id = "shrine_wind_1f"
        if map_id not in self.map_ids():
            map_id = "shrine_wind_1f"
        state["world"] = map_id
        state["map_id"] = map_id
        super().__init__(game, state)
        self.world = map_id
        self.map_id = map_id
        self.shrine_key, floor = map_id.rsplit("_", 1)
        self.floor = int(floor[0])
        shrine = SHRINE_DUNGEONS[self.shrine_key]
        self.boss_id = shrine["boss"]
        self.dungeon_name = shrine["name"]
        self.field_id = shrine["field"]
        self.route_data = FIELD_ROUTES[self.field_id]
        self.EXIT = shrine["exit"]
        self.STAIRS = shrine["stairs"]
        self.boss_position = shrine["boss_pos"]
        self.encounter_rate = 0.08 if self.floor == 1 else 0
        self.enemy_pool = ("bat", "skeleton")
        self.chests = {shrine["chest_pos"]: shrine["chest"]} if self.floor == 1 else {}
        self.walls = {
            (x, y) for x in range(self.COLS) for y in range(self.ROWS)
            if x in (0, self.COLS - 1) or y in (0, self.ROWS - 1)
        }
        self.style = shrine["style"]
        self._build_shrine_layout(shrine["style"])
        self.walls.difference_update({self.EXIT, self.STAIRS, self.boss_position,
                                      shrine["chest_pos"], self.ENTRY})
        fallback = (self.EXIT[0] + (1 if self.EXIT[0] < 12 else -1), 14) if self.floor == 1 else (3, 14)
        self.position_recovered = self._restore_player_position(fallback) or self.position_recovered
        self.message = f"{self.dungeon_name} {self.floor}층 · 계단과 보물상자를 찾아보세요."
        if self.floor == 2:
            self.message = f"{self.dungeon_name} 2층 · 제단의 수호자가 기다리고 있습니다."

    def _build_shrine_layout(self, style):
        """Hand-place a different corridor plan for each shrine and each floor."""
        if style == "wind":
            # Wind: narrow, alternating passages around an open circular altar room.
            self.walls.update((6, y) for y in range(2, 14) if y not in (4, 10))
            self.walls.update((12, y) for y in range(2, 12) if y not in (7, 10))
            self.walls.update((18, y) for y in range(4, 14) if y not in (6, 7, 11))
            self.walls.update((x, 5) for x in range(6, 19) if x not in (9, 15))
            if self.floor == 2:
                self.walls.update((x, 3) for x in range(7, 18) if x not in (12,))
                self.walls.update((x, 11) for x in range(7, 18) if x not in (12,))
                self.walls.update((7, y) for y in range(3, 12) if y not in (7,))
                self.walls.update((17, y) for y in range(3, 12) if y not in (7,))
        elif style == "earth":
            # Earth: broad mine galleries, support pillars, and a side chamber.
            self.walls.update((x, 4) for x in range(2, 23) if x not in (5, 12, 19))
            self.walls.update((x, 10) for x in range(2, 23) if x not in (8, 16, 21))
            self.walls.update((8, y) for y in range(4, 11) if y not in (7,))
            self.walls.update((16, y) for y in range(4, 11) if y not in (6,))
            self.walls.update({(4, 7), (12, 6), (12, 8), (20, 7)})
            if self.floor == 2:
                self.walls.update((x, 7) for x in range(5, 20) if x != 12)
                self.walls.update((6, y) for y in range(2, 13) if y in (3, 4, 10, 11))
                self.walls.update((18, y) for y in range(2, 13) if y in (3, 4, 10, 11))
        else:
            # Fire: a symmetrical temple with a long central nave and side chapels.
            self.walls.update((6, y) for y in range(2, 14) if y not in (7, 11))
            self.walls.update((18, y) for y in range(2, 14) if y not in (7, 11))
            self.walls.update((x, 4) for x in range(6, 19) if x not in (12,))
            self.walls.update((x, 10) for x in range(6, 19) if x not in (12,))
            if self.floor == 2:
                self.walls.update((x, 3) for x in range(8, 17) if x not in (12,))
                self.walls.update((x, 11) for x in range(8, 17) if x not in (12,))
                self.walls.update((8, y) for y in range(3, 12) if y not in (7,))
                self.walls.update((16, y) for y in range(3, 12) if y not in (7,))

    @staticmethod
    def map_ids():
        return tuple(f"{shrine}_{floor}f" for shrine in SHRINE_DUNGEONS for floor in (1, 2))

    @classmethod
    def is_dungeon_map(cls, map_id):
        return map_id in cls.map_ids() or map_id == "dungeon"

    def serialize(self):
        state = super().serialize()
        state["map_id"] = self.map_id
        return state

    def _stair_spawn(self):
        x, y = self.STAIRS
        return (x + 1 if x <= 12 else x - 1, y)

    def _interact(self):
        x, y = self.player["x"], self.player["y"]
        near = lambda point: (x - point[0]) ** 2 + (y - point[1]) ** 2 <= 1.1
        if self.floor == 2 and near(self.boss_position):
            if self.quest_flags[self.boss_id]:
                self.message = "수호자는 쓰러졌고 제단의 봉인이 정화되었습니다."
            else:
                self.game.start_battle(self.boss_id)
        elif near(self.EXIT):
            if self.floor == 1:
                self.game.enter_world(self.field_id, self.route_data["return_dungeon"])
            else:
                self.game.enter_world(f"{self.shrine_key}_1f", self._stair_spawn())
        elif near(self.STAIRS):
            if self.floor == 1:
                self.game.enter_world(f"{self.shrine_key}_2f", self._stair_spawn())
            else:
                self.game.enter_world(f"{self.shrine_key}_1f", self._stair_spawn())
        else:
            nearest = min(self.chests, key=lambda point: (point[0] - x) ** 2 + (point[1] - y) ** 2,
                          default=None)
            if nearest and near(nearest) and nearest not in self.opened:
                if self.chests[nearest] == "broken_sword":
                    quest = self.sub_quests["sq_old_sword"]
                    if quest["status"] != "IN_PROGRESS":
                        self.message = "먼저 마을에서 가렌의 부탁을 받아야 합니다."
                        return
                    self.opened.add(nearest)
                    self.quest_items.add("broken_old_sword")
                    quest["progress"] = min(quest["target"], quest["progress"] + 1)
                    self.message = "빛바랜 상자에서 부러진 옛 검을 발견했습니다."
                    self.game.save_game()
                else:
                    self._open_chest(nearest)
            else:
                self.message = "주변에는 상호작용할 대상이 없습니다."

    def hud_title(self):
        return f"{self.dungeon_name} {self.floor}층"

    def floor_tile(self, x, y):
        return f"dfloor_{self.style}_{int(tile_noise(x, y, 61) * 3)}"

    def wall_tile(self, x, y):
        """Walls with open floor below show their brick face; others show the dark top."""
        below = (x, y + 1)
        if y + 1 < self.ROWS and below not in self.walls:
            return f"dwall_face_{self.style}"
        return f"dwall_top_{self.style}"

    def dungeon_decals(self):
        if getattr(self, "_decals", None) is None:
            name = {"wind": "tuft", "earth": "pebbles", "fire": "ember"}[self.style]
            special = {self.EXIT, self.STAIRS, self.boss_position, self.ENTRY, *self.chests}
            self._decals = {(x, y): name for x in range(self.COLS) for y in range(self.ROWS)
                            if (x, y) not in self.walls and (x, y) not in special
                            and tile_noise(x, y, 62) < 0.07}
        return self._decals

    def draw(self, surface):
        t = TILE_SIZE
        cam_x, cam_y = (round(v) for v in self._camera())
        surface.fill((20, 16, 20), (0, 0, 800, self.VIEW_HEIGHT))
        start_x, end_x = max(0, cam_x // t), min(self.COLS, (cam_x + 800) // t + 2)
        start_y, end_y = max(0, cam_y // t), min(self.ROWS, (cam_y + self.VIEW_HEIGHT) // t + 2)
        decals = self.dungeon_decals()
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                pos = (x * t - cam_x, y * t - cam_y)
                if (x, y) in self.walls:
                    name = self.wall_tile(x, y)
                    surface.blit(sprite(name, (t, t)), pos)
                    if name.startswith("dwall_face_") and tile_noise(x, y, 63) < 0.14:
                        surface.blit(sprite(f"wall_torch_{self.style}", (t, t)), pos)
                else:
                    surface.blit(sprite(self.floor_tile(x, y), (t, t)), pos)
                    if (x, y - 1) in self.walls:
                        shade = pygame.Surface((t, 6), pygame.SRCALPHA)
                        shade.fill((20, 14, 20, 70))
                        surface.blit(shade, pos)
                    if (x, y) in decals:
                        surface.blit(sprite(decals[(x, y)], (t, t)), pos)
                if (x, y) in self.chests:
                    name = "chest_open" if (x, y) in self.opened else "chest"
                    surface.blit(sprite(name, (t, t)), pos)
        sx, sy = self.STAIRS
        surface.blit(sprite("dstairs", (t, t)), (sx * t - cam_x, sy * t - cam_y))
        ex, ey = self.EXIT
        surface.blit(sprite(f"portal_dungeon_{int(self.portal_clock * 3) % 2}", (48, 64)),
                     (ex * t - cam_x - 8, ey * t - cam_y - 32))
        if self.floor == 2 and not self.quest_flags[self.boss_id]:
            bx, by = self.boss_position
            boss = fit_sprite(ENEMIES[self.boss_id]["sprite"], (48, 48))
            surface.blit(sprite("shadow", (36, 12)), (bx * t + t // 2 - 18 - cam_x, (by + 1) * t - 8 - cam_y))
            surface.blit(boss, (bx * t + t // 2 - boss.get_width() // 2 - cam_x,
                                (by + 1) * t - boss.get_height() - cam_y))
        foot_x = round(self.player["x"] * t + t / 2) - cam_x
        foot_y = round((self.player["y"] + 1) * t) - cam_y
        surface.blit(sprite("shadow", (26, 10)), (foot_x - 13, foot_y - 7))
        surface.blit(hero_sprite(self.weapon, self.armor, (t, t + 16), self.facing,
                                 int(self.walk_clock) % 2 if self.walk_clock else 0),
                     (foot_x - t // 2, foot_y - t - 16))
        self._draw_dialogue(surface)
        self._draw_hud(surface)

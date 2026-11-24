"""The Oak Valley plaza: chief's hall, Marta's cottage, Garen's quarters and Logan's stall."""

import pygame
from scenes.field_scene import FieldScene
from gameplay.world_data import FIELD_ROUTES
from settings import TILE_SIZE, WIDTH
from utils.pixel_art import NPC_SIZE, PALETTE, hero_sprite, sprite

OUTLINE = PALETTE["outline"]
# One cozy roof family: each building gets its own hue at the same softness and value.
# (base, row line, shingle seam, bright eave)
ROOFS = {
    "cottage": ((72, 120, 126), (100, 152, 150), (54, 92, 104), (140, 190, 176)),
    "shop": ((166, 98, 62), (200, 130, 84), (128, 72, 50), (226, 164, 106)),
    "chief": ((160, 76, 62), (196, 106, 80), (122, 56, 50), (226, 140, 102)),
}


class VillageScene(FieldScene):
    COLS, ROWS = 25, 16
    VILLAGER = (7, 8)
    CHIEF = (12, 7)
    FOUNTAIN = (12, 11)
    GATE = (12, 15)
    FIELD_GATES = {"field_west": (0, 8), "field_east": (24, 8), "field_south": (12, 15),
                   "village_north_shrine": (12, 0)}
    QUEST_HOUSE_DOOR = (5, 7)
    KNIGHT_HOUSE_DOOR = (19, 7)
    LOGAN = (16, 10)
    LOGAN_CRATES = ((15, 10), (17, 10))

    def __init__(self, game, state=None):
        state = dict(state or {})
        state["world"] = "village"
        super().__init__(game, state)
        self.world = "village"
        self.encounter_rate = 0
        self.message = "광장 중앙 촌장 집과 북쪽 제단 길을 살펴보세요."
        self.chests = {}
        self.walls = {
            (x, y) for x in range(self.COLS) for y in range(self.ROWS)
            if (x in (0, self.COLS - 1) or y in (0, self.ROWS - 1))
            and (x, y) not in self.FIELD_GATES.values()
        }
        self.walls.update((x, y) for x in range(3, 7) for y in range(3, 7))
        self.walls.update((x, y) for x in range(17, 23) for y in range(3, 7))
        self.walls.update((x, y) for x in range(8, 17) for y in range(2, 7))
        self.trees = {
            (2, 11), (3, 11), (4, 12), (6, 12), (7, 13), (3, 14),
            (21, 11), (22, 11), (20, 12), (22, 13), (19, 14),
            (9, 13), (15, 13),
        }
        self.solid_npcs = {self.VILLAGER, self.LOGAN}
        self.walls.update(self.LOGAN_CRATES)
        self.walls.update(self.trees)
        self.walls.add(self.FOUNTAIN)
        self.walls.difference_update({self.GATE, self.VILLAGER, self.CHIEF, (12, 1), (7, 1)})
        self.position_recovered = self._restore_player_position((12, 13)) or self.position_recovered
        if self.position_recovered:
            self.message = "저장 위치를 마을 입구로 복구했습니다."

    def _interact(self):
        x, y = self.player["x"], self.player["y"]
        near = lambda target, radius=1.0: (x - target[0]) ** 2 + (y - target[1]) ** 2 <= radius ** 2
        if near(self.QUEST_HOUSE_DOOR):
            self.game.enter_world("village_house_1", (12, 12))
        elif near(self.KNIGHT_HOUSE_DOOR):
            self.game.enter_world("village_house_2", (12, 12))
        elif near(self.LOGAN, 1.4):
            self._interact_logan()
        elif any(near(gate) for gate in self.FIELD_GATES.values()):
            route_id, gate = min(self.FIELD_GATES.items(),
                                 key=lambda item: (item[1][0] - x) ** 2 + (item[1][1] - y) ** 2)
            spawn = FIELD_ROUTES[route_id]["village_spawn"] if route_id in FIELD_ROUTES else (12, 12)
            self.game.enter_world(route_id, spawn)
        elif near(self.CHIEF):
            self.game.enter_world("village_chief_house", (12, 12))
        elif near(self.FOUNTAIN, 1.2):
            if self.quest_flags["final_boss"]:
                self.show_dialogue([
                    "별빛 분수가 다시 안전한 빛을 내뿜는다.",
                    "그날의 축제를 다시 떠올려 본다...",
                ], action="epilogue")
            elif self.quest_flags["star_sword_awakened"]:
                self.show_dialogue([
                    "\ud558\ud558\ud558! \uc218\uace0\ud588\ub2e4, \uc560\uc1a1\uc774. \ub124\uac00 \ubaa8\uc544\uc900 \uc138 \uac1c\uc758 \uc778\uc7a5, \ub9c8\uc655\ub2d8\uaed8 \ubc14\uce58\ub3c4\ub85d \ud558\uc9c0!",
                    "\ud751\uae30\uc0ac \ub9d0\ud3ec\uc2a4\uac00 \ubcc4\ube5b \ubd84\uc218 \uc55e\uc5d0 \ubaa8\uc2b5\uc744 \ub4dc\ub7ec\ub0c8\ub2e4!",
                ], action="final_boss")
            elif self.check_fountain_awakening():
                self.show_dialogue([
                    "\uc138 \uc778\uc7a5\uc774 \ubd84\uc218\uc5d0 \ubaa8\uc774\uc790 \ubcc4\ube5b\uc758 \uac80\uc774 \uae68\uc5b4\ub0ac\ub2e4!",
                    "\uac80\uc744 \ub4e4\uace0 \ub2e4\uc2dc \ubd84\uc218\ub85c \uc640\uc11c \ub9c8\uc655\uad70\uc744 \ub9c9\uc544\ub77c!",
                ])
            else:
                self.show_dialogue(["\ubd84\uc218\uc758 \ube5b\uc774 \uc57d\ud574\uc84c\ub2e4. \ub3d9\ucabd\u00b7\uc11c\ucabd\u00b7\ub0a8\ucabd \uc81c\ub2e8\uc758 \uc778\uc7a5\uc744 \ubaa8\ub450 \ubaa8\uc544\uc57c \ud55c\ub2e4."])
        elif near(self.VILLAGER):
            if self.quest_flags["final_boss"]:
                self.show_dialogue(["광장 주민: 수호 기사님! 아이들이 모두 기사님 흉내를 내며 놀아요."])
            else:
                self.show_dialogue(["광장 주민: 동쪽 숲길이 가장 순해요. 서쪽 협곡과 남쪽 화산은 조심하세요."])
        else:
            self.message = "\uc8fc\ubcc0\uc5d0\ub294 \uc0c1\ud638\uc791\uc6a9\ud560 \ub300\uc0c1\uc774 \uc5c6\uc2b5\ub2c8\ub2e4."

    def _interact_logan(self):
        cleared = sum(self.quest_flags[key] for key in ("shrine_wind", "shrine_earth", "shrine_fire"))
        if self.quest_flags["final_boss"]:
            advice = "별빛의 검이라니... 대장장이 평생 이런 검은 처음 보네. 뭐든 골라 보게!"
        elif self.quest_flags["star_sword_awakened"] or cleared == 3:
            advice = "흑기사와 싸우기 전에 고급 회복약을 넉넉히 챙기게. 녀석의 암흑 베기는 아프다네."
        elif cleared:
            advice = "바위 골렘은 단단하니 좋은 무기를, 화염 리자드맨은 화력이 세니 갑옷을 챙기게."
        else:
            advice = "처음이라면 동쪽 숲길부터 가 보게. 슬라임 정도는 녹슨 검으로도 충분하지."
        self.show_dialogue(["어서 오게! 잡화상 로건일세.", advice], action="open_shop")

    @staticmethod
    def _draw_shingles(surface, points, bounds, colors):
        pygame.draw.polygon(surface, colors[0], points)
        pygame.draw.polygon(surface, OUTLINE, points, 3)
        left, top, width, height = bounds
        for row in range(9, height - 4, 10):
            half = width * (row / height) / 2
            center = left + width / 2
            pygame.draw.line(surface, colors[1], (round(center - half), top + row),
                             (round(center + half), top + row), 2)
            step = 11
            for index, px in enumerate(range(round(center - half + 4), round(center + half), step)):
                offset = 5 if (row // 10) % 2 else 0
                pygame.draw.line(surface, colors[2], (px + offset, top + row - 7),
                                 (px + offset, top + row - 1), 1)

    @staticmethod
    def _draw_window(surface, rect, flower_box=False):
        pygame.draw.rect(surface, OUTLINE, rect.inflate(6, 6))
        pygame.draw.rect(surface, (93, 151, 163), rect)
        pygame.draw.rect(surface, (211, 177, 115), rect, 3)
        pygame.draw.line(surface, (235, 205, 150), rect.midtop, rect.midbottom, 2)
        pygame.draw.line(surface, (235, 205, 150), rect.midleft, rect.midright, 2)
        if flower_box:
            box = pygame.Rect(rect.x - 2, rect.bottom + 2, rect.width + 4, 6)
            pygame.draw.rect(surface, (105, 60, 39), box)
            pygame.draw.line(surface, (74, 112, 55), (box.x + 5, box.y), (box.x + 7, box.y - 5), 2)
            pygame.draw.line(surface, (177, 76, 63), (box.centerx, box.y), (box.centerx + 2, box.y - 5), 2)
            pygame.draw.line(surface, (237, 187, 92), (box.right - 5, box.y), (box.right - 7, box.y - 4), 2)

    def _draw_house(self, surface, tile_x, tile_y, shop=False):
        x, y = tile_x * TILE_SIZE, tile_y * TILE_SIZE
        width = (7 if shop else 6) * TILE_SIZE
        bounds = pygame.Rect(x - 10, y - 10, width + 24, 214)
        layer = pygame.Surface((WIDTH, 512), pygame.SRCALPHA)
        self._paint_house(layer, tile_x, tile_y, shop)
        crop = layer.subsurface(bounds).copy()
        scaled = pygame.transform.smoothscale(crop, (round(bounds.width * 0.8), round(bounds.height * 0.8)))
        surface.blit(scaled, (round(bounds.centerx - scaled.get_width() / 2),
                              round(bounds.centery - scaled.get_height() / 2)))

    def _paint_house(self, surface, tile_x, tile_y, shop=False):
        """Paint the two plaza cottages as detailed timber buildings with steep tiled roofs."""
        x, y = tile_x * TILE_SIZE, tile_y * TILE_SIZE
        width = (7 if shop else 6) * TILE_SIZE
        eaves_y = y + 94
        wall_top = y + 81
        wall_bottom = y + 190

        # Rear chimney and shadow make the gabled silhouette stand out from the grass.
        chimney_x = x + width - 53 if shop else x + 31
        pygame.draw.rect(surface, OUTLINE, (chimney_x, y + 7, 25, 61))
        pygame.draw.rect(surface, (143, 116, 92), (chimney_x + 4, y + 12, 17, 52))
        for brick_y in range(y + 19, y + 61, 12):
            pygame.draw.line(surface, (94, 74, 61), (chimney_x + 4, brick_y),
                             (chimney_x + 21, brick_y), 2)
        for brick_x in (chimney_x + 10, chimney_x + 19):
            pygame.draw.line(surface, (94, 74, 61), (brick_x, y + 20), (brick_x, y + 31), 1)

        # Deep shadow, stone foundation, and timber framed front wall.
        pygame.draw.rect(surface, (54, 43, 38), (x + 10, wall_top + 10, width - 20, wall_bottom - wall_top))
        pygame.draw.rect(surface, (111, 82, 60), (x + 14, wall_top, width - 28, wall_bottom - wall_top))
        pygame.draw.rect(surface, (75, 62, 54), (x + 10, wall_bottom - 12, width - 20, 15))
        for stone_x in range(x + 12, x + width - 12, 18):
            pygame.draw.rect(surface, (135, 119, 103), (stone_x, wall_bottom - 10, 14, 6))
            pygame.draw.line(surface, (81, 72, 65), (stone_x + 7, wall_bottom - 10),
                             (stone_x + 7, wall_bottom - 4), 1)

        wall_color = (176, 128, 84) if shop else (150, 106, 70)
        pygame.draw.rect(surface, wall_color, (x + 20, wall_top, width - 40, wall_bottom - wall_top - 12))
        for plank_x in range(x + 23, x + width - 22, 12):
            pygame.draw.line(surface, (93, 63, 47), (plank_x, wall_top + 4),
                             (plank_x, wall_bottom - 14), 2)
            pygame.draw.line(surface, (195, 145, 92), (plank_x + 3, wall_top + 6),
                             (plank_x + 3, wall_bottom - 17), 1)
        pygame.draw.rect(surface, (70, 52, 42), (x + 15, wall_top - 4, width - 30, 10))
        pygame.draw.line(surface, (207, 166, 109), (x + 19, wall_top + 3),
                         (x + width - 19, wall_top + 3), 2)

        # The silhouettes differ: a centered cottage gable and a taller offset shop gable.
        if shop:
            apex_x = x + int(width * 0.62)
            roof_points = [(x - 7, eaves_y + 12), (apex_x, y - 3),
                           (x + width + 7, eaves_y + 12)]
        else:
            apex_x = x + width // 2
            roof_points = [(x - 7, eaves_y + 12), (apex_x, y - 4),
                           (x + width + 7, eaves_y + 12)]
        roof = ROOFS["shop" if shop else "cottage"]
        self._draw_shingles(surface, roof_points,
                            (x, y, width, eaves_y - y + 20), (roof[0], roof[1], roof[2]))
        pygame.draw.line(surface, roof[3], (x + 8, eaves_y + 10),
                         (x + width - 8, eaves_y + 10), 4)
        pygame.draw.line(surface, OUTLINE, (x + 8, eaves_y + 17),
                         (x + width - 8, eaves_y + 17), 3)

        # Gable timber and a small attic vent sit above the front wall.
        pygame.draw.line(surface, (77, 48, 39), (x + 25, eaves_y - 2), (apex_x, y + 17), 5)
        pygame.draw.line(surface, (77, 48, 39), (apex_x, y + 17), (x + width - 25, eaves_y - 2), 5)
        pygame.draw.rect(surface, (68, 49, 39), (apex_x - 9, y + 44, 18, 16))
        pygame.draw.rect(surface, (194, 152, 94), (apex_x - 6, y + 47, 12, 10), 2)

        # Windows, door, and threshold keep the two fronts readable at game scale.
        window_y = wall_top + 28
        self._draw_window(surface, pygame.Rect(x + 29, window_y, 27, 24), flower_box=shop)
        self._draw_window(surface, pygame.Rect(x + width - 56, window_y, 27, 24), flower_box=not shop)
        door_width = 34 if shop else 30
        door_x = x + (width - door_width) // 2
        door_y = wall_bottom - 51
        pygame.draw.rect(surface, (48, 38, 34), (door_x - 4, door_y - 5, door_width + 8, 55))
        pygame.draw.rect(surface, (91, 54, 38), (door_x, door_y, door_width, 50))
        pygame.draw.rect(surface, (161, 101, 59), (door_x + 4, door_y + 4, door_width - 8, 42))
        pygame.draw.line(surface, (101, 61, 42), (door_x + door_width // 2, door_y + 5),
                         (door_x + door_width // 2, door_y + 44), 2)
        pygame.draw.circle(surface, self.game.colors["gold"], (door_x + door_width - 7, door_y + 27), 2)
        pygame.draw.rect(surface, (191, 163, 111), (door_x - 6, wall_bottom - 5, door_width + 12, 7))

    def road_tiles(self):
        road = {(12, y) for y in range(9, 16)}
        road.update({(12, 9), (11, 9), (10, 9), (9, 8), (8, 8), (7, 8), (6, 8), (5, 8), (4, 8), (3, 8)})
        road.update({(13, 9), (14, 9), (15, 9), (16, 8), (17, 8), (18, 8), (19, 8), (20, 8), (21, 8)})
        road.update((x, 8) for x in range(0, 4))
        road.update((x, 8) for x in range(21, self.COLS))
        road.update((7, y) for y in range(1, 10))
        road.update((x, 1) for x in range(7, 13))
        road.update({(18, 9), (18, 10), (18, 11), (19, 11), (12, 7), (12, 8)})
        return road

    def ground_decals(self):
        """Walkable, purely visual ground details: flowers and pebbles off the road."""
        if getattr(self, "_decals", None) is None:
            road = self.road_tiles()
            blocked = self.walls | road | set(self.trees) | {self.FOUNTAIN, self.VILLAGER, self.LOGAN}
            decals = {}
            for y in range(1, self.ROWS - 1):
                for x in range(1, self.COLS - 1):
                    if (x, y) in blocked:
                        continue
                    roll = (x * 73 + y * 151 + x * y * 17) % 23
                    if roll in (0, 7):
                        decals[(x, y)] = "flower_patch" if (x + y) % 2 else "flower_patch_1"
                    elif roll == 13:
                        decals[(x, y)] = "pebbles"
            self._decals = decals
        return self._decals

    def _draw_border(self, surface, x, y, rect):
        surface.blit(sprite(f"grass_{(x * 7 + y * 13) % 16}", (TILE_SIZE, TILE_SIZE)), rect)
        if y in (0, self.ROWS - 1):
            surface.blit(sprite("fence", (TILE_SIZE, TILE_SIZE)), rect)
        else:
            surface.blit(sprite("fence_v", (TILE_SIZE, TILE_SIZE)), rect)

    def _draw_shadow(self, surface, center_x, bottom_y, width=26):
        surface.blit(sprite("shadow", (width, 10)), (round(center_x - width / 2), round(bottom_y - 7)))

    def draw(self, surface):
        # Reuse the common HUD and player state, then paint this map over the field.
        super().draw(surface)
        road = self.road_tiles()
        decals = self.ground_decals()
        for y in range(self.ROWS):
            for x in range(self.COLS):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if x in (0, self.COLS - 1) or y in (0, self.ROWS - 1):
                    self._draw_border(surface, x, y, rect)
                else:
                    surface.blit(sprite(f"grass_{(x * 7 + y * 13) % 16}", (TILE_SIZE, TILE_SIZE)), rect)
                    if (x, y) in road:
                        mask = ((1 if (x, y - 1) in road else 0)
                                | (2 if (x + 1, y) in road else 0)
                                | (4 if (x, y + 1) in road else 0)
                                | (8 if (x - 1, y) in road else 0)
                                | (16 if (x + 1, y - 1) in road else 0)
                                | (32 if (x + 1, y + 1) in road else 0)
                                | (64 if (x - 1, y + 1) in road else 0)
                                | (128 if (x - 1, y - 1) in road else 0))
                        surface.blit(sprite(f"trail_{mask}_{(x + y) % 3}", (TILE_SIZE, TILE_SIZE)), rect)
                    elif (x, y) in decals:
                        surface.blit(sprite(decals[(x, y)], (TILE_SIZE, TILE_SIZE)), rect)
        for tx, ty in sorted(self.trees, key=lambda p: p[1]):
            surface.blit(sprite(self.tree_kind((tx, ty)), (48, 64)), (tx * TILE_SIZE - 8, ty * TILE_SIZE - 32))
        self._draw_house(surface, 2, 2)
        self._draw_house(surface, 16, 2, shop=True)
        self._draw_chief_house(surface)
        self._draw_logan_stall(surface)
        fx, fy = self.FOUNTAIN
        self._draw_shadow(surface, fx * TILE_SIZE + TILE_SIZE / 2, (fy + 1) * TILE_SIZE, 40)
        surface.blit(sprite("star_fountain", (48, 64)), (fx * TILE_SIZE - 8, fy * TILE_SIZE - 32))
        for gate_id, (gx, gy) in self.FIELD_GATES.items():
            draw_x = min(max(gx, 1), self.COLS - 2)
            draw_y = 1 if gate_id == "village_north_shrine" else gy
            name = "gate_arch"
            surface.blit(sprite(name, (48, 64)), (draw_x * TILE_SIZE - 8, draw_y * TILE_SIZE - 32))
        for position, sprite_name in ((self.VILLAGER, "townsfolk"), (self.LOGAN, "shopkeeper")):
            self._draw_shadow(surface, position[0] * TILE_SIZE + TILE_SIZE / 2, (position[1] + 1) * TILE_SIZE)
            surface.blit(sprite(sprite_name, NPC_SIZE),
                         (position[0] * TILE_SIZE, position[1] * TILE_SIZE - 16))
        px = round(self.player["x"] * TILE_SIZE + TILE_SIZE / 2)
        py = round((self.player["y"] + 1) * TILE_SIZE)
        self._draw_shadow(surface, px, py)
        surface.blit(hero_sprite(self.weapon, self.armor, (TILE_SIZE, TILE_SIZE + 16),
                                 self.facing, int(self.walk_clock) % 2 if self.walk_clock else 0),
                     (px - TILE_SIZE // 2, py - TILE_SIZE - 16))
        for tx, ty in self.trees:
            if self.player["y"] < ty <= self.player["y"] + 1.2:
                surface.blit(sprite(self.tree_kind((tx, ty)), (48, 64)), (tx * TILE_SIZE - 8, ty * TILE_SIZE - 32))
        self._draw_dialogue(surface)

    def _draw_chief_house(self, surface):
        """Paint the chief's hall: steep red tile roof, half-timbered gable, striped awning and planters."""
        left, right = 8 * TILE_SIZE, 17 * TILE_SIZE
        cx = (left + right) // 2
        ground = 7 * TILE_SIZE  # The door tile (12, 7) sits just below the front step.
        eaves = ground - 78
        outline = OUTLINE
        roof_base, roof_line, roof_seam, roof_eave = ROOFS["chief"]

        # Chimney behind the left roof slope.
        pygame.draw.rect(surface, outline, (left + 42, eaves - 66, 26, 52))
        pygame.draw.rect(surface, (128, 98, 82), (left + 46, eaves - 62, 18, 46))
        for brick_y in range(eaves - 56, eaves - 18, 10):
            pygame.draw.line(surface, (88, 66, 56), (left + 46, brick_y), (left + 63, brick_y), 2)

        # Stone foundation and plastered ground floor framed by dark timber.
        pygame.draw.rect(surface, (70, 60, 54), (left + 10, ground - 22, right - left - 20, 22))
        for index, stone_x in enumerate(range(left + 12, right - 14, 17)):
            pygame.draw.rect(surface, (138, 124, 108) if index % 2 else (118, 106, 94),
                             (stone_x, ground - 19 + (index % 2) * 2, 14, 7))
            pygame.draw.rect(surface, (108, 97, 86), (stone_x + 6, ground - 9, 13, 6))
        wall = pygame.Rect(left + 16, eaves - 4, right - left - 32, ground - 22 - eaves + 4)
        pygame.draw.rect(surface, outline, wall.inflate(6, 2))
        pygame.draw.rect(surface, (214, 199, 168), wall)
        for beam_x in (wall.left + 4, wall.left + 64, wall.right - 70, wall.right - 10):
            pygame.draw.rect(surface, (92, 60, 43), (beam_x, wall.top, 6, wall.height))
        pygame.draw.rect(surface, (92, 60, 43), (wall.left, wall.top + 4, wall.width, 6))
        for wx in (wall.left + 20, wall.right - 54):
            self._draw_window(surface, pygame.Rect(wx, wall.top + 18, 28, 24), flower_box=True)

        # Wide main roof: a trapezoid of red-brown shingles with a bright eave line.
        ridge = eaves - 60
        roof = [(left - 6, eaves + 6), (left + 54, ridge), (right - 54, ridge), (right + 6, eaves + 6)]
        pygame.draw.polygon(surface, roof_base, roof)
        for row, ry in enumerate(range(ridge + 8, eaves + 4, 9)):
            t = (ry - ridge) / (eaves + 6 - ridge)
            x0, x1 = left + 54 - 60 * t, right - 54 + 60 * t
            pygame.draw.line(surface, roof_line, (round(x0), ry), (round(x1), ry), 2)
            for sx in range(round(x0) + (6 if row % 2 else 0), round(x1), 12):
                pygame.draw.line(surface, roof_seam, (sx, ry - 7), (sx, ry - 1), 1)
        pygame.draw.polygon(surface, outline, roof, 3)
        pygame.draw.line(surface, roof_eave, (left - 2, eaves + 4), (right + 2, eaves + 4), 3)

        # Front cross gable rising above the ridge, with a half-timbered plaster face.
        apex_y = ridge - 22
        gable = [(cx - 76, eaves + 14), (cx, apex_y), (cx + 76, eaves + 14)]
        face = [(cx - 50, eaves + 2), (cx, apex_y + 26), (cx + 50, eaves + 2)]
        self._draw_shingles(surface, gable, (cx - 76, apex_y, 152, eaves + 14 - apex_y),
                            (roof_base, roof_line, roof_seam))
        pygame.draw.polygon(surface, (226, 212, 182), face)
        pygame.draw.polygon(surface, (92, 60, 43), face, 4)
        pygame.draw.line(surface, (92, 60, 43), (cx, apex_y + 28), (cx, eaves + 2), 4)
        pygame.draw.line(surface, (92, 60, 43), (cx - 30, eaves + 2), (cx, apex_y + 44), 3)
        pygame.draw.line(surface, (92, 60, 43), (cx + 30, eaves + 2), (cx, apex_y + 44), 3)
        self._draw_window(surface, pygame.Rect(cx - 9, apex_y + 50, 18, 16))

        # Hanging vines spilling over the eaves.
        for vx in (left + 22, left + 40, right - 44, right - 26):
            for step in range(4):
                pygame.draw.circle(surface, (64, 108, 58) if step % 2 else (86, 136, 70),
                                   (vx + (step % 2) * 3, eaves + 8 + step * 5), 5)
            pygame.draw.circle(surface, (214, 96, 104), (vx + 2, eaves + 12), 2)

        # Dark recessed door under a white-and-grey striped awning.
        door = pygame.Rect(cx - 18, ground - 62, 36, 42)
        pygame.draw.rect(surface, outline, door.inflate(10, 6))
        pygame.draw.rect(surface, (62, 44, 40), door)
        pygame.draw.rect(surface, (98, 66, 48), door.inflate(-8, -6))
        pygame.draw.line(surface, (62, 44, 40), (cx, door.top + 3), (cx, door.bottom - 3), 2)
        pygame.draw.circle(surface, self.game.colors["gold"], (cx + 10, door.centery + 2), 2)
        awning_top, awning_bottom = door.top - 22, door.top - 4
        stripes = 8
        for index in range(stripes):
            tx0 = cx - 34 + index * 68 / stripes
            bx0 = cx - 42 + index * 84 / stripes
            poly = [(tx0, awning_top), (tx0 + 68 / stripes, awning_top),
                    (bx0 + 84 / stripes, awning_bottom), (bx0, awning_bottom)]
            pygame.draw.polygon(surface, (236, 232, 220) if index % 2 == 0 else (150, 154, 156), poly)
            pygame.draw.circle(surface, (236, 232, 220) if index % 2 == 0 else (150, 154, 156),
                               (round(bx0 + 42 / stripes), awning_bottom), round(42 / stripes))
        pygame.draw.line(surface, outline, (cx - 35, awning_top), (cx + 35, awning_top), 2)

        # Wooden steps, planters and a lantern flank the entrance.
        pygame.draw.rect(surface, (88, 58, 40), (cx - 26, ground - 20, 52, 10))
        pygame.draw.rect(surface, (128, 86, 54), (cx - 24, ground - 19, 48, 4))
        pygame.draw.rect(surface, (88, 58, 40), (cx - 30, ground - 10, 60, 10))
        pygame.draw.rect(surface, (128, 86, 54), (cx - 28, ground - 9, 56, 4))
        for px in (cx - 54, cx + 40):
            pygame.draw.rect(surface, (96, 62, 44), (px, ground - 18, 16, 16))
            for bx, by, color in ((3, -20, (70, 120, 62)), (11, -22, (88, 140, 72)), (7, -27, (70, 120, 62))):
                pygame.draw.circle(surface, color, (px + bx, ground + by), 7)
            for fx, fy, color in ((4, -24, (235, 194, 88)), (11, -28, (214, 96, 104)), (8, -18, (238, 230, 210))):
                pygame.draw.circle(surface, color, (px + fx, ground + fy), 2)
        lamp_x = cx + 62
        pygame.draw.line(surface, (46, 40, 38), (lamp_x, ground - 2), (lamp_x, ground - 46), 3)
        pygame.draw.rect(surface, (46, 40, 38), (lamp_x - 6, ground - 56, 12, 12))
        pygame.draw.rect(surface, (247, 205, 112), (lamp_x - 3, ground - 53, 6, 7))

    def _draw_logan_stall(self, surface):
        """Logan's open-air stall: crates of goods beside him and a striped canopy overhead."""
        t = TILE_SIZE
        left, right = 15 * t - 2, 18 * t + 2
        top = 10 * t - 26
        for post_x in (left + 4, right - 8):
            pygame.draw.rect(surface, (74, 50, 36), (post_x, top, 5, t + 30))
        for cx, cy in self.LOGAN_CRATES:
            box = pygame.Rect(cx * t + 2, cy * t + 8, t - 4, t - 8)
            pygame.draw.rect(surface, OUTLINE, box.inflate(2, 2))
            pygame.draw.rect(surface, (152, 102, 60), box)
            pygame.draw.line(surface, (104, 68, 44), box.topleft, box.bottomright, 2)
            pygame.draw.line(surface, (104, 68, 44), box.topright, box.bottomleft, 2)
        sword_x = 17 * t + 8
        pygame.draw.line(surface, (196, 204, 206), (sword_x, 10 * t - 8), (sword_x + 14, 10 * t + 10), 3)
        pygame.draw.line(surface, (150, 108, 60), (sword_x - 2, 10 * t + 4), (sword_x + 6, 10 * t - 2), 3)
        for index, color in enumerate(((206, 62, 62), (74, 120, 214), (206, 62, 62))):
            pygame.draw.rect(surface, (52, 46, 44), (15 * t + 6 + index * 8, 10 * t + 1, 7, 9))
            pygame.draw.rect(surface, color, (15 * t + 7 + index * 8, 10 * t + 4, 5, 5))
        stripes = 8
        width = (right - left) / stripes
        for index in range(stripes):
            x0 = left + index * width
            color = ROOFS["chief"][1] if index % 2 == 0 else (240, 228, 200)
            pygame.draw.polygon(surface, color, [(x0 + 4, top - 14), (x0 + width + 4, top - 14),
                                                 (x0 + width, top + 4), (x0, top + 4)])
            pygame.draw.circle(surface, color, (round(x0 + width / 2), top + 4), round(width / 2))
        pygame.draw.line(surface, OUTLINE, (left + 4, top - 14), (right + 4, top - 14), 2)

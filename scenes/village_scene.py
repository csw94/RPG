"""A safe village hub with a blacksmith, healer, and road to the wilds."""

import pygame
from scenes.field_scene import FieldScene
from settings import TILE_SIZE
from utils.pixel_art import hero_sprite, sprite


class VillageScene(FieldScene):
    COLS, ROWS = 25, 16
    VILLAGER = (7, 8)
    CHIEF = (12, 6)
    FOUNTAIN = (12, 8)
    GATE = (12, 15)
    QUEST_HOUSE_DOOR = (4, 7)
    BLACKSMITH_DOOR = (19, 7)

    def __init__(self, game, state=None):
        state = dict(state or {})
        state["world"] = "village"
        super().__init__(game, state)
        self.world = "village"
        self.encounter_rate = 0
        self.message = "스페이스바로 대장간 주인과 대화하고 남쪽 문으로 나가세요."
        self.chests = {}
        self.walls = {
            (x, y) for x in range(self.COLS) for y in range(self.ROWS)
            if (x in (0, self.COLS - 1) or y in (0, self.ROWS - 1)) and (x, y) != self.GATE
        }
        self.walls.update((x, y) for x in range(2, 8) for y in range(2, 8))
        self.walls.update((x, y) for x in range(16, 23) for y in range(2, 8))
        self.trees = {
            (2, 11), (3, 11), (4, 12), (6, 12), (7, 13), (3, 14),
            (21, 11), (22, 11), (20, 12), (22, 13), (19, 14),
            (9, 3), (10, 3), (13, 3), (14, 3), (9, 13), (15, 13),
        }
        self.solid_npcs = {self.VILLAGER, self.CHIEF}
        self.walls.update(self.trees)
        self.walls.add(self.FOUNTAIN)
        self.walls.difference_update({self.GATE, self.VILLAGER, self.CHIEF})
        self.position_recovered = self._restore_player_position((12, 13)) or self.position_recovered
        if self.position_recovered:
            self.message = "저장 위치를 마을 입구로 복구했습니다."

    def _interact(self):
        x, y = self.player["x"], self.player["y"]
        near = lambda target, radius=1.0: (x - target[0]) ** 2 + (y - target[1]) ** 2 <= radius ** 2
        cleared = sum(self.quest_flags[key] for key in ("shrine_wind", "shrine_earth", "shrine_fire"))

        if near(self.QUEST_HOUSE_DOOR):
            self.game.enter_world("village_house_1", (12, 12))
        elif near(self.BLACKSMITH_DOOR):
            self.game.enter_world("village_house_2", (12, 12))
        elif near(self.CHIEF):
            if not self.quest_flags["prologue_done"]:
                self.quest_flags["prologue_done"] = 1
                if "rusty_sword" not in self.owned_weapons:
                    self.owned_weapons.append("rusty_sword")
                self.weapon = "rusty_sword"
                self.potions = min(10, self.potions + 2)
                self.show_dialogue([
                    "\ud070\uc77c\uc77c\uc138! \ub9c8\uc744\uc744 \uc9c0\ud0a4\ub358 \ubcc4\ube5b \ubd84\uc218\uc758 \ube5b\uc774 \uc57d\ud574\uc9c0\uace0 \uc788\uc5b4.",
                    "\ub3d9\u00b7\uc11c\u00b7\ub0a8 \uc138 \uacf3\uc758 \uace0\ub300 \uc81c\ub2e8\uc5d0 \ub9c8\ubb3c\uc758 \uae30\uc6b4\uc774 \uc11c\ub838\ub2e4\ub294\uad70. \ubd09\uc778\uc11d\uc744 \uc815\ud654\ud574 \uc8fc\uac8c!",
                    "\ub179\uc2a8 \ucca0\uac80\uacfc \ud68c\ubcf5\uc57d(\uc18c) 2\uac1c\ub97c \ud68d\ub4dd\ud588\uc2b5\ub2c8\ub2e4.",
                ])
                self.game.save_game()
            elif cleared == 3:
                self.show_dialogue(["\uc138 \uac1c\uc758 \uc778\uc7a5\uc774 \ubaa8\ub450 \ubaa8\uc600\uad6c\ub098! \ub9c8\uc744 \uc911\uc559\uc758 \ubcc4\ube5b \ubd84\uc218\ub85c \uac00\uc11c \uc778\uc7a5\uc744 \ubc14\uce58\uac8c!"])
            elif cleared:
                self.show_dialogue(["\uc624\uc624, \uc81c\ub2e8\uc758 \ube5b\uc774 \ub3cc\uc544\uc624\uace0 \uc788\uad70! \ub098\uba38\uc9c0 \uc81c\ub2e8\ub3c4 \ubd80\ub514 \uc870\uc2ec\ud574\uc11c \ub2e4\ub140\uc624\uac8c."])
            else:
                self.show_dialogue(["\ub3d9\u00b7\uc11c\u00b7\ub0a8 \uc138 \uacf3\uc758 \uace0\ub300 \uc81c\ub2e8\uc744 \uc815\ud654\ud574 \uc8fc\uac8c. \ubcc4\ube5b \ubd84\uc218\uc758 \ube5b\uc774 \ub9c8\uc744\uc744 \uc9c0\ud0a4\uace0 \uc788\ub124."])
        elif near(self.FOUNTAIN, 1.2):
            if self.quest_flags["final_boss"]:
                self.show_dialogue([
                    "\ubcc4\ube5b \ubd84\uc218\uac00 \ub2e4\uc2dc \uc548\uc804\ud55c \ube5b\uc744 \ub0b4\ubfdc\ub294\ub2e4.",
                    "\uadf8\ub300\ub294 \uc655\uad6d\uc758 \uc815\uc2dd \uae30\uc0ac\ub85c \uc784\uba85\ub418\uc5c8\ub2e4. \ubaa8\ud5d8 \uc644\ub8cc!",
                ])
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
            self.show_dialogue(["\uad11\uc7a5 \uc8fc\ubbfc: \ubd81\ucabd \uc624\uc194\uae38\uc740 \ub3d9\ucabd \uc81c\ub2e8\uc73c\ub85c \uc774\uc5b4\uc838\uc694. \uc11c\ucabd\uacfc \ub0a8\ucabd\uc5d0\ub3c4 \uae38\uc774 \uc788\uc5b4\uc694."])
        elif near(self.GATE):
            self.game.enter_world("field", (12, 2))
        else:
            self.message = "\uc8fc\ubcc0\uc5d0\ub294 \uc0c1\ud638\uc791\uc6a9\ud560 \ub300\uc0c1\uc774 \uc5c6\uc2b5\ub2c8\ub2e4."

    @staticmethod
    def _draw_shingles(surface, points, bounds, colors):
        pygame.draw.polygon(surface, colors[0], points)
        pygame.draw.polygon(surface, (72, 35, 31), points, 3)
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
        pygame.draw.rect(surface, (48, 45, 40), rect.inflate(6, 6))
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
        """Paint the two plaza cottages as detailed timber buildings with steep tiled roofs."""
        x, y = tile_x * TILE_SIZE, tile_y * TILE_SIZE
        width = (7 if shop else 6) * TILE_SIZE
        eaves_y = y + 94
        wall_top = y + 81
        wall_bottom = y + 190

        # Rear chimney and shadow make the gabled silhouette stand out from the grass.
        chimney_x = x + width - 53 if shop else x + 31
        pygame.draw.rect(surface, (68, 58, 52), (chimney_x, y + 7, 25, 61))
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

        wall_color = (163, 119, 78) if shop else (132, 93, 63)
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
        self._draw_shingles(surface, roof_points,
                            (x, y, width, eaves_y - y + 20),
                            ((121, 48, 39), (175, 74, 51), (205, 104, 69)))
        pygame.draw.line(surface, (221, 122, 77), (x + 8, eaves_y + 10),
                         (x + width - 8, eaves_y + 10), 4)
        pygame.draw.line(surface, (72, 42, 36), (x + 8, eaves_y + 17),
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

        if shop:
            sign = pygame.Rect(x + width - 23, wall_top + 9, 32, 28)
            pygame.draw.rect(surface, (61, 42, 34), sign.inflate(5, 5))
            pygame.draw.rect(surface, (137, 77, 42), sign)
            pygame.draw.rect(surface, self.game.colors["gold"], sign, 2)
            pygame.draw.rect(surface, self.game.colors["gold"], (sign.centerx - 3, sign.centery - 3, 6, 6))

    def draw(self, surface):
        # Reuse the common HUD and player state, then paint this map over the field.
        super().draw(surface)
        road = {(12, y) for y in range(9, 16)}
        road.update({(12, 9), (11, 9), (10, 9), (9, 8), (8, 8), (7, 8), (6, 8), (5, 8), (4, 8), (3, 8)})
        road.update({(13, 9), (14, 9), (15, 9), (16, 8), (17, 8), (18, 8), (19, 8), (20, 8), (21, 8)})
        road.update({(18, 9), (18, 10), (18, 11), (19, 11)})
        for y in range(self.ROWS):
            for x in range(self.COLS):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if (x, y) in self.walls:
                    surface.blit(sprite("stone", (TILE_SIZE, TILE_SIZE)), rect)
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
                if (x, y) in self.trees:
                    surface.blit(sprite("tree", (48, 64)), (rect.x - 8, rect.y - 32))
        self._draw_house(surface, 2, 2)
        self._draw_house(surface, 16, 2, shop=True)
        fx, fy = self.FOUNTAIN
        surface.blit(sprite("star_fountain", (48, 64)), (fx * TILE_SIZE - 8, fy * TILE_SIZE - 32))
        gx, gy = self.GATE
        surface.blit(sprite("portal_town", (48, 64)), (gx * TILE_SIZE - 8, gy * TILE_SIZE - 32))
        for position, sprite_name in ((self.VILLAGER, "villager"), (self.CHIEF, "chief")):
            surface.blit(sprite(sprite_name, (TILE_SIZE, TILE_SIZE)),
                         (position[0] * TILE_SIZE, position[1] * TILE_SIZE))
        px = round(self.player["x"] * TILE_SIZE + TILE_SIZE / 2)
        py = round((self.player["y"] + 1) * TILE_SIZE)
        surface.blit(hero_sprite(self.weapon, self.armor, (TILE_SIZE, TILE_SIZE + 16),
                                 self.facing, int(self.walk_clock) % 2 if self.walk_clock else 0),
                     (px - TILE_SIZE // 2, py - TILE_SIZE - 16))
        for tx, ty in self.trees:
            if self.player["y"] < ty <= self.player["y"] + 1.2:
                surface.blit(sprite("tree", (48, 64)), (tx * TILE_SIZE - 8, ty * TILE_SIZE - 32))
        self._draw_dialogue(surface)

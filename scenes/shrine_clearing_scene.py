"""A small, quiet northern shrine clearing beside the village."""

import pygame

from scenes.field_scene import FieldScene
from settings import TILE_SIZE
from utils.pixel_art import hero_sprite, sprite, walk_frame


class ShrineClearingScene(FieldScene):
    COLS, ROWS = 32, 21
    ALTAR = (15, 7)
    SPAWN = (15, 17)

    def __init__(self, game, state=None):
        state = dict(state or {})
        state["world"] = "village_north_shrine"
        super().__init__(game, state)
        self.world = "village_north_shrine"
        self.encounter_rate = 0
        self.message = "북쪽 별빛 제단입니다. 남쪽 문으로 광장에 돌아갈 수 있습니다."
        self.altar_positions = {"shrine_wind": self.ALTAR}
        self.portal_position = (15, self.ROWS - 2)
        self.path = {(15, y) for y in range(9, self.ROWS - 1)}
        self.walls = {(x, y) for x in range(self.COLS) for y in range(self.ROWS)
                      if x in (0, self.COLS - 1) or y in (0, self.ROWS - 1)}
        ox, oy = 3, 2
        self.rocks = {(x + ox, y + oy) for x, y in ((7, 4), (8, 3), (16, 3), (17, 4), (6, 8), (18, 8),
                                                     (7, 11), (17, 11), (9, 13), (15, 13))}
        self.rocks |= {(4, 17), (27, 17), (8, 2), (23, 2)}
        self.trees = {(x + ox, y + oy) for x, y in ((3, 3), (4, 3), (3, 4), (20, 3), (21, 3), (21, 4),
                                                     (3, 10), (4, 10), (20, 10), (21, 10), (5, 13), (19, 13))}
        self.trees |= {(1, 2), (2, 4), (1, 9), (2, 12), (1, 16), (3, 18), (29, 2), (30, 5), (29, 9),
                       (30, 12), (29, 16), (27, 19), (11, 1), (19, 1), (6, 19), (24, 19)}
        self.trees -= self.path
        self.walls.update(self.rocks)
        self.walls.update(self.trees)
        self.walls.add(self.ALTAR)
        self.walls.difference_update(self.path | {self.portal_position})
        self._restore_player_position(self.SPAWN)

    def _interact(self):
        x, y = self.player["x"], self.player["y"]
        if (x - self.ALTAR[0]) ** 2 + (y - self.ALTAR[1]) ** 2 <= 1.5:
            self.show_dialogue(["마을 북쪽에 세워진 오래된 별빛 제단이다.",
                                "제단의 빛은 광장의 분수와 함께 마을을 지켜왔다."])
        elif (x - self.portal_position[0]) ** 2 + (y - self.portal_position[1]) ** 2 <= 1.5:
            from scenes.village_scene import VillageScene
            self.game.enter_world("village", VillageScene.SHRINE_RETURN)
        else:
            self.message = "제단으로 이어지는 작은 숲길입니다."

    def draw(self, surface):
        super().draw(surface)
        cam_x, cam_y = (round(v) for v in self._camera())
        t = TILE_SIZE
        view = surface.subsurface(pygame.Rect(0, 0, surface.get_width(), self.VIEW_HEIGHT))
        for x in range(self.COLS):
            for y in range(self.ROWS):
                if (x in (0, self.COLS - 1) or y in (0, self.ROWS - 1)) and (x, y) != self.portal_position:
                    position = (x * t - cam_x, y * t - cam_y)
                    view.blit(sprite(self.ground_tile(x, y), (t, t)), position)
                    fence = "fence" if y in (0, self.ROWS - 1) else "fence_v"
                    view.blit(sprite(fence, (t, t)), position)
        altar = self.altar_positions["shrine_wind"]
        # A two-step stone dais with four glowing pillars marks the old star altar.
        center = (altar[0] * t + t // 2 - cam_x, altar[1] * t + t // 2 - cam_y)
        for radius, color in ((62, (78, 74, 70)), (56, (132, 126, 114)), (40, (98, 94, 88)), (35, (162, 156, 140))):
            pygame.draw.ellipse(view, color, pygame.Rect(0, 0, radius * 2, radius * 1.3).move(
                center[0] - radius, center[1] - radius * 0.65 + 8))
        for dx, dy in ((-52, -22), (52, -22), (-52, 30), (52, 30)):
            px, py = center[0] + dx, center[1] + dy
            pygame.draw.rect(view, (64, 60, 58), (px - 6, py - 30, 12, 34))
            pygame.draw.rect(view, (148, 142, 128), (px - 4, py - 28, 8, 30))
            pygame.draw.circle(view, (126, 190, 235), (px, py - 34), 5)
            pygame.draw.circle(view, (222, 242, 255), (px, py - 34), 2)
        view.blit(sprite("star_fountain", (48, 64)), (altar[0] * t - 8 - cam_x, altar[1] * t - 32 - cam_y))
        view.blit(sprite("gate_arch", (48, 64)),
                  (self.portal_position[0] * t - 8 - cam_x, self.portal_position[1] * t - 32 - cam_y))
        if self.player["y"] <= altar[1] + 1:
            # Keep the hero visible when standing behind the dais.
            px = round(self.player["x"] * t + t / 2) - cam_x
            py = round((self.player["y"] + 1) * t) - cam_y
            view.blit(hero_sprite(self.weapon, self.armor, (t, t + 16), self.facing,
                                  walk_frame(self.walk_clock)), (px - t // 2, py - t - 16))
        self._draw_dialogue(surface)

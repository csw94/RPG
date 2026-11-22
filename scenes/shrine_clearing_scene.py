"""A small, quiet northern shrine clearing beside the village."""

import pygame

from scenes.field_scene import FieldScene
from settings import TILE_SIZE
from utils.pixel_art import sprite


class ShrineClearingScene(FieldScene):
    COLS, ROWS = 25, 16

    def __init__(self, game, state=None):
        state = dict(state or {})
        state["world"] = "village_north_shrine"
        super().__init__(game, state)
        self.world = "village_north_shrine"
        self.encounter_rate = 0
        self.message = "북쪽 별빛 제단입니다. 남쪽 문으로 광장에 돌아갈 수 있습니다."
        self.altar_positions = {"shrine_wind": (12, 5)}
        self.portal_position = (12, 14)
        self.path = {(12, y) for y in range(7, 15)}
        self.walls = {(x, y) for x in range(self.COLS) for y in range(self.ROWS)
                      if x in (0, self.COLS - 1) or y in (0, self.ROWS - 1)}
        self.rocks = {(7, 4), (8, 3), (16, 3), (17, 4), (6, 8), (18, 8),
                      (7, 11), (17, 11), (9, 13), (15, 13)}
        self.trees = {(3, 3), (4, 3), (3, 4), (20, 3), (21, 3), (21, 4),
                      (3, 10), (4, 10), (20, 10), (21, 10), (5, 13), (19, 13)}
        self.walls.update(self.rocks)
        self.walls.update(self.trees)
        self.walls.add((12, 5))
        self.walls.difference_update(self.path | {(12, 14)})
        self._restore_player_position((12, 12))

    def _interact(self):
        x, y = self.player["x"], self.player["y"]
        if (x - 12) ** 2 + (y - 5) ** 2 <= 1.5:
            self.show_dialogue(["마을 북쪽에 세워진 오래된 별빛 제단이다.",
                                "제단의 빛은 광장의 분수와 함께 마을을 지켜왔다."])
        elif (x - self.portal_position[0]) ** 2 + (y - self.portal_position[1]) ** 2 <= 1.5:
            self.game.enter_world("village", (12, 1))
        else:
            self.message = "제단으로 이어지는 작은 숲길입니다."

    def draw(self, surface):
        super().draw(surface)
        for x in range(self.COLS):
            for y in range(self.ROWS):
                if x in (0, self.COLS - 1) or y in (0, self.ROWS - 1):
                    surface.blit(sprite("stone", (TILE_SIZE, TILE_SIZE)), (x * TILE_SIZE, y * TILE_SIZE))
        altar = self.altar_positions["shrine_wind"]
        # A two-step stone dais with four glowing pillars marks the old star altar.
        center = (altar[0] * TILE_SIZE + TILE_SIZE // 2, altar[1] * TILE_SIZE + TILE_SIZE // 2)
        for radius, color in ((62, (78, 74, 70)), (56, (132, 126, 114)), (40, (98, 94, 88)), (35, (162, 156, 140))):
            pygame.draw.ellipse(surface, color, pygame.Rect(0, 0, radius * 2, radius * 1.3).move(
                center[0] - radius, center[1] - radius * 0.65 + 8))
        for dx, dy in ((-52, -22), (52, -22), (-52, 30), (52, 30)):
            px, py = center[0] + dx, center[1] + dy
            pygame.draw.rect(surface, (64, 60, 58), (px - 6, py - 30, 12, 34))
            pygame.draw.rect(surface, (148, 142, 128), (px - 4, py - 28, 8, 30))
            pygame.draw.circle(surface, (126, 190, 235), (px, py - 34), 5)
            pygame.draw.circle(surface, (222, 242, 255), (px, py - 34), 2)
        surface.blit(sprite("star_fountain", (48, 64)),
                     (altar[0] * TILE_SIZE - 8, altar[1] * TILE_SIZE - 32))
        surface.blit(sprite("portal_town", (48, 64)),
                     (self.portal_position[0] * TILE_SIZE - 8,
                      self.portal_position[1] * TILE_SIZE - 32))

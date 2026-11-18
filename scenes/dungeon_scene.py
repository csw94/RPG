"""A separate ruin map with stone corridors, treasure, and dangerous encounters."""

import pygame
from scenes.field_scene import FieldScene
from settings import TILE_SIZE
from utils.pixel_art import hero_sprite, sprite


class DungeonScene(FieldScene):
    EXIT = (2, 14)

    def __init__(self, game, state=None):
        state = dict(state or {})
        state["world"] = "dungeon"
        super().__init__(game, state)
        self.world = "dungeon"
        self.encounter_rate = 0.16
        self.enemy_pool = ("slime", "skeleton")
        self.message = "유적의 보물상자를 찾고 계단으로 필드에 돌아가세요."
        self.chests = {(5, 3): "gold", (20, 12): "potion"}
        self.walls = {
            (x, y) for x in range(self.COLS) for y in range(self.ROWS)
            if x in (0, self.COLS - 1) or y in (0, self.ROWS - 1)
        }
        self.walls.update((7, y) for y in range(2, 13) if y != 8)
        self.walls.update((x, 5) for x in range(7, 22) if x != 12)
        self.walls.update((15, y) for y in range(5, 14) if y != 10)
        self.walls.update((x, 10) for x in range(15, 22) if x != 18)
        self.position_recovered = self._restore_player_position((3, 14)) or self.position_recovered
        if self.position_recovered:
            self.message = "저장 위치를 던전 입구로 복구했습니다."

    def _interact(self):
        position = (self.player["x"], self.player["y"])
        if position == self.EXIT:
            self.game.enter_world("field", (22, 12))
        elif position in self.chests and position not in self.opened:
            self._open_chest(position)
        else:
            self.message = "낡은 석벽과 어둠이 길을 막고 있습니다."

    def draw(self, surface):
        super().draw(surface)
        for y in range(self.ROWS):
            for x in range(self.COLS):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if (x, y) in self.walls:
                    surface.blit(sprite("stone", (TILE_SIZE, TILE_SIZE)), rect)
                    if (x, y) in ((7, 4), (15, 8), (18, 5)):
                        surface.blit(sprite("torch", (TILE_SIZE, TILE_SIZE)), rect)
                else:
                    floor = f"dungeon_floor_{(x + y) % 2}"
                    surface.blit(sprite(floor, (TILE_SIZE, TILE_SIZE)), rect)
                if (x, y) in self.chests:
                    chest = "chest_open" if (x, y) in self.opened else "chest"
                    surface.blit(sprite(chest, (TILE_SIZE, TILE_SIZE)), rect)
                if (x, y) == self.EXIT:
                    surface.blit(sprite("stairs", (TILE_SIZE, TILE_SIZE)), rect)
        px, py = self.player["x"] * TILE_SIZE, self.player["y"] * TILE_SIZE
        pygame.draw.rect(surface, (31, 31, 36), (px + 7, py + 27, 18, 3))
        surface.blit(hero_sprite(self.weapon, self.armor, (TILE_SIZE, TILE_SIZE + 16)), (px, py - 16))

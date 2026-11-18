"""A safe village hub with a blacksmith, healer, and road to the wilds."""

import pygame
from scenes.field_scene import FieldScene
from settings import TILE_SIZE
from utils.pixel_art import hero_sprite, sprite


class VillageScene(FieldScene):
    SHOPKEEPER = (19, 7)
    VILLAGER = (7, 8)
    GATE = (12, 15)

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
        self.walls.update((x, y) for x in range(2, 8) for y in range(2, 6))
        self.walls.update((x, y) for x in range(16, 23) for y in range(2, 6))
        self.walls.discard((4, 5))
        self.walls.discard((19, 5))
        self.position_recovered = self._restore_player_position((12, 13)) or self.position_recovered
        if self.position_recovered:
            self.message = "저장 위치를 마을 입구로 복구했습니다."

    def _interact(self):
        position = (self.player["x"], self.player["y"])
        if position == self.SHOPKEEPER:
            self.message = "대장간 주인: 좋은 장비를 골라 보시오."
            self.game.open_shop()
        elif position == self.VILLAGER:
            self.message = "마을 주민: 북쪽 길을 따라가면 오래된 유적이 나옵니다."
        elif position == self.GATE:
            self.game.enter_world("field", (12, 2))
        else:
            self.message = "평화로운 왕국의 작은 마을입니다."

    def _draw_house(self, surface, tile_x, tile_y, shop=False):
        x, y = tile_x * TILE_SIZE, tile_y * TILE_SIZE
        width = (7 if shop else 6) * TILE_SIZE
        # Two rows of hand-laid red roof shingles.
        for row in range(2):
            for column in range(width // TILE_SIZE):
                surface.blit(sprite("roof", (TILE_SIZE, TILE_SIZE)),
                             (x + column * TILE_SIZE, y + row * TILE_SIZE))
        wall_top = y + 2 * TILE_SIZE
        pygame.draw.rect(surface, (173, 143, 99), (x, wall_top, width, 2 * TILE_SIZE))
        pygame.draw.rect(surface, (109, 83, 62), (x, wall_top, width, 3), 0)
        for column in range(1, width // TILE_SIZE):
            pygame.draw.rect(surface, (145, 115, 82), (x + column * TILE_SIZE, wall_top + 3, 2, 2 * TILE_SIZE - 3))
        door_x = x + (3 if shop else 2) * TILE_SIZE
        pygame.draw.rect(surface, (61, 39, 31), (door_x, wall_top + TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(surface, (137, 77, 42), (door_x + 4, wall_top + TILE_SIZE + 3, TILE_SIZE - 8, TILE_SIZE - 3))
        pygame.draw.rect(surface, self.game.colors["gold"], (door_x + 21, wall_top + TILE_SIZE + 16, 3, 3))
        for window_x in (x + 18, x + width - 42):
            pygame.draw.rect(surface, (54, 75, 75), (window_x, wall_top + 10, 24, 19))
            pygame.draw.rect(surface, self.game.colors["gold"], (window_x + 10, wall_top + 10, 3, 19))
            pygame.draw.rect(surface, self.game.colors["gold"], (window_x, wall_top + 18, 24, 3))
        if shop:
            sign = pygame.Rect(x + width - 22, wall_top + 8, 34, 23)
            pygame.draw.rect(surface, (61, 39, 31), sign.inflate(4, 4))
            pygame.draw.rect(surface, (137, 77, 42), sign)
            pygame.draw.rect(surface, self.game.colors["gold"], sign, 2)
            pygame.draw.rect(surface, self.game.colors["gold"], (sign.centerx - 2, sign.centery - 2, 5, 5))

    def draw(self, surface):
        # Reuse the common HUD and player state, then paint this map over the field.
        super().draw(surface)
        road = {(12, y) for y in range(5, 16)}
        road.update((x, 8) for x in range(2, 23))
        road.update((x, 7) for x in range(17, 22))
        for y in range(self.ROWS):
            for x in range(self.COLS):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if (x, y) in self.walls:
                    surface.blit(sprite("stone", (TILE_SIZE, TILE_SIZE)), rect)
                else:
                    tile = "dirt" if (x, y) in road else f"grass_{(x + y * 2) % 4}"
                    surface.blit(sprite(tile, (TILE_SIZE, TILE_SIZE)), rect)
        self._draw_house(surface, 2, 2)
        self._draw_house(surface, 16, 2, shop=True)
        surface.blit(sprite("well", (TILE_SIZE, TILE_SIZE)), (12 * TILE_SIZE, 8 * TILE_SIZE))
        surface.blit(sprite("stairs", (TILE_SIZE, TILE_SIZE)), (self.GATE[0] * TILE_SIZE, self.GATE[1] * TILE_SIZE))
        for position, sprite_name in ((self.SHOPKEEPER, "shopkeeper"), (self.VILLAGER, "villager")):
            surface.blit(sprite(sprite_name, (TILE_SIZE, TILE_SIZE)),
                         (position[0] * TILE_SIZE, position[1] * TILE_SIZE))
        px, py = self.player["x"] * TILE_SIZE, self.player["y"] * TILE_SIZE
        surface.blit(hero_sprite(self.weapon, self.armor, (TILE_SIZE, TILE_SIZE)), (px, py))

"""Top-down exploration field."""

import random
import pygame
from scenes.base_scene import BaseScene
from settings import TILE_SIZE
from utils.pixel_art import sprite


class FieldScene(BaseScene):
    COLS, ROWS = 25, 16

    def __init__(self, game, state=None):
        super().__init__(game)
        state = state or {}
        self.player = {"x": int(state.get("x", 2)), "y": int(state.get("y", 2))}
        self.hp = int(state.get("hp", 30))
        self.max_hp = int(state.get("max_hp", 30))
        self.mp = int(state.get("mp", 10))
        self.max_mp = int(state.get("max_mp", 10))
        self.level = int(state.get("level", 1))
        self.xp = int(state.get("xp", 0))
        self.potions = int(state.get("potions", 3))
        self.opened = {tuple(position) for position in state.get("opened", [])}
        self.message = "WASD 또는 방향키로 탐험하세요."
        self.move_cooldown = 0.0
        self.walls = {(x, y) for x in range(self.COLS) for y in range(self.ROWS)
                      if x in (0, self.COLS - 1) or y in (0, self.ROWS - 1)}
        self.walls.update({(8, y) for y in range(2, 11) if y != 6})
        self.walls.update({(x, 10) for x in range(8, 18) if x != 13})
        self.chests = {(5, 4): "포션", (18, 6): "골드", (20, 12): "포션"}

    def serialize(self):
        return {**self.player, "hp": self.hp, "max_hp": self.max_hp, "mp": self.mp,
                "max_mp": self.max_mp, "level": self.level, "xp": self.xp,
                "potions": self.potions, "opened": sorted(self.opened)}

    def _blocked(self, x, y):
        return (x, y) in self.walls

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.save_game()
                    self.game.change_scene("title")
                elif event.key == pygame.K_SPACE:
                    self._interact()
                elif event.key == pygame.K_F5:
                    self.game.save_game()
                    self.message = "진행 상황을 저장했습니다."
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(686, 536, 92, 38).collidepoint(event.pos):
                    self.game.save_game()
                    self.message = "진행 상황을 저장했습니다."

    def _interact(self):
        target = (self.player["x"], self.player["y"])
        if target in self.chests and target not in self.opened:
            self.opened.add(target)
            reward = self.chests[target]
            if reward == "포션":
                self.potions += 1
                self.message = "상자를 열어 포션을 얻었습니다!"
            else:
                self.xp += 20
                self.message = "상자에서 오래된 골드를 찾았습니다. 경험치 +20"
            self.game.save_game()
        else:
            self.message = "주변에는 아무것도 없습니다."

    def update(self, dt):
        self.move_cooldown = max(0.0, self.move_cooldown - dt)
        keys = pygame.key.get_pressed()
        dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        if (dx or dy) and self.move_cooldown <= 0:
            if dx and dy:
                dy = 0
            nx, ny = self.player["x"] + dx, self.player["y"] + dy
            if not self._blocked(nx, ny):
                self.player.update(x=nx, y=ny)
                self.move_cooldown = 0.12
                if (nx, ny) in self.chests and (nx, ny) not in self.opened:
                    self.message = "스페이스를 눌러 상자를 여세요."
                elif random.random() < 0.10:
                    self.game.start_battle()

    def draw(self, surface):
        surface.fill(self.game.colors["ink"])
        decorations = {
            (3, 6): "flower_yellow", (6, 8): "flower_red", (11, 3): "flower_yellow",
            (14, 7): "flower_red", (18, 3): "flower_yellow", (21, 8): "flower_red",
        }
        for y in range(self.ROWS):
            for x in range(self.COLS):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if (x, y) in self.walls:
                    surface.blit(sprite("stone", (TILE_SIZE, TILE_SIZE)), rect)
                    if (x, y) in ((8, 4), (8, 8)):
                        surface.blit(sprite("torch", (TILE_SIZE, TILE_SIZE)), rect)
                else:
                    tile = "dirt" if y == 6 and 8 <= x <= 18 else f"grass_{(x * 3 + y) % 4}"
                    surface.blit(sprite(tile, (TILE_SIZE, TILE_SIZE)), rect)
                    if (x, y) in decorations and (x, y) not in self.chests:
                        surface.blit(sprite(decorations[(x, y)], (16, 16)), (rect.x + 8, rect.y + 8))
                if (x, y) in self.chests:
                    chest = "chest_open" if (x, y) in self.opened else "chest"
                    surface.blit(sprite(chest, (TILE_SIZE, TILE_SIZE)), rect)
        px, py = self.player["x"] * TILE_SIZE, self.player["y"] * TILE_SIZE
        pygame.draw.rect(surface, (34, 62, 55), (px + 7, py + 27, 18, 3))
        surface.blit(sprite("player", (TILE_SIZE, TILE_SIZE)), (px, py))
        pygame.draw.rect(surface, self.game.colors["ink"], (0, 512, 800, 88))
        pygame.draw.rect(surface, self.game.colors["gold"], (0, 512, 800, 4))
        pygame.draw.rect(surface, self.game.colors["panel"], (8, 520, 784, 72))
        pygame.draw.rect(surface, self.game.colors["gold"], (8, 520, 784, 72), 2)
        self.text(surface, f"슬롯 {self.game.active_slot}  ·  Lv.{self.level}  HP {self.hp}/{self.max_hp}  MP {self.mp}/{self.max_mp}  포션 {self.potions}", (20, 526), 19)
        self.text(surface, self.message, (20, 558), 16, self.game.colors["muted"])
        self.button(surface, pygame.Rect(686, 536, 92, 38), "저장", False, 17)

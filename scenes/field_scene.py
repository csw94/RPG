"""Top-down exploration field."""

import random
import pygame
from scenes.base_scene import BaseScene
from settings import TILE_SIZE


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
                if pygame.Rect(690, 12, 98, 40).collidepoint(event.pos):
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
        for y in range(self.ROWS):
            for x in range(self.COLS):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                shade = self.game.colors["green"] if (x + y) % 2 else self.game.colors["dark_green"]
                pygame.draw.rect(surface, shade, rect)
                pygame.draw.rect(surface, (48, 103, 73), rect, 1)
                if (x, y) in self.walls:
                    pygame.draw.rect(surface, (97, 82, 70), rect.inflate(-2, -2), border_radius=4)
                    pygame.draw.rect(surface, (139, 118, 92), rect.inflate(-6, -8), 2, border_radius=3)
                elif (x, y) in self.chests and (x, y) not in self.opened:
                    pygame.draw.rect(surface, (132, 76, 42), rect.inflate(-8, -10), border_radius=4)
                    pygame.draw.rect(surface, self.game.colors["gold"], rect.inflate(-8, -10), 2, border_radius=4)
                    pygame.draw.rect(surface, self.game.colors["gold"], (rect.centerx - 3, rect.centery - 1, 6, 8))
        px, py = self.player["x"] * TILE_SIZE, self.player["y"] * TILE_SIZE
        pygame.draw.ellipse(surface, (28, 47, 58), (px + 5, py + 23, 23, 7))
        pygame.draw.rect(surface, (64, 121, 199), (px + 8, py + 12, 16, 15), border_radius=4)
        pygame.draw.circle(surface, (246, 205, 151), (px + 16, py + 9), 8)
        pygame.draw.rect(surface, (89, 58, 43), (px + 8, py + 2, 16, 5), border_radius=2)
        pygame.draw.rect(surface, self.game.colors["panel"], (0, 512, 800, 88))
        self.text(surface, f"Lv.{self.level}  HP {self.hp}/{self.max_hp}  MP {self.mp}/{self.max_mp}  포션 {self.potions}", (18, 520), 20)
        self.text(surface, self.message, (18, 553), 17, self.game.colors["muted"])
        self.button(surface, pygame.Rect(690, 520, 94, 40), "저장", False, 18)

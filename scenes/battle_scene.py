"""Turn-based battle scene."""

import pygame
from scenes.base_scene import BaseScene


class BattleScene(BaseScene):
    ACTIONS = ("공격", "스킬", "포션", "도망")

    def __init__(self, game):
        super().__init__(game)
        self.selected = 0
        self.enemy_hp = 24
        self.enemy_max_hp = 24
        self.message = "슬라임이 나타났다!"
        self.done = False
        self.result_timer = 0.0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % 4
                elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % 4
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._act()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self._buttons()):
                    if rect.collidepoint(event.pos):
                        self.selected = i
                        self._act()

    def _buttons(self):
        return [pygame.Rect(104 + (i % 2) * 310, 434 + (i // 2) * 58, 280, 46) for i in range(4)]

    def _act(self):
        if self.done:
            self.game.finish_battle()
            return
        field = self.game.field
        if self.selected == 0:
            self.enemy_hp -= 8 + field.level * 2
            self.message = "용사의 검이 빛났다!"
        elif self.selected == 1:
            if field.mp < 3:
                self.message = "MP가 부족합니다."
                return
            field.mp -= 3
            self.enemy_hp -= 15 + field.level * 2
            self.message = "파이어 볼트!"
        elif self.selected == 2:
            if field.potions <= 0:
                self.message = "포션이 없습니다."
                return
            field.potions -= 1
            field.hp = min(field.max_hp, field.hp + 18)
            self.message = "포션으로 HP를 회복했습니다."
        else:
            self.message = "무사히 전투에서 벗어났습니다."
            self.done = True
            self.result_timer = 0.7
            return
        if self.enemy_hp <= 0:
            field.xp += 25
            self.message = "슬라임을 물리쳤다! 경험치 +25"
            if field.xp >= field.level * 50:
                field.xp -= field.level * 50
                field.level += 1
                field.max_hp += 5
                field.max_mp += 2
                field.hp = field.max_hp
                field.mp = field.max_mp
                self.message = "레벨 업! 완전히 회복했습니다."
            self.done = True
            self.result_timer = 1.0
            self.game.save_game()
            return
        field.hp = max(0, field.hp - 5)
        if field.hp == 0:
            field.hp = max(1, field.max_hp // 2)
            self.message = "기절했지만 마을 입구에서 깨어났습니다."
            field.player.update(x=2, y=2)
            self.done = True
            self.result_timer = 1.1

    def update(self, dt):
        if self.done:
            self.result_timer -= dt
            if self.result_timer <= 0:
                self.game.finish_battle()

    def draw(self, surface):
        surface.fill((38, 54, 75))
        pygame.draw.rect(surface, (57, 83, 90), (0, 330, 800, 270))
        pygame.draw.ellipse(surface, (39, 50, 53), (160, 310, 150, 35))
        pygame.draw.ellipse(surface, (39, 50, 53), (490, 295, 165, 42))
        # Hero and slime are rendered from simple shapes, so no image assets are required.
        pygame.draw.rect(surface, (61, 121, 196), (205, 246, 65, 76), border_radius=12)
        pygame.draw.circle(surface, (246, 203, 151), (237, 222), 30)
        pygame.draw.rect(surface, (104, 65, 47), (208, 191, 59, 14), border_radius=5)
        pygame.draw.ellipse(surface, (114, 207, 130), (520, 215, 105, 88))
        pygame.draw.circle(surface, (255, 255, 255), (550, 246), 8)
        pygame.draw.circle(surface, (255, 255, 255), (592, 246), 8)
        pygame.draw.circle(surface, (34, 43, 51), (552, 247), 3)
        pygame.draw.circle(surface, (34, 43, 51), (594, 247), 3)
        pygame.draw.rect(surface, self.game.colors["panel"], (58, 28, 255, 86), border_radius=10)
        self.text(surface, "용사", (78, 42), 20)
        self._bar(surface, 78, 77, 215, self.game.field.hp, self.game.field.max_hp, self.game.colors["red"])
        pygame.draw.rect(surface, self.game.colors["panel"], (486, 28, 255, 86), border_radius=10)
        self.text(surface, "초록 슬라임", (506, 42), 20)
        self._bar(surface, 506, 77, 215, max(0, self.enemy_hp), self.enemy_max_hp, self.game.colors["green"])
        pygame.draw.rect(surface, self.game.colors["panel"], (0, 374, 800, 226))
        self.text(surface, self.message, (400, 401), 19, self.game.colors["gold"], True)
        for i, (label, rect) in enumerate(zip(self.ACTIONS, self._buttons())):
            if i == 2:
                label = f"포션 ({self.game.field.potions})"
            self.button(surface, rect, label, i == self.selected)
        self.text(surface, f"HP {self.game.field.hp}/{self.game.field.max_hp}   MP {self.game.field.mp}/{self.game.field.max_mp}",
                  (400, 570), 17, self.game.colors["muted"], True)

    @staticmethod
    def _bar(surface, x, y, width, value, maximum, color):
        pygame.draw.rect(surface, (55, 61, 73), (x, y, width, 14), border_radius=6)
        fill = int(width * max(0, value) / maximum) if maximum else 0
        if fill:
            pygame.draw.rect(surface, color, (x, y, fill, 14), border_radius=6)

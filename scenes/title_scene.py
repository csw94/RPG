"""Title menu."""

import pygame
from scenes.base_scene import BaseScene
from utils.pixel_art import sprite


class TitleScene(BaseScene):
    OPTIONS = ("새 게임", "이어하기", "종료")

    def __init__(self, game):
        super().__init__(game)
        self.selected = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(self.OPTIONS)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(self.OPTIONS)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._choose()
                elif event.key == pygame.K_ESCAPE:
                    self.game.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self._buttons()):
                    if rect.collidepoint(event.pos):
                        self.selected = i
                        self._choose()

    def _buttons(self):
        return [pygame.Rect(285, 330 + i * 62, 230, 48) for i in range(3)]

    def _choose(self):
        if self.selected == 0:
            self.game.new_game()
        elif self.selected == 1:
            if self.game.save_manager.has_save():
                self.game.load_game()
            else:
                self.game.notice = "저장된 모험이 없습니다. 새 게임을 시작해 주세요."
        else:
            self.game.running = False

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(self.game.colors["ink"])
        for x, y, radius in ((90, 100, 2), (680, 135, 3), (140, 460, 2), (720, 465, 2), (570, 90, 2)):
            pygame.draw.rect(surface, self.game.colors["cream"], (x - radius, y - radius, radius * 2 + 1, radius * 2 + 1))
        self.text(surface, "CHRONICLES", (400, 126), 48, self.game.colors["gold"], True)
        self.text(surface, "OF PIXEL", (400, 182), 34, self.game.colors["cream"], True)
        self.text(surface, "작은 용사의 첫 번째 모험", (400, 224), 20, self.game.colors["muted"], True)
        surface.blit(sprite("player", (64, 64)), (368, 244))
        for i, (label, rect) in enumerate(zip(self.OPTIONS, self._buttons())):
            self.button(surface, rect, label, i == self.selected)
        if self.game.notice:
            self.text(surface, self.game.notice, (400, 550), 17, self.game.colors["gold"], True)

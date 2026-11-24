"""A small yes/no dialog drawn over a parchment card; '아니오' is the safe default."""

import pygame

from scenes.base_scene import BaseScene
from utils import ui


class ConfirmScene(BaseScene):
    OPTIONS = ("예", "아니오")

    def __init__(self, game, back, title, lines, on_yes):
        super().__init__(game)
        self.back = back
        self.back_name = game.scene_name
        self.title = title
        self.lines = list(lines)
        self.on_yes = on_yes
        self.choice = 1  # 아니오

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d,
                                 pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                    self.choice = 1 - self.choice
                    self.sfx("cursor")
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._decide(self.choice == 0)
                elif event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    self._decide(False)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for index, rect in enumerate(self._buttons()):
                    if rect.collidepoint(event.pos):
                        self._decide(index == 0)

    def _decide(self, yes):
        self.sfx("confirm" if yes else "cursor")
        self.game.scene, self.game.scene_name = self.back, self.back_name
        if yes:
            self.on_yes()

    def update(self, dt):
        pass

    @staticmethod
    def _buttons():
        return [pygame.Rect(250 + i * 170, 380, 130, 42) for i in range(2)]

    def draw(self, surface):
        if hasattr(self.back, "draw"):
            self.back.draw(surface)
        veil = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        veil.fill((10, 8, 16, 150))
        surface.blit(veil, (0, 0))
        card = ui.frame(surface, pygame.Rect(150, 170, 500, 280), "parchment")
        title = self.game.font(24).render(self.title, True, ui.INK)
        surface.blit(title, title.get_rect(midtop=(card.centerx, card.y + 16)))
        for index, line in enumerate(self.lines):
            image = self.game.font(15).render(line, True, ui.INK_SOFT)
            surface.blit(image, image.get_rect(midtop=(card.centerx, card.y + 66 + index * 26)))
        for index, (label, rect) in enumerate(zip(self.OPTIONS, self._buttons())):
            self.button(surface, rect, label, index == self.choice, 19)

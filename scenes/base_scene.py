"""Base interface and shared drawing helpers for scenes."""

from abc import ABC, abstractmethod
import pygame


class BaseScene(ABC):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def handle_events(self, events):
        raise NotImplementedError

    @abstractmethod
    def update(self, dt):
        raise NotImplementedError

    @abstractmethod
    def draw(self, surface):
        raise NotImplementedError

    def text(self, surface, value, pos, size=24, color=None, center=False):
        image = self.game.font(size).render(str(value), True, color or self.game.colors["cream"])
        rect = image.get_rect(center=pos) if center else image.get_rect(topleft=pos)
        surface.blit(image, rect)
        return rect

    def button(self, surface, rect, label, selected=False, size=22):
        pygame.draw.rect(surface, self.game.colors["gold"] if selected else self.game.colors["panel"], rect, border_radius=8)
        pygame.draw.rect(surface, self.game.colors["cream"], rect, 2, border_radius=8)
        self.text(surface, label, rect.center, size, self.game.colors["ink"] if selected else self.game.colors["cream"], True)

"""Base interface and shared drawing helpers for scenes."""

from abc import ABC, abstractmethod
import pygame

from utils import ui


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

    def sfx(self, name):
        """Play a sound effect if the game has audio (tests and headless runs may not)."""
        audio = getattr(self.game, "audio", None)
        if audio:
            audio.play(name)

    def button(self, surface, rect, label, selected=False, size=22):
        ui.button(surface, self.game.font, rect, label, selected, size)

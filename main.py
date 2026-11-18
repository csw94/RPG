"""Chronicles of Pixel entry point."""

import pygame

from db.save_manager import SaveManager
from scenes.battle_scene import BattleScene
from scenes.field_scene import FieldScene
from scenes.title_scene import TitleScene
from settings import COLORS, FPS, HEIGHT, TITLE, WIDTH
from utils.resource import resource_path


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.colors = COLORS
        self.running = True
        self.save_manager = SaveManager()
        self.notice = ""
        self.field = None
        self.active_slot = None
        self.scene_name = "title"
        self.scene = TitleScene(self)
        self._fonts = {}

    def font(self, size):
        if size not in self._fonts:
            font_path = resource_path("assets/fonts/game_font.ttf")
            try:
                self._fonts[size] = pygame.font.Font(font_path, size)
            except (FileNotFoundError, OSError):
                # Keep the game runnable if a distributor removes the optional font asset.
                self._fonts[size] = pygame.font.Font(None, size)
        return self._fonts[size]

    def change_scene(self, name):
        self.scene_name = name
        self.scene = TitleScene(self) if name == "title" else FieldScene(self)

    def new_game(self, slot):
        self.notice = ""
        self.active_slot = slot
        self.field = FieldScene(self)
        self.scene_name, self.scene = "field", self.field
        self.save_game()

    def load_game(self, slot):
        data = self.save_manager.load(slot)
        if data:
            self.notice = ""
            self.active_slot = slot
            self.field = FieldScene(self, data)
            self.scene_name, self.scene = "field", self.field

    def save_game(self):
        if self.field:
            self.save_manager.save(self.field.serialize(), self.active_slot)

    def start_battle(self):
        self.scene_name = "battle"
        self.scene = BattleScene(self)

    def finish_battle(self):
        self.save_game()
        self.scene_name, self.scene = "field", self.field

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            self.scene.handle_events(events)
            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    Game().run()

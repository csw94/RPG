"""Chronicles of Pixel entry point."""

import pygame

from db.save_manager import SaveManager
from gameplay.world_data import FIELD_ROUTES, MAP_GRAPH
from scenes.battle_scene import BattleScene
from scenes.dungeon_scene import DungeonScene
from scenes.epilogue_scene import EpilogueScene
from scenes.field_scene import FieldScene
from scenes.house_scene import HouseInteriorScene
from scenes.shop_scene import ShopScene
from scenes.shrine_clearing_scene import ShrineClearingScene
from scenes.status_scene import StatusScene
from scenes.title_scene import TitleScene
from scenes.village_scene import VillageScene
from settings import COLORS, FPS, HEIGHT, TITLE, WIDTH
from utils.resource import resource_path


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        try:
            pygame.display.set_icon(pygame.image.load(resource_path("assets/icon.png")))
        except (FileNotFoundError, pygame.error):
            pass  # The window still opens with the default icon.
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
        state = {
            "world": "village", "x": 15, "y": 15,
            "level": 1, "hp": 100, "max_hp": 100, "atk": 15, "defense": 5,
            "mp": 10, "max_mp": 10, "gold": 0, "potions": 0, "high_potions": 0,
            "weapon": "rusty_sword", "armor": "traveler_clothes",
            "owned_weapons": ["rusty_sword"], "owned_armors": ["traveler_clothes"],
            "quest_flags": {
                "prologue_done": 0, "shrine_wind": 0, "shrine_earth": 0,
                "shrine_fire": 0, "star_sword_awakened": 0, "final_boss": 0,
            },
        }
        self.field = self._create_world(state)
        self.scene_name, self.scene = self.field.world, self.field
        self.save_game()

    def load_game(self, slot):
        data = self.save_manager.load(slot)
        if data:
            self.notice = ""
            self.active_slot = slot
            self.field = self._create_world(data)
            self.scene_name, self.scene = self.field.world, self.field

    def _create_world(self, state):
        state = dict(state)
        if state.get("world") == "field":
            # Legacy saves used a single combined field; resume them at the eastern route's entrance.
            x, y = FIELD_ROUTES["field_east"]["village_spawn"]
            state.update(world="field_east", x=float(x), y=float(y))
        if state.get("world") in ("village_chief_house", "village_house_1", "village_house_2"):
            return HouseInteriorScene(self, state)
        if state.get("world") == "village_north_shrine":
            return ShrineClearingScene(self, state)
        if DungeonScene.is_dungeon_map(state.get("world", state.get("map_id", ""))):
            return DungeonScene(self, state)
        worlds = {"field": FieldScene, "village": VillageScene, "dungeon": DungeonScene}
        world_type = worlds.get(state.get("world", "field"), FieldScene)
        return world_type(self, state)

    def enter_world(self, world, position):
        current_map = "village_square" if self.field.world == "village" else self.field.world
        target_map = "village_square" if world == "village" else world
        if target_map not in MAP_GRAPH.get(current_map, ()):
            raise ValueError(f"map {current_map!r} has no exit to {target_map!r}")
        state = self.field.serialize()
        state.update(world=world, map_id=world, x=position[0], y=position[1])
        self.field = self._create_world(state)
        self.scene_name, self.scene = self.field.world, self.field
        self.save_game()

    def open_shop(self):
        self.scene_name = "shop"
        self.scene = ShopScene(self)

    def open_status(self):
        self.scene_name = "status"
        self.scene = StatusScene(self)

    def save_game(self):
        if self.field:
            self.save_manager.save(self.field.serialize(), self.active_slot)

    def start_battle(self, enemy_type="slime"):
        self.scene_name = "battle"
        self.scene = BattleScene(self, enemy_type)

    def start_epilogue(self):
        self.scene_name = "epilogue"
        self.scene = EpilogueScene(self)

    def finish_battle(self):
        self.save_game()
        scene_types = {"field": FieldScene, "village": VillageScene, "dungeon": DungeonScene}
        expected = scene_types.get(self.field.world, FieldScene)
        if not isinstance(self.field, expected):
            self.field = self._create_world(self.field.serialize())
        self.scene_name, self.scene = self.field.world, self.field
        if self.field.pending_epilogue:
            self.field.pending_epilogue = False
            self.start_epilogue()
        elif self.field.pending_dialogue:
            lines = self.field.pending_dialogue
            self.field.pending_dialogue = None
            self.field.show_dialogue(lines)

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

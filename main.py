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
from utils import display, user_settings
from utils.audio import RATE, Audio, music_for
from utils.resource import resource_path

AUTOSAVE_SECONDS = 60  # quiet save while exploring


class Game:
    def __init__(self):
        pygame.mixer.pre_init(RATE, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption(TITLE)
        try:
            pygame.display.set_icon(pygame.image.load(resource_path("assets/icon.png")))
        except (FileNotFoundError, pygame.error):
            pass  # The window still opens with the default icon.
        # Scenes draw on an 800x600 canvas; present() scales it to the window size.
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.settings = user_settings.load()
        try:
            self.desktop = pygame.display.get_desktop_sizes()[0]
        except (pygame.error, IndexError):
            self.desktop = (WIDTH, HEIGHT)
        self.display_modes = display.available_modes(self.desktop)
        self.window = None
        self.view = pygame.Rect(0, 0, WIDTH, HEIGHT)
        self.apply_display(self.settings["display"])
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
        self.audio = Audio()
        self.autosave_clock = 0.0
        self.audio.set_volumes(self.settings["music"], self.settings["sfx"])

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

    def new_game(self, slot, difficulty="normal"):
        self.notice = ""
        self.active_slot = slot
        state = {
            "world": "village", "x": 15, "y": 15, "difficulty": difficulty,
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

    def open_shop(self, shop="logan"):
        self.scene_name = "shop"
        self.scene = ShopScene(self, shop)

    def apply_display(self, mode):
        """Resize the window (or go fullscreen); unknown or oversized modes fall back to 1x."""
        if mode not in self.display_modes:
            mode = "1x"
        self.settings["display"] = mode
        flags = pygame.FULLSCREEN if mode == "fullscreen" else 0
        try:
            self.window = pygame.display.set_mode(display.window_size(mode, self.desktop), flags)
        except pygame.error:
            self.settings["display"] = "1x"
            self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.view = display.view_rect(self.window.get_size())

    def save_settings(self):
        user_settings.save(self.settings)

    def open_settings(self):
        from scenes.settings_scene import SettingsScene
        self.audio.play("cursor")
        self.scene, self.scene_name = SettingsScene(self, self.scene), "settings"

    def present(self):
        if self.view.size == (WIDTH, HEIGHT) and self.window.get_size() == (WIDTH, HEIGHT):
            self.window.blit(self.canvas, (0, 0))
        else:
            self.window.fill((0, 0, 0))
            self.window.blit(pygame.transform.scale(self.canvas, self.view.size), self.view.topleft)
        pygame.display.flip()

    def tick_autosave(self, dt):
        """Save quietly every AUTOSAVE_SECONDS while walking around (not mid-dialogue)."""
        field = getattr(self, "field", None)
        if field is None or self.scene is not field or self.scene_name == "title":
            return
        self.autosave_clock += dt
        if self.autosave_clock >= AUTOSAVE_SECONDS and not field.dialogue_lines:
            self.autosave_clock = 0.0
            self.save_game()
            field.autosave_flash = 2.0

    def shutdown(self):
        """Closing the window keeps the adventure: save first if one is open."""
        if getattr(self, "field", None) is not None and self.scene_name != "title" and self.active_slot:
            self.save_game()
        self.running = False

    def count_play_time(self, dt):
        """Play time grows while an adventure is open (not on the title screen)."""
        if getattr(self, "field", None) is not None and self.scene_name != "title":
            self.field.play_time += dt

    def open_status(self):
        self.audio.play("cursor")
        self.scene_name = "status"
        self.scene = StatusScene(self)

    def save_game(self):
        if self.field:
            from gameplay.achievements import check_achievements
            if check_achievements(self.field):
                self.audio.play("level_up")
            self.save_manager.save(self.field.serialize(), self.active_slot)

    def start_battle(self, enemy_type="slime"):
        self.scene_name = "battle"
        self.scene = BattleScene(self, enemy_type)

    def start_new_game_plus(self):
        """Begin the next cycle in the same slot, carrying the hero over."""
        from gameplay.new_game_plus import new_game_plus_state

        self.field = self._create_world(new_game_plus_state(self.field.serialize()))
        self.scene_name, self.scene = self.field.world, self.field
        self.field.message = f"{self.field.cycle}회차 모험이 시작되었습니다. 촌장님께 인사드리고 떠나세요."
        self.save_game()

    def retry_battle(self, snapshot, enemy_type):
        """After a defeat: restore the pre-battle state and fight the same enemy again."""
        self.field = self._create_world(snapshot)
        self.save_game()
        self.start_battle(enemy_type)

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
            events = display.map_events(pygame.event.get(), self.view)
            for event in events:
                if event.type == pygame.QUIT:
                    self.shutdown()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                    self.audio.toggle_mute()
            self.scene.handle_events(events)
            self.scene.update(dt)
            self.count_play_time(dt)
            self.tick_autosave(dt)
            enemy = getattr(self.scene, "enemy", None) if self.scene_name == "battle" else None
            track = getattr(self.scene, "music_track", None)
            self.audio.update(track or music_for(self.scene_name, enemy["id"] if enemy else None))
            self.scene.draw(self.canvas)
            self.present()
        pygame.quit()


if __name__ == "__main__":
    Game().run()

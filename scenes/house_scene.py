"""Interiors for the herb cottage and Logan's blacksmith shop."""

import pygame

from scenes.field_scene import FieldScene
from settings import HEIGHT, TILE_SIZE, WIDTH
from utils.pixel_art import hero_sprite, sprite


class HouseInteriorScene(FieldScene):
    COLS, ROWS = 25, 16
    DOOR = (12, 14)

    def __init__(self, game, state=None):
        state = dict(state or {})
        self.house_id = state.get("world", "village_house_1")
        if self.house_id not in ("village_chief_house", "village_house_1", "village_house_2"):
            self.house_id = "village_house_1"
        state["world"] = self.house_id
        super().__init__(game, state)
        self.world = self.house_id
        self.encounter_rate = 0
        self.player.update(x=float(state.get("x", 12)), y=float(state.get("y", 12)))
        self.message = "SPACE로 주민과 대화하거나 문으로 나가세요."
        if self.house_id == "village_house_1":
            self.npcs = ((7, 6), (17, 6))
        else:
            self.npcs = ((12, 6),)
        self.solid_npcs = set(self.npcs)
        self.walls = {
            (x, y) for x in range(self.COLS) for y in range(self.ROWS)
            if x in (0, self.COLS - 1) or y in (0, self.ROWS - 1)
        }
        self._build_furniture_collision()
        self._restore_player_position((12, 12))

    def _build_furniture_collision(self):
        if self.house_id == "village_house_1":
            self.walls.update({(x, y) for x in range(2, 6) for y in range(2, 4)})
            self.walls.update({(x, y) for x in range(19, 23) for y in range(2, 4)})
            self.walls.update({(x, 8) for x in range(3, 8)})
            self.walls.update({(12, y) for y in range(2, 7) if y != 5})
        elif self.house_id == "village_house_2":
            self.walls.update({(x, y) for x in range(2, 6) for y in range(2, 4)})
            self.walls.update({(x, 7) for x in range(4, 9)})
            self.walls.update({(x, y) for x in range(19, 23) for y in range(2, 4)})
            self.walls.update({(x, y) for x in range(17, 22) for y in range(9, 11)})
        self.walls.difference_update({(12, 13), *self.npcs})

    def serialize(self):
        state = super().serialize()
        state["world"] = self.house_id
        return state

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.save_game()
                    self.game.enter_world("village", self._outside_door())
                elif event.key == pygame.K_SPACE:
                    if self.dialogue_lines:
                        self._advance_dialogue()
                    else:
                        self._interact()
                elif event.key == pygame.K_F5:
                    self.game.save_game()
                    self.message = "진행 상황을 저장했습니다."
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(686, 536, 92, 38).collidepoint(event.pos):
                    self.game.save_game()
                    self.message = "진행 상황을 저장했습니다."

    def _outside_door(self):
        if self.house_id == "village_chief_house":
            return (12, 7)
        return (5, 8) if self.house_id == "village_house_1" else (19, 8)

    def _interact(self):
        x, y = self.player["x"], self.player["y"]
        if (x - self.DOOR[0]) ** 2 + (y - self.DOOR[1]) ** 2 <= 1.4:
            self.game.save_game()
            self.game.enter_world("village", self._outside_door())
            return
        if self.house_id == "village_house_1":
            if (x - self.npcs[0][0]) ** 2 + (y - self.npcs[0][1]) ** 2 <= 1.5:
                self._offer_sidequest("sq_moon_herb")
            elif (x - self.npcs[1][0]) ** 2 + (y - self.npcs[1][1]) ** 2 <= 1.5:
                self._offer_sidequest("sq_old_sword")
            else:
                self.message = "침대와 약초 서랍이 놓인 작은 오두막입니다."
        elif self.house_id == "village_chief_house" and (x - self.npcs[0][0]) ** 2 + (y - self.npcs[0][1]) ** 2 <= 1.5:
            self._interact_chief()
        elif (x - self.npcs[0][0]) ** 2 + (y - self.npcs[0][1]) ** 2 <= 1.5:
            self.show_dialogue(["어서 오세요. 대장장이 로건입니다.",
                                "장비를 살펴보고 필요한 물건을 골라보세요."], action="open_shop")
        else:
            self.message = "화덕과 모루가 놓인 대장간입니다."

    def _interact_chief(self):
        cleared = sum(self.quest_flags[key] for key in ("shrine_wind", "shrine_earth", "shrine_fire"))
        if not self.quest_flags["prologue_done"]:
            self.quest_flags["prologue_done"] = 1
            if "rusty_sword" not in self.owned_weapons:
                self.owned_weapons.append("rusty_sword")
            self.weapon = "rusty_sword"
            self.potions = min(10, self.potions + 2)
            self.show_dialogue([
                "별빛 분수의 결계가 약해지고 마을 외곽에 마물들이 나타났네.",
                "동·서·남 세 제단의 봉인석을 정화해 마을을 지켜주게.",
                "녹슨 철검과 회복약 두 개를 주겠네. 출발 전에 준비하게.",
            ])
            self.game.save_game()
        elif cleared == 3:
            self.show_dialogue(["세 개의 인장을 모두 모았구나. 광장의 별빛 분수에 바치게."])
        elif cleared:
            self.show_dialogue(["정화한 제단의 빛이 돌아오고 있네. 나머지 길도 조심해서 다녀오게."])
        else:
            self.show_dialogue(["세 제단을 원하는 순서로 공략해도 좋네. 마을 사람들의 부탁도 살펴보게."])

    def _advance_dialogue(self):
        if self.dialogue_lines:
            next_index = self.dialogue_index + 1
            if next_index >= len(self.dialogue_lines) and self.dialogue_action == "open_shop":
                self.dialogue_lines = []
                self.dialogue_index = 0
                self.dialogue_action = None
                self.game.open_shop()
                return
        super()._advance_dialogue()

    def update(self, dt):
        super().update(dt)

    @staticmethod
    def _wood_floor(surface):
        for y in range(16):
            for x in range(25):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                color = (105, 73, 53) if (x + y) % 2 else (119, 83, 58)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.line(surface, (84, 58, 45), (rect.x + 2, rect.y + 9),
                                 (rect.right - 2, rect.y + 9), 1)
                pygame.draw.line(surface, (139, 100, 67), (rect.x + 4, rect.y + 25),
                                 (rect.right - 3, rect.y + 25), 1)
        pygame.draw.rect(surface, (48, 37, 34), (0, 0, WIDTH, 32))
        pygame.draw.rect(surface, (76, 59, 48), (0, 32, WIDTH, 5))
        pygame.draw.rect(surface, (48, 37, 34), (0, 0, 32, 512))
        pygame.draw.rect(surface, (48, 37, 34), (WIDTH - 32, 0, 32, 512))
        pygame.draw.rect(surface, (119, 83, 58), (11 * TILE_SIZE, 13 * TILE_SIZE, 3 * TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(surface, (81, 54, 43), (11 * TILE_SIZE, 14 * TILE_SIZE, 3 * TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(surface, (175, 134, 86), (12 * TILE_SIZE + 5, 13 * TILE_SIZE, TILE_SIZE - 10, TILE_SIZE))

    def _draw_quest_cottage(self, surface):
        # Bed alcoves, a shared rug, herb shelves, and a work table.
        pygame.draw.rect(surface, (63, 45, 36), (12 * TILE_SIZE - 5, 2 * TILE_SIZE, 10, 3 * TILE_SIZE))
        pygame.draw.rect(surface, (63, 45, 36), (12 * TILE_SIZE - 5, 6 * TILE_SIZE, 10, TILE_SIZE))
        pygame.draw.rect(surface, (79, 54, 40), (7 * TILE_SIZE, 2 * TILE_SIZE, 4 * TILE_SIZE, 3))
        pygame.draw.rect(surface, (79, 54, 40), (7 * TILE_SIZE, 3 * TILE_SIZE, 4 * TILE_SIZE, 3))
        for index, color in enumerate(((177, 75, 54), (201, 162, 78), (82, 129, 104), (97, 125, 157), (182, 119, 65))):
            pygame.draw.rect(surface, color, (7 * TILE_SIZE + 5 + index * 20, 2 * TILE_SIZE - 8, 12, 8))
        for x in (2, 19):
            pygame.draw.rect(surface, (54, 42, 37), (x * TILE_SIZE - 3, 2 * TILE_SIZE - 3, 4 * TILE_SIZE + 6, 3 * TILE_SIZE + 6))
            pygame.draw.rect(surface, (133, 89, 60), (x * TILE_SIZE, 2 * TILE_SIZE, 4 * TILE_SIZE, 3 * TILE_SIZE))
            pygame.draw.rect(surface, (190, 190, 166), (x * TILE_SIZE + 5, 2 * TILE_SIZE + 5, 4 * TILE_SIZE - 10, 24))
            pygame.draw.rect(surface, (103, 139, 156), (x * TILE_SIZE + 5, 2 * TILE_SIZE + 30, 4 * TILE_SIZE - 10, 57))
            pygame.draw.rect(surface, (76, 52, 43), (x * TILE_SIZE + 5, 2 * TILE_SIZE + 30, 4 * TILE_SIZE - 10, 57), 3)
        pygame.draw.rect(surface, (133, 53, 43), (8 * TILE_SIZE, 7 * TILE_SIZE, 8 * TILE_SIZE, 3 * TILE_SIZE))
        pygame.draw.rect(surface, (206, 157, 91), (8 * TILE_SIZE, 7 * TILE_SIZE, 8 * TILE_SIZE, 3 * TILE_SIZE), 3)
        for index in range(6):
            pygame.draw.rect(surface, (81, 54, 42), (2 * TILE_SIZE, 6 * TILE_SIZE + index * 3, 4 * TILE_SIZE, 2))
            pygame.draw.rect(surface, (117, 147, 74), (2 * TILE_SIZE + 8 + index * 16, 6 * TILE_SIZE - 5, 7, 8))
        for index, color in enumerate(((181, 113, 68), (206, 182, 129), (113, 143, 105))):
            pygame.draw.rect(surface, (68, 49, 39), (6 * TILE_SIZE + index * 15, 6 * TILE_SIZE, 12, 18))
            pygame.draw.rect(surface, color, (6 * TILE_SIZE + 2 + index * 15, 6 * TILE_SIZE + 4, 8, 11))
        pygame.draw.rect(surface, (70, 46, 36), (9 * TILE_SIZE, 5 * TILE_SIZE, 5 * TILE_SIZE, 2 * TILE_SIZE))
        pygame.draw.rect(surface, (157, 111, 67), (9 * TILE_SIZE + 4, 5 * TILE_SIZE + 4, 5 * TILE_SIZE - 8, 2 * TILE_SIZE - 8))
        pygame.draw.rect(surface, (75, 48, 38), (11 * TILE_SIZE, 12 * TILE_SIZE, 3 * TILE_SIZE, TILE_SIZE))

    def _draw_blacksmith(self, surface):
        # Hot forge, anvil, weapon rack, counter, and a small shop rug.
        pygame.draw.rect(surface, (61, 43, 37), (2 * TILE_SIZE, 2 * TILE_SIZE, 5 * TILE_SIZE, 5 * TILE_SIZE))
        pygame.draw.rect(surface, (109, 75, 56), (2 * TILE_SIZE + 6, 2 * TILE_SIZE + 6, 5 * TILE_SIZE - 12, 5 * TILE_SIZE - 12))
        pygame.draw.rect(surface, (39, 33, 32), (3 * TILE_SIZE, 3 * TILE_SIZE, 3 * TILE_SIZE, 3 * TILE_SIZE))
        pygame.draw.rect(surface, (203, 90, 42), (3 * TILE_SIZE + 8, 4 * TILE_SIZE, 3 * TILE_SIZE - 16, 2 * TILE_SIZE))
        pygame.draw.circle(surface, (244, 175, 63), (4 * TILE_SIZE + 16, 5 * TILE_SIZE), 10)
        # Anvil silhouette.
        pygame.draw.rect(surface, (59, 65, 69), (8 * TILE_SIZE, 8 * TILE_SIZE, 4 * TILE_SIZE, 13))
        pygame.draw.polygon(surface, (105, 115, 119), [(7 * TILE_SIZE + 8, 8 * TILE_SIZE),
                         (12 * TILE_SIZE + 8, 8 * TILE_SIZE), (11 * TILE_SIZE + 8, 8 * TILE_SIZE + 11),
                         (8 * TILE_SIZE, 8 * TILE_SIZE + 11)])
        pygame.draw.rect(surface, (67, 46, 37), (8 * TILE_SIZE + 10, 8 * TILE_SIZE + 13, 3 * TILE_SIZE, 2 * TILE_SIZE))
        # Wall mounted tools and the sales counter.
        pygame.draw.rect(surface, (55, 39, 33), (17 * TILE_SIZE, 2 * TILE_SIZE, 5 * TILE_SIZE, 5 * TILE_SIZE))
        for index in range(4):
            px = 18 * TILE_SIZE + index * 25
            pygame.draw.line(surface, (194, 179, 147), (px, 2 * TILE_SIZE + 7), (px + 6, 4 * TILE_SIZE), 3)
            pygame.draw.line(surface, (131, 140, 143), (px - 3, 2 * TILE_SIZE + 7), (px + 9, 2 * TILE_SIZE + 7), 4)
        pygame.draw.rect(surface, (64, 43, 34), (16 * TILE_SIZE, 10 * TILE_SIZE, 7 * TILE_SIZE, 2 * TILE_SIZE))
        pygame.draw.rect(surface, (157, 103, 59), (16 * TILE_SIZE + 4, 10 * TILE_SIZE + 4, 7 * TILE_SIZE - 8, 2 * TILE_SIZE - 8))
        pygame.draw.rect(surface, (142, 46, 40), (9 * TILE_SIZE, 11 * TILE_SIZE, 7 * TILE_SIZE, 2 * TILE_SIZE))

    def draw(self, surface):
        surface.fill((38, 31, 29))
        self._wood_floor(surface)
        if self.house_id == "village_house_1":
            self._draw_quest_cottage(surface)
            title = "약초상의 오두막"
            sprites = ("villager", "chief")
        elif self.house_id == "village_house_2":
            self._draw_blacksmith(surface)
            title = "로건의 대장간"
            sprites = ("shopkeeper",)
        else:
            self._draw_chief_office(surface)
            title = "촌장 발렌의 집"
            sprites = ("chief",)
        for position, sprite_name in zip(self.npcs, sprites):
            surface.blit(sprite(sprite_name, (TILE_SIZE, TILE_SIZE)),
                         (position[0] * TILE_SIZE, position[1] * TILE_SIZE))
        px = round(self.player["x"] * TILE_SIZE + TILE_SIZE / 2)
        py = round((self.player["y"] + 1) * TILE_SIZE)
        surface.blit(hero_sprite(self.weapon, self.armor, (TILE_SIZE, TILE_SIZE + 16), self.facing,
                                 int(self.walk_clock) % 2 if self.walk_clock else 0),
                     (px - TILE_SIZE // 2, py - TILE_SIZE - 16))
        pygame.draw.rect(surface, self.game.colors["ink"], (0, 512, WIDTH, HEIGHT - 512))
        pygame.draw.rect(surface, self.game.colors["gold"], (0, 512, WIDTH, 4))
        pygame.draw.rect(surface, self.game.colors["panel"], (8, 520, 784, 72))
        pygame.draw.rect(surface, self.game.colors["gold"], (8, 520, 784, 72), 2)
        self.text(surface, f"{title}  ·  Lv.{self.level}  HP {self.hp}/{self.max_hp}  MP {self.mp}/{self.max_mp}  금화 {self.gold}",
                  (20, 526), 18)
        self.text(surface, self.message, (20, 558), 16, self.game.colors["muted"])
        self.button(surface, pygame.Rect(686, 536, 92, 38), "저장", False, 17)
        self._draw_dialogue(surface)

    @staticmethod
    def _draw_chief_office(surface):
        # A map desk, village records, a formal rug, and the chief's chair.
        pygame.draw.rect(surface, (58, 43, 36), (2 * TILE_SIZE, 2 * TILE_SIZE, 5 * TILE_SIZE, 3 * TILE_SIZE))
        pygame.draw.rect(surface, (119, 80, 53), (2 * TILE_SIZE + 5, 2 * TILE_SIZE + 5,
                                                   5 * TILE_SIZE - 10, 3 * TILE_SIZE - 10))
        for index, color in enumerate(((98, 132, 91), (93, 125, 154), (193, 157, 92))):
            pygame.draw.rect(surface, color, (3 * TILE_SIZE + index * 30, 3 * TILE_SIZE, 25, 25))
            pygame.draw.line(surface, (67, 56, 43), (3 * TILE_SIZE + index * 30, 3 * TILE_SIZE + 12),
                             (3 * TILE_SIZE + index * 30 + 25, 3 * TILE_SIZE + 12), 2)
        pygame.draw.rect(surface, (129, 41, 37), (8 * TILE_SIZE, 8 * TILE_SIZE, 9 * TILE_SIZE, 4 * TILE_SIZE))
        pygame.draw.rect(surface, (209, 175, 111), (8 * TILE_SIZE, 8 * TILE_SIZE, 9 * TILE_SIZE, 4 * TILE_SIZE), 3)
        pygame.draw.rect(surface, (76, 52, 40), (9 * TILE_SIZE, 4 * TILE_SIZE, 7 * TILE_SIZE, 2 * TILE_SIZE))
        pygame.draw.rect(surface, (164, 119, 74), (9 * TILE_SIZE + 4, 4 * TILE_SIZE + 4,
                                                     7 * TILE_SIZE - 8, 2 * TILE_SIZE - 8))
        pygame.draw.rect(surface, (79, 54, 42), (10 * TILE_SIZE, 2 * TILE_SIZE, 5 * TILE_SIZE, 2 * TILE_SIZE))
        for index in range(5):
            pygame.draw.rect(surface, (190 - index * 12, 156 - index * 10, 104 - index * 6),
                             (10 * TILE_SIZE + index * 28, 2 * TILE_SIZE + 4, 22, 25))

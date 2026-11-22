"""Interiors for Marta's herb cottage, Garen's quarters and the chief's house."""

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
        # Marta keeps the herb cottage; Garen lives alone in house 2; Valen in the chief's house.
        self.npcs = ((7, 6),) if self.house_id == "village_house_1" else ((12, 6),)
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
            self.walls.update({(x, y) for x in range(2, 6) for y in range(2, 5)})      # bed
            self.walls.update({(x, y) for x in range(9, 16) for y in range(2, 4)})     # hearth
            self.walls.update({(x, y) for x in range(19, 23) for y in range(2, 4)})    # weapon rack
            self.walls.update({(3, 9), (3, 10), (21, 9), (21, 10)})                    # armor stands
            self.walls.update({(x, y) for x in range(17, 20) for y in range(11, 13)})  # map table
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
        near_npc = (x - self.npcs[0][0]) ** 2 + (y - self.npcs[0][1]) ** 2 <= 1.5
        if self.house_id == "village_house_1":
            if near_npc:
                self._offer_sidequest("sq_moon_herb")
            else:
                self.message = "침대와 약초 서랍이 놓인 작은 오두막입니다."
        elif self.house_id == "village_house_2":
            if near_npc:
                self._interact_garen()
            else:
                self.message = "낡은 갑옷과 왕국 깃발이 걸린 노기사의 거처입니다."
        elif near_npc:
            self._interact_chief()
        else:
            self.message = "마을 지도와 기록이 쌓인 촌장의 집무실입니다."

    def _interact_garen(self):
        quest = self.sub_quests["sq_old_sword"]
        if self.quest_flags["final_boss"] and quest["status"] == "COMPLETED":
            self.show_dialogue(["내 휘장을 단 기사가 마을을 구했군. 이보다 자랑스러울 수 없네."])
        elif self.quest_flags["final_boss"]:
            self.show_dialogue(["훌륭한 검술이었네, 수호 기사여. 젊은 날의 나를 보는 것 같군."])
        else:
            self._offer_sidequest("sq_old_sword")

    def _interact_chief(self):
        cleared = sum(self.quest_flags[key] for key in ("shrine_wind", "shrine_earth", "shrine_fire"))
        if self.quest_flags["final_boss"]:
            self.show_dialogue(["오크밸리의 수호 기사여, 그대 덕분에 별빛 결계가 다시 빛나고 있네.",
                                "언제든 마을에 들러 쉬어 가게."])
        elif not self.quest_flags["prologue_done"]:
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

    def _draw_knight_quarters(self, surface):
        # A soldier's bed, stone hearth under the kingdom banner, a weapon rack,
        # two old armor stands and the table where Garen keeps his maps.
        t = TILE_SIZE
        pygame.draw.rect(surface, (54, 42, 37), (2 * t - 3, 2 * t - 3, 4 * t + 6, 3 * t + 6))
        pygame.draw.rect(surface, (109, 78, 55), (2 * t, 2 * t, 4 * t, 3 * t))
        pygame.draw.rect(surface, (196, 194, 176), (2 * t + 6, 2 * t + 5, 4 * t - 12, 20))
        pygame.draw.rect(surface, (122, 46, 44), (2 * t + 6, 2 * t + 28, 4 * t - 12, 3 * t - 34))
        pygame.draw.line(surface, (210, 170, 92), (2 * t + 6, 2 * t + 40), (6 * t - 6, 2 * t + 40), 2)

        pygame.draw.rect(surface, (78, 76, 78), (9 * t, t + 12, 7 * t, 2 * t + 20))
        for row in range(3):
            for col in range(7):
                pygame.draw.rect(surface, (118, 115, 112) if (row + col) % 2 else (102, 99, 98),
                                 (9 * t + 4 + col * t - (row % 2) * 10, t + 16 + row * 18, t - 6, 14))
        pygame.draw.rect(surface, (36, 28, 27), (11 * t, 2 * t + 8, 3 * t, t + 16))
        pygame.draw.polygon(surface, (219, 104, 44), [(11 * t + 14, 3 * t + 24), (12 * t + 16, 2 * t + 14),
                                                      (13 * t + 18, 3 * t + 24)])
        pygame.draw.polygon(surface, (248, 186, 72), [(12 * t, 3 * t + 24), (12 * t + 16, 2 * t + 28),
                                                      (13 * t, 3 * t + 24)])
        banner = pygame.Rect(12 * t + 2, t - 22, t - 4, 40)
        pygame.draw.rect(surface, (39, 66, 124), banner)
        pygame.draw.polygon(surface, (39, 66, 124), [banner.bottomleft, (banner.centerx, banner.bottom + 8),
                                                     banner.bottomright])
        pygame.draw.circle(surface, self.game.colors["gold"], (banner.centerx, banner.y + 18), 6, 2)

        pygame.draw.rect(surface, (55, 39, 33), (19 * t, 2 * t, 4 * t, 2 * t))
        for index in range(4):
            px = 19 * t + 14 + index * 30
            pygame.draw.line(surface, (190, 196, 198), (px, 2 * t + 6), (px, 4 * t - 4), 4)
            pygame.draw.line(surface, (140, 98, 58), (px - 7, 3 * t + 6), (px + 7, 3 * t + 6), 3)
            pygame.draw.rect(surface, (120, 78, 46), (px - 2, 3 * t + 8, 4, 12))

        for sx in (3, 21):
            cx = sx * t + t // 2
            pygame.draw.line(surface, (78, 56, 42), (cx, 9 * t), (cx, 11 * t), 4)
            pygame.draw.rect(surface, (64, 58, 52), (cx - 14, 10 * t + 20, 28, 8))
            pygame.draw.rect(surface, (138, 148, 150), (cx - 12, 9 * t + 2, 24, 26))
            pygame.draw.rect(surface, (186, 194, 194), (cx - 8, 9 * t + 5, 8, 18))
            pygame.draw.rect(surface, (120, 128, 132), (cx - 9, 8 * t + 8, 18, 18))
            pygame.draw.rect(surface, (40, 42, 46), (cx - 6, 8 * t + 15, 12, 3))

        pygame.draw.rect(surface, (39, 66, 124), (7 * t, 6 * t + 16, 11 * t, 4 * t))
        pygame.draw.rect(surface, (196, 164, 98), (7 * t, 6 * t + 16, 11 * t, 4 * t), 3)
        pygame.draw.rect(surface, (64, 44, 34), (17 * t, 11 * t, 3 * t, 2 * t))
        pygame.draw.rect(surface, (150, 104, 62), (17 * t + 4, 11 * t + 4, 3 * t - 8, 2 * t - 8))
        pygame.draw.rect(surface, (222, 204, 160), (17 * t + 14, 11 * t + 10, 40, 28))
        pygame.draw.line(surface, (140, 98, 58), (17 * t + 20, 11 * t + 18), (17 * t + 46, 11 * t + 30), 2)

    def draw(self, surface):
        surface.fill((38, 31, 29))
        self._wood_floor(surface)
        if self.house_id == "village_house_1":
            self._draw_quest_cottage(surface)
            title = "약초상의 오두막"
            sprites = ("villager",)
        elif self.house_id == "village_house_2":
            self._draw_knight_quarters(surface)
            title = "노기사 가렌의 거처"
            sprites = ("old_knight",)
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

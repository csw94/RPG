"""Turn-based battle scene."""

import pygame
from gameplay.enemies import ENEMIES
from gameplay.equipment import ARMORS, WEAPONS
from scenes.base_scene import BaseScene
from utils.pixel_art import hero_sprite, sprite


def _pixel_hill(surface, color, center_x, top_y, width, height):
    """Build a stepped hill from broad horizontal pixel bands."""
    bands = max(1, height // 8)
    for band in range(bands):
        half_width = max(4, int((band + 1) * width / (bands * 2)))
        y = top_y + band * 8
        pygame.draw.rect(surface, color, (center_x - half_width, y, half_width * 2, 8))


class BattleScene(BaseScene):
    ACTIONS = ("공격", "스킬", "포션", "도망")

    def __init__(self, game, enemy_type="slime"):
        super().__init__(game)
        self.selected = 0
        self.enemy = ENEMIES.get(enemy_type, ENEMIES["slime"])
        self.enemy_hp = self.enemy["hp"]
        self.enemy_max_hp = self.enemy["hp"]
        self.message = f"{self.enemy['name']}이(가) 나타났다!"
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
        weapon = WEAPONS.get(field.weapon, WEAPONS["rusty_sword"])
        armor = ARMORS.get(field.armor, ARMORS["traveler_clothes"])
        if self.selected == 0:
            self.enemy_hp -= max(1, 6 + field.level * 2 + weapon["attack"] - self.enemy["defense"])
            self.message = "용사의 검이 빛났다!"
        elif self.selected == 1:
            if field.mp < 3:
                self.message = "MP가 부족합니다."
                return
            field.mp -= 3
            self.enemy_hp -= max(1, 13 + field.level * 2 + weapon["attack"] // 2 - self.enemy["defense"])
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
            field.xp += self.enemy["xp"]
            field.gold += self.enemy["gold"]
            self.message = f"{self.enemy['name']} 격파! 경험치 +{self.enemy['xp']} · 금화 +{self.enemy['gold']}"
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
        field.hp = max(0, field.hp - max(1, self.enemy["attack"] - armor["defense"]))
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
        surface.fill((112, 174, 205))
        # Chunky cloud and hill clusters establish a pixel-art battle backdrop.
        for x, y, width in ((72, 147, 92), (546, 129, 116), (333, 207, 54)):
            pygame.draw.rect(surface, (210, 230, 215), (x, y, width, 12))
            pygame.draw.rect(surface, (210, 230, 215), (x + 14, y - 10, width - 28, 10))
            pygame.draw.rect(surface, (151, 201, 211), (x + 8, y + 12, width - 16, 5))
        _pixel_hill(surface, (93, 151, 115), 110, 228, 220, 80)
        _pixel_hill(surface, (73, 132, 102), 555, 213, 290, 91)
        pygame.draw.rect(surface, (64, 131, 83), (0, 307, 800, 67))
        pygame.draw.rect(surface, (46, 108, 70), (0, 307, 800, 9))
        for x in range(0, 800, 32):
            pygame.draw.rect(surface, (73, 145, 87), (x + (x % 3) * 3, 321 + (x % 4) * 5, 4, 7))
        pygame.draw.rect(surface, (42, 86, 66), (170, 314, 132, 9))
        pygame.draw.rect(surface, (42, 86, 66), (500, 304, 150, 11))
        surface.blit(hero_sprite(self.game.field.weapon, self.game.field.armor, (80, 80)), (198, 224))
        surface.blit(sprite(self.enemy["sprite"], self.enemy["size"]), (518, 211))
        pygame.draw.rect(surface, self.game.colors["ink"], (54, 24, 263, 94))
        pygame.draw.rect(surface, self.game.colors["cream"], (58, 28, 255, 86))
        pygame.draw.rect(surface, self.game.colors["panel"], (61, 31, 249, 80))
        self.text(surface, "용사", (78, 42), 20)
        self._bar(surface, 78, 77, 215, self.game.field.hp, self.game.field.max_hp, self.game.colors["red"])
        pygame.draw.rect(surface, self.game.colors["ink"], (482, 24, 263, 94))
        pygame.draw.rect(surface, self.game.colors["cream"], (486, 28, 255, 86))
        pygame.draw.rect(surface, self.game.colors["panel"], (489, 31, 249, 80))
        self.text(surface, self.enemy["name"], (506, 42), 20)
        self._bar(surface, 506, 77, 215, max(0, self.enemy_hp), self.enemy_max_hp, self.game.colors["green"])
        pygame.draw.rect(surface, self.game.colors["ink"], (0, 374, 800, 226))
        pygame.draw.rect(surface, self.game.colors["gold"], (0, 374, 800, 4))
        pygame.draw.rect(surface, self.game.colors["panel"], (8, 382, 784, 210))
        pygame.draw.rect(surface, self.game.colors["gold"], (8, 382, 784, 210), 2)
        self.text(surface, self.message, (400, 401), 19, self.game.colors["gold"], True)
        for i, (label, rect) in enumerate(zip(self.ACTIONS, self._buttons())):
            if i == 2:
                label = f"포션 ({self.game.field.potions})"
            self.button(surface, rect, label, i == self.selected)
        weapon = WEAPONS.get(self.game.field.weapon, WEAPONS["rusty_sword"])
        armor = ARMORS.get(self.game.field.armor, ARMORS["traveler_clothes"])
        self.text(surface, f"HP {self.game.field.hp}/{self.game.field.max_hp}   MP {self.game.field.mp}/{self.game.field.max_mp}   공격+{weapon['attack']} 방어+{armor['defense']}",
                  (400, 570), 17, self.game.colors["muted"], True)

    @staticmethod
    def _bar(surface, x, y, width, value, maximum, color):
        pygame.draw.rect(surface, (55, 61, 73), (x, y, width, 14))
        fill = int(width * max(0, value) / maximum) if maximum else 0
        if fill:
            pygame.draw.rect(surface, color, (x, y, fill, 14))

"""Turn-based encounters for the Oak Valley story."""

import random
import pygame

from gameplay.enemies import ENEMIES
from scenes.base_scene import BaseScene
from utils.pixel_art import hero_sprite, sprite


class BattleScene(BaseScene):
    ACTIONS = ("\uacf5\uaca9", "\uc2a4\ud0ac", "\ud3ec\uc158", "\ub3c4\ub9dd")

    def __init__(self, game, enemy_type="slime"):
        super().__init__(game)
        self.selected = 0
        self.enemy = ENEMIES.get(enemy_type, ENEMIES["slime"])
        self.enemy_hp = self.enemy["hp"]
        self.enemy_max_hp = self.enemy["hp"]
        self.turn = 0
        self.enraged = False
        self.message = f"{self.enemy['name']}\uc774(\uac00) \ub098\ud0c0\ub0ac\ub2e4!"
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
                for index, rect in enumerate(self._buttons()):
                    if rect.collidepoint(event.pos):
                        self.selected = index
                        self._act()

    def _buttons(self):
        return [pygame.Rect(104 + (i % 2) * 310, 434 + (i // 2) * 58, 280, 46) for i in range(4)]

    def _act(self):
        if self.done:
            self.game.finish_battle()
            return
        field = self.game.field
        action_message = ""
        if self.selected == 0:
            damage = max(1, field.attack_power - self.enemy["defense"])
            self.enemy_hp -= damage
            action_message = f"\uac80\uc744 \ud718\ub450\ub974\uc5b4 {damage}\uc758 \ud53c\ud574\ub97c \uc8fc\uc5c8\ub2e4."
        elif self.selected == 1:
            if field.mp < 3:
                self.message = "MP\uac00 \ubd80\uc871\ud569\ub2c8\ub2e4."
                return
            field.mp -= 3
            damage = max(1, field.attack_power + 10 - self.enemy["defense"])
            self.enemy_hp -= damage
            action_message = f"\ube5b\uc758 \ud0c4\uc744 \ubc1c\ud788\uc5b4 {damage}\uc758 \ud53c\ud574\ub97c \uc785\ud614\ub2e4!"
        elif self.selected == 2:
            if field.potions > 0:
                field.potions -= 1
                healed = min(50, field.max_hp - field.hp)
                field.hp = min(field.max_hp, field.hp + 50)
                action_message = f"\ud68c\ubcf5\uc57d(\uc18c)\uc73c\ub85c HP {healed}\uc744 \ud68c\ubcf5\ud588\ub2e4."
            elif field.high_potions > 0:
                field.high_potions -= 1
                healed = min(120, field.max_hp - field.hp)
                field.hp = min(field.max_hp, field.hp + 120)
                action_message = f"\uace0\uae09 \ud68c\ubcf5\uc57d\uc73c\ub85c HP {healed}\uc744 \ud68c\ubcf5\ud588\ub2e4."
            else:
                self.message = "\uc0ac\uc6a9\ud560 \ud3ec\uc158\uc774 \uc5c6\uc2b5\ub2c8\ub2e4."
                return
        else:
            if self.enemy["pattern"] in ("gust", "earthquake", "enrage", "dark_arts"):
                self.message = "\ubcf4\uc2a4\uc758 \uc555\ub3c4\uc801\uc778 \uae30\uc6b4\uc5d0 \ub3c4\ub9dd\uce60 \uc218 \uc5c6\ub2e4!"
                return
            self.message = "\uc804\ud22c\uc5d0\uc11c \ub3c4\ub9dd\ud588\ub2e4."
            self.done = True
            self.result_timer = 0.65
            return

        if self.enemy_hp <= 0:
            reward = field.resolve_battle_victory(self.enemy["id"])
            if self.enemy["id"] == "final_boss":
                field.pending_dialogue = [
                    "\ud06c\uc73d... \uace0\uc791 \ubcc0\ubc29\uc758 \uacac\uc2b5 \uae30\uc0ac\uc5d0\uac8c \uc774\ub7f0 \ube5b\uc758 \ud798\uc774... \ub9d0\ub3c4 \uc548 \ub3fc...!",
                    "\ub9d0\ud3ec\uc2a4\ub97c \ubb3c\ub9ac\uce58\uace0 \uc655\uad6d \uae30\uc0ac\ub85c \uc784\uba85\ub418\uc5c8\ub2e4. \uc5d4\ub529 \ud074\ub9ac\uc5b4!",
                ]
            self.message = f"{self.enemy['name']} \uaca9\ud30c! {reward}"
            self.done = True
            self.result_timer = 1.3
            self.game.save_game()
            return

        self.turn += 1
        self.message = action_message + " " + self._enemy_turn(field)
        if field.hp <= 0:
            field.hp = max(1, field.max_hp // 2)
            field.player.update(x=12, y=13)
            field.world = "village"
            field.message = "\ud798\uacb0\ud558\uac8c \uae68\uc5b4\ub098 \uc624\ud06c\ubc38\ub9ac\ub85c \ub3cc\uc544\uc654\ub2e4."
            self.message += " \uc758\uc2dd\uc744 \uc783\uc5c8\ub2e4..."
            self.done = True
            self.result_timer = 1.4
        self.game.save_game()

    def _enemy_turn(self, field):
        pattern = self.enemy["pattern"]
        evasion = field.evasion_bonus > 0 and random.random() < field.evasion_bonus / 100

        def hit(amount, fixed=False):
            if evasion:
                return 0
            damage = amount if fixed else max(1, amount - field.defense_power)
            field.hp = max(0, field.hp - damage)
            return damage

        if pattern == "double_stab":
            first = hit(max(1, self.enemy["attack"] // 2))
            second = hit(max(1, self.enemy["attack"] // 2))
            if evasion:
                return "\ud68c\ud53c \ubcf4\ub108\uc2a4\ub85c \uc5f0\uc18d \ucc0c\ub974\uae30\ub97c \ud53c\ud588\ub2e4!"
            return f"\uace0\ube14\ub9b0\uc758 \uc5f0\uc18d \ucc0c\ub974\uae30! {first + second} \ud53c\ud574."
        if pattern == "gust" and self.turn % 2 == 0:
            amount = hit(15, fixed=True)
            return "\ud3ed\ud48d \ub3cc\ud48d! \ubc29\uc5b4\ub97c \ubb34\uc2dc\ud55c 15 \ud53c\ud574." if amount else "\ud3ed\ud48d\uc744 \ud68c\ud53c\ud588\ub2e4!"
        if pattern == "earthquake" and self.turn % 3 == 0:
            amount = hit(30, fixed=True)
            return "\ubc14\uc704 \uace8\ub818\uc758 \uc9c0\uc9c4! 30 \ud53c\ud574." if amount else "\uc9c0\uc9c4\uc758 \ucda9\uaca9\uc744 \ud68c\ud53c\ud588\ub2e4!"
        if pattern == "enrage" and not self.enraged and self.enemy_hp <= self.enemy_max_hp // 2:
            self.enraged = True
            return "\ud654\uc5fc \ub9ac\uc790\ub4dc\ub9e8\uc774 \uad11\ud3ed\ud654\ud588\ub2e4! ATK +5"
        attack = self.enemy["attack"] + (5 if pattern == "enrage" and self.enraged else 0)
        if pattern == "dark_arts" and self.turn % 3 == 0:
            amount = hit(18, fixed=True)
            return "\uc5b4\ub460\uc758 \ud30c\ub3d9! \ubaa8\ub4e0 \uac83\uc744 \ud718\uac10\ud558\uba70 18 \ud53c\ud574." if amount else "\uc5b4\ub460\uc758 \ud30c\ub3d9\uc744 \ube5b\uc73c\ub85c \ud76c\uc11d\ud588\ub2e4!"
        if pattern == "dark_arts":
            attack += 8
        amount = hit(attack)
        if evasion:
            return "\uc801\uc758 \uacf5\uaca9\uc744 \ud68c\ud53c\ud588\ub2e4!"
        label = "\uc554\ud751 \ubca0\uae30" if pattern == "dark_arts" else "\uc801\uc758 \uacf5\uaca9"
        return f"{label}! {amount}\uc758 \ud53c\ud574\ub97c \ubc1b\uc558\ub2e4."

    def update(self, dt):
        if self.done:
            self.result_timer -= dt
            if self.result_timer <= 0:
                self.game.finish_battle()

    def draw(self, surface):
        surface.fill((112, 174, 205))
        for x, y, width in ((72, 147, 92), (546, 129, 116), (333, 207, 54)):
            pygame.draw.rect(surface, (210, 230, 215), (x, y, width, 12))
            pygame.draw.rect(surface, (210, 230, 215), (x + 14, y - 10, width - 28, 10))
            pygame.draw.rect(surface, (151, 201, 211), (x + 8, y + 12, width - 16, 5))
        pygame.draw.rect(surface, (64, 131, 83), (0, 307, 800, 67))
        pygame.draw.rect(surface, (46, 108, 70), (0, 307, 800, 9))
        surface.blit(hero_sprite(self.game.field.weapon, self.game.field.armor, (80, 120)), (198, 184))
        surface.blit(sprite(self.enemy["sprite"], self.enemy["size"]), (518, 211))
        self._panel(surface, pygame.Rect(54, 24, 263, 94))
        self.text(surface, "\uc218\ud638\uc790", (78, 42), 20)
        self._bar(surface, 78, 77, 215, self.game.field.hp, self.game.field.max_hp, self.game.colors["red"])
        self._panel(surface, pygame.Rect(482, 24, 263, 94))
        self.text(surface, self.enemy["name"], (506, 42), 20)
        self._bar(surface, 506, 77, 215, max(0, self.enemy_hp), self.enemy_max_hp, self.game.colors["green"])
        pygame.draw.rect(surface, self.game.colors["ink"], (0, 374, 800, 226))
        pygame.draw.rect(surface, self.game.colors["gold"], (0, 374, 800, 4))
        pygame.draw.rect(surface, self.game.colors["panel"], (8, 382, 784, 210))
        pygame.draw.rect(surface, self.game.colors["gold"], (8, 382, 784, 210), 2)
        self.text(surface, self.message, (400, 401), 18, self.game.colors["gold"], True)
        for index, (label, rect) in enumerate(zip(self.ACTIONS, self._buttons())):
            if index == 2:
                label = f"\ud3ec\uc158 ({self.game.field.potions}/{self.game.field.high_potions})"
            self.button(surface, rect, label, index == self.selected)
        field = self.game.field
        self.text(surface, f"HP {field.hp}/{field.max_hp}   MP {field.mp}/{field.max_mp}   ATK {field.attack_power}   DEF {field.defense_power}",
                  (400, 570), 16, self.game.colors["muted"], True)

    def _panel(self, surface, rect):
        pygame.draw.rect(surface, self.game.colors["ink"], rect)
        pygame.draw.rect(surface, self.game.colors["cream"], rect.inflate(-8, -8))
        pygame.draw.rect(surface, self.game.colors["panel"], rect.inflate(-14, -14))

    @staticmethod
    def _bar(surface, x, y, width, value, maximum, color):
        pygame.draw.rect(surface, (55, 61, 73), (x, y, width, 14))
        fill = int(width * max(0, value) / maximum) if maximum else 0
        if fill:
            pygame.draw.rect(surface, color, (x, y, fill, 14))

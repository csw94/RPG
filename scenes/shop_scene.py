"""Village equipment shop with weapon, armor, and potion purchases."""

import pygame

from utils import ui
from gameplay.equipment import ARMORS, SHOP_ITEMS, WEAPONS, item_info
from scenes.base_scene import BaseScene


class ShopScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.selected = 0
        self.message = "\uace8\ub4dc\ub85c \uc7a5\ube44\ub97c \uad6c\ub9e4\ud558\uac70\ub098 \uc18c\uc9c0\ud488\uc744 \ucc59\uae30\uc138\uc694."

    @staticmethod
    def panel_rect():
        return pygame.Rect(52, 20, 696, 560)

    @staticmethod
    def close_rect():
        return pygame.Rect(330, 506, 140, 40)

    def _rows(self):
        return [pygame.Rect(118, 158 + index * 62, 564, 48) for index in range(len(SHOP_ITEMS))]

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._close()
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(SHOP_ITEMS)
                    self.sfx("cursor")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(SHOP_ITEMS)
                    self.sfx("cursor")
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._purchase()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for index, rect in enumerate(self._rows()):
                    if rect.collidepoint(event.pos):
                        self.selected = index
                        self._purchase()
                        break
                if self.close_rect().collidepoint(event.pos):
                    self._close()

    def _close(self):
        self.game.save_game()
        self.game.scene_name = self.game.field.world
        self.game.scene = self.game.field

    def _purchase(self):
        item = SHOP_ITEMS[self.selected]
        info = item_info(item)
        player = self.game.field
        if item["kind"] == "potion":
            inventory = "high_potions" if item["id"] == "high_potion" else "potions"
            if getattr(player, inventory) >= 10:
                self.message = "\ud3ec\uc158\uc740 \uc885\ub958\ubcc4\ub85c 10\uac1c\uae4c\uc9c0 \uc18c\uc9c0\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4."
                return
            if player.gold < info["price"]:
                self.message = "\uace8\ub4dc\uac00 \ubd80\uc871\ud569\ub2c8\ub2e4."
                return
            player.gold -= info["price"]
            setattr(player, inventory, getattr(player, inventory) + 1)
            self.sfx("coin")
            self.message = f"{info['name']}\uc744(\ub97c) \uac00\ubc29\uc5d0 \ub123\uc5c8\uc2b5\ub2c8\ub2e4."
            self.game.save_game()
            return

        kind = item["kind"]
        owned = player.owned_weapons if kind == "weapon" else player.owned_armors
        active_attribute = "weapon" if kind == "weapon" else "armor"
        if item["id"] not in owned:
            if player.gold < info["price"]:
                self.message = "\uace8\ub4dc\uac00 \ubd80\uc871\ud569\ub2c8\ub2e4. \ud544\ub4dc\uc5d0\uc11c \ubaa8\ud5d8\ud558\uba70 \ubc8c\uc5b4 \ubcf4\uc138\uc694."
                return
            player.gold -= info["price"]
            owned.append(item["id"])
        if kind == "armor":
            old = ARMORS.get(player.armor, ARMORS["traveler_clothes"])
            health_delta = info.get("health", 0) - old.get("health", 0)
            player.max_hp += health_delta
            player.hp = min(player.max_hp, player.hp + max(0, health_delta))
        setattr(player, active_attribute, item["id"])
        self.sfx("coin")
        self.message = f"{info['name']}\uc744(\ub97c) \uc7a5\ucc29\ud588\uc2b5\ub2c8\ub2e4."
        self.game.save_game()

    def update(self, dt):
        pass

    def _frame(self, surface, rect, fill=None, active=False):
        ui.frame_around(surface, rect, "walnut", active)

    def _item_text(self, item):
        player = self.game.field
        info = item_info(item)
        if item["kind"] == "weapon":
            detail = f"ATK +{info['attack']}"
            owned = item["id"] in player.owned_weapons
            active = player.weapon == item["id"]
            quantity = None
        elif item["kind"] == "armor":
            detail = f"DEF +{info['defense']}" + (f", HP +{info['health']}" if info.get("health") else "")
            owned = item["id"] in player.owned_armors
            active = player.armor == item["id"]
            quantity = None
        else:
            detail = f"HP {info['heal']} \ud68c\ubcf5"
            quantity = player.high_potions if item["id"] == "high_potion" else player.potions
            owned = quantity > 0
            active = False
        if item["kind"] == "potion":
            price = f"\ubcf4\uc720 {quantity}/10 \u00b7 {info['price']} G"
        else:
            price = "\uc7a5\ucc29 \uc911" if active else ("\ubcf4\uc720" if owned else f"{info['price']} G")
        return f"{info['name']}   \u00b7   {detail}", price

    def draw(self, surface):
        ui.plank_strip(surface, (0, 0, surface.get_width(), surface.get_height()))
        ui.frame(surface, self.panel_rect(), "walnut", border=8)
        self.text(surface, "\uc624\ud06c\ubc38\ub9ac \uc0c1\uc810", (400, 70), 32, self.game.colors["gold"], True)
        gold = self.text(surface, f"\ubcf4\uc720 \uace8\ub4dc {self.game.field.gold} G", (410, 108), 19,
                         self.game.colors["cream"], True)
        ui.coin(surface, (gold.left - 14, gold.centery))
        weapon = WEAPONS.get(self.game.field.weapon, WEAPONS["rusty_sword"])
        armor = ARMORS.get(self.game.field.armor, ARMORS["traveler_clothes"])
        self.text(surface, f"\uc7a5\ucc29 \uc911: {weapon['name']} \u00b7 {armor['name']}", (400, 137), 16,
                  self.game.colors["muted"], True)
        for index, (item, rect) in enumerate(zip(SHOP_ITEMS, self._rows())):
            self._frame(surface, rect, self.game.colors["panel"], index == self.selected)
            label, price = self._item_text(item)
            self.text(surface, label, (rect.x + 14, rect.y + 13), 17, self.game.colors["cream"])
            price_image = self.game.font(16).render(price, True, self.game.colors["gold"])
            surface.blit(price_image, price_image.get_rect(midright=(rect.right - 14, rect.centery)))
        self.text(surface, self.message, (400, 486), 16, self.game.colors["cream"], True)
        self.button(surface, self.close_rect(), "\ub9c8\uc744\ub85c", False, 18)
        self.text(surface, "\u2191\u2193 \uc120\ud0dd \u00b7 Enter \uad6c\ub9e4/\uc7a5\ucc29 \u00b7 ESC \ub3cc\uc544\uac00\uae30", (400, 558), 13,
                  self.game.colors["muted"], True)

"""Village equipment shop with weapon, armor, and potion purchases."""

import pygame
from gameplay.equipment import ARMORS, SHOP_ITEMS, WEAPONS, item_info
from scenes.base_scene import BaseScene


class ShopScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.selected = 0
        self.message = "금화를 사용해 장비를 구입하거나 착용하세요."

    def _rows(self):
        return [pygame.Rect(118, 158 + index * 62, 564, 48) for index in range(len(SHOP_ITEMS))]

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._close()
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(SHOP_ITEMS)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(SHOP_ITEMS)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._purchase()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for index, rect in enumerate(self._rows()):
                    if rect.collidepoint(event.pos):
                        self.selected = index
                        self._purchase()
                        break
                if pygame.Rect(330, 512, 140, 42).collidepoint(event.pos):
                    self._close()

    def _close(self):
        self.game.save_game()
        self.game.scene_name = "village"
        self.game.scene = self.game.field

    def _purchase(self):
        item = SHOP_ITEMS[self.selected]
        info = item_info(item)
        player = self.game.field
        if item["kind"] == "potion":
            if player.gold < info["price"]:
                self.message = "금화가 부족합니다."
                return
            player.gold -= info["price"]
            player.potions += 1
            self.message = "회복 포션을 가방에 넣었습니다."
            self.game.save_game()
            return

        kind = item["kind"]
        owned = player.owned_weapons if kind == "weapon" else player.owned_armors
        active_attribute = "weapon" if kind == "weapon" else "armor"
        if item["id"] not in owned:
            if player.gold < info["price"]:
                self.message = "금화가 부족합니다. 모험을 더 하고 오세요."
                return
            player.gold -= info["price"]
            owned.append(item["id"])
        setattr(player, active_attribute, item["id"])
        self.message = f"{info['name']}을(를) 착용했습니다."
        self.game.save_game()

    def update(self, dt):
        pass

    def _frame(self, surface, rect, fill, selected=False):
        trim = self.game.colors["gold"] if selected else self.game.colors["muted"]
        pygame.draw.rect(surface, self.game.colors["ink"], rect.inflate(6, 6))
        pygame.draw.rect(surface, trim, rect.inflate(3, 3))
        pygame.draw.rect(surface, fill, rect)
        pygame.draw.rect(surface, self.game.colors["cream"], rect, 1)

    def _item_text(self, item):
        player = self.game.field
        info = item_info(item)
        if item["kind"] == "weapon":
            detail = f"공격 +{info['attack']}"
            owned = item["id"] in player.owned_weapons
            active = player.weapon == item["id"]
        elif item["kind"] == "armor":
            detail = f"방어 +{info['defense']}"
            owned = item["id"] in player.owned_armors
            active = player.armor == item["id"]
        else:
            detail = "HP 18 회복"
            owned = False
            active = False
        price = "보유 중" if active else ("착용" if owned else f"{info['price']} G")
        return f"{info['name']}   ·   {detail}", price

    def draw(self, surface):
        surface.fill((32, 42, 34))
        pygame.draw.rect(surface, (73, 54, 39), (58, 28, 684, 544))
        pygame.draw.rect(surface, self.game.colors["gold"], (58, 28, 684, 544), 4)
        pygame.draw.rect(surface, self.game.colors["cream"], (67, 37, 666, 526), 1)
        self.text(surface, "마을 대장간", (400, 75), 32, self.game.colors["gold"], True)
        self.text(surface, f"보유 금화 {self.game.field.gold} G", (400, 112), 19, self.game.colors["cream"], True)
        weapon = WEAPONS.get(self.game.field.weapon, WEAPONS["rusty_sword"])
        armor = ARMORS.get(self.game.field.armor, ARMORS["traveler_clothes"])
        self.text(surface, f"착용 중: {weapon['name']} · {armor['name']}", (400, 137), 16,
                  self.game.colors["muted"], True)
        for index, (item, rect) in enumerate(zip(SHOP_ITEMS, self._rows())):
            self._frame(surface, rect, self.game.colors["panel"], index == self.selected)
            label, price = self._item_text(item)
            self.text(surface, label, (rect.x + 14, rect.y + 13), 17, self.game.colors["cream"])
            price_image = self.game.font(16).render(price, True, self.game.colors["gold"])
            surface.blit(price_image, price_image.get_rect(midright=(rect.right - 14, rect.centery)))
        self.text(surface, self.message, (400, 486), 16, self.game.colors["cream"], True)
        self.button(surface, pygame.Rect(330, 512, 140, 42), "마을로", False, 18)
        self.text(surface, "↑/↓ 선택 · Enter 구매/착용 · ESC 돌아가기", (400, 562), 13,
                  self.game.colors["muted"], True)

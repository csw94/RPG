"""Logan's stall: weapons, armor, accessories and potions on four tabs.

Stock widens as shrines are cleared. Buying gear equips it at once; gear you already own
can be re-equipped here for free.
"""

import pygame

from gameplay.equipment import SHOP_ITEMS, SHOP_TABS, item_info, shop_stock
from gameplay.world_data import SHRINES
from scenes.base_scene import BaseScene
from utils import ui

TAB_IDS = [tab for tab, _ in SHOP_TABS]
SHOPS = {"logan": ("오크밸리 상점", "로건: 천천히 골라 보게. 제단을 정화할 때마다 새 물건을 들여놓지!"),
         "mira": ("미라의 물약 상점", "미라: 물약은 넉넉히! 해독제도 잊지 마세요.")}


class ShopScene(BaseScene):
    def __init__(self, game, shop="logan"):
        super().__init__(game)
        self.shop = shop
        self.tabs = [tab for tab in TAB_IDS if any(i["kind"] == tab and i.get("shop", "logan") == shop
                                                   for i in SHOP_ITEMS)]
        self.tab = self.tabs[0]
        self.selected = 0
        self.title, self.message = SHOPS[shop]

    # --- stock ------------------------------------------------------------------------
    def cleared(self):
        return sum(1 for key in SHRINES if self.game.field.quest_flags.get(key))

    def items(self):
        return shop_stock(self.cleared(), self.tab, self.shop)

    def locked_count(self):
        return len([i for i in SHOP_ITEMS if i["kind"] == self.tab and i.get("shop", "logan") == self.shop]) \
            - len(self.items())

    # --- layout -----------------------------------------------------------------------
    @staticmethod
    def panel_rect():
        return pygame.Rect(52, 20, 696, 560)

    @staticmethod
    def close_rect():
        return pygame.Rect(330, 506, 140, 40)

    def _tab_rects(self):
        start = 400 - (len(self.tabs) * 144 - 12) // 2
        return [pygame.Rect(start + index * 144, 156, 132, 34) for index in range(len(self.tabs))]

    def _rows(self):
        return [pygame.Rect(118, 200 + index * 44, 564, 38) for index in range(len(self.items()))]

    # --- input ------------------------------------------------------------------------
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._close()
                elif event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
                    step = -1 if event.key in (pygame.K_LEFT, pygame.K_a) else 1
                    self._switch_tab(self.tabs[(self.tabs.index(self.tab) + step) % len(self.tabs)])
                elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s) and self.items():
                    step = -1 if event.key in (pygame.K_UP, pygame.K_w) else 1
                    self.selected = (self.selected + step) % len(self.items())
                    self.sfx("cursor")
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._purchase()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for tab, rect in zip(self.tabs, self._tab_rects()):
                    if rect.collidepoint(event.pos):
                        self._switch_tab(tab)
                for index, rect in enumerate(self._rows()):
                    if rect.collidepoint(event.pos):
                        self.selected = index
                        self._purchase()
                        break
                if self.close_rect().collidepoint(event.pos):
                    self._close()

    def _switch_tab(self, tab):
        if tab != self.tab:
            self.tab, self.selected = tab, 0
            self.sfx("cursor")

    def _close(self):
        self.game.save_game()
        self.game.scene_name = self.game.field.world
        self.game.scene = self.game.field

    def _purchase(self):
        items = self.items()
        if not items:
            return
        item = items[min(self.selected, len(items) - 1)]
        info = item_info(item)
        player = self.game.field
        if item["kind"] == "potion":
            cap = player.item_cap(item["id"])
            if player.item_count(item["id"]) >= cap:
                self.message = f"{info['name']}은(는) {cap}개까지 가질 수 있습니다."
                return
            if player.gold < info["price"]:
                self.message = "골드가 부족합니다."
                return
            player.gold -= info["price"]
            player.add_item(item["id"])
            self.sfx("coin")
            self.message = f"{info['name']}을(를) 가방에 넣었습니다."
            self.game.save_game()
            return

        kind = item["kind"]
        owned = {"weapon": player.owned_weapons, "armor": player.owned_armors,
                 "accessory": player.owned_accessories}[kind]
        if getattr(player, kind) == item["id"]:
            self.message = f"{info['name']}은(는) 이미 장착 중입니다."
            return
        if item["id"] not in owned:
            if player.gold < info["price"]:
                self.message = "골드가 부족합니다. 필드에서 모험하며 벌어 보세요."
                return
            player.gold -= info["price"]
            owned.append(item["id"])
        player.equip(kind, item["id"])
        self.sfx("coin")
        self.message = f"{info['name']}을(를) 장착했습니다."
        self.game.save_game()

    def update(self, dt):
        pass

    # --- drawing ----------------------------------------------------------------------
    @staticmethod
    def _detail(item, info):
        if item["kind"] == "weapon":
            return f"ATK +{info['attack']}"
        if item["kind"] == "armor":
            return f"DEF +{info['defense']}"
        return info["desc"]

    def _price_text(self, item, info):
        player = self.game.field
        if item["kind"] == "potion":
            return f"보유 {player.item_count(item['id'])}/{player.item_cap(item['id'])} · {info['price']} G"
        owned = {"weapon": player.owned_weapons, "armor": player.owned_armors,
                 "accessory": player.owned_accessories}[item["kind"]]
        if getattr(player, item["kind"]) == item["id"]:
            return "장착 중"
        return "보유 · 장착" if item["id"] in owned else f"{info['price']} G"

    def draw(self, surface):
        colors, player = self.game.colors, self.game.field
        ui.plank_strip(surface, (0, 0, surface.get_width(), surface.get_height()))
        ui.frame(surface, self.panel_rect(), "walnut", border=8)
        self.text(surface, self.title, (400, 62), 30, colors["gold"], True)
        gold = self.text(surface, f"보유 골드 {player.gold} G", (410, 98), 19, colors["cream"], True)
        ui.coin(surface, (gold.left - 14, gold.centery))
        accessory = player.accessory_info.get("name", "장신구 없음")
        self.text(surface, f"장착 중: {player.weapon_info['name']} · {player.armor_info['name']} · {accessory}",
                  (400, 126), 15, colors["muted"], True)

        labels = dict(SHOP_TABS)
        for tab, rect in zip(self.tabs, self._tab_rects()):
            self.button(surface, rect, labels[tab], tab == self.tab, 17)

        items = self.items()
        for index, (item, rect) in enumerate(zip(items, self._rows())):
            info = item_info(item)
            ui.frame_around(surface, rect, "walnut", index == self.selected)
            self.text(surface, f"{info['name']}   ·   {self._detail(item, info)}", (rect.x + 14, rect.y + 9), 16,
                      colors["cream"])
            price = self.game.font(15).render(self._price_text(item, info), True, colors["gold"])
            surface.blit(price, price.get_rect(midright=(rect.right - 14, rect.centery)))
        if items:
            chosen = item_info(items[min(self.selected, len(items) - 1)])
            self.text(surface, chosen["desc"], (400, 434), 15, colors["cream"], True)
        if self.locked_count():
            self.text(surface, f"제단을 더 정화하면 새 물건 {self.locked_count()}개가 들어옵니다.", (400, 456), 14,
                      colors["muted"], True)
        self.text(surface, self.message, (400, 482), 16, colors["gold"], True)
        self.button(surface, self.close_rect(), "마을로", False, 18)
        self.text(surface, "←→ 탭 · ↑↓ 선택 · Enter 구매/장착 · ESC 돌아가기", (400, 558), 13, colors["muted"], True)

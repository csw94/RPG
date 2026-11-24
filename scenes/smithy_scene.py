"""Bron's smithy: hammer the equipped weapon (+3 ATK) or armour (+2 DEF) up to +3 for gold."""

import pygame

from scenes.base_scene import BaseScene
from utils import ui

MAX_UPGRADE = 3
STEP_BONUS = {"weapon": 3, "armor": 2}
BASE_COST = {"weapon": 80, "armor": 60}


def upgrade_cost(kind, level):
    """Gold to go from ``level`` to ``level + 1``."""
    return BASE_COST[kind] * (level + 1)


class SmithyScene(BaseScene):
    ROWS = ("weapon", "armor")

    def __init__(self, game, back):
        super().__init__(game)
        self.back = back
        self.back_name = game.scene_name
        self.row = 0
        self.message = "브론: 어느 걸 두드려 줄까? 쇠는 뜨거울 때 쳐야지!"

    @property
    def field(self):
        return self.game.field

    def _item(self, kind):
        field = self.field
        item_id = field.weapon if kind == "weapon" else field.armor
        info = field.weapon_info if kind == "weapon" else field.armor_info
        return item_id, info, field.upgrades.get(item_id, 0)

    # --- input ------------------------------------------------------------------------
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    self._close()
                elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                    self.row = 1 - self.row
                    self.sfx("cursor")
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                    self._upgrade(self.ROWS[self.row])
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for index, rect in enumerate(self._row_rects()):
                    if rect.collidepoint(event.pos):
                        self.row = index
                        self._upgrade(self.ROWS[index])
                if self.close_rect().collidepoint(event.pos):
                    self._close()

    def _upgrade(self, kind):
        field = self.field
        item_id, info, level = self._item(kind)
        if level >= MAX_UPGRADE:
            self.message = f"브론: {info['name']}은(는) 이미 최고로 단련됐네."
            return
        cost = upgrade_cost(kind, level)
        if field.gold < cost:
            self.message = f"브론: 금화가 {cost - field.gold}G 모자라는군."
            return
        field.gold -= cost
        field.upgrades[item_id] = level + 1
        self.sfx("hit")
        self.message = f"땅! 땅! {info['name']} +{level + 1} 완성!"
        self.game.save_game()

    def _close(self):
        self.sfx("cursor")
        self.game.scene, self.game.scene_name = self.back, self.back_name

    def update(self, dt):
        pass

    # --- drawing ----------------------------------------------------------------------
    @staticmethod
    def _row_rects():
        return [pygame.Rect(130, 200 + index * 96, 540, 80) for index in range(2)]

    @staticmethod
    def close_rect():
        return pygame.Rect(330, 470, 140, 40)

    def draw(self, surface):
        colors, field = self.game.colors, self.field
        ui.plank_strip(surface, (0, 0, surface.get_width(), surface.get_height()))
        ui.frame(surface, pygame.Rect(90, 40, 620, 520), "walnut", border=8)
        self.text(surface, "브론의 대장간", (400, 82), 30, colors["gold"], True)
        gold = self.text(surface, f"보유 골드 {field.gold} G", (410, 124), 18, colors["cream"], True)
        ui.coin(surface, (gold.left - 14, gold.centery))
        for index, (kind, rect) in enumerate(zip(self.ROWS, self._row_rects())):
            item_id, info, level = self._item(kind)
            body = ui.frame(surface, rect, "parchment", index == self.row)
            label = "무기" if kind == "weapon" else "방어구"
            stat = "공격력" if kind == "weapon" else "방어력"
            title = f"{label}  {info['name']}" + (f" +{level}" if level else "")
            surface.blit(self.game.font(19).render(title, True, ui.INK), (body.x + 14, body.y + 8))
            bonus = STEP_BONUS[kind] * level
            detail = f"강화 보너스 {stat} +{bonus}"
            if level < MAX_UPGRADE:
                detail += f"   →   +{level + 1}: {stat} +{bonus + STEP_BONUS[kind]}  ·  {upgrade_cost(kind, level)} G"
            else:
                detail += "   ·   최고 단계"
            surface.blit(self.game.font(15).render(detail, True, ui.INK_SOFT), (body.x + 14, body.y + 40))
            for step in range(MAX_UPGRADE):
                pip = pygame.Rect(body.right - 26 - (MAX_UPGRADE - step - 1) * 20, body.y + 10, 14, 14)
                pygame.draw.rect(surface, ui.OUTLINE, pip)
                pygame.draw.rect(surface, (214, 172, 88) if step < level else (150, 130, 110), pip.inflate(-2, -2))
        self.text(surface, self.message, (400, 420), 16, colors["gold"], True)
        self.button(surface, self.close_rect(), "돌아가기", False, 18)
        self.text(surface, "↑↓ 선택 · Enter 강화 · ESC 돌아가기", (400, 530), 13, colors["muted"], True)

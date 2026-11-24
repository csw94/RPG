"""Status screen (I / Tab): hero stats, gear, items, skills and quest progress."""

import pygame

from gameplay.combat import SKILLS, xp_to_next
from gameplay.equipment import POTION_CAP
from scenes.base_scene import BaseScene
from utils import ui
from utils.pixel_art import hero_sprite

QUEST_NAMES = {"sq_moon_herb": "달빛 약초", "sq_old_sword": "노기사의 검", "sq_goblin_hunt": "고블린 소탕"}
SEALS = (("shrine_wind", "바람의 제단"), ("shrine_earth", "대지의 폐광"), ("shrine_fire", "불꽃의 신전"))
ITEM_NAMES = {"broken_old_sword": "부러진 옛 검", "knights_crest": "기사단 휘장"}
TOGGLE_KEYS = (pygame.K_i, pygame.K_TAB)


class StatusScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.field = game.field

    # --- content ----------------------------------------------------------------------
    def skill_rows(self):
        return [{**skill, "learned": skill["level"] <= self.field.level} for skill in SKILLS.values()]

    def quest_rows(self):
        rows = []
        for quest_id, name in QUEST_NAMES.items():
            quest = self.field.sub_quests[quest_id]
            status = quest["status"]
            if status == "COMPLETED":
                text = "완료"
            elif status == "NOT_STARTED":
                text = "미수락"
            elif quest["progress"] >= quest["target"]:
                text = f"{quest['progress']}/{quest['target']} · 보고하기"
            else:
                text = f"진행 중 {quest['progress']}/{quest['target']}"
            rows.append((name, text))
        return rows

    def seal_rows(self):
        return [(name, bool(self.field.quest_flags.get(flag))) for flag, name in SEALS]

    # --- input ------------------------------------------------------------------------
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (*TOGGLE_KEYS, pygame.K_ESCAPE):
                self._close()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.close_rect().collidepoint(event.pos):
                    self._close()

    def _close(self):
        self.game.scene_name = self.field.world
        self.game.scene = self.field

    def update(self, dt):
        pass

    @staticmethod
    def close_rect():
        return pygame.Rect(330, 526, 140, 34)

    # --- drawing ----------------------------------------------------------------------
    def draw(self, surface):
        f, colors = self.field, self.game.colors
        ui.plank_strip(surface, (0, 0, surface.get_width(), surface.get_height()))
        ui.frame(surface, pygame.Rect(20, 14, 760, 572), "walnut", border=8)
        self.text(surface, "수호자의 기록", (400, 44), 28, colors["gold"], True)

        # Left: portrait and core stats.
        card = ui.frame(surface, pygame.Rect(40, 72, 230, 444), "parchment")
        hero = hero_sprite(f.weapon, f.armor, (96, 144))
        surface.blit(hero, (card.centerx - 48, card.y + 10))
        y = card.y + 162
        self._ink(surface, f"Lv.{f.level}", (card.x + 12, y), 20)
        need = xp_to_next(f.level)
        self._ink(surface, f"EXP {f.xp}/{need}", (card.right - 12, y + 3), 14, right=True)
        ui.bar(surface, pygame.Rect(card.x + 12, y + 26, card.width - 24, 8), f.xp, need, (214, 172, 88))
        y += 44
        for label, value, maximum, color in (("HP", f.hp, f.max_hp, (196, 72, 60)),
                                             ("MP", f.mp, f.max_mp, (70, 120, 190))):
            self._ink(surface, label, (card.x + 12, y), 15)
            self._ink(surface, f"{value}/{maximum}", (card.right - 12, y), 15, right=True)
            ui.bar(surface, pygame.Rect(card.x + 12, y + 20, card.width - 24, 10), value, maximum, color)
            y += 38
        weapon, armor, accessory = f.weapon_info, f.armor_info, f.accessory_info
        attack_detail = f"기본 {f.atk} + 무기 {weapon['attack']}"
        if accessory.get("attack"):
            attack_detail += f" + 장신구 {accessory['attack']}"
        for label, total, detail in (("공격력", f.attack_power, attack_detail),
                                     ("방어력", f.defense_power, f"기본 {f.defense} + 방어구 {armor['defense']}")):
            self._ink(surface, label, (card.x + 12, y), 15)
            self._ink(surface, str(total), (card.right - 12, y), 17, right=True)
            self._ink(surface, detail, (card.x + 12, y + 19), 12, soft=True)
            y += 42
        if f.evasion:
            self._ink(surface, f"회피 {f.evasion}%", (card.x + 12, y), 13, soft=True)

        # Right top: gear and items.
        gear = ui.frame(surface, pygame.Rect(286, 72, 474, 124), "parchment")
        self._ink(surface, "장비 · 소지품", (gear.x + 12, gear.y + 6), 16)
        self._ink(surface, f"무기  {weapon['name']} ({weapon['desc'] if weapon.get('element') else '공격 +' + str(weapon['attack'])})",
                  (gear.x + 12, gear.y + 28), 13)
        self._ink(surface, f"방어구  {armor['name']} (방어 +{armor['defense']})", (gear.x + 12, gear.y + 45), 13)
        self._ink(surface, "장신구  " + (f"{accessory['name']} ({accessory['desc']})" if accessory else "없음"),
                  (gear.x + 12, gear.y + 62), 13, soft=not accessory)
        ui.coin(surface, (gear.right - 90, gear.y + 15))
        self._ink(surface, f"{f.gold} G", (gear.right - 12, gear.y + 7), 16, right=True)
        self._ink(surface, f"회복약(소) {f.potions}/{POTION_CAP}   고급 회복약 {f.high_potions}/{POTION_CAP}",
                  (gear.x + 12, gear.y + 80), 13)
        items = [ITEM_NAMES.get(item, item) for item in sorted(f.quest_items)]
        self._ink(surface, "중요 물품  " + (", ".join(items) if items else "없음"), (gear.x + 12, gear.y + 97),
                  13, soft=not items)

        # Right middle: skills.
        skills = ui.frame(surface, pygame.Rect(286, 204, 474, 146), "parchment")
        self._ink(surface, "기술", (skills.x + 12, skills.y + 6), 16)
        for index, skill in enumerate(self.skill_rows()):
            col, row = index % 2, index // 2
            x, y = skills.x + 12 + col * 230, skills.y + 28 + row * 38
            if skill["learned"]:
                self._ink(surface, f"{skill['name']}  {skill['mp']}MP", (x, y), 14)
                self._ink(surface, skill["desc"], (x, y + 18), 12, soft=True)
            else:
                self._ink(surface, f"??? (Lv.{skill['level']}에 습득)", (x, y), 14, soft=True)

        # Right bottom: seals and side quests.
        quests = ui.frame(surface, pygame.Rect(286, 358, 474, 158), "parchment")
        self._ink(surface, "제단의 인장", (quests.x + 12, quests.y + 6), 16)
        for index, (name, done) in enumerate(self.seal_rows()):
            x = quests.x + 12 + index * 152
            box = pygame.Rect(x, quests.y + 32, 14, 14)
            pygame.draw.rect(surface, ui.INK_SOFT, box, 2)
            if done:
                pygame.draw.rect(surface, (214, 172, 88), box.inflate(-6, -6))
            self._ink(surface, name, (x + 20, quests.y + 30), 14, soft=not done)
        self._ink(surface, "마을 사람들의 부탁", (quests.x + 12, quests.y + 58), 16)
        for index, (name, text) in enumerate(self.quest_rows()):
            y = quests.y + 82 + index * 18
            self._ink(surface, name, (quests.x + 12, y), 14)
            self._ink(surface, text, (quests.right - 12, y), 14, right=True, soft=text == "미수락")

        self.button(surface, self.close_rect(), "닫기", False, 18)
        self.text(surface, "I / Tab / ESC 닫기", (400, 570), 13, colors["muted"], True)

    def _ink(self, surface, value, pos, size, right=False, soft=False):
        image = self.game.font(size).render(str(value), True, ui.INK_SOFT if soft else ui.INK)
        rect = image.get_rect(topright=pos) if right else image.get_rect(topleft=pos)
        surface.blit(image, rect)
        return rect

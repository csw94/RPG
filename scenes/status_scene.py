"""Status screen (I / Tab): hero stats, gear, items, skills and quest progress."""

import pygame

from gameplay.combat import SKILLS, xp_to_next
from gameplay.equipment import POTION_CAP
from gameplay.objectives import next_objective
from scenes.base_scene import BaseScene
from utils import ui
from utils.pixel_art import hero_sprite

QUEST_NAMES = {"sq_moon_herb": "달빛 약초", "sq_old_sword": "노기사의 검", "sq_goblin_hunt": "고블린 소탕",
               "sq_wolf_hunt": "숲의 사냥꾼", "sq_magma_ore": "용암석 수집", "sq_bat_hunt": "동굴 소탕",
               "sq_frost_hunt": "고원의 정령"}
SEALS = (("shrine_wind", "바람의 제단"), ("shrine_earth", "대지의 폐광"), ("shrine_fire", "불꽃의 신전"),
         ("shrine_ice", "얼음 제단"))
ITEM_NAMES = {"broken_old_sword": "부러진 옛 검", "knights_crest": "기사단 휘장"}
TOGGLE_KEYS = (pygame.K_i, pygame.K_TAB)
PAGES = (("record", "기록"), ("map", "지도"))
HERO_MARK = (255, 200, 40)
MAP_COLORS = {"ground": (118, 150, 92), "path": (204, 176, 124), "water": (88, 150, 200), "lava": (224, 112, 52), "ice": (150, 196, 230), "snow": (226, 232, 240),
              "tree": (58, 104, 64), "rock": (120, 116, 112), "wall": (62, 52, 58), "floor": (150, 138, 128)}
MARKER_STYLE = {  # colour, label for the legend
    "chest": ((236, 196, 84), "상자"), "herb": ((150, 230, 120), "약초"), "town": ((250, 250, 240), "마을"),
    "dungeon": ((170, 120, 255), "던전"), "gate": ((250, 250, 240), "출입구"), "door": ((214, 150, 96), "문"),
    "exit": ((250, 250, 240), "나가는 길"), "stairs": ((120, 200, 255), "계단"), "boss": ((240, 70, 70), "보스"),
    "npc": ((255, 170, 200), "주민"), "shop": ((236, 196, 84), "상점"), "fountain": ((120, 200, 255), "분수"),
    "altar": ((170, 120, 255), "제단"), "bed": ((150, 230, 120), "침대"),
}


class StatusScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.field = game.field
        self.page = "record"
        self.clock = 0.0

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
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                self.page = "map" if self.page == "record" else "record"
                self.sfx("cursor")
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.close_rect().collidepoint(event.pos):
                    self._close()

    def _close(self):
        self.game.scene_name = self.field.world
        self.game.scene = self.field

    def update(self, dt):
        self.clock += dt

    @staticmethod
    def close_rect():
        return pygame.Rect(330, 526, 140, 34)

    # --- drawing ----------------------------------------------------------------------
    def draw(self, surface):
        ui.plank_strip(surface, (0, 0, surface.get_width(), surface.get_height()))
        ui.frame(surface, pygame.Rect(20, 14, 760, 572), "walnut", border=8)
        if self.page == "map":
            self._draw_map(surface)
        else:
            self._draw_record(surface)
        for index, (page, label) in enumerate(PAGES):
            self.button(surface, pygame.Rect(600 + index * 82, 28, 74, 30), label, page == self.page, 15)
        self.button(surface, self.close_rect(), "닫기", False, 18)
        self.text(surface, "←→ 기록 / 지도 · I / Tab / ESC 닫기", (400, 570), 13, self.game.colors["muted"], True)

    # --- map page ---------------------------------------------------------------------
    def map_rect(self):
        f = self.field
        cell = max(4, min(720 // f.COLS, 400 // f.ROWS))
        width, height = f.COLS * cell, f.ROWS * cell
        return pygame.Rect(400 - width // 2, 74 + (400 - height) // 2, width, height)

    def _tile_color(self, x, y):
        f = self.field
        indoor = hasattr(f, "floor_tile") or hasattr(f, "ROOM")
        if (x, y) in getattr(f, "lava", ()):
            return MAP_COLORS["lava"]
        if (x, y) in getattr(f, "water", ()):
            return MAP_COLORS["water"]
        if (x, y) in getattr(f, "ice", ()):
            return MAP_COLORS["ice"]
        if (x, y) in getattr(f, "trees", ()):
            return MAP_COLORS["tree"]
        if (x, y) in getattr(f, "rocks", ()):
            return MAP_COLORS["rock"]
        if (x, y) in f.walls:
            return MAP_COLORS["wall"]
        if (x, y) in getattr(f, "path", ()):
            return MAP_COLORS["path"]
        if indoor:
            return MAP_COLORS["floor"]
        return MAP_COLORS["snow"] if getattr(f, "theme", "") == "snow" else MAP_COLORS["ground"]

    def _draw_map(self, surface):
        f, colors = self.field, self.game.colors
        self.text(surface, f"지도 · {f.hud_title()}", (400, 44), 26, colors["gold"], True)
        rect = self.map_rect()
        cell = rect.width // f.COLS
        ui.frame(surface, rect.inflate(16, 16), "walnut")
        for y in range(f.ROWS):
            for x in range(f.COLS):
                surface.fill(self._tile_color(x, y), (rect.x + x * cell, rect.y + y * cell, cell, cell))
        kinds = []
        for kind, (x, y) in f.map_markers():
            color, _label = MARKER_STYLE.get(kind, ((255, 255, 255), kind))
            center = (rect.x + x * cell + cell // 2, rect.y + y * cell + cell // 2)
            radius = max(3, cell // 2)
            pygame.draw.circle(surface, ui.OUTLINE, center, radius + 1)
            pygame.draw.circle(surface, color, center, radius)
            if kind not in kinds:
                kinds.append(kind)
        # The hero blinks so it stands out from the markers.
        px = rect.x + int(f.player["x"] * cell) + cell // 2
        py = rect.y + int(f.player["y"] * cell) + cell // 2
        if int(self.clock * 3) % 2 == 0:
            size = max(4, cell // 2 + 2)
            pygame.draw.circle(surface, ui.OUTLINE, (px, py), size + 3)
            pygame.draw.circle(surface, HERO_MARK, (px, py), size + 2)
            pygame.draw.circle(surface, (255, 255, 255), (px, py), size - 1)
        legend = [("나", HERO_MARK)] + [(MARKER_STYLE[k][1], MARKER_STYLE[k][0]) for k in kinds if k in MARKER_STYLE]
        x = 400 - sum(self.game.font(13).size(label)[0] + 26 for label, _ in legend) // 2
        for label, color in legend:
            pygame.draw.circle(surface, ui.OUTLINE, (x + 6, 490), 6)
            pygame.draw.circle(surface, color, (x + 6, 490), 5)
            image = self.game.font(13).render(label, True, colors["cream"])
            surface.blit(image, (x + 15, 482))
            x += image.get_width() + 26
        self.text(surface, "다음 목표: " + next_objective(f), (400, 514), 15, colors["gold"], True)

    # --- record page ------------------------------------------------------------------
    def _draw_record(self, surface):
        f, colors = self.field, self.game.colors
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
            x = quests.x + 12 + index * 114
            box = pygame.Rect(x, quests.y + 32, 14, 14)
            pygame.draw.rect(surface, ui.INK_SOFT, box, 2)
            if done:
                pygame.draw.rect(surface, (214, 172, 88), box.inflate(-6, -6))
            self._ink(surface, name, (x + 20, quests.y + 31), 13, soft=not done)
        self._ink(surface, "마을 사람들의 부탁", (quests.x + 12, quests.y + 54), 15)
        for index, (name, text) in enumerate(self.quest_rows()):
            col, row = divmod(index, 4)
            x, y = quests.x + 12 + col * 232, quests.y + 76 + row * 17
            self._ink(surface, name, (x, y), 13)
            self._ink(surface, text, (x + 212, y), 13, right=True, soft=text == "미수락")


    def _ink(self, surface, value, pos, size, right=False, soft=False):
        image = self.game.font(size).render(str(value), True, ui.INK_SOFT if soft else ui.INK)
        rect = image.get_rect(topright=pos) if right else image.get_rect(topleft=pos)
        surface.blit(image, rect)
        return rect

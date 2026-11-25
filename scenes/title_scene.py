"""Medieval title menu and three-slot save selector."""

import pygame

from gameplay.difficulty import DIFFICULTIES, DIFFICULTY_ORDER
from gameplay.records import slot_summary
from utils import title_art, ui
from scenes.base_scene import BaseScene
from utils.pixel_art import sprite


class TitleScene(BaseScene):
    SLOT_COUNT = 3
    OPTIONS = ("새 모험 시작", "모험 이어하기", "조작법", "설정", "게임 종료")
    SLOT_LABELS = ("제1 슬롯", "제2 슬롯", "제3 슬롯")

    def __init__(self, game):
        super().__init__(game)
        self.mode = "menu"
        self.selected = 0
        self.slot_action = "new"
        self.confirm_overwrite = False
        self.slot_data = self.game.save_manager.list_saves()
        self.pending_slot = None
        self.difficulty_index = DIFFICULTY_ORDER.index("normal")
        self.notice = ""
        self.clock = 0.0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.mode == "difficulty":
                    self._difficulty_key(event.key)
                elif event.key == pygame.K_ESCAPE:
                    if self.confirm_overwrite:
                        self.confirm_overwrite = False
                        self.notice = "덮어쓰기를 취소했습니다."
                    elif self.mode == "slots":
                        self.mode = "menu"
                        self.notice = ""
                    else:
                        self.game.running = False
                elif self.mode == "menu":
                    self._menu_key(event.key)
                else:
                    self._slot_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.mode == "difficulty":
                    for index, rect in enumerate(self._difficulty_cards()):
                        if rect.collidepoint(event.pos):
                            self.difficulty_index = index
                            self._start_new_game()
                elif self.mode == "menu":
                    for index, rect in enumerate(self._menu_buttons()):
                        if rect.collidepoint(event.pos):
                            self.selected = index
                            self._choose_menu()
                            break
                else:
                    bins = [self.delete_button(index) for index in range(self.SLOT_COUNT)]
                    hit = next((i for i, rect in enumerate(bins) if rect and rect.collidepoint(event.pos)), None)
                    if hit is not None:
                        self.selected = hit
                        self.confirm_overwrite = False
                        self._ask_delete()
                        continue
                    for index, rect in enumerate(self._slot_cards()):
                        if rect.collidepoint(event.pos):
                            if self.selected == index and self.confirm_overwrite:
                                self._choose_slot()
                            else:
                                self.selected = index
                                self.confirm_overwrite = False
                                self._choose_slot()
                            break
                    if pygame.Rect(328, 492, 144, 42).collidepoint(event.pos):
                        self.mode = "menu"
                        self.confirm_overwrite = False
                        self.notice = ""

    def _menu_key(self, key):
        if key in (pygame.K_UP, pygame.K_w):
            self.selected = (self.selected - 1) % len(self.OPTIONS)
            self.sfx("cursor")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.selected = (self.selected + 1) % len(self.OPTIONS)
            self.sfx("cursor")
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.sfx("confirm")
            self._choose_menu()

    def _slot_key(self, key):
        if key in (pygame.K_LEFT, pygame.K_a, pygame.K_UP, pygame.K_w):
            self.selected = (self.selected - 1) % self.SLOT_COUNT
            self.confirm_overwrite = False
            self.sfx("cursor")
        elif key in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN, pygame.K_s):
            self.selected = (self.selected + 1) % self.SLOT_COUNT
            self.confirm_overwrite = False
            self.sfx("cursor")
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.sfx("confirm")
            self._choose_slot()
        elif key == pygame.K_DELETE:
            self.confirm_overwrite = False
            self._ask_delete()

    def delete_button(self, index):
        """The bin button in a slot card's corner, or None for an empty slot."""
        if index + 1 not in self.slot_data:
            return None
        card = self._slot_cards()[index]
        return pygame.Rect(card.right - 34, card.top + 10, 24, 24)

    def _ask_delete(self):
        slot = self.selected + 1
        if slot not in self.slot_data:
            self.notice = "이 슬롯에는 지울 기록이 없습니다."
            return
        from scenes.confirm_scene import ConfirmScene
        label = self.SLOT_LABELS[self.selected]
        self.sfx("cursor")
        self.game.scene = ConfirmScene(self.game, self, f"{label} 기록을 삭제할까요?",
                                       ["삭제한 모험 기록은 되돌릴 수 없습니다.",
                                        "레벨, 장비, 진행 상황이 모두 사라집니다."],
                                       lambda: self._delete_slot(slot))

    def _delete_slot(self, slot):
        self.game.save_manager.delete(slot)
        if self.game.active_slot == slot:
            # The adventure left open behind the title screen no longer has a save to go back to.
            self.game.active_slot, self.game.field = None, None
        self.slot_data = self.game.save_manager.list_saves()
        self.notice = f"{self.SLOT_LABELS[slot - 1]}의 기록을 삭제했습니다."

    def _menu_buttons(self):
        return [pygame.Rect(285, 286 + i * 46, 230, 38) for i in range(len(self.OPTIONS))]

    def _slot_cards(self):
        return [pygame.Rect(88 + i * 210, 244, 194, 214) for i in range(3)]

    def _choose_menu(self):
        choice = self.OPTIONS[self.selected]
        if choice == "게임 종료":
            self.game.running = False
            return
        if choice == "조작법":
            from scenes.help_scene import HelpScene
            self.game.scene, self.game.scene_name = HelpScene(self.game, self), "help"
            return
        if choice == "설정":
            self.game.open_settings()
            return
        self.slot_action = "new" if choice == "새 모험 시작" else "load"
        self.mode = "slots"
        self.selected = 0
        self.confirm_overwrite = False
        self.notice = "새 모험을 시작할 슬롯을 고르세요." if self.slot_action == "new" else "이어갈 저장 슬롯을 고르세요."

    def _choose_slot(self):
        slot = self.selected + 1
        occupied = slot in self.slot_data
        if self.slot_action == "load":
            if occupied:
                self.game.load_game(slot)
            else:
                self.notice = "이 슬롯에는 저장된 모험이 없습니다."
            return
        if occupied and not self.confirm_overwrite:
            self.confirm_overwrite = True
            self.notice = f"{self.SLOT_LABELS[self.selected]}의 기록을 덮어쓰려면 Enter를 한 번 더 누르세요."
            return
        self.pending_slot = slot
        self.mode = "difficulty"
        self.difficulty_index = DIFFICULTY_ORDER.index("normal")
        self.notice = ""

    def _difficulty_key(self, key):
        if key == pygame.K_ESCAPE:
            self.mode = "slots"
            self.confirm_overwrite = False
        elif key in (pygame.K_LEFT, pygame.K_a, pygame.K_UP, pygame.K_w):
            self.difficulty_index = (self.difficulty_index - 1) % len(DIFFICULTY_ORDER)
            self.sfx("cursor")
        elif key in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN, pygame.K_s):
            self.difficulty_index = (self.difficulty_index + 1) % len(DIFFICULTY_ORDER)
            self.sfx("cursor")
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.sfx("confirm")
            self._start_new_game()

    def _start_new_game(self):
        self.game.new_game(self.pending_slot, DIFFICULTY_ORDER[self.difficulty_index])

    @staticmethod
    def _difficulty_cards():
        return [pygame.Rect(88 + i * 210, 220, 194, 220) for i in range(len(DIFFICULTY_ORDER))]

    def _draw_difficulty(self, surface):
        colors = self.game.colors
        self._soft_label(surface, "난이도 선택", (400, 85), 34, colors["gold"])
        self.text(surface, "모험 중에도 설정(O)에서 바꿀 수 있습니다", (400, 130), 17, colors["cream"], True)
        for index, (key, rect) in enumerate(zip(DIFFICULTY_ORDER, self._difficulty_cards())):
            info = DIFFICULTIES[key]
            self._frame(surface, rect, colors["panel"], index == self.difficulty_index)
            self.text(surface, info["name"], (rect.centerx, rect.top + 40), 26,
                      colors["gold"] if index == self.difficulty_index else colors["cream"], True)
            words, lines, line = info["desc"].replace(". ", ".|").split("|"), [], ""
            for part in " ".join(words).split(" "):
                candidate = f"{line} {part}".strip()
                if self.game.font(14).size(candidate)[0] > rect.width - 24 and line:
                    lines.append(line)
                    line = part
                else:
                    line = candidate
            lines.append(line)
            for row, text in enumerate(lines[:6]):
                self.text(surface, text, (rect.centerx, rect.top + 92 + row * 22), 14, colors["muted"], True)
        self.text(surface, "←→ 선택 · Enter 시작 · ESC 뒤로", (400, 564), 15, colors["muted"], True)

    def update(self, dt):
        self.clock += dt

    def _frame(self, surface, rect, fill=None, active=False):
        ui.frame_around(surface, rect, "walnut", active)

    def _draw_background(self, surface):
        """Oak Valley at night (cached), animated stars and fireflies, and a wooden footer."""
        surface.blit(title_art.backdrop(), (0, 0))
        title_art.draw_overlay(surface, self.clock)
        if self.mode == "slots":
            veil = pygame.Surface((800, 600), pygame.SRCALPHA)
            veil.fill((12, 10, 28, 110))
            surface.blit(veil, (0, 0))
        ui.plank_strip(surface, (0, 548, 800, 52))

    def _soft_label(self, surface, value, center, size, color):
        """Text on a translucent dark pill so it stays readable over the meadow."""
        width = self.game.font(size).size(str(value))[0] + 28
        pill = pygame.Surface((width, size + 14), pygame.SRCALPHA)
        pygame.draw.rect(pill, (16, 12, 24, 150), pill.get_rect(), border_radius=8)
        surface.blit(pill, pill.get_rect(center=center))
        self.text(surface, value, center, size, color, True)

    def _draw_menu(self, surface):
        header = pygame.Rect(132, 38, 536, 126)
        self._frame(surface, header, self.game.colors["panel"], True)
        self.text(surface, "별빛 결계의 수호자", (400, 84), 40, self.game.colors["gold"], True)
        self.text(surface, "CHRONICLES OF PIXEL", (400, 129), 17, self.game.colors["cream"], True)
        shadow = pygame.Surface((60, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (16, 24, 20, 110), shadow.get_rect())
        surface.blit(shadow, (370, 262))
        surface.blit(sprite("player", (64, 96)), (368, 174))
        for index, (label, rect) in enumerate(zip(self.OPTIONS, self._menu_buttons())):
            self.button(surface, rect, label, index == self.selected, 20)
        self.text(surface, "방향키로 선택 · Enter로 결정", (400, 568), 16, self.game.colors["muted"], True)
        if self.notice:
            self._soft_label(surface, self.notice, (400, 528), 16, self.game.colors["gold"])

    def _draw_slots(self, surface):
        self._soft_label(surface, "모험 기록", (400, 85), 34, self.game.colors["gold"])
        self.text(surface, "저장할 슬롯을 선택하세요", (400, 130), 19, self.game.colors["cream"], True)
        for index, (rect, label) in enumerate(zip(self._slot_cards(), self.SLOT_LABELS)):
            state = self.slot_data.get(index + 1)
            self._frame(surface, rect, self.game.colors["panel"], index == self.selected)
            self._draw_crest(surface, (rect.centerx, rect.top + 49), small=True)
            self.text(surface, label, (rect.centerx, rect.top + 92), 20, self.game.colors["gold"], True)
            if state:
                first, second, third = slot_summary(state)
                self.text(surface, first, (rect.centerx, rect.top + 126), 17, self.game.colors["cream"], True)
                self.text(surface, second, (rect.centerx, rect.top + 153), 15, self.game.colors["cream"], True)
                ending = third.startswith("★")
                self.text(surface, third, (rect.centerx, rect.top + 178), 15,
                          self.game.colors["gold"] if ending else self.game.colors["muted"], True)
            else:
                self.text(surface, "빈 슬롯", (rect.centerx, rect.top + 149), 18, self.game.colors["muted"], True)
            bin_rect = self.delete_button(index)
            if bin_rect:
                self._draw_bin(surface, bin_rect, index == self.selected)
        self.button(surface, pygame.Rect(328, 492, 144, 42), "뒤로", False, 18)
        action_text = "선택한 슬롯에 새 모험을 기록합니다." if self.slot_action == "new" else "선택한 저장 기록을 불러옵니다."
        help_text = f"{action_text}  ·  Enter 선택  ·  Del 기록 삭제  ·  ESC 뒤로"
        self.text(surface, help_text, (400, 564), 15, self.game.colors["muted"], True)
        if self.notice:
            self.text(surface, self.notice, (400, 190), 16, self.game.colors["gold"], True)

    def _draw_bin(self, surface, rect, active):
        """A small rubbish-bin button; it turns red on the selected card."""
        pygame.draw.rect(surface, (30, 22, 20), rect.inflate(4, 4), border_radius=6)
        pygame.draw.rect(surface, (150, 58, 46) if active else (92, 70, 54), rect, border_radius=5)
        ink = (246, 230, 200)
        cx = rect.centerx
        pygame.draw.rect(surface, ink, (cx - 3, rect.y + 4, 6, 2))            # handle
        pygame.draw.rect(surface, ink, (rect.x + 5, rect.y + 6, rect.width - 10, 2))  # lid
        body = pygame.Rect(rect.x + 7, rect.y + 9, rect.width - 14, rect.height - 13)
        pygame.draw.rect(surface, ink, body, 2)
        for x in (cx - 2, cx + 1):
            pygame.draw.line(surface, ink, (x, body.y + 3), (x, body.bottom - 3), 1)

    def _draw_crest(self, surface, center, small=False):
        scale = 2 if small else 3
        x, y = center
        points = [(x, y - 12 * scale), (x + 9 * scale, y - 8 * scale),
                  (x + 8 * scale, y + 4 * scale), (x, y + 12 * scale),
                  (x - 8 * scale, y + 4 * scale), (x - 9 * scale, y - 8 * scale)]
        pygame.draw.polygon(surface, (37, 66, 54), points)
        pygame.draw.polygon(surface, self.game.colors["gold"], points, max(2, scale))
        pygame.draw.rect(surface, self.game.colors["cream"], (x - scale, y - 5 * scale, scale * 2, scale * 7))
        pygame.draw.rect(surface, self.game.colors["gold"], (x - 4 * scale, y - scale, scale * 8, scale * 2))

    def draw(self, surface):
        self._draw_background(surface)
        if self.mode == "menu":
            self._draw_menu(surface)
        elif self.mode == "difficulty":
            self._draw_difficulty(surface)
        else:
            self._draw_slots(surface)

"""Medieval title menu and three-slot save selector."""

import pygame

from utils import title_art, ui
from scenes.base_scene import BaseScene
from utils.pixel_art import sprite


class TitleScene(BaseScene):
    SLOT_COUNT = 3
    OPTIONS = ("새 모험 시작", "모험 이어하기", "조작법", "게임 종료")
    SLOT_LABELS = ("제1 슬롯", "제2 슬롯", "제3 슬롯")

    def __init__(self, game):
        super().__init__(game)
        self.mode = "menu"
        self.selected = 0
        self.slot_action = "new"
        self.confirm_overwrite = False
        self.slot_data = self.game.save_manager.list_saves()
        self.notice = ""
        self.clock = 0.0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
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
                if self.mode == "menu":
                    for index, rect in enumerate(self._menu_buttons()):
                        if rect.collidepoint(event.pos):
                            self.selected = index
                            self._choose_menu()
                            break
                else:
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
        self.game.new_game(slot)

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
                self.text(surface, f"레벨 {state.get('level', 1)}", (rect.centerx, rect.top + 126), 18,
                          self.game.colors["cream"], True)
                self.text(surface, f"HP {state.get('hp', 0)}/{state.get('max_hp', 0)}", (rect.centerx, rect.top + 153), 16,
                          self.game.colors["cream"], True)
                self.text(surface, f"금화 {state.get('gold', 0)} · 포션 {state.get('potions', 0)}", (rect.centerx, rect.top + 178), 15,
                          self.game.colors["muted"], True)
            else:
                self.text(surface, "빈 슬롯", (rect.centerx, rect.top + 149), 18, self.game.colors["muted"], True)
        self.button(surface, pygame.Rect(328, 492, 144, 42), "뒤로", False, 18)
        action_text = "선택한 슬롯에 새 모험을 기록합니다." if self.slot_action == "new" else "선택한 저장 기록을 불러옵니다."
        help_text = f"{action_text}  ·  방향키/Enter 선택  ·  ESC 뒤로"
        self.text(surface, help_text, (400, 564), 15, self.game.colors["muted"], True)
        if self.notice:
            self.text(surface, self.notice, (400, 190), 16, self.game.colors["gold"], True)

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
        else:
            self._draw_slots(surface)

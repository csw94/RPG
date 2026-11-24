"""Controls and tips, opened from the title menu (and from the settings screen)."""

import pygame

from scenes.base_scene import BaseScene
from utils import ui

CONTROLS = (
    ("방향키 / WASD", "이동, 메뉴 고르기"),
    ("스페이스바", "대화·조사·상자·문과 계단, 대화 넘기기"),
    ("I / Tab", "상태 화면(능력치·장비·기술·부탁)"),
    ("O", "설정(음량·화면 크기)"),
    ("F5 / 저장 버튼", "지금 상태 저장"),
    ("M", "소리 켜기 / 끄기"),
    ("ESC", "저장하고 타이틀로, 메뉴에서는 뒤로"),
    ("Enter / 스페이스", "전투 행동 결정, 연출 빨리 보기"),
)

TIPS = (
    "마르타 오두막·가렌 거처의 침대에서 쉬면 HP·MP가 모두 회복됩니다.",
    "약점 속성 기술은 1.5배 피해. 적의 저항 속성은 절반만 들어갑니다.",
    "전투에서 이기면 MP가 2 회복되고, 지면 바로 다시 도전할 수 있습니다.",
)


class HelpScene(BaseScene):
    def __init__(self, game, back):
        super().__init__(game)
        self.back = back
        self.back_name = game.scene_name

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN,
                                                               pygame.K_SPACE, pygame.K_BACKSPACE):
                self._close()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and self.close_rect().collidepoint(event.pos):
                self._close()

    def _close(self):
        self.sfx("cursor")
        self.game.scene, self.game.scene_name = self.back, self.back_name

    def update(self, dt):
        if hasattr(self.back, "clock"):
            self.back.clock += dt  # keep the title's stars twinkling underneath

    @staticmethod
    def close_rect():
        return pygame.Rect(330, 530, 140, 36)

    def draw(self, surface):
        colors = self.game.colors
        ui.plank_strip(surface, (0, 0, surface.get_width(), surface.get_height()))
        ui.frame(surface, pygame.Rect(40, 20, 720, 562), "walnut", border=8)
        self.text(surface, "조작법", (400, 52), 30, colors["gold"], True)
        card = ui.frame(surface, pygame.Rect(70, 84, 660, 300), "parchment")
        for index, (keys, action) in enumerate(CONTROLS):
            y = card.y + 14 + index * 35
            pill = pygame.Rect(card.x + 14, y - 3, 190, 28)
            pygame.draw.rect(surface, ui.WOOD_DARK, pill, border_radius=6)
            label = self.game.font(16).render(keys, True, ui.PARCHMENT)
            surface.blit(label, label.get_rect(center=pill.center))
            surface.blit(self.game.font(16).render(action, True, ui.INK), (pill.right + 18, y + 1))
        tips = ui.frame(surface, pygame.Rect(70, 396, 660, 120), "parchment")
        surface.blit(self.game.font(17).render("모험 팁", True, ui.INK), (tips.x + 14, tips.y + 10))
        for index, tip in enumerate(TIPS):
            surface.blit(self.game.font(14).render("· " + tip, True, ui.INK_SOFT),
                         (tips.x + 14, tips.y + 38 + index * 22))
        self.button(surface, self.close_rect(), "돌아가기", False, 18)

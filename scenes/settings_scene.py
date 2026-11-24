"""Settings (title menu or O in the field): music/effect volume and window size."""

import pygame

from gameplay.difficulty import DIFFICULTIES, DIFFICULTY_ORDER
from scenes.base_scene import BaseScene
from utils import ui

DISPLAY_LABELS = {"1x": "기본 (800×600)", "1.5x": "1.5배 (1200×900)", "2x": "2배 (1600×1200)",
                  "fullscreen": "전체 화면"}
ROWS = ("music", "sfx", "display", "help", "close")
ROW_LABELS = {"music": "배경음악", "sfx": "효과음", "display": "화면 크기", "difficulty": "난이도",
              "help": "조작법 보기", "close": "닫기"}


class SettingsScene(BaseScene):
    def __init__(self, game, back):
        super().__init__(game)
        self.back = back
        self.back_name = game.scene_name
        self.row = 0
        # Difficulty belongs to the current save, so it is offered only during an adventure.
        field = getattr(game, "field", None)
        self.rows = list(ROWS)
        if field is not None and back is field:
            self.rows.insert(self.rows.index("display") + 1, "difficulty")

    # --- input ------------------------------------------------------------------------
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self._key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for index, rect in enumerate(self._row_rects()):
                    if rect.collidepoint(event.pos):
                        self.row = index
                        name = self.rows[index]
                        if name in ("help", "close"):
                            self._activate()
                        else:
                            self._change(-1 if event.pos[0] < rect.centerx else 1)

    def _key(self, key):
        if key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_o):
            self._close()
        elif key in (pygame.K_UP, pygame.K_w):
            self.row = (self.row - 1) % len(self.rows)
            self.sfx("cursor")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.row = (self.row + 1) % len(self.rows)
            self.sfx("cursor")
        elif key in (pygame.K_LEFT, pygame.K_a):
            self._change(-1)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self._change(1)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self._activate()

    def _change(self, step):
        name, settings = self.rows[self.row], self.game.settings
        if name in ("music", "sfx"):
            settings[name] = max(0, min(10, settings[name] + step))
            self.game.audio.set_volumes(settings["music"], settings["sfx"])
            self.sfx("cursor")  # effect volume can be heard right away
        elif name == "display":
            modes = self.game.display_modes
            current = modes.index(settings["display"]) if settings["display"] in modes else 0
            settings["display"] = modes[(current + step) % len(modes)]
            self.game.apply_display(settings["display"])
        elif name == "difficulty":
            field = self.game.field
            current = DIFFICULTY_ORDER.index(field.difficulty)
            field.difficulty = DIFFICULTY_ORDER[max(0, min(len(DIFFICULTY_ORDER) - 1, current + step))]
            self.sfx("cursor")

    def _activate(self):
        name = self.rows[self.row]
        if name == "help":
            from scenes.help_scene import HelpScene
            self.sfx("confirm")
            self.game.scene, self.game.scene_name = HelpScene(self.game, self), "help"
        elif name == "close":
            self._close()
        else:
            self._change(1)

    def _close(self):
        self.game.save_settings()
        self.sfx("cursor")
        self.game.scene, self.game.scene_name = self.back, self.back_name

    def update(self, dt):
        if hasattr(self.back, "clock") and not hasattr(self.back, "engine"):
            self.back.clock += dt

    # --- drawing ----------------------------------------------------------------------
    def _row_rects(self):
        step = 64 if len(self.rows) <= 5 else 54
        return [pygame.Rect(170, 154 + index * step, 460, 46) for index in range(len(self.rows))]

    def draw(self, surface):
        colors, settings = self.game.colors, self.game.settings
        ui.plank_strip(surface, (0, 0, surface.get_width(), surface.get_height()))
        ui.frame(surface, pygame.Rect(120, 60, 560, 480), "walnut", border=8)
        self.text(surface, "설정", (400, 104), 30, colors["gold"], True)
        for index, (name, rect) in enumerate(zip(self.rows, self._row_rects())):
            selected = index == self.row
            if name in ("help", "close"):
                self.button(surface, rect.inflate(-160, 0), ROW_LABELS[name], selected, 19)
                continue
            body = ui.frame(surface, rect, "parchment", selected)
            surface.blit(self.game.font(18).render(ROW_LABELS[name], True, ui.INK), (body.x + 12, body.y + 9))
            if name in ("display", "difficulty"):
                value = (DISPLAY_LABELS.get(settings["display"], settings["display"]) if name == "display"
                         else DIFFICULTIES[self.game.field.difficulty]["name"])
                label = self.game.font(17).render(f"<   {value}   >", True, ui.INK)
                surface.blit(label, label.get_rect(midright=(body.right - 14, body.centery)))
            else:
                self._volume_bar(surface, body, settings[name])
        self.text(surface, "↑↓ 고르기 · ←→ 바꾸기 · ESC 닫기 (자동 저장)", (400, 512), 14, colors["muted"], True)

    def _volume_bar(self, surface, body, level):
        x0 = body.right - 14 - 10 * 18
        for step in range(10):
            cell = pygame.Rect(x0 + step * 18, body.y + 10, 14, body.height - 20)
            pygame.draw.rect(surface, ui.OUTLINE, cell)
            pygame.draw.rect(surface, (214, 172, 88) if step < level else (120, 100, 86), cell.inflate(-2, -2))
        number = self.game.font(16).render(str(level), True, ui.INK)
        surface.blit(number, number.get_rect(midright=(x0 - 10, body.centery)))

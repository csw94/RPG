"""The Starlight Library: pick a book on the left, read its pages on the right."""

import pygame

from gameplay.library import BOOKS
from scenes.base_scene import BaseScene
from utils import ui

BOOK_IDS = list(BOOKS)


class LibraryScene(BaseScene):
    def __init__(self, game, back):
        super().__init__(game)
        self.back = back
        self.back_name = game.scene_name
        self.book = 0
        self.page = 0
        self._mark_if_finished()

    @property
    def field(self):
        return self.game.field

    def _pages(self):
        return BOOKS[BOOK_IDS[self.book]]["pages"]

    def _mark_if_finished(self):
        if self.page == len(self._pages()) - 1:
            self.field.books_read.add(BOOK_IDS[self.book])

    # --- input ------------------------------------------------------------------------
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    self._close()
                elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                    step = -1 if event.key in (pygame.K_UP, pygame.K_w) else 1
                    self.book = (self.book + step) % len(BOOK_IDS)
                    self.page = 0
                    self.sfx("cursor")
                    self._mark_if_finished()
                elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                    self._turn(1)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self._turn(-1)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for index, rect in enumerate(self._book_rects()):
                    if rect.collidepoint(event.pos):
                        self.book, self.page = index, 0
                        self._mark_if_finished()
                if self.close_rect().collidepoint(event.pos):
                    self._close()

    def _turn(self, step):
        page = max(0, min(len(self._pages()) - 1, self.page + step))
        if page != self.page:
            self.page = page
            self.sfx("talk")
            self._mark_if_finished()

    def _close(self):
        self.sfx("cursor")
        self.game.save_game()
        self.game.scene, self.game.scene_name = self.back, self.back_name

    def update(self, dt):
        pass

    # --- drawing ----------------------------------------------------------------------
    @staticmethod
    def _book_rects():
        return [pygame.Rect(48, 110 + index * 58, 226, 50) for index in range(len(BOOK_IDS))]

    @staticmethod
    def close_rect():
        return pygame.Rect(330, 512, 140, 38)

    def draw(self, surface):
        colors, read = self.game.colors, self.field.books_read
        ui.plank_strip(surface, (0, 0, surface.get_width(), surface.get_height()))
        ui.frame(surface, pygame.Rect(24, 18, 752, 564), "walnut", border=8)
        self.text(surface, "별빛 도서관", (400, 56), 28, colors["gold"], True)
        self.text(surface, f"읽은 책 {len(read & set(BOOK_IDS))}/{len(BOOK_IDS)}", (400, 88), 14, colors["cream"], True)
        for index, (book_id, rect) in enumerate(zip(BOOK_IDS, self._book_rects())):
            body = ui.frame(surface, rect, "parchment", index == self.book)
            title = self.game.font(15).render(BOOKS[book_id]["title"], True, ui.INK)
            surface.blit(title, title.get_rect(midleft=(body.x + 10, body.centery)))
            if book_id in read:
                mark = self.game.font(12).render("읽음", True, (120, 90, 40))
                surface.blit(mark, mark.get_rect(midright=(body.right - 8, body.centery)))
        page_box = ui.frame(surface, pygame.Rect(290, 110, 462, 384), "parchment")
        book = BOOKS[BOOK_IDS[self.book]]
        heading = self.game.font(20).render(book["title"], True, ui.INK)
        surface.blit(heading, (page_box.x + 18, page_box.y + 14))
        words, rows, current = book["pages"][self.page].split(), [], ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if self.game.font(16).size(candidate)[0] > page_box.width - 36 and current:
                rows.append(current)
                current = word
            else:
                current = candidate
        rows.append(current)
        for index, row in enumerate(rows):
            surface.blit(self.game.font(16).render(row, True, ui.INK_SOFT), (page_box.x + 18, page_box.y + 58 + index * 28))
        footer = self.game.font(14).render(f"{self.page + 1} / {len(book['pages'])}  ◀ ▶", True, ui.INK_SOFT)
        surface.blit(footer, footer.get_rect(bottomright=(page_box.right - 14, page_box.bottom - 10)))
        self.button(surface, self.close_rect(), "나가기", False, 17)
        self.text(surface, "↑↓ 책 고르기 · ←→ 페이지 넘기기 · ESC 나가기", (400, 562), 13, colors["muted"], True)

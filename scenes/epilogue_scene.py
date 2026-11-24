"""Act 4 epilogue: the barrier returns and the hero is knighted in the plaza."""

import math

import pygame

from utils import ui

from gameplay.records import format_play_time
from settings import HEIGHT, TILE_SIZE, WIDTH
from utils.pixel_art import NPC_SIZE, sprite


SEAL_COLORS = ((124, 214, 168), (214, 164, 92), (236, 96, 66))


def epilogue_lines(field):
    """Return (speaker, text) pairs; villagers remember the favours the hero did for them."""
    quests = field.sub_quests
    done = lambda quest_id: quests[quest_id]["status"] == "COMPLETED"
    return [
        ("흑기사 말포스", "크윽... 변방의 견습 기사에게 이런 빛의 힘이... 이 굴욕은 잊지 않겠다...!"),
        ("", "말포스가 검은 안개가 되어 흩어지자, 별빛 분수에서 눈부신 빛기둥이 솟아올랐다."),
        ("", "바람·대지·불꽃·얼음의 인장이 하늘로 떠올라, 별빛 결계가 오크밸리를 다시 감싼다."),
        ("촌장 발렌", "보았는가! 결계가 완전히 돌아왔네. 오크밸리는 이제 안전하네!"),
        ("약초상 마르타", "자네가 구해 준 달빛 약초 덕에 다친 사람들도 금방 낫겠구먼." if done("sq_moon_herb")
         else "숲길에 다시 약초가 피겠구먼. 고맙네, 젊은이."),
        ("노기사 가렌", "내 휘장을 단 기사가 마을을 구했군. 이보다 자랑스러울 수 없네." if done("sq_old_sword")
         else "훌륭한 검술이었네. 젊은 날의 나를 보는 것 같군."),
        ("떠돌이 상인 토비", "협곡 길도 뚫렸으니, 왕도까지 이 소식을 퍼뜨리겠어!" if done("sq_goblin_hunt")
         else "이런 영웅담이라면 왕도에서도 비싸게 팔리겠는걸!"),
        ("잡화상 로건", "별빛의 검이라니... 대장장이 평생 이런 검은 처음 보네."),
        ("촌장 발렌", "왕국의 이름으로, 그대를 오크밸리의 수호 기사로 임명하노라."),
        ("촌장 발렌", "앞으로도 이 마을과 별빛 결계를 지켜 주게, 새로운 수호자여!"),
        ("", "마을 사람들의 환호성이 광장을 가득 메웠다."),
    ]


class EpilogueScene:
    HERO = (15, 15)
    CROWD = {
        "촌장 발렌": ((13, 14), "chief"),
        "약초상 마르타": ((12, 15), "villager"),
        "노기사 가렌": ((17, 14), "old_knight"),
        "떠돌이 상인 토비": ((18, 15), "merchant"),
    }
    SPEAKER_SPOTS = {"흑기사 말포스": (15, 11), "잡화상 로건": (19, 12)}
    CHEER_FROM = 3

    def __init__(self, game):
        self.game = game
        self.field = game.field
        self.field.dialogue_lines = []
        self.field.player.update(x=float(self.HERO[0]), y=float(self.HERO[1]))
        self.field.facing = "up"
        self.lines = epilogue_lines(self.field)
        self.index = 0
        self.clock = 0.0
        self.card = False
        self.card_clock = 0.0

    # --- flow -----------------------------------------------------------------
    def handle_events(self, events):
        for event in events:
            advance = (event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN)) or (
                event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not self.card:
                self._show_card()
            elif advance:
                self.advance()

    def advance(self):
        if self.card:
            if self.card_clock > 0.6:
                self.finish()
            return
        self.index += 1
        if self.index >= len(self.lines):
            self._show_card()

    def _show_card(self):
        self.index = len(self.lines) - 1
        self.card = True
        self.card_clock = 0.0

    def finish(self):
        self.field.message = "별빛 결계가 돌아왔습니다. 수호 기사로서 자유롭게 마을을 둘러보세요."
        self.game.scene_name, self.game.scene = self.field.world, self.field
        self.game.save_game()

    def update(self, dt):
        self.clock += dt
        if self.card:
            self.card_clock += dt

    def record_rows(self):
        f = self.field
        done = sum(q["status"] == "COMPLETED" for q in f.sub_quests.values())
        return [
            ("레벨", f"Lv.{f.level}"), ("플레이 시간", format_play_time(f.play_time)),
            ("공격력", f.attack_power), ("방어력", f.defense_power),
            ("전투 승리", f"{f.stats['wins']}회"), ("마을의 부탁", f"{done} / {len(f.sub_quests)}"),
            ("금화", f"{f.gold} G"), ("최대 HP", f.max_hp),
        ]

    # --- drawing --------------------------------------------------------------
    def text(self, surface, value, pos, size=18, color=None, center=False):
        image = self.game.font(size).render(str(value), True, color or self.game.colors["cream"])
        rect = image.get_rect(center=pos) if center else image.get_rect(topleft=pos)
        surface.blit(image, rect)

    def draw(self, surface):
        if self.card:
            self._draw_card(surface)
            return
        self.field.draw(surface)
        self._draw_light(surface)
        self._draw_crowd(surface)
        self._draw_dialogue(surface)

    def _draw_light(self, surface):
        cam_x, cam_y = self.field._camera()
        fx, fy = self.field.FOUNTAIN
        cx, base = fx * TILE_SIZE + TILE_SIZE // 2 - cam_x, fy * TILE_SIZE - 12 - cam_y
        darkness = 120 if self.index == 0 else max(0, 90 - self.index * 30)
        if darkness:
            shade = pygame.Surface((WIDTH, 512), pygame.SRCALPHA)
            shade.fill((16, 14, 40, darkness))
            surface.blit(shade, (0, 0))
        if self.index == 0:
            knight = sprite("dark_knight", (40, 60))
            mx, my = self.SPEAKER_SPOTS["흑기사 말포스"]
            surface.blit(knight, (mx * TILE_SIZE - 4 - cam_x, my * TILE_SIZE - 28 - cam_y))
            return
        glow = pygame.Surface((WIDTH, 512), pygame.SRCALPHA)
        pulse = 0.5 + 0.5 * math.sin(self.clock * 3)
        for width, alpha in ((46, 40), (26, 70), (10, 140)):
            w = width + pulse * 6
            pygame.draw.rect(glow, (214, 236, 255, alpha), (cx - w / 2, 0, w, base))
        pygame.draw.circle(glow, (232, 244, 255, 90), (cx, base), 34 + pulse * 6)
        for n in range(18):
            px = cx + math.sin(n * 2.3 + self.clock * 1.4) * (60 + n * 9)
            py = (base - (self.clock * 40 + n * 37) % base)
            pygame.draw.circle(glow, (255, 240, 180, 200), (round(px), round(py)), 2 if n % 3 else 3)
        if self.index >= 2:
            for n, color in enumerate(SEAL_COLORS):
                angle = self.clock * 1.6 + n * math.tau / 3
                ox, oy = cx + math.cos(angle) * 54, base - 40 + math.sin(angle) * 18
                pygame.draw.circle(glow, (*color, 90), (round(ox), round(oy)), 11)
                pygame.draw.circle(glow, (*color, 255), (round(ox), round(oy)), 6)
        surface.blit(glow, (0, 0))

    def _draw_crowd(self, surface):
        cam_x, cam_y = self.field._camera()
        cheering = self.index >= self.CHEER_FROM
        speaker = self.lines[self.index][0]
        for order, (name, ((x, y), sprite_name)) in enumerate(self.CROWD.items()):
            hop = abs(math.sin(self.clock * 6 + order)) * 6 if cheering else 0
            surface.blit(sprite(sprite_name, NPC_SIZE), (x * TILE_SIZE - cam_x, y * TILE_SIZE - 16 - hop - cam_y))
        spot = self.CROWD.get(speaker, (self.SPEAKER_SPOTS.get(speaker),))[0]
        if spot:
            ax = spot[0] * TILE_SIZE + TILE_SIZE // 2 - cam_x
            ay = spot[1] * TILE_SIZE - 30 - cam_y - 4 * abs(math.sin(self.clock * 4))
            if speaker == "흑기사 말포스":
                ay -= 30
            pygame.draw.polygon(surface, self.game.colors["gold"], [(ax - 7, ay - 9), (ax + 7, ay - 9), (ax, ay)])
            pygame.draw.polygon(surface, self.game.colors["ink"], [(ax - 7, ay - 9), (ax + 7, ay - 9), (ax, ay)], 1)

    def _draw_dialogue(self, surface):
        colors = self.game.colors
        ui.plank_strip(surface, (0, 512, WIDTH, HEIGHT - 512))
        # The dialogue lives in the bottom bar so the crowd around the fountain stays visible.
        box = ui.frame(surface, pygame.Rect(8, 518, 784, 76), "parchment")

        hint = f"4막 · 새로운 수호자   {self.index + 1}/{len(self.lines)}   SPACE 다음 · ESC 건너뛰기"
        hint_width = self.game.font(13).size(hint)[0]
        hint_box = pygame.Rect(WIDTH - hint_width - 30, 490, hint_width + 20, 22)
        pygame.draw.rect(surface, colors["ink"], hint_box)
        self.text(surface, hint, hint_box.center, 13, colors["muted"], True)

        speaker, line = self.lines[self.index]
        if speaker:
            tag = pygame.Rect(box.x + 14, 488, self.game.font(16).size(speaker)[0] + 24, 26)
            ui.frame(surface, tag.inflate(6, 6), "walnut", True, border=3)
            self.text(surface, speaker, tag.center, 16, colors["cream"], True)
        rows, current = [], ""
        for word in line.split():
            candidate = f"{current} {word}".strip()
            if self.game.font(18).size(candidate)[0] > box.width - 40 and current:
                rows.append(current)
                current = word
            else:
                current = candidate
        rows.append(current)
        color = ui.INK if speaker else ui.INK_SOFT
        top = box.y + (22 if len(rows) == 1 else 10)
        for row_index, row in enumerate(rows[:2]):
            self.text(surface, row, (box.x + 20, top + row_index * 26), 18, color)

    def _draw_card(self, surface):
        colors = self.game.colors
        surface.fill((14, 16, 34))
        for n in range(70):
            x = (n * 137) % WIDTH
            y = (n * 71 + n * n * 3) % 400
            twinkle = 0.5 + 0.5 * math.sin(self.card_clock * 2 + n)
            pygame.draw.circle(surface, (200 + round(55 * twinkle), 220, 255), (x, y), 1 if n % 4 else 2)
        fade = min(1.0, self.card_clock / 1.2)
        gold = tuple(round(c * fade) for c in colors["gold"])
        cream = tuple(round(c * fade) for c in colors["cream"])
        muted = tuple(round(c * fade) for c in colors["muted"])
        self.text(surface, "별빛 결계의 수호자", (WIDTH // 2, 120), 40, gold, True)
        self.text(surface, "4막 · 새로운 수호자", (WIDTH // 2, 172), 20, cream, True)
        self.text(surface, "견습 기사는 오크밸리의 수호 기사가 되었다.", (WIDTH // 2, 222), 18, cream, True)

        f = self.field
        stats = self.record_rows()
        panel = pygame.Rect(180, 250, 440, 182)
        pygame.draw.rect(surface, tuple(round(c * fade) for c in colors["panel"]), panel)
        pygame.draw.rect(surface, gold, panel, 2)
        for i, (label, value) in enumerate(stats):
            col, row = i % 2, i // 2
            x, y = panel.x + 24 + col * 214, panel.y + 18 + row * 40
            self.text(surface, label, (x, y), 16, muted)
            self.text(surface, value, (x + 96, y - 2), 19, cream)
        if "knights_crest" in f.quest_items:
            self.text(surface, "기사의 휘장을 가슴에 단 채", (WIDTH // 2, 452), 16, muted, True)
        self.text(surface, "THE END", (WIDTH // 2, 492), 30, gold, True)
        if self.card_clock > 0.6:
            self.text(surface, "SPACE / Enter  마을로 돌아가기", (WIDTH // 2, 548), 16, muted, True)

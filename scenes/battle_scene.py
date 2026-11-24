"""Turn-based encounters: menus on top of ``gameplay.combat.BattleEngine``.

The engine resolves a whole round at once and returns events; this scene plays them back
one by one (lunges, hit shake, floating numbers) and only then hands control back.
"""

import pygame

from gameplay.combat import STATUS_NAMES, BattleEngine
from scenes.base_scene import BaseScene
from utils import battle_art, ui
from utils.pixel_art import enemy_idle, hero_sprite

EVENT_TIME = {"damage": 0.55, "heal": 0.5, "miss": 0.45, "status": 0.55, "status_tick": 0.5,
              "level_up": 1.0, "xp": 0.8, "defeat": 0.7, "lose": 0.9, "skill": 0.45,
              "attack": 0.32, "stunned": 0.6, "guard": 0.5}
ELEMENT_COLORS = {"light": (255, 236, 150), "wind": (150, 230, 190), "earth": (214, 170, 110),
                  "fire": (255, 140, 70), "dark": (170, 120, 220), "none": (255, 255, 255)}
STATUS_COLORS = {"poison": (150, 96, 190), "burn": (230, 110, 54), "stun": (230, 200, 90)}


class BattleScene(BaseScene):
    ACTIONS = ("공격", "스킬", "포션", "도망")

    def __init__(self, game, enemy_type="slime", rng=None):
        super().__init__(game)
        # The state right before the fight, so a defeat can be retried from here.
        self.snapshot = game.field.serialize()
        self.defeat_choice = 0        # 0 retry, 1 back to the village
        self.engine = BattleEngine(game.field, enemy_type, rng=rng)
        self.enemy = self.engine.enemy
        self.selected = 0
        self.skill_index = 0
        self.mode = "menu"            # menu | skills | playing | done
        self.queue = []
        self.current = None
        self.event_timer = 0.0
        self.popups = []              # dicts: text, color, x, y, age
        self.shake = {"hero": 0.0, "enemy": 0.0}
        self.lunge = {"hero": 0.0, "enemy": 0.0}
        self.shown_enemy_hp = self.engine.enemy_hp
        self.lines = [f"{self.enemy['name']}이(가) 나타났다!"]
        self.done_timer = 0.0
        self.clock = 0.0              # drives the enemy's idle animation
        self.kind = self.backdrop_kind()  # fixed: losing moves the hero to the village mid-fight
        self.sfx("encounter")

    # --- compatibility helpers ------------------------------------------------------
    @property
    def message(self):
        return self.lines[-1] if self.lines else ""

    @property
    def done(self):
        return self.mode == "done"

    def skill_list(self):
        return self.engine.available_skills()

    # --- input ----------------------------------------------------------------------
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self._key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._click(event.pos)

    def _key(self, key):
        confirm = key in (pygame.K_RETURN, pygame.K_SPACE)
        back = key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_x)
        step = -1 if key in (pygame.K_LEFT, pygame.K_a, pygame.K_UP, pygame.K_w) else \
            1 if key in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN, pygame.K_s) else 0
        if self.mode == "done":
            if self.engine.result == "lose" and step:
                self.defeat_choice = (self.defeat_choice + step) % 2
                self.sfx("cursor")
            elif confirm:
                self._leave()
        elif self.mode == "playing":
            if confirm:
                self.event_timer = 0  # skip ahead
        elif self.mode == "skills":
            skills = self.skill_list()
            if back:
                self.mode = "menu"
                self.sfx("cursor")
            elif step:
                self.skill_index = (self.skill_index + step) % len(skills)
                self.sfx("cursor")
            elif confirm:
                self._run("skill", skills[self.skill_index]["id"])
        else:
            if step:
                self.selected = (self.selected + step) % 4
                self.sfx("cursor")
            elif confirm:
                self._choose()

    def _click(self, pos):
        if self.mode == "done":
            if self.engine.result == "lose":
                for index, rect in enumerate(self._defeat_buttons()):
                    if rect.collidepoint(pos):
                        self.defeat_choice = index
                        self._leave()
                return
            self._leave()
        elif self.mode == "skills":
            for index, rect in enumerate(self._skill_buttons()):
                if rect.collidepoint(pos):
                    self.skill_index = index
                    self._run("skill", self.skill_list()[index]["id"])
                    return
        elif self.mode == "menu":
            for index, rect in enumerate(self._buttons()):
                if rect.collidepoint(pos):
                    self.selected = index
                    self._choose()

    def _leave(self):
        if self.engine.result == "lose" and self.defeat_choice == 0:
            self.sfx("confirm")
            self.game.retry_battle(self.snapshot, self.enemy["id"])
        else:
            self.game.finish_battle()

    def _choose(self):
        if self.selected == 1:
            self.sfx("confirm")
            self.mode = "skills"
            self.skill_index = min(self.skill_index, len(self.skill_list()) - 1)
            return
        self._run(("attack", None, "item", "flee")[self.selected])

    def _run(self, action, skill_id=None):
        self.sfx("confirm")
        events = self.engine.act(action, skill_id)
        self.game.save_game()
        self.queue = list(events)
        self.current = None
        self.event_timer = 0
        self.mode = "playing"

    # --- playback -------------------------------------------------------------------
    def update(self, dt):
        self.clock += dt
        for side in self.shake:
            self.shake[side] = max(0.0, self.shake[side] - dt)
            self.lunge[side] = max(0.0, self.lunge[side] - dt)
        for popup in self.popups:
            popup["age"] += dt
        self.popups = [p for p in self.popups if p["age"] < 1.0]
        if self.mode == "playing":
            self.event_timer -= dt
            while self.event_timer <= 0:
                if not self.queue:
                    self._finish_round()
                    break
                self._start(self.queue.pop(0))
        elif self.mode == "done":
            self.done_timer += dt

    def _start(self, event):
        self.current = event
        self.event_timer = EVENT_TIME.get(event["type"], 0.4)
        if event.get("text"):
            self.lines = (self.lines + [event["text"]])[-3:]
        kind, target = event["type"], event.get("target")
        self._cue(event)
        x = {"hero": battle_art.HERO_SPOT * 2, "enemy": battle_art.ENEMY_SPOT * 2}.get(target, 400)
        if kind in ("attack", "skill"):
            self.lunge[event["actor"]] = 0.25
        elif kind in ("damage", "status_tick"):
            self.shake[target] = 0.35
            if event.get("weak"):
                label, color = f"{event['amount']} 약점!", (255, 214, 90)
            elif event.get("crit"):
                label, color = f"{event['amount']}!!", (255, 120, 90)
            elif kind == "status_tick":
                label, color = str(event["amount"]), STATUS_COLORS[event["status"]]
            else:
                label, color = str(event["amount"]), ELEMENT_COLORS.get(event.get("element"), (255, 255, 255))
            self._popup(label, color, x)
            if target == "enemy":
                self.shown_enemy_hp = max(0, self.shown_enemy_hp - event["amount"])
        elif kind == "heal":
            self._popup(f"+{event['amount']}", (130, 230, 140), x)
            if target == "enemy":
                self.shown_enemy_hp = min(self.engine.enemy_max_hp, self.shown_enemy_hp + event["amount"])
        elif kind == "miss":
            self._popup("MISS", (200, 210, 230), x)
        elif kind == "status":
            self._popup(STATUS_NAMES[event["status"]], STATUS_COLORS[event["status"]], x)
        elif kind == "level_up":
            self._popup(f"LEVEL {event['level']}!", (255, 222, 110), battle_art.HERO_SPOT * 2)

    def _cue(self, event):
        kind, target = event["type"], event.get("target")
        if kind == "damage":
            name = "hurt" if target == "hero" else "crit" if event.get("crit") else "weak" if event.get("weak") else "hit"
        else:
            name = {"skill": "skill", "heal": "heal", "miss": "miss", "status": "status", "stunned": "status",
                    "status_tick": "hurt", "guard": "guard", "level_up": "level_up", "defeat": "victory",
                    "lose": "defeat", "flee": "flee"}.get(kind)
        if name:
            self.sfx(name)

    def _popup(self, text, color, x):
        self.popups.append({"text": text, "color": color, "x": x, "y": 186 - 30 * len(self.popups), "age": 0.0})

    def _finish_round(self):
        self.current = None
        self.shown_enemy_hp = max(0, self.engine.enemy_hp)
        self.mode = "done" if self.engine.result else "menu"

    # --- scene picking (used by draw and tests) ----------------------------------------
    def backdrop_kind(self):
        """Fight where you stand: dungeon style, route theme, or the village square."""
        field = self.game.field
        shrine = getattr(field, "shrine_key", None)
        if shrine:
            return f"dungeon_{shrine.replace('shrine_', '')}"
        if getattr(field, "world", "") == "village":
            return "village"
        return getattr(field, "theme", "forest")

    # --- drawing --------------------------------------------------------------------
    def _buttons(self):
        return [pygame.Rect(104 + (i % 2) * 310, 446 + (i // 2) * 56, 280, 46) for i in range(4)]

    def _defeat_buttons(self):
        return [pygame.Rect(250 + i * 160, 470, 140, 44) for i in range(2)]

    def _skill_buttons(self):
        return [pygame.Rect(36 + (i % 3) * 248, 446 + (i // 3) * 56, 236, 46)
                for i in range(len(self.skill_list()))]

    def _offset(self, side, direction):
        shake = self.shake[side]
        dx = int(6 * (1 if int(shake * 40) % 2 else -1)) if shake else 0
        lunge = self.lunge[side]
        dx += int(direction * 28 * (lunge / 0.25) * (1 - lunge / 0.25) * 4) if lunge else 0
        return dx

    def draw(self, surface):
        field = self.game.field
        surface.blit(battle_art.backdrop(self.kind), (0, 0))
        feet = battle_art.FEET_Y * 2
        hero = hero_sprite(field.weapon, field.armor, (80, 120))
        hx = battle_art.HERO_SPOT * 2 - hero.get_width() // 2 + self._offset("hero", 1)
        surface.blit(hero, (hx, feet - hero.get_height()))
        if self.mode == "done" and self.engine.result == "win":
            pass  # the defeated enemy is gone
        else:
            enemy, bob = enemy_idle(self.enemy["sprite"], self.enemy["size"], self.clock)
            ex = battle_art.ENEMY_SPOT * 2 - enemy.get_width() // 2 + self._offset("enemy", -1)
            if self.shake["enemy"] and int(self.shake["enemy"] * 30) % 2:
                enemy = enemy.copy()
                enemy.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MAX)
            surface.blit(enemy, (ex, feet - enemy.get_height() + 4 + bob))
        self._draw_status_panels(surface)
        for popup in self.popups:
            alpha = 255 if popup["age"] < 0.6 else int(255 * (1 - (popup["age"] - 0.6) / 0.4))
            font = self.game.font(36)
            image = font.render(popup["text"], True, popup["color"])
            edge = font.render(popup["text"], True, (36, 24, 22))
            y = popup["y"] - int(popup["age"] * 40)
            layers = [(edge, dx, dy) for dx in (-2, 0, 2) for dy in (-2, 0, 2) if dx or dy] + [(image, 0, 0)]
            for img, dx, dy in layers:
                img.set_alpha(max(0, alpha))
                surface.blit(img, img.get_rect(center=(popup["x"] + dx, y + dy)))
        self._draw_bottom(surface)

    def _draw_status_panels(self, surface):
        field, engine = self.game.field, self.engine
        ui.frame(surface, pygame.Rect(54, 24, 263, 104), "walnut")
        self.text(surface, f"수호자  Lv.{field.level}", (78, 38), 20)
        shown_hp = 0 if engine.result == "lose" else field.hp  # field HP is already the post-wake value
        self._bar(surface, 78, 70, 215, shown_hp, field.max_hp, self.game.colors["red"])
        self._bar(surface, 78, 90, 215, field.mp, field.max_mp, self.game.colors["blue"], 8)
        badges = [STATUS_NAMES[s] for s in engine.statuses["hero"]] + (["수호"] if engine.guarding else [])
        self._badges(surface, badges, (78, 104))
        ui.frame(surface, pygame.Rect(482, 24, 263, 104), "walnut")
        self.text(surface, self.enemy["name"], (506, 38), 20)
        self._bar(surface, 506, 70, 215, self.shown_enemy_hp, engine.enemy_max_hp, self.game.colors["green"])
        self._badges(surface, [STATUS_NAMES[s] for s in engine.statuses["enemy"]], (506, 92))

    def _badges(self, surface, names, pos):
        x, y = pos
        for name in names:
            image = self.game.font(16).render(name, True, (250, 240, 220))
            rect = pygame.Rect(x, y, image.get_width() + 10, 18)
            pygame.draw.rect(surface, (96, 62, 48), rect, border_radius=4)
            surface.blit(image, image.get_rect(center=rect.center))
            x = rect.right + 4

    def _draw_bottom(self, surface):
        field = self.game.field
        ui.plank_strip(surface, (0, 374, 800, 226))
        ui.frame(surface, pygame.Rect(8, 380, 784, 214), "walnut")
        recent = self.lines[-2:]
        for index, line in enumerate(recent):
            latest = index == len(recent) - 1
            self.text(surface, line, (400, 402 + index * 22), 18,
                      self.game.colors["gold"] if latest else self.game.colors["muted"], True)
        if self.mode == "skills":
            skills = self.skill_list()
            for index, (skill, rect) in enumerate(zip(skills, self._skill_buttons())):
                usable = field.mp >= skill["mp"]
                label = f"{skill['name']}  {skill['mp']}MP"
                self.button(surface, rect, label if usable else f"({label})", index == self.skill_index, 20)
            chosen = skills[self.skill_index]
            footer = f"{chosen['desc']}   ·   MP {field.mp}/{field.max_mp}   ·   Esc: 뒤로"
        elif self.mode == "done" and self.engine.result == "lose":
            for index, (label, rect) in enumerate(zip(("다시 도전", "마을로 돌아가기"), self._defeat_buttons())):
                self.button(surface, rect, label, index == self.defeat_choice, 18)
            footer = ("전투 직전 상태로 같은 적과 다시 싸웁니다." if self.defeat_choice == 0
                      else "HP 절반으로 오크밸리에서 깨어납니다.")
        elif self.mode == "done":
            footer = "Enter: 계속"
            self.text(surface, footer, (400, 520), 22, self.game.colors["cream"], True)
            footer = ""
        elif self.mode == "playing":
            footer = "Enter: 빨리 보기"
        else:
            for index, (label, rect) in enumerate(zip(self.ACTIONS, self._buttons())):
                if index == 2:
                    label = f"포션 ({field.potions}/{field.high_potions})"
                self.button(surface, rect, label, index == self.selected)
            footer = (f"HP {field.hp}/{field.max_hp}   MP {field.mp}/{field.max_mp}   "
                      f"ATK {field.attack_power}   DEF {field.defense_power}   "
                      f"EXP {field.xp}/{self._xp_needed()}")
        if footer:
            self.text(surface, footer, (400, 572), 16, self.game.colors["muted"], True)

    def _xp_needed(self):
        from gameplay.combat import xp_to_next

        return xp_to_next(self.game.field.level)

    @staticmethod
    def _bar(surface, x, y, width, value, maximum, color, height=14):
        pygame.draw.rect(surface, (55, 61, 73), (x, y, width, height))
        fill = int(width * max(0, value) / maximum) if maximum else 0
        if fill:
            pygame.draw.rect(surface, color, (x, y, min(width, fill), height))

"""Turn-based battle rules, independent of drawing.

``BattleEngine.act`` resolves one full round (hero action, status ticks, enemy action)
and returns a list of *events*. BattleScene plays those events back as animations, so
the rules can be tested without pygame and the visuals stay in sync with the rules.

Event types: message, attack, skill, damage, heal, miss, status, status_tick, stunned,
guard, defeat, xp, level_up, flee, lose. Every event carries a Korean ``text`` for the log
(may be empty).
"""

import random

from gameplay.difficulty import difficulty_of
from gameplay.enemies import ENEMIES

ELEMENTS = ("none", "light", "wind", "earth", "fire", "dark")
BOSS_PATTERNS = ("gust", "earthquake", "enrage", "dark_arts", "abyss", "blizzard")
FREEZE_CHANCE = 0.25

SKILLS = {
    "light_bolt": {"id": "light_bolt", "name": "빛의 탄", "mp": 3, "level": 1, "kind": "attack",
                   "power": 10, "element": "light", "desc": "빛 속성 공격"},
    "heal_light": {"id": "heal_light", "name": "회복의 빛", "mp": 4, "level": 2, "kind": "heal",
                   "power": 40, "element": "light", "desc": "HP 회복 · 상태이상 해제"},
    "guard": {"id": "guard", "name": "수호 자세", "mp": 2, "level": 3, "kind": "guard",
              "power": 0, "element": "none", "desc": "이번 턴 받는 피해 절반"},
    "wind_slash": {"id": "wind_slash", "name": "바람 베기", "mp": 5, "level": 4, "kind": "attack",
                   "power": 14, "element": "wind", "desc": "바람 속성 공격"},
    "earth_smash": {"id": "earth_smash", "name": "대지 강타", "mp": 6, "level": 6, "kind": "attack",
                    "power": 18, "element": "earth", "desc": "대지 속성 · 기절 확률"},
    "flame_slash": {"id": "flame_slash", "name": "화염 참격", "mp": 6, "level": 8, "kind": "attack",
                    "power": 16, "element": "fire", "desc": "화염 속성 · 화상"},
    "star_storm": {"id": "star_storm", "name": "별빛 폭풍", "mp": 10, "level": 10, "kind": "attack",
                   "power": 30, "element": "light", "desc": "빛 속성 · 가장 강한 공격"},
    "holy_prayer": {"id": "holy_prayer", "name": "성스러운 기도", "mp": 12, "level": 12, "kind": "heal",
                    "power": 160, "element": "light", "desc": "HP 크게 회복 · 상태이상 해제"},
}
STATUS_NAMES = {"poison": "독", "burn": "화상", "stun": "기절"}
CRIT_CHANCE = 0.08
VICTORY_MP = 2  # a little MP back after every win, so skills stay usable
LEVEL_GAINS = {"max_hp": 12, "max_mp": 3, "atk": 2, "defense": 1}


def xp_to_next(level):
    """Experience needed to go from ``level`` to ``level + 1``."""
    return 20 + level * 15


def skills_for_level(level):
    return [skill for skill in SKILLS.values() if skill["level"] <= level]


class BattleEngine:
    def __init__(self, field, enemy_id, rng=None):
        self.field = field
        self.rng = rng or random.Random()
        self.enemy = ENEMIES.get(enemy_id, ENEMIES["slime"])
        self.difficulty = difficulty_of(field)
        self.enemy_hp = round(self.enemy["hp"] * self.difficulty["enemy_hp"])
        self.enemy_max_hp = self.enemy_hp
        self.statuses = {"hero": {}, "enemy": {}}
        self.guarding = False
        self.enraged = False
        self.howl = 0
        self.turn = 0
        self.phase = 1  # the final boss turns to phase 2 below half HP
        self.thawed = False  # a hero who just lost a turn to ice can't be refrozen at once
        self.result = None
        self.log = []

    # --- helpers ------------------------------------------------------------------
    @property
    def is_boss(self):
        return self.enemy["pattern"] in BOSS_PATTERNS

    def available_skills(self):
        return skills_for_level(self.field.level)

    def _emit(self, events, **event):
        event.setdefault("text", "")
        events.append(event)
        self.log.append(event)
        return event

    def _vary(self, amount):
        return max(1, round(amount * self.rng.uniform(0.9, 1.1)))

    def _element_mult(self, element):
        if element in self.enemy.get("weak", ()):
            return 1.5, "weak"
        if element in self.enemy.get("resist", ()):
            return 0.5, "resist"
        return 1.0, None

    def _hit_enemy(self, events, raw, element="none", crit=False):
        mult, tag = self._element_mult(element)
        amount = max(1, round(self._vary(raw) * mult * (1.5 if crit else 1)))
        self.enemy_hp -= amount
        note = {"weak": " 약점을 찔렀다!", "resist": " 효과가 약하다..."}.get(tag, "")
        self._emit(events, type="damage", target="enemy", amount=amount, element=element, crit=crit,
                   weak=tag == "weak", resist=tag == "resist",
                   text=("치명타! " if crit else "") + f"{amount}의 피해." + note)
        return amount

    def _hit_hero(self, events, raw, fixed=False, element="none", label="적의 공격"):
        field = self.field
        if field.evasion > 0 and self.rng.random() < field.evasion / 100:
            self._emit(events, type="miss", target="hero", text=f"{label}을(를) 회피했다!")
            return 0
        amount = raw if fixed else max(1, self._vary(raw - field.defense_power))
        amount = max(1, round(amount * self.difficulty["damage"]))
        if self.guarding:
            amount //= 2
        field.hp = max(0, field.hp - amount)
        self._emit(events, type="damage", target="hero", amount=amount, element=element,
                   text=f"{label}! {amount}의 피해." + (" (수호)" if self.guarding else ""))
        return amount

    def _apply_status(self, events, target, status, turns, text=None):
        if target == "hero" and status in self.field.immunities:
            self._emit(events, type="message", text=f"장비가 {STATUS_NAMES[status]}을(를) 막아냈다!")
            return
        self.statuses[target][status] = turns
        who = "적" if target == "enemy" else "수호자"
        self._emit(events, type="status", target=target, status=status,
                   text=text or f"{who}이(가) {STATUS_NAMES[status]} 상태가 되었다!")

    def _try_freeze(self, events, chance=FREEZE_CHANCE):
        if self.thawed or "stun" in self.statuses["hero"] or self.rng.random() >= chance:
            return
        self._apply_status(events, "hero", "stun", 1, text="몸이 꽁꽁 얼어붙었다! 다음 턴에 움직일 수 없다.")

    def _tick(self, events, target):
        statuses = self.statuses[target]
        for status in ("poison", "burn"):
            if status not in statuses:
                continue
            if target == "enemy":
                amount = max(4, self.enemy_max_hp // 14) if status == "burn" else max(3, self.enemy_max_hp // 16)
                self.enemy_hp -= amount
            else:
                amount = 6 if status == "poison" else 8
                self.field.hp = max(0, self.field.hp - amount)
            self._emit(events, type="status_tick", target=target, status=status, amount=amount,
                       text=f"{STATUS_NAMES[status]} 피해 {amount}.")
            statuses[status] -= 1
            if statuses[status] <= 0:
                del statuses[status]

    # --- a full round --------------------------------------------------------------
    def act(self, action, skill_id=None):
        events = []
        if self.result:
            return events
        field = self.field
        if action in ("attack", "skill", "item", "flee") and self.statuses["hero"].pop("stun", None):
            self.thawed = True
            self._emit(events, type="stunned", target="hero", text="몸이 얼어붙어 움직일 수 없다!")
            return self._round_tail(events)
        if action == "attack":
            weapon = field.weapon_info
            crit = self.rng.random() < CRIT_CHANCE + weapon.get("crit", 0) + field.accessory_info.get("crit", 0)
            self._emit(events, type="attack", actor="hero", text="검을 휘둘렀다.")
            self._hit_enemy(events, field.attack_power - self.enemy["defense"],
                            element=weapon.get("element", "none"), crit=crit)
            proc = weapon.get("proc")
            if proc and self.enemy_hp > 0 and proc[0] not in self.statuses["enemy"]:
                status, chance, turns = proc
                if status == "stun" and self.is_boss:
                    chance /= 2
                if self.rng.random() < chance:
                    self._apply_status(events, "enemy", status, turns)
        elif action == "skill":
            skill = SKILLS.get(skill_id)
            if not skill or skill["level"] > field.level:
                self._emit(events, type="message", text="아직 익히지 못한 기술이다.")
                return events
            if field.mp < skill["mp"]:
                self._emit(events, type="message", text="MP가 부족합니다.")
                return events
            field.mp -= skill["mp"]
            self._emit(events, type="skill", actor="hero", skill=skill["id"], element=skill["element"],
                       text=f"{skill['name']}!")
            if skill["kind"] == "attack":
                self._hit_enemy(events, field.attack_power + skill["power"] - self.enemy["defense"],
                                element=skill["element"])
                if skill["id"] == "flame_slash" and self.enemy_hp > 0:
                    self._apply_status(events, "enemy", "burn", 3)
                if skill["id"] == "earth_smash" and self.enemy_hp > 0:
                    if self.rng.random() < (0.15 if self.is_boss else 0.35):
                        self._apply_status(events, "enemy", "stun", 1)
            elif skill["kind"] == "heal":
                amount = min(field.max_hp - field.hp, skill["power"] + field.level * 4)
                field.hp += amount
                self.statuses["hero"].clear()
                self._emit(events, type="heal", target="hero", amount=amount, text=f"HP {amount} 회복.")
            else:
                self.guarding = True
                self._emit(events, type="guard", target="hero", text="방패를 굳게 세웠다.")
        elif action == "item":
            if field.potions > 0:
                field.potions -= 1
                amount = min(50, field.max_hp - field.hp)
                label = "회복약(소)"
            elif field.high_potions > 0:
                field.high_potions -= 1
                amount = min(120, field.max_hp - field.hp)
                label = "고급 회복약"
            else:
                self._emit(events, type="message", text="사용할 포션이 없습니다.")
                return events
            field.hp += amount
            self._emit(events, type="heal", target="hero", amount=amount, text=f"{label}으로 HP {amount} 회복.")
        elif action == "flee":
            if self.is_boss:
                self._emit(events, type="message", text="보스의 압도적인 기운에 도망칠 수 없다!")
                return events
            self.result = "flee"
            self._tally("flees")
            self._emit(events, type="flee", text="전투에서 도망쳤다.")
            return events
        else:
            return events

        return self._round_tail(events)

    def _round_tail(self, events):
        """Everything after the hero's action: statuses, the enemy's turn, defeat checks."""
        field = self.field
        if self.enemy_hp <= 0:
            return self._win(events)
        self._tick(events, "enemy")
        if self.enemy_hp <= 0:
            return self._win(events)
        self._check_phase(events)
        self.turn += 1
        if self.statuses["enemy"].pop("stun", None):
            self._emit(events, type="stunned", target="enemy", text="적은 기절해서 움직이지 못한다!")
        else:
            self._enemy_turn(events)
        self.thawed = False
        self._tick(events, "hero")
        self.guarding = False
        if field.hp <= 0:
            return self._lose(events)
        return events

    def _tally(self, key):
        stats = getattr(self.field, "stats", None)
        if stats is not None:
            stats[key] = stats.get(key, 0) + 1

    def _check_phase(self, events):
        if self.enemy["id"] != "final_boss" or self.phase != 1 or self.enemy_hp > self.enemy_max_hp // 2:
            return
        self.phase = 2
        self.statuses["enemy"].clear()
        self._emit(events, type="phase", target="enemy", phase=2,
                   text="흑기사 말포스: 별빛 따위에 무릎 꿇을 성싶으냐!")
        self._emit(events, type="message", text="말포스가 어둠의 갑옷을 벗어 던졌다! 공격이 거세진다.")

    def _enemy_turn(self, events):
        enemy, pattern = self.enemy, self.enemy["pattern"]
        self._emit(events, type="attack", actor="enemy", text="")
        attack = enemy["attack"] + self.howl
        if pattern == "double_stab":
            self._hit_hero(events, max(1, attack // 2), label="연속 찌르기")
            self._hit_hero(events, max(1, attack // 2), label="연속 찌르기")
        elif pattern == "gust" and self.turn % 2 == 0:
            self._hit_hero(events, 15, fixed=True, element="wind", label="폭풍 돌풍")
        elif pattern == "earthquake" and self.turn % 3 == 0:
            self._hit_hero(events, 30, fixed=True, element="earth", label="바위 골렘의 지진")
        elif pattern == "enrage" and not self.enraged and self.enemy_hp <= self.enemy_max_hp // 2:
            self.enraged = True
            self._emit(events, type="message", text="화염 리자드맨이 광폭화했다! ATK +5")
        elif pattern == "dark_arts" and self.turn % (2 if self.phase == 2 else 3) == 0:
            self._hit_hero(events, 24 if self.phase == 2 else 18, fixed=True, element="dark", label="어둠의 파동")
        elif pattern == "blizzard" and self.turn % 3 == 0:
            if self._hit_hero(events, 30, fixed=True, label="눈보라"):
                self._try_freeze(events, 0.35)
        elif pattern == "freeze":
            if self._hit_hero(events, attack, label="서리 공격"):
                self._try_freeze(events)
        elif pattern == "abyss" and self.turn % 3 == 0:
            self._hit_hero(events, 52, fixed=True, element="dark", label="심연의 폭풍")
        elif pattern == "howl" and self.turn % 3 == 0:
            self.howl += 3
            self._emit(events, type="message", text="숲늑대가 울부짖었다! 공격력이 올랐다.")
        elif pattern == "drain":
            dealt = self._hit_hero(events, attack, label="흡혈")
            if dealt:
                healed = min(self.enemy_max_hp - self.enemy_hp, dealt // 2)
                self.enemy_hp += healed
                self._emit(events, type="heal", target="enemy", amount=healed, text=f"박쥐가 {healed} 회복했다.")
        else:
            bonus = 5 if self.enraged else 0
            bonus += (16 if self.phase == 2 else 8) if pattern == "dark_arts" else 0
            label = {"dark_arts": "암흑 베기", "poison": "독 공격", "burn": "불꽃 공격"}.get(pattern, "적의 공격")
            dealt = self._hit_hero(events, attack + bonus, label=label)
            if dealt and pattern in ("poison", "burn") and self.rng.random() < 0.3:
                if pattern not in self.statuses["hero"]:
                    self._apply_status(events, "hero", pattern, 3)
            if pattern == "enrage" and self.enraged and dealt and self.rng.random() < 0.25:
                self._apply_status(events, "hero", "burn", 2)

    def _win(self, events):
        field = self.field
        self.result = "win"
        self._tally("wins")
        self.enemy_hp = 0
        self._emit(events, type="defeat", target="enemy", text=f"{self.enemy['name']} 격파!")
        field.mp = min(field.max_mp, field.mp + VICTORY_MP + field.accessory_info.get("victory_mp", 0))
        reward = field.resolve_battle_victory(self.enemy["id"])
        if self.enemy["id"] == "final_boss":
            field.pending_epilogue = True
        xp = self.enemy.get("xp", 0)
        if xp:
            self._emit(events, type="xp", amount=xp, text=f"{reward} · 경험치 +{xp}")
            for up in field.gain_xp(xp):
                learned = f" 새 기술: {', '.join(up['skills'])}" if up["skills"] else ""
                self._emit(events, type="level_up", level=up["level"], skills=up["skills"],
                           text=f"레벨 {up['level']}!{learned}")
        else:
            self._emit(events, type="message", text=reward)
        return events

    def _lose(self, events):
        from scenes.village_scene import VillageScene

        field = self.field
        self.result = "lose"
        self._tally("losses")
        field.hp = max(1, field.max_hp // 2)
        self.statuses["hero"].clear()
        field.player.update(x=float(VillageScene.START[0]), y=float(VillageScene.START[1]))
        field.world = "village"
        field.message = "힘겹게 깨어나 오크밸리로 돌아왔다. 마을 집의 침대에서 쉬면 회복된다."
        self._emit(events, type="lose", text="의식을 잃었다...")
        return events

"""Achievements, judged from what a save already records (flags, stats, bestiary, gear)."""

from gameplay.enemies import ENEMIES
from gameplay.equipment import ACCESSORIES, ARMORS, LEGACY_IDS, WEAPONS
from gameplay.world_data import SHRINES


def gear_owned(field):
    owned = set(field.owned_weapons) | set(field.owned_armors) | set(field.owned_accessories)
    everything = (set(WEAPONS) | set(ARMORS) | set(ACCESSORIES)) - LEGACY_IDS
    return len(owned & everything), len(everything)


def _flags(field):
    return field.quest_flags


ACHIEVEMENTS = {
    "first_win": {"name": "첫 승리", "desc": "전투에서 처음 이겼다",
                  "check": lambda f: f.stats.get("wins", 0) >= 1},
    "hunter": {"name": "베테랑 사냥꾼", "desc": "전투에서 100번 이겼다",
               "check": lambda f: f.stats.get("wins", 0) >= 100},
    "first_seal": {"name": "첫 번째 인장", "desc": "제단 하나를 정화했다",
                   "check": lambda f: any(_flags(f).get(key) for key in SHRINES)},
    "all_seals": {"name": "네 개의 인장", "desc": "네 제단을 모두 정화했다",
                  "check": lambda f: all(_flags(f).get(key) for key in SHRINES)},
    "ending": {"name": "수호 기사", "desc": "흑기사 말포스를 물리쳤다",
               "check": lambda f: bool(_flags(f).get("final_boss"))},
    "abyss": {"name": "심연을 걷는 자", "desc": "심연의 군주 녹스를 물리쳤다",
              "check": lambda f: bool(_flags(f).get("abyss_lord"))},
    "helper": {"name": "마을의 해결사", "desc": "마을 사람들의 부탁을 모두 들어주었다",
               "check": lambda f: all(q["status"] == "COMPLETED" for q in f.sub_quests.values())},
    "bestiary": {"name": "도감 완성", "desc": "모든 적을 만나 보았다",
                 "check": lambda f: set(ENEMIES) <= set(getattr(f, "bestiary", {}))},
    "collector": {"name": "수집가", "desc": "장비를 15가지 모았다",
                  "check": lambda f: gear_owned(f)[0] >= 15},
    "veteran": {"name": "숙련된 수호자", "desc": "레벨 10에 도달했다",
                "check": lambda f: f.level >= 10},
    "hard_ending": {"name": "강철 의지", "desc": "어려움 난이도로 엔딩을 보았다",
                    "check": lambda f: bool(_flags(f).get("final_boss")) and f.difficulty == "hard"},
    "speedrun": {"name": "별빛 질주", "desc": "1시간 안에 엔딩을 보았다",
                 "check": lambda f: bool(_flags(f).get("final_boss")) and f.play_time <= 3600},
    "rich": {"name": "오크밸리의 부자", "desc": "금화 1000G를 모았다",
             "check": lambda f: f.gold >= 1000},
    "ng_plus": {"name": "다시 별빛 아래", "desc": "2회차 모험을 시작했다",
                "check": lambda f: getattr(f, "cycle", 1) >= 2},
}


def check_achievements(field):
    """Unlock every newly earned achievement; queue a notice for each. Returns new ids."""
    new = []
    for achievement_id, achievement in ACHIEVEMENTS.items():
        if achievement_id in field.achievements:
            continue
        if achievement["check"](field):
            field.achievements.add(achievement_id)
            field.achievement_toasts.append(achievement["name"])
            new.append(achievement_id)
    return new

"""Play records: readable play time and the short summary shown on save-slot cards."""

from gameplay.difficulty import DIFFICULTIES
from gameplay.world_data import SHRINES


def format_play_time(seconds):
    minutes = int(seconds) // 60
    hours, minutes = divmod(minutes, 60)
    return f"{hours}시간 {minutes:02d}분" if hours else f"{minutes}분"


def slot_summary(state):
    """Three short lines for a save slot: level and time, seals, and ending/notes."""
    flags = state.get("quest_flags", {}) or {}
    seals = sum(1 for key in SHRINES if flags.get(key))
    cycle = int(state.get("cycle", 1))
    prefix = f"{cycle}회차 · " if cycle > 1 else ""
    lines = [f"{prefix}레벨 {state.get('level', 1)} · {format_play_time(state.get('play_time', 0))}",
             f"인장 {seals}/{len(SHRINES)} · {DIFFICULTIES.get(state.get('difficulty'), DIFFICULTIES['normal'])['name']}"]
    if flags.get("abyss_lord"):
        lines.append("★ 엔딩 · 심연 정복")
    elif flags.get("final_boss"):
        lines.append("★ 엔딩 달성")
    else:
        lines.append(f"HP {state.get('hp', 0)}/{state.get('max_hp', 0)}")
    return lines

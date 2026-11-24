"""The 'next goal' hint shown on the map page, derived from story flags."""

from gameplay.world_data import NORTH_UNLOCK

SHRINE_PLACES = (("shrine_wind", "동쪽 바람의 제단"), ("shrine_earth", "서쪽 대지의 폐광"),
                 ("shrine_fire", "남쪽 불꽃의 신전"), ("shrine_ice", "북쪽 얼음 제단"))


def next_objective(field):
    flags = field.quest_flags
    if not flags.get("prologue_done"):
        return "광장 가운데 촌장 발렌의 집에 들어가 이야기를 들으세요."
    cleared = sum(1 for key, _ in SHRINE_PLACES if flags.get(key))
    north_open = cleared >= NORTH_UNLOCK or flags.get("shrine_ice")
    remaining = [name for key, name in SHRINE_PLACES if not flags.get(key)
                 and (key != "shrine_ice" or north_open)]
    if remaining and not flags.get("star_sword_awakened"):
        hint = "" if north_open else " (북쪽 길은 제단 두 곳을 정화하면 열립니다)"
        return "남은 제단을 정화하세요: " + ", ".join(remaining) + hint
    if not flags.get("star_sword_awakened"):
        return "네 인장을 광장의 별빛 분수에 바치세요."
    if not flags.get("final_boss"):
        return "별빛 분수 앞에서 흑기사 말포스와 결전을 치르세요."
    if not flags.get("abyss_lord"):
        return "북쪽 별빛 제단 아래, 별빛 심연의 군주를 물리치세요."
    return "모든 모험을 마쳤습니다. 오크밸리를 자유롭게 둘러보세요!"

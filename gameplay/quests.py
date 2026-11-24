"""Villager requests: one table holds the name, goal, dialogue and reward of every request.

Fields
  name           shown on the status screen
  target         how many things to gather/defeat
  kill           enemy id counted on each victory (None when progress comes from elsewhere,
                 e.g. picking moon herbs or finding the old sword)
  requires_item  quest item that must be in the bag to hand the request in
  offer / done   dialogue when offering / when handing in
  reward         gold, potions, high_potions, atk, defense, accessory, quest_item

Who gives each request (and when) stays in the scene that owns the NPC.
"""

QUESTS = {
    "sq_moon_herb": {
        "name": "달빛 약초", "target": 3, "kill": None,
        "offer": ["콜록콜록... 마물들 때문에 동쪽 숲길에 못 나간 지 오래라네.",
                  "반짝이는 달빛 약초 3송이만 구해다 주겠나?"],
        "done": ["오오, 이 은은한 향기! 고맙네 젊은이.", "특제 고급 회복약 두 병을 받아두게."],
        "reward": {"gold": 100, "high_potions": 2},
    },
    "sq_old_sword": {
        "name": "노기사의 검", "target": 1, "kill": None, "requires_item": "broken_old_sword",
        "offer": ["젊은 시절 서쪽 폐광에서 마물과 싸우다 내 검을 잃어버렸지...",
                  "폐광 1층 어딘가에 남아있을 텐데, 찾아줄 수 있겠나?"],
        "done": ["이 흠집... 틀림없는 내 검이야. 이제 미련을 놓을 수 있겠군.",
                 "현역 시절 휘장을 자네에게 물려주겠네."],
        "reward": {"atk": 4, "defense": 4, "quest_item": "knights_crest"},
    },
    "sq_goblin_hunt": {
        "name": "고블린 소탕", "target": 5, "kill": "goblin",
        "offer": ["이봐, 모험가! 협곡 길목에 고블린 척후병 놈들이 진을 치고 있어.",
                  "5마리만 혼내주면 두둑히 사례하지!"],
        "done": ["속이 다 시원하군! 약속한 보수야.", "로건 가게에서 장비를 맞추도록 해."],
        "reward": {"gold": 180, "potions": 3},
    },
    "sq_wolf_hunt": {
        "name": "숲의 사냥꾼", "target": 4, "kill": "wolf",
        "offer": ["광장 주민: 요즘 숲늑대들이 밤마다 울어서 잠을 못 자요...",
                  "동쪽 숲길의 숲늑대 4마리만 쫓아 주시면 할아버지의 부적을 드릴게요!"],
        "done": ["광장 주민: 어젯밤엔 푹 잤어요! 정말 고마워요.",
                 "할아버지의 늑대 송곳니 부적이에요. 급소가 잘 보인대요! (상점에서 장착)"],
        "reward": {"gold": 60, "accessory": "wolf_fang_charm"},
    },
    "sq_magma_ore": {
        "name": "용암석 수집", "target": 3, "kill": "magma_slime",
        "offer": ["로건: 아, 마침 잘 왔네! 남쪽 화산의 마그마 슬라임 몸속엔 좋은 용암석이 있지.",
                  "3마리만 잡아서 가져다주면 팔찌를 하나 만들어 주겠네."],
        "done": ["로건: 이 열기 좀 보게! 최고의 용암석이야.", "용암석 팔찌일세. 불길도 막아 주지. 노점에서 장착하게."],
        "reward": {"gold": 100, "accessory": "ember_bracelet"},
    },
    "sq_bat_hunt": {
        "name": "동굴 소탕", "target": 4, "kill": "bat",
        "offer": ["검을 찾아 준 자네라면 믿을 수 있지. 하나만 더 부탁하세.",
                  "바람의 제단 1층에 동굴 박쥐가 들끓어 순례자들이 못 들어간다네. 4마리만 잡아 주게."],
        "done": ["순례자들이 다시 제단을 찾는다는군. 역시 내가 사람 보는 눈은 있어.",
                 "기사단 시절의 수호자의 훈장일세. 자네가 지녀 주게."],
        "reward": {"accessory": "guardian_medal"},
    },
    "sq_frost_hunt": {
        "name": "고원의 정령", "target": 4, "kill": "frost_wisp",
        "offer": ["사냥꾼 하른: 쉿, 조용히... 서리 정령들이 사냥감을 전부 얼려 버렸다네.",
                  "정령 4마리만 흩어 주면, 얼음 속에서 캐낸 귀한 보석을 주지."],
        "done": ["사냥꾼 하른: 고원이 다시 숨을 쉬는군. 고맙네, 젊은이.",
                 "얼음 심장일세. 지니고 있으면 냉기가 몸을 얼리지 못하지. (상점에서 장착)"],
        "reward": {"gold": 120, "accessory": "frost_heart"},
    },
}


def kill_quests():
    """{quest id: enemy id} for requests advanced by defeating enemies."""
    return {quest_id: quest["kill"] for quest_id, quest in QUESTS.items() if quest.get("kill")}

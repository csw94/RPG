"""Interiors for Marta's herb cottage, Garen's quarters and the chief's house."""

import pygame

from gameplay.world_data import SHRINES
from scenes.field_scene import FieldScene
from settings import HEIGHT, TILE_SIZE, WIDTH
from utils.interior_art import interior_sprite
from utils.pixel_art import NPC_SIZE, PALETTE, hero_sprite, walk_frame, sprite, npc_sprite


def _item(name, x, y, w=1, h=1, solid=True):
    return {"sprite": name, "x": x, "y": y, "w": w, "h": h, "solid": solid}


# Every house shares one compact room. Furniture standing against the back wall is two
# tiles tall (its top half overlaps the wall face); only the floor half is solid.
# Both the drawing and the collision are derived from these lists.
LAYOUTS = {
    "village_house_1": {  # Marta's herb cottage
        "wall": "wall_cottage",
        "items": (
            _item("window", 9, 1, 1, 2, False), _item("window", 16, 1, 1, 2, False),
            _item("herb_shelf", 5, 2, 2, 2), _item("bookshelf", 12, 2, 2, 2),
            _item("bed_green", 18, 2, 2, 3),
            _item("rug_green_3x2", 11, 10, 3, 2, False),
            _item("worktable", 8, 5, 2, 2), _item("cauldron", 5, 6), _item("jars", 5, 8),
            _item("crate", 5, 9), _item("table", 14, 8, 2, 2),
            _item("chair_right", 13, 8), _item("chair_left", 16, 8),
            _item("barrel", 19, 7), _item("plant_pot", 19, 6),
            _item("plant_pot", 5, 13), _item("plant_pot", 19, 13),
        ),
    },
    "village_house_2": {  # Garen's quarters
        "wall": "wall_stone",
        "items": (
            _item("window", 8, 1, 1, 2, False), _item("window", 16, 1, 1, 2, False),
            _item("banner", 10, 1, 1, 2, False), _item("banner", 14, 1, 1, 2, False),
            _item("bed_red", 5, 2, 2, 3), _item("chest", 7, 3),
            _item("fireplace", 11, 2, 3, 2), _item("weapon_rack", 17, 2, 2, 2),
            _item("barrel", 19, 3), _item("crate", 19, 4),
            _item("rug_blue_5x3", 10, 6, 5, 3, False),
            _item("armor_stand", 5, 8, 1, 2), _item("armor_stand", 19, 8, 1, 2),
            _item("map_table", 15, 10, 3, 2), _item("chair_right", 14, 10),
            _item("plant_pot", 5, 13), _item("barrel", 19, 13),
        ),
    },
    "village_inn": {  # Rosa's Sleepy Bear: hearth, dining tables, a guest bed
        "wall": "wall_cottage",
        "items": (
            _item("window", 9, 1, 1, 2, False), _item("window", 16, 1, 1, 2, False),
            _item("fireplace", 5, 2, 3, 2), _item("bed_green", 18, 2, 2, 3),
            _item("barrel", 14, 3), _item("barrel", 15, 3),
            _item("table", 6, 8, 2, 2), _item("chair_right", 5, 8), _item("chair_left", 8, 8),
            _item("table", 16, 8, 2, 2), _item("chair_right", 15, 8), _item("chair_left", 18, 8),
            _item("rug_red_3x2", 11, 9, 3, 2, False),
            _item("plant_pot", 5, 13), _item("plant_pot", 19, 13), _item("crate", 19, 11),
        ),
    },
    "village_smithy": {  # Bron's forge: furnace, racks of blades and armour
        "wall": "wall_stone",
        "items": (
            _item("fireplace", 5, 2, 3, 2), _item("weapon_rack", 8, 2, 2, 2),
            _item("weapon_rack", 15, 2, 2, 2), _item("armor_stand", 18, 2, 1, 2), _item("armor_stand", 19, 2, 1, 2),
            _item("worktable", 7, 6, 2, 2), _item("barrel", 5, 9), _item("barrel", 19, 9),
            _item("crate", 5, 10), _item("crate", 19, 10), _item("chest", 17, 6),
            _item("banner", 11, 1, 1, 2, False), _item("banner", 13, 1, 1, 2, False),
        ),
    },
    "village_library": {  # Edel's library: shelves on every wall, a reading table
        "wall": "wall_plaster",
        "items": (
            _item("bookshelf", 5, 2, 2, 2), _item("bookshelf", 7, 2, 2, 2),
            _item("bookshelf", 15, 2, 2, 2), _item("bookshelf", 17, 2, 2, 2),
            _item("desk", 11, 4, 3, 2), _item("globe", 6, 6), _item("plant_pot", 19, 5),
            _item("map_table", 15, 9, 3, 2), _item("chair_right", 14, 9),
            _item("bookshelf", 5, 9, 2, 2), _item("rug_blue_5x3", 10, 8, 5, 3, False),
            _item("plant_pot", 5, 13), _item("plant_pot", 19, 13),
        ),
    },
    "village_apothecary": {  # Mira's shop: herb shelves, a bubbling cauldron
        "wall": "wall_cottage",
        "items": (
            _item("window", 10, 1, 1, 2, False),
            _item("herb_shelf", 5, 2, 2, 2), _item("cabinet", 7, 2, 2, 2),
            _item("herb_shelf", 15, 2, 2, 2), _item("herb_shelf", 17, 2, 2, 2),
            _item("worktable", 11, 4, 2, 2), _item("cauldron", 7, 7), _item("jars", 5, 7), _item("jars", 5, 9),
            _item("crate", 18, 9), _item("plant_pot", 19, 6),
            _item("rug_green_3x2", 11, 10, 3, 2, False),
            _item("plant_pot", 5, 13), _item("plant_pot", 19, 13),
        ),
    },
    "village_chief_house": {  # Chief Valen's office
        "wall": "wall_plaster",
        "items": (
            _item("window", 9, 1, 1, 2, False), _item("window", 15, 1, 1, 2, False),
            _item("wall_map", 11, 1, 3, 2, False),
            _item("bookshelf", 5, 2, 2, 2), _item("bookshelf", 7, 2, 2, 2),
            _item("bookshelf", 16, 2, 2, 2), _item("cabinet", 18, 2, 2, 2),
            _item("desk", 11, 4, 3, 2), _item("globe", 6, 5), _item("plant_pot", 19, 5),
            _item("rug_red_5x3", 10, 8, 5, 3, False),
            _item("bench", 5, 10, 2, 1), _item("chest", 19, 10),
            _item("plant_pot", 5, 13), _item("plant_pot", 19, 13),
        ),
    },
}


HOUSES = {  # title, resident sprite
    "village_house_1": ("약초상의 오두막", "villager"),
    "village_house_2": ("노기사 가렌의 거처", "old_knight"),
    "village_chief_house": ("촌장 발렌의 집", "chief"),
    "village_inn": ("여관 「졸린 곰」", "innkeeper"),
    "village_smithy": ("브론의 대장간", "blacksmith"),
    "village_library": ("별빛 도서관", "librarian"),
    "village_apothecary": ("미라의 물약 상점", "apothecary"),
}
# The district shops: which keeper stands behind each counter (see FieldScene.visit_keeper).
KEEPERS = {"village_inn": "inn", "village_smithy": "smithy", "village_library": "library",
           "village_apothecary": "apothecary"}
FLAVOUR = {
    "village_inn": "벽난로가 따뜻하게 타오르는 여관 식당입니다.",
    "village_smithy": "쇳물 냄새와 망치 소리가 가득한 대장간입니다.",
    "village_library": "오래된 종이 냄새가 나는 조용한 도서관입니다.",
    "village_apothecary": "약초와 물약 냄새가 은은하게 풍기는 가게입니다.",
}


class HouseInteriorScene(FieldScene):
    COLS, ROWS = 25, 16
    DOOR = (12, 14)
    ROOM = (5, 3, 19, 13)  # walkable floor: left, top, right, bottom (inclusive)

    def __init__(self, game, state=None):
        state = dict(state or {})
        self.house_id = state.get("world", "village_house_1")
        if self.house_id not in HOUSES:
            self.house_id = "village_house_1"
        state["world"] = self.house_id
        super().__init__(game, state)
        self.world = self.house_id
        self.encounter_rate = 0
        self.player.update(x=float(state.get("x", 12)), y=float(state.get("y", 12)))
        self.message = "SPACE로 주민과 대화하거나 문으로 나가세요."
        # Marta keeps the herb cottage; Garen lives alone in house 2; Valen in the chief's house.
        self.npcs = ((7, 6),) if self.house_id == "village_house_1" else ((12, 6),)
        self.solid_npcs = set(self.npcs)
        left, top, right, bottom = self.ROOM
        self.walls = {
            (x, y) for x in range(self.COLS) for y in range(self.ROWS)
            if not (left <= x <= right and top <= y <= bottom)
        }
        self.walls.discard(self.DOOR)
        self.layout = LAYOUTS[self.house_id]["items"]
        for item in self.layout:
            self.walls.update(self.solid_tiles(item))
        # Beds are free resting spots (Marta's cottage and Garen's quarters).
        self.bed = next((item for item in self.layout if item["sprite"].startswith("bed_")), None)
        self.walls.difference_update({(12, 13), *self.npcs})
        self._restore_player_position((12, 12))

    def solid_tiles(self, item):
        """Floor tiles a furniture item blocks (wall-face parts never count)."""
        if not item["solid"]:
            return set()
        top = self.ROOM[1]
        return {(x, y) for x in range(item["x"], item["x"] + item["w"])
                for y in range(max(top, item["y"]), item["y"] + item["h"])}

    def serialize(self):
        state = super().serialize()
        state["world"] = self.house_id
        return state

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.save_game()
                    self.game.enter_world("village", self._outside_door())
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_z):
                    if self.dialogue_lines:
                        self._press_dialogue()
                    else:
                        self._interact()
                elif event.key in (pygame.K_i, pygame.K_TAB) and not self.dialogue_lines:
                    self.game.open_status()
                elif event.key == pygame.K_b and not self.dialogue_lines:
                    self.game.open_status("bag")
                elif event.key == pygame.K_o and not self.dialogue_lines:
                    self.game.open_settings()
                elif event.key == pygame.K_F5:
                    self.sfx("save")
                    self.game.save_game()
                    self.message = "진행 상황을 저장했습니다."
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(686, 536, 92, 38).collidepoint(event.pos):
                    self.sfx("save")
                    self.game.save_game()
                    self.message = "진행 상황을 저장했습니다."

    def _outside_door(self):
        from scenes.village_scene import VillageScene
        return VillageScene.HOUSE_EXITS[self.house_id]

    def _interact(self):
        x, y = self.player["x"], self.player["y"]
        if (x - self.DOOR[0]) ** 2 + (y - self.DOOR[1]) ** 2 <= 1.4:
            self.game.save_game()
            self.game.enter_world("village", self._outside_door())
            return
        near_npc = (x - self.npcs[0][0]) ** 2 + (y - self.npcs[0][1]) ** 2 <= 1.5
        if not near_npc and self._near_bed() and self.house_id in ("village_house_1", "village_house_2"):
            self._rest()
        elif self.house_id in KEEPERS:
            if near_npc:
                self.visit_keeper(KEEPERS[self.house_id])
            else:
                self.message = FLAVOUR[self.house_id]
        elif self.house_id == "village_house_1":
            if near_npc:
                self._offer_sidequest("sq_moon_herb")
            else:
                self.message = "침대와 약초 서랍이 놓인 작은 오두막입니다."
        elif self.house_id == "village_house_2":
            if near_npc:
                self._interact_garen()
            else:
                self.message = "낡은 갑옷과 왕국 깃발이 걸린 노기사의 거처입니다."
        elif near_npc:
            self._interact_chief()
        else:
            self.message = "마을 지도와 기록이 쌓인 촌장의 집무실입니다."

    def hud_title(self):
        return HOUSES[self.house_id][0]

    def map_markers(self):
        markers = [("door", self.DOOR)] + [("npc", p) for p in self.npcs]
        if self.bed and self.house_id in ("village_house_1", "village_house_2"):
            markers += [("bed", p) for p in self.solid_tiles(self.bed)]
        return markers

    def _near_bed(self):
        if not self.bed:
            return False
        x, y = self.player["x"], self.player["y"]
        return any((x - bx) ** 2 + (y - by) ** 2 <= 1.6 for bx, by in self.solid_tiles(self.bed))

    def _rest(self):
        healed = self.hp < self.max_hp or self.mp < self.max_mp
        self.hp, self.mp = self.max_hp, self.max_mp
        self.game.save_game()
        self.sfx("heal" if healed else "talk")
        if healed:
            self.show_dialogue(["포근한 침대에서 잠시 눈을 붙였다.", "HP와 MP가 모두 회복되었다. (저장 완료)"])
        else:
            self.show_dialogue(["아직은 피곤하지 않다. 침대는 언제든 쉬어 갈 수 있다."])

    def _interact_garen(self):
        quest = self.sub_quests["sq_old_sword"]
        if quest["status"] == "COMPLETED" and self.sub_quests["sq_bat_hunt"]["status"] != "COMPLETED":
            self._offer_sidequest("sq_bat_hunt")
        elif self.quest_flags["final_boss"] and quest["status"] == "COMPLETED":
            self.show_dialogue(["내 휘장을 단 기사가 마을을 구했군. 이보다 자랑스러울 수 없네."])
        elif self.quest_flags["final_boss"]:
            self.show_dialogue(["훌륭한 검술이었네, 수호 기사여. 젊은 날의 나를 보는 것 같군."])
        else:
            self._offer_sidequest("sq_old_sword")

    def _interact_chief(self):
        cleared = sum(self.quest_flags[key] for key in SHRINES)
        if self.quest_flags["final_boss"]:
            self.show_dialogue(["오크밸리의 수호 기사여, 그대 덕분에 별빛 결계가 다시 빛나고 있네.",
                                "...그런데 먼 땅의 결계들도 흔들린다는 소식이 들려오는군.",
                                "더 강해진 그대라면, 처음부터 다시 새 여정을 떠나 보겠나?"],
                               action="offer_new_game_plus")
        elif not self.quest_flags["prologue_done"]:
            self.quest_flags["prologue_done"] = 1
            if "rusty_sword" not in self.owned_weapons:
                self.owned_weapons.append("rusty_sword")
            self.weapon = "rusty_sword"
            self.potions = min(10, self.potions + 2)
            self.show_dialogue([
                "별빛 분수의 결계가 약해지고 마을 외곽에 마물들이 나타났네.",
                "동·서·남·북 네 제단의 봉인석을 정화해 마을을 지켜주게. 북쪽 길은 두 제단을 정화하면 얼음이 녹을 걸세.",
                "녹슨 철검과 회복약 두 개를 주겠네. 출발 전에 준비하게.",
            ])
            self.game.save_game()
        elif cleared == len(SHRINES):
            self.show_dialogue(["네 개의 인장을 모두 모았구나. 광장의 별빛 분수에 바치게."])
        elif cleared:
            self.show_dialogue(["정화한 제단의 빛이 돌아오고 있네. 나머지 길도 조심해서 다녀오게."])
        else:
            self.show_dialogue(["동·서·남 제단은 원하는 순서로 공략해도 좋네. 마을 사람들의 부탁도 살펴보게."])

    def _advance_dialogue(self):
        if self.dialogue_lines:
            next_index = self.dialogue_index + 1
            if next_index >= len(self.dialogue_lines) and self.dialogue_action == "open_shop":
                self.dialogue_lines = []
                self.dialogue_index = 0
                self.dialogue_action = None
                self.game.open_shop()
                return
        super()._advance_dialogue()

    def update(self, dt):
        super().update(dt)


    def _draw_room(self, surface):
        t = TILE_SIZE
        left, top, right, bottom = self.ROOM
        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                surface.blit(interior_sprite(f"floor_{(x * 3 + y * 5) % 3}"), (x * t, y * t))
        wall = LAYOUTS[self.house_id]["wall"]
        for x in range(left, right + 1):
            surface.blit(interior_sprite(wall), (x * t, (top - 2) * t))
        # A soft shade along the foot of the back wall gives the room depth.
        shade = pygame.Surface(((right - left + 1) * t, 10), pygame.SRCALPHA)
        shade.fill((40, 26, 30, 60))
        surface.blit(shade, (left * t, top * t))
        # Thick wall tops seen from above frame the room; the doorway is cut into the front.
        rim, cap = PALETTE["outline"], (98, 74, 66)
        frame_top = (top - 2) * t - 12
        frame_bottom = (bottom + 1) * t + 12
        pygame.draw.rect(surface, rim, (left * t - 12, frame_top, (right - left + 1) * t + 24, 12))
        pygame.draw.rect(surface, rim, (left * t - 12, frame_top, 12, frame_bottom - frame_top))
        pygame.draw.rect(surface, rim, ((right + 1) * t, frame_top, 12, frame_bottom - frame_top))
        pygame.draw.rect(surface, rim, (left * t - 12, (bottom + 1) * t, (right - left + 1) * t + 24, 12))
        pygame.draw.rect(surface, cap, (left * t - 10, frame_top + 2, (right - left + 1) * t + 20, 3))
        dx, dy = self.DOOR
        surface.blit(interior_sprite("doorway"), (dx * t, dy * t))

    def _draw_window_light(self, surface):
        t = TILE_SIZE
        glow = pygame.Surface((3 * t, 3 * t), pygame.SRCALPHA)
        pygame.draw.polygon(glow, (255, 236, 170, 34), ((t, 0), (2 * t, 0), (3 * t, 3 * t), (0, 3 * t)))
        for item in self.layout:
            if item["sprite"] == "window":
                surface.blit(glow, ((item["x"] - 1) * t, self.ROOM[1] * t))

    def draw(self, surface):
        surface.fill((24, 18, 22))
        self._draw_room(surface)
        title, npc_name = HOUSES[self.house_id]
        t = TILE_SIZE
        flat = [item for item in self.layout if not item["solid"]]
        for item in flat:
            surface.blit(interior_sprite(item["sprite"]), (item["x"] * t, item["y"] * t))
        self._draw_window_light(surface)
        # Depth-sort furniture, the NPC and the hero by their bottom edge.
        actors = [(item["y"] + item["h"], 0, "item", item) for item in self.layout if item["solid"]]
        actors += [(y + 1, 1, "npc", (x, y)) for x, y in self.npcs]
        actors.append((self.player["y"] + 1, 1, "hero", None))
        for _bottom, _order, kind, data in sorted(actors, key=lambda a: (a[0], a[1])):
            if kind == "item":
                surface.blit(interior_sprite(data["sprite"]), (data["x"] * t, data["y"] * t))
            elif kind == "npc":
                surface.blit(sprite("shadow", (26, 10)), (data[0] * t + 3, (data[1] + 1) * t - 7))
                surface.blit(npc_sprite(npc_name, NPC_SIZE, self.portal_clock, data[0]), (data[0] * t, data[1] * t - 16))
            else:
                px = round(self.player["x"] * t + t / 2)
                py = round((self.player["y"] + 1) * t)
                surface.blit(sprite("shadow", (26, 10)), (px - 13, py - 7))
                surface.blit(hero_sprite(self.weapon, self.armor, (t, t + 16), self.facing,
                                         walk_frame(self.walk_clock)),
                             (px - t // 2, py - t - 16))
        self._draw_hud(surface, title)
        self._draw_dialogue(surface)

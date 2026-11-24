"""Scrolling top-down overworld with continuous movement and tile collision."""

import math
import random

import pygame

from scenes.base_scene import BaseScene
from settings import HEIGHT, TILE_SIZE, WIDTH
from utils.pixel_art import NPC_SIZE, hero_sprite, sprite
from gameplay.equipment import ARMORS, WEAPONS
from gameplay.world_data import FIELD_ROUTES


class FieldScene(BaseScene):
    # The overworld is larger than the view; town and dungeon scenes override these.
    COLS, ROWS = 40, 24
    VIEW_HEIGHT = 512
    PLAYER_RADIUS = 0.25
    NPC_RADIUS = 0.70
    WALK_SPEED = 4.6  # map tiles per second

    def __init__(self, game, state=None):
        super().__init__(game)
        state = state or {}
        self.world = state.get("world", "field")
        self.route_data = FIELD_ROUTES.get(self.world)
        self.toby_position = self.route_data.get("toby") if self.route_data else ((7, 12) if self.world == "field" else None)
        self.player = {"x": float(state.get("x", 2)), "y": float(state.get("y", 2))}
        self.hp = int(state.get("hp", 100))
        self.max_hp = int(state.get("max_hp", 100))
        self.mp = int(state.get("mp", 10))
        self.max_mp = int(state.get("max_mp", 10))
        self.level = int(state.get("level", 1))
        self.xp = int(state.get("xp", 0))
        self.potions = int(state.get("potions", 0))
        self.high_potions = int(state.get("high_potions", 0))
        self.gold = int(state.get("gold", 0))
        self.atk = int(state.get("atk", 15))
        self.defense = int(state.get("defense", state.get("def", 5)))
        self.evasion_bonus = int(state.get("evasion_bonus", 0))
        self.quest_flags = {key: int(value) for key, value in state.get("quest_flags", {}).items()}
        for key in ("prologue_done", "shrine_wind", "shrine_earth", "shrine_fire", "star_sword_awakened", "final_boss"):
            self.quest_flags.setdefault(key, 0)
        quest_targets = {"sq_moon_herb": 3, "sq_old_sword": 1, "sq_goblin_hunt": 5}
        saved_quests = state.get("sub_quests", {})
        self.sub_quests = {
            quest_id: {"status": saved_quests.get(quest_id, {}).get("status", "NOT_STARTED"),
                       "progress": int(saved_quests.get(quest_id, {}).get("progress", 0)),
                       "target": target}
            for quest_id, target in quest_targets.items()
        }
        self.collected_herbs = {tuple(point) for point in state.get("collected_herbs", ())}
        self.weapon = state.get("weapon", "rusty_sword")
        self.armor = state.get("armor", "traveler_clothes")
        self.owned_weapons = list(state.get("owned_weapons", ["rusty_sword"]))
        self.owned_armors = list(state.get("owned_armors", ["traveler_clothes"]))
        self.quest_items = set(state.get("quest_items", ()))
        saved_opened = state.get("opened_by_world", {})
        self.opened_by_world = {
            world: {tuple(position) for position in positions}
            for world, positions in saved_opened.items()
        } if isinstance(saved_opened, dict) else {}
        if not self.opened_by_world and state.get("opened"):
            self.opened_by_world["field"] = {tuple(position) for position in state["opened"]}
        self.opened = self.opened_by_world.setdefault(self.world, set())
        self.message = "WASD \ub610\ub294 \ubc29\ud5a5\ud0a4\ub85c \uc774\ub3d9 \u00b7 \uc2a4\ud398\uc774\uc2a4\ub85c \uc0c1\ud638\uc791\uc6a9"
        self.facing = "down"
        self.walk_clock = 0.0
        self.portal_clock = 0.0
        self.encounter_rate = 0.10
        self.enemy_pool = ("slime", "goblin")
        self.chests = {}
        self.trees = set()
        self.rocks = set()
        self.water = set()
        self.lava = set()
        self.bridge = set()
        self.path = set()
        self.solid_npcs = set()
        self.dialogue_lines = []
        self.dialogue_index = 0
        self.dialogue_action = None
        self.pending_dialogue = None
        self.pending_epilogue = False
        self.altar_positions = {}
        self.herb_positions = set()
        self.walls = set()
        self._build_map()
        if self.route_data:
            self.encounter_rate = self.route_data["encounter_rate"]
            self.enemy_pool = self.route_data["enemy_pool"]
            self.herb_positions = set(self.route_data["herbs"])
            self.message = f"{self.route_data['name']} · 제단 입구를 찾아보세요."
            if self.toby_position:
                self.solid_npcs.add(self.toby_position)
                self.walls.discard(self.toby_position)
        safe_spawns = {"field": (2, 2), "village": (12, 13), "dungeon": (3, 14)}
        safe_spawns.update({map_id: data["village_spawn"] for map_id, data in FIELD_ROUTES.items()})
        self.position_recovered = self._restore_player_position(safe_spawns.get(self.world, (2, 2)))
        if self.position_recovered:
            self.message = "\uc800\uc7a5\ub41c \uc704\uce58\uac00 \ub9c9\ud600 \uc788\uc5b4 \uc548\uc804\ud55c \uc7a5\uc18c\ub85c \uc774\ub3d9\ud588\uc2b5\ub2c8\ub2e4."

    def _build_map(self):
        self.walls = {
            (x, y) for x in range(self.COLS) for y in range(self.ROWS)
            if x == 0 or y == 0 or x == self.COLS - 1 or y == self.ROWS - 1
        }
        if self.route_data:
            self._build_route_map()
            return
        if self.world != "field":
            return

        # Hand-laid trails curve between the village gate, clearing and dungeon.
        self._add_path(((2, 2), (5, 3), (8, 5), (11, 5), (12, 3), (12, 1)), 0.9)
        self._add_path(((11, 5), (14, 7), (17, 9), (18, 12), (22, 13), (27, 15), (31, 18), (37, 19)), 1.1)
        self._add_path(((18, 12), (18, 8), (20, 6)), 0.75)
        self._add_path(((22, 13), (22, 17), (25, 20)), 0.8)
        self._add_path(((18, 12), (23, 9), (27, 6), (31, 5)), 0.9)
        self._add_path(((11, 5), (8, 8), (6, 13), (4, 17)), 0.9)
        self._add_path(((22, 17), (22, 21)), 0.9)
        self.altar_positions = {
            "shrine_wind": (31, 5),
            "shrine_earth": (4, 17),
            "shrine_fire": (22, 21),
        }

        # Small lake in the western glade and a winding river on the eastern edge.
        lake = {
            (5, 10), (6, 10), (7, 10), (4, 11), (5, 11), (6, 11), (7, 11), (8, 11),
            (4, 12), (5, 12), (6, 12), (7, 12), (8, 12), (5, 13), (6, 13), (7, 13),
        }
        river = set()
        for y in range(1, self.ROWS - 1):
            center = 34 + round(math.sin(y * 0.43) * 1.4)
            river.update((x, y) for x in range(center - 1, center + 2))
        self.water = (lake | river) - self.path
        self.bridge = {(x, y) for x in range(32, 37) for y in (18, 19)}
        self.water.difference_update(self.bridge)

        # Groves have soft, irregular outlines and leave room around trails and landmarks.
        rng = random.Random(73152)
        groves = (
            (2, 17, 8, 5), (14, 2, 6, 4), (23, 2, 7, 5),
            (27, 7, 5, 5), (36, 3, 3, 6), (2, 21, 5, 2),
            (25, 20, 7, 3), (36, 19, 3, 4), (9, 14, 4, 5),
        )
        landmarks = {(2, 2), (12, 1), (22, 13), (5, 4), (18, 6), (20, 12), (30, 20), *self.altar_positions.values()}
        for gx, gy, gw, gh in groves:
            for y in range(gy, min(gy + gh, self.ROWS - 1)):
                for x in range(gx, min(gx + gw, self.COLS - 1)):
                    if ((x - gx - gw / 2) / max(1, gw / 2)) ** 2 + ((y - gy - gh / 2) / max(1, gh / 2)) ** 2 > 1.25:
                        continue
                    if (x, y) in self.path or (x, y) in self.water or (x, y) in landmarks:
                        continue
                    if rng.random() > 0.76:
                        continue
                    self.trees.add((x, y))

        self.rocks = {(10, 10), (3, 15), (15, 14), (24, 8), (29, 17), (31, 21), (7, 18)}
        self.rocks = {p for p in self.rocks if p not in self.path and p not in self.water and p not in self.trees}
        self.walls.update(self.trees)
        self.walls.update(self.rocks)
        self.walls.update(self.water)
        self.walls.difference_update(self.bridge)
        self.chests = {(5, 4): "potion", (18, 6): "gold", (20, 12): "potion", (30, 20): "high_potion"}

    def _build_route_map(self):
        data = self.route_data
        self._add_path(data["path"], 1.05)
        landmarks = {data["village_portal"], data["dungeon_portal"], *data["herbs"], *data["chests"]}
        if data.get("toby"):
            landmarks.add(data["toby"])
        rng = random.Random({"field_east": 1103, "field_west": 2207, "field_south": 3301}[self.world])
        if data["theme"] == "forest":
            for gx, gy, gw, gh in data["groves"]:
                for ty in range(gy, min(gy + gh, self.ROWS - 1)):
                    for tx in range(gx, min(gx + gw, self.COLS - 1)):
                        if (tx, ty) not in self.path and (tx, ty) not in landmarks and rng.random() < 0.42:
                            self.trees.add((tx, ty))
            self.water = {(7, 4), (8, 4), (9, 4), (9, 5), (10, 5), (10, 6),
                          (29, 14), (30, 14), (31, 14), (31, 15), (32, 15)} - self.path
        elif data["theme"] == "canyon":
            self.rocks = {(8, y) for y in range(2, 8)} | {(15, y) for y in range(13, 21)}
            self.rocks |= {(x, 3) for x in range(10, 18)} | {(x, 19) for x in range(24, 33)}
            self.rocks -= self.path | landmarks
        else:
            self.lava = {(x, y) for x in range(5, 10) for y in range(7, 11)}
            self.lava |= {(x, y) for x in range(24, 30) for y in range(12, 16)}
            self.lava |= {(17, 3), (18, 3), (18, 4), (19, 4)}
            self.lava -= self.path | landmarks
            self.rocks = {(x, 5) for x in range(5, 10)} | {(x, 18) for x in range(30, 37)}
            self.rocks -= self.path | landmarks
        self.walls.update(self.trees)
        self.walls.update(self.rocks)
        self.walls.update(self.water)
        self.walls.update(self.lava)
        self.chests = dict(data["chests"])
        self.herb_positions = set(data["herbs"])

    def _add_path(self, points, radius):
        for start, end in zip(points, points[1:]):
            steps = max(abs(end[0] - start[0]), abs(end[1] - start[1]), 1) * 3
            for step in range(steps + 1):
                t = step / steps
                cx = start[0] + (end[0] - start[0]) * t
                cy = start[1] + (end[1] - start[1]) * t
                reach = math.ceil(radius)
                for y in range(round(cy) - reach, round(cy) + reach + 1):
                    for x in range(round(cx) - reach, round(cx) + reach + 1):
                        if (x - cx) ** 2 + (y - cy) ** 2 <= radius * radius + 0.4:
                            if 0 < x < self.COLS - 1 and 0 < y < self.ROWS - 1:
                                self.path.add((x, y))

    @property
    def theme(self):
        return self.route_data["theme"] if self.route_data else "forest"

    def ground_tile(self, tx, ty):
        prefix = {"canyon": "canyon", "volcanic": "ash"}.get(self.theme, "grass")
        return f"{prefix}_{(tx * 17 + ty * 23) % 16}"

    def tree_kind(self, position):
        x, y = position
        return ("tree_round", "tree_round", "tree_fruit", "tree_pine")[(x * 5 + y * 3) % 4]

    def rock_kind(self, position):
        x, y = position
        prefix = {"volcanic": "basalt", "canyon": "rock"}.get(self.theme, "mossrock")
        return f"{prefix}_{(x * 7 + y * 5) % 3}"

    def field_decals(self):
        """Walkable ground details per theme, kept off everything the player interacts with."""
        if getattr(self, "_decals", None) is None:
            busy = (self.walls | self.path | set(self.chests) | self.herb_positions
                    | self.water | self.lava | self.bridge | set(self.altar_positions.values()))
            if self.route_data:
                busy |= {self.route_data["village_portal"], self.route_data["dungeon_portal"]}
            if self.toby_position:
                busy.add(self.toby_position)
            names = {
                "forest": ("flower_patch", "tuft", "flower_patch_1", "tuft", "pebbles"),
                "canyon": ("dry_tuft", "dry_tuft", "dry_tuft"),
                "volcanic": ("ember", "ember", "pebbles"),
            }[self.theme]
            decals = {}
            for y in range(1, self.ROWS - 1):
                for x in range(1, self.COLS - 1):
                    if (x, y) in busy:
                        continue
                    roll = (x * 73 + y * 151 + x * y * 17) % 19
                    if roll in (0, 11):
                        decals[(x, y)] = names[(x * 3 + y) % len(names)]
            self._decals = decals
        return self._decals

    def serialize(self):
        opened_by_world = {
            world: [list(position) for position in sorted(positions)]
            for world, positions in self.opened_by_world.items()
        }
        opened_by_world[self.world] = [list(position) for position in sorted(self.opened)]
        return {**self.player, "world": self.world, "hp": self.hp, "max_hp": self.max_hp,
                "mp": self.mp, "max_mp": self.max_mp, "level": self.level, "xp": self.xp,
                "potions": self.potions, "high_potions": self.high_potions, "gold": self.gold,
                "atk": self.atk, "defense": self.defense, "evasion_bonus": self.evasion_bonus,
                "quest_flags": self.quest_flags, "weapon": self.weapon,
                "armor": self.armor, "owned_weapons": self.owned_weapons,
                "owned_armors": self.owned_armors, "quest_items": sorted(self.quest_items),
                "sub_quests": self.sub_quests,
                "collected_herbs": [list(point) for point in sorted(self.collected_herbs)],
                "opened": sorted(self.opened),
                "opened_by_world": opened_by_world}

    @property
    def attack_power(self):
        return self.atk + WEAPONS.get(self.weapon, WEAPONS["rusty_sword"])["attack"]

    @property
    def defense_power(self):
        return self.defense + ARMORS.get(self.armor, ARMORS["traveler_clothes"])["defense"]

    def show_dialogue(self, lines, action=None):
        self.dialogue_lines = list(lines)
        self.dialogue_index = 0
        self.dialogue_action = action

    def _advance_dialogue(self):
        if not self.dialogue_lines:
            return
        self.dialogue_index += 1
        if self.dialogue_index < len(self.dialogue_lines):
            return
        action = self.dialogue_action
        self.dialogue_lines = []
        self.dialogue_index = 0
        self.dialogue_action = None
        if action and action.startswith("accept_subquest:"):
            quest_id = action.split(":", 1)[1]
            self.sub_quests[quest_id]["status"] = "IN_PROGRESS"
            self.game.save_game()
            return
        if action and action.startswith("complete_subquest:"):
            self._complete_sidequest(action.split(":", 1)[1])
            return
        if action == "open_shop":
            self.game.open_shop()
        elif action == "final_boss":
            self.game.start_battle("final_boss")
        elif action == "epilogue":
            self.game.start_epilogue()

    def _offer_sidequest(self, quest_id):
        quest = self.sub_quests[quest_id]
        status, progress, target = quest["status"], quest["progress"], quest["target"]
        if status == "NOT_STARTED":
            lines, action = {
                "sq_moon_herb": (["콜록콜록... 마물들 때문에 동쪽 숲길에 못 나간 지 오래라네.",
                                  "반짝이는 달빛 약초 3송이만 구해다 주겠나?"], "accept_subquest:sq_moon_herb"),
                "sq_old_sword": (["젊은 시절 서쪽 폐광에서 마물과 싸우다 내 검을 잃어버렸지...",
                                  "폐광 1층 어딘가에 남아있을 텐데, 찾아줄 수 있겠나?"], "accept_subquest:sq_old_sword"),
                "sq_goblin_hunt": (["이봐, 모험가! 협곡 길목에 고블린 척후병 놈들이 진을 치고 있어.",
                                    "5마리만 혼내주면 두둑히 사례하지!"], "accept_subquest:sq_goblin_hunt"),
            }[quest_id]
            self.show_dialogue(lines, action)
        elif status == "IN_PROGRESS" and progress >= target:
            ready = quest_id != "sq_old_sword" or "broken_old_sword" in self.quest_items
            if ready:
                lines, action = {
                    "sq_moon_herb": (["오오, 이 은은한 향기! 고맙네 젊은이.",
                                      "특제 고급 회복약 두 병을 받아두게."], "complete_subquest:sq_moon_herb"),
                    "sq_old_sword": (["이 흠집... 틀림없는 내 검이야. 이제 미련을 놓을 수 있겠군.",
                                      "현역 시절 휘장을 자네에게 물려주겠네."], "complete_subquest:sq_old_sword"),
                    "sq_goblin_hunt": (["속이 다 시원하군! 약속한 보수야.",
                                        "로건 가게에서 장비를 맞추도록 해."], "complete_subquest:sq_goblin_hunt"),
                }[quest_id]
                self.show_dialogue(lines, action)
            else:
                self.show_dialogue([f"진행 상황 {progress}/{target}. 목표를 마치고 다시 오게."])
        elif status == "IN_PROGRESS":
            self.show_dialogue([f"부탁한 일의 진행 상황은 {progress}/{target}이라네."])
        else:
            self.show_dialogue(["도와줘서 고맙네. 보답은 이미 전했어."])

    def _complete_sidequest(self, quest_id):
        quest = self.sub_quests[quest_id]
        if quest["status"] != "IN_PROGRESS" or quest["progress"] < quest["target"]:
            return False
        if quest_id == "sq_moon_herb":
            self.gold += 100
            self.high_potions = min(10, self.high_potions + 2)
        elif quest_id == "sq_old_sword":
            if "broken_old_sword" not in self.quest_items:
                return False
            self.atk += 4
            self.defense += 4
            self.quest_items.add("knights_crest")
        elif quest_id == "sq_goblin_hunt":
            self.gold += 180
            self.potions = min(10, self.potions + 3)
        quest["status"] = "COMPLETED"
        self.game.save_game()
        return True

    def _interact_sidequest_npc(self, quest_id, position):
        x, y = self.player["x"], self.player["y"]
        if (x - position[0]) ** 2 + (y - position[1]) ** 2 > 1.2:
            return False
        self._offer_sidequest(quest_id)
        return True

    def clear_shrine(self, shrine_key):
        if shrine_key not in ("shrine_wind", "shrine_earth", "shrine_fire"):
            return False
        if self.quest_flags[shrine_key]:
            return False
        self.quest_flags[shrine_key] = 1
        self.level += 1
        self.max_hp += 30
        self.hp = self.max_hp
        self.atk += 5
        self.defense += 3
        if shrine_key == "shrine_wind":
            self.evasion_bonus = 15
        elif shrine_key == "shrine_earth":
            self.max_hp += 50
            self.hp = self.max_hp
            self.defense += 5
        else:
            self.atk += 10
        self.game.save_game()
        return True

    def check_fountain_awakening(self):
        required = ("shrine_wind", "shrine_earth", "shrine_fire")
        if not all(self.quest_flags[key] for key in required):
            return False
        if not self.quest_flags["star_sword_awakened"]:
            self.quest_flags["star_sword_awakened"] = 1
            self.weapon = "star_sword"
            if "star_sword" not in self.owned_weapons:
                self.owned_weapons.append("star_sword")
            self.game.save_game()
        return True

    def resolve_battle_victory(self, enemy_id):
        from gameplay.enemies import ENEMIES

        enemy = ENEMIES[enemy_id]
        self.gold += enemy["gold"]
        if enemy["potion_drop"] and self.potions < 10:
            self.potions = min(10, self.potions + enemy["potion_drop"])
        if enemy_id in ("shrine_wind", "shrine_earth", "shrine_fire"):
            self.clear_shrine(enemy_id)
        if enemy_id == "goblin":
            quest = self.sub_quests["sq_goblin_hunt"]
            if quest["status"] == "IN_PROGRESS":
                quest["progress"] = min(quest["target"], quest["progress"] + 1)
        if enemy_id == "final_boss":
            self.quest_flags["final_boss"] = 1
            self.game.save_game()
            return "\uc5d4\ub529 \ud574\uae08 \u00b7 \uc655\uad6d \uae30\uc0ac \uc784\uba85"
        self.game.save_game()
        return f"\ubcf4\uc0c1: \uae08\ud654 {enemy['gold']}G" + (f", \ud68c\ubcf5\uc57d +{enemy['potion_drop']}" if enemy["potion_drop"] else "")


    def _blocked(self, x, y):
        radius = self.PLAYER_RADIUS
        min_distance = radius + self.NPC_RADIUS
        for npc_x, npc_y in self.solid_npcs:
            if (x - npc_x) ** 2 + (y - npc_y) ** 2 < min_distance ** 2:
                return True
        for chest_x, chest_y in self.chests:
            if (x - chest_x) ** 2 + (y - chest_y) ** 2 < min_distance ** 2:
                return True
        for px, py in ((x - radius, y - radius), (x + radius, y - radius),
                       (x - radius, y + radius), (x + radius, y + radius)):
            tx, ty = math.floor(px + 0.5), math.floor(py + 0.5)
            if not (0 <= tx < self.COLS and 0 <= ty < self.ROWS) or (tx, ty) in self.walls:
                return True
        return False

    def _restore_player_position(self, fallback):
        if self._blocked(self.player["x"], self.player["y"]):
            self.player.update(x=float(fallback[0]), y=float(fallback[1]))
            return True
        return False

    def _camera(self):
        center_x = self.player["x"] * TILE_SIZE + TILE_SIZE / 2
        center_y = self.player["y"] * TILE_SIZE + TILE_SIZE / 2
        max_x = max(0, self.COLS * TILE_SIZE - WIDTH)
        max_y = max(0, self.ROWS * TILE_SIZE - self.VIEW_HEIGHT)
        return (max(0, min(max_x, center_x - WIDTH / 2)),
                max(0, min(max_y, center_y - self.VIEW_HEIGHT / 2)))

    @staticmethod
    def _key_direction(keys):
        dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        if dx and dy:
            dx *= 0.70710678
            dy *= 0.70710678
        return dx, dy

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.save_game()
                    self.game.change_scene("title")
                elif event.key == pygame.K_SPACE:
                    if self.dialogue_lines:
                        self._advance_dialogue()
                    else:
                        self._interact()
                elif event.key == pygame.K_F5:
                    self.game.save_game()
                    self.message = "\uc9c4\ud589 \uc0c1\ud669\uc744 \uc800\uc7a5\ud588\uc2b5\ub2c8\ub2e4."
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(686, 536, 92, 38).collidepoint(event.pos):
                    self.game.save_game()
                    self.message = "\uc9c4\ud589 \uc0c1\ud669\uc744 \uc800\uc7a5\ud588\uc2b5\ub2c8\ub2e4."

    def _interact(self):
        px, py = self.player["x"], self.player["y"]
        if self.toby_position and self._interact_sidequest_npc("sq_goblin_hunt", self.toby_position):
            return
        nearest = min(self.chests, key=lambda p: (p[0] - px) ** 2 + (p[1] - py) ** 2, default=None)
        if nearest and (nearest[0] - px) ** 2 + (nearest[1] - py) ** 2 <= 1.15 and nearest not in self.opened:
            self._open_chest(nearest)
        elif self.world == "field" and self.altar_positions and min(
                (point[0] - px) ** 2 + (point[1] - py) ** 2 for point in self.altar_positions.values()) <= 1.35:
            altar = min(self.altar_positions, key=lambda key: (self.altar_positions[key][0] - px) ** 2 + (self.altar_positions[key][1] - py) ** 2)
            if self.quest_flags[altar]:
                self.message = "이 제단의 봉인석은 이미 정화되었습니다."
            else:
                dungeon_entries = {"shrine_wind": (3, 14), "shrine_earth": (12, 13),
                                   "shrine_fire": (21, 14)}
                self.game.enter_world(f"{altar}_1f", dungeon_entries[altar])
        elif self.route_data and self._near_point(self.route_data["dungeon_portal"], px, py, 1.25):
            self.game.enter_world(f"{self.route_data['shrine']}_1f", self.route_data["dungeon_spawn"])
        elif self.route_data and self._near_point(self.route_data["village_portal"], px, py, 1.25):
            self.game.enter_world("village", self.route_data["return_village"])
        elif self.herb_positions and any(
                point not in self.collected_herbs and (point[0] - px) ** 2 + (point[1] - py) ** 2 <= 1.2
                for point in self.herb_positions):
            herb = min((point for point in self.herb_positions if point not in self.collected_herbs),
                       key=lambda point: (point[0] - px) ** 2 + (point[1] - py) ** 2)
            quest = self.sub_quests["sq_moon_herb"]
            if quest["status"] == "IN_PROGRESS":
                self.collected_herbs.add(herb)
                quest["progress"] = min(quest["target"], quest["progress"] + 1)
                self.message = f"달빛 약초를 채집했습니다. {quest['progress']}/{quest['target']}"
                self.game.save_game()
            else:
                self.message = "달빛 약초입니다. 마르타의 부탁을 받고 채집할 수 있습니다."
        elif self.world == "field" and (px - 12) ** 2 + (py - 1) ** 2 <= 1.25:
            self.game.enter_world("village", (12, 14))
        else:
            self.message = "\uc8fc\ubcc0\uc5d0\ub294 \uc0c1\ud638\uc791\uc6a9\ud560 \ub300\uc0c1\uc774 \uc5c6\uc2b5\ub2c8\ub2e4."

    @staticmethod
    def _near_point(point, x, y, radius):
        return (point[0] - x) ** 2 + (point[1] - y) ** 2 <= radius ** 2

    def _open_chest(self, position):
        self.opened.add(position)
        if self.chests[position] == "potion":
            self.potions = min(10, self.potions + 1)
            self.message = "\uc0c1\uc790\ub97c \uc5f4\uc5b4 \ud3ec\uc158\uc744 \uc5bb\uc5c8\uc2b5\ub2c8\ub2e4!"
        elif self.chests[position] == "high_potion":
            self.high_potions = min(10, self.high_potions + 1)
            self.message = "\uc0c1\uc790\uc5d0\uc11c \uace0\uae09 \ud68c\ubcf5\uc57d\uc744 \uc5bb\uc5c8\uc2b5\ub2c8\ub2e4!"
        else:
            self.xp += 20
            self.gold += 25
            self.message = "\uc0c1\uc790\uc5d0\uc11c \uae08\ud654\uc640 \uacbd\ud5d8\uce58 20\uc744 \uc5bb\uc5c8\uc2b5\ub2c8\ub2e4!"
        self.game.save_game()

    def update(self, dt):
        self.portal_clock += dt
        keys = pygame.key.get_pressed()
        dx, dy = self._key_direction(keys)
        moving = bool(dx or dy)
        if moving:
            self.facing = "right" if dx > 0.25 else "left" if dx < -0.25 else "down" if dy > 0 else "up"
            distance = self.WALK_SPEED * dt
            nx, ny = self.player["x"] + dx * distance, self.player["y"] + dy * distance
            moved = False
            # Axis-separated collision keeps movement smooth along walls and tree trunks.
            if not self._blocked(nx, self.player["y"]):
                self.player["x"] = nx
                moved = True
            if not self._blocked(self.player["x"], ny):
                self.player["y"] = ny
                moved = True
            if moved:
                self.walk_clock += dt * 10
            else:
                self.walk_clock = 0.0
            if moved and self.encounter_rate and random.random() < self.encounter_rate * dt:
                self.game.start_battle(random.choice(self.enemy_pool))
        else:
            self.walk_clock = 0.0

    def _draw_ground(self, surface, camera_x, camera_y):
        start_x = max(0, int(camera_x // TILE_SIZE))
        end_x = min(self.COLS, int((camera_x + WIDTH) // TILE_SIZE) + 2)
        start_y = max(0, int(camera_y // TILE_SIZE))
        end_y = min(self.ROWS, int((camera_y + self.VIEW_HEIGHT) // TILE_SIZE) + 2)
        for ty in range(start_y, end_y):
            for tx in range(start_x, end_x):
                position = (tx, ty)
                rect = pygame.Rect(round(tx * TILE_SIZE - camera_x), round(ty * TILE_SIZE - camera_y), TILE_SIZE, TILE_SIZE)
                surface.blit(sprite(self.ground_tile(tx, ty), (TILE_SIZE, TILE_SIZE)), rect)
                if position in self.lava:
                    mask = ((1 if (tx, ty - 1) in self.lava else 0)
                            | (2 if (tx + 1, ty) in self.lava else 0)
                            | (4 if (tx, ty + 1) in self.lava else 0)
                            | (8 if (tx - 1, ty) in self.lava else 0)
                            | (16 if (tx + 1, ty - 1) in self.lava else 0)
                            | (32 if (tx + 1, ty + 1) in self.lava else 0)
                            | (64 if (tx - 1, ty + 1) in self.lava else 0)
                            | (128 if (tx - 1, ty - 1) in self.lava else 0))
                    surface.blit(sprite(f"lava_edge_{mask}_{(tx + ty + int(self.portal_clock * 2)) % 2}",
                                        (TILE_SIZE, TILE_SIZE)), rect)
                elif position in self.water:
                    mask = ((1 if (tx, ty - 1) in self.water else 0)
                            | (2 if (tx + 1, ty) in self.water else 0)
                            | (4 if (tx, ty + 1) in self.water else 0)
                            | (8 if (tx - 1, ty) in self.water else 0)
                            | (16 if (tx + 1, ty - 1) in self.water else 0)
                            | (32 if (tx + 1, ty + 1) in self.water else 0)
                            | (64 if (tx - 1, ty + 1) in self.water else 0)
                            | (128 if (tx - 1, ty - 1) in self.water else 0))
                    surface.blit(sprite(f"water_edge_{mask}_{(tx + ty) % 2}", (TILE_SIZE, TILE_SIZE)), rect)
                elif position in self.bridge:
                    pygame.draw.rect(surface, (111, 76, 48), rect)
                    pygame.draw.rect(surface, (178, 127, 75), rect.inflate(-5, -7))
                    pygame.draw.line(surface, (87, 58, 40), (rect.left + 3, rect.top + 8), (rect.right - 3, rect.top + 8), 2)
                    pygame.draw.line(surface, (87, 58, 40), (rect.left + 3, rect.bottom - 8), (rect.right - 3, rect.bottom - 8), 2)
                elif position in self.path:
                    mask = ((1 if (tx, ty - 1) in self.path else 0)
                            | (2 if (tx + 1, ty) in self.path else 0)
                            | (4 if (tx, ty + 1) in self.path else 0)
                            | (8 if (tx - 1, ty) in self.path else 0)
                            | (16 if (tx + 1, ty - 1) in self.path else 0)
                            | (32 if (tx + 1, ty + 1) in self.path else 0)
                            | (64 if (tx - 1, ty + 1) in self.path else 0)
                            | (128 if (tx - 1, ty - 1) in self.path else 0))
                    surface.blit(sprite(f"trail_{mask}_{(tx * 3 + ty) % 3}", (TILE_SIZE, TILE_SIZE)), rect)
                elif position in self.field_decals():
                    surface.blit(sprite(self.field_decals()[position], (TILE_SIZE, TILE_SIZE)), rect)

    def _draw_dialogue(self, surface):
        if not self.dialogue_lines:
            return
        box = pygame.Rect(38, 385, 724, 116)
        pygame.draw.rect(surface, self.game.colors["ink"], box.inflate(6, 6))
        pygame.draw.rect(surface, self.game.colors["gold"], box.inflate(2, 2))
        pygame.draw.rect(surface, self.game.colors["panel"], box)
        pygame.draw.rect(surface, self.game.colors["cream"], box, 1)
        line = self.dialogue_lines[self.dialogue_index]
        words, rows, current = line.split(), [], ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if self.game.font(18).size(candidate)[0] > box.width - 44 and current:
                rows.append(current)
                current = word
            else:
                current = candidate
        if current:
            rows.append(current)
        for index, row in enumerate(rows[:3]):
            self.text(surface, row, (box.x + 20, box.y + 17 + index * 25), 18, self.game.colors["cream"])
        self.text(surface, "SPACE  \ub2e4\uc74c", (box.right - 118, box.bottom - 27), 14, self.game.colors["gold"])


    def draw(self, surface):
        surface.fill(self.game.colors["ink"])
        camera_x, camera_y = self._camera()
        self._draw_ground(surface, camera_x, camera_y)

        start_x = max(0, int(camera_x // TILE_SIZE) - 1)
        end_x = min(self.COLS, int((camera_x + WIDTH) // TILE_SIZE) + 2)
        start_y = max(0, int(camera_y // TILE_SIZE) - 1)
        end_y = min(self.ROWS, int((camera_y + self.VIEW_HEIGHT) // TILE_SIZE) + 2)
        visible_objects = []
        visible_objects.extend((x, y, "tree") for x, y in self.trees)
        visible_objects.extend((x, y, "rock") for x, y in self.rocks)
        visible_objects.extend((x, y, "chest") for x, y in self.chests)
        visible_objects.extend((x, y, "moon_herb") for x, y in self.herb_positions
                               if (x, y) not in self.collected_herbs)
        if self.toby_position:
            visible_objects.append((*self.toby_position, "toby"))
        visible_objects.extend((x, y, key) for key, (x, y) in self.altar_positions.items())
        visible_objects.extend(((12, 1, "portal_town"),) if self.world == "field" else ())
        if self.route_data:
            visible_objects.extend((
                (*self.route_data["village_portal"], "portal_town"),
                (*self.route_data["dungeon_portal"], "portal_dungeon"),
            ))
        for x, y, kind in sorted(visible_objects, key=lambda obj: (obj[1], obj[0])):
            if not (start_x <= x < end_x and start_y <= y < end_y):
                continue
            sx, sy = round(x * TILE_SIZE - camera_x), round(y * TILE_SIZE - camera_y)
            if kind == "tree":
                surface.blit(sprite(self.tree_kind((x, y)), (48, 64)), (sx - 8, sy - 32))
            elif kind == "rock":
                surface.blit(sprite(self.rock_kind((x, y)), (TILE_SIZE, TILE_SIZE)), (sx, sy))
            elif kind == "chest":
                name = "chest_open" if (x, y) in self.opened else "chest"
                surface.blit(sprite(name, (TILE_SIZE, TILE_SIZE)), (sx, sy))
            elif kind in self.altar_positions:
                altar_name = kind.replace("shrine_", "altar_", 1)
                surface.blit(sprite(altar_name, (TILE_SIZE, TILE_SIZE)), (sx, sy))
            elif kind == "moon_herb":
                surface.blit(sprite("flower_yellow", (TILE_SIZE, TILE_SIZE)), (sx, sy))
            elif kind == "toby":
                surface.blit(sprite("shadow", (26, 10)), (sx + 3, sy + TILE_SIZE - 7))
                surface.blit(sprite("merchant", NPC_SIZE), (sx, sy - 16))
            else:
                portal_name = "gate_arch" if kind == "portal_town" else f"portal_dungeon_{int(self.portal_clock * 3) % 2}"
                surface.blit(sprite(portal_name, (48, 64)), (sx - 8, sy - 32))

        foot_x = round(self.player["x"] * TILE_SIZE + TILE_SIZE / 2 - camera_x)
        foot_y = round((self.player["y"] + 1) * TILE_SIZE - camera_y)
        surface.blit(sprite("shadow", (26, 10)), (foot_x - 13, foot_y - 7))
        frame = int(self.walk_clock) % 2 if self.walk_clock else 0
        surface.blit(hero_sprite(self.weapon, self.armor, (TILE_SIZE, TILE_SIZE + 16), self.facing, frame),
                     (foot_x - TILE_SIZE // 2, foot_y - TILE_SIZE - 16))
        for tx, ty in self.trees:
            if self.player["y"] < ty <= self.player["y"] + 1.2 and start_x <= tx < end_x and start_y <= ty < end_y:
                sx, sy = round(tx * TILE_SIZE - camera_x), round(ty * TILE_SIZE - camera_y)
                surface.blit(sprite(self.tree_kind((tx, ty)), (48, 64)), (sx - 8, sy - 32))

        # Keep quest herbs visible even when the player or a foreground canopy overlaps them.
        for hx, hy in self.herb_positions - self.collected_herbs:
            if start_x <= hx < end_x and start_y <= hy < end_y:
                sx, sy = round(hx * TILE_SIZE - camera_x), round(hy * TILE_SIZE - camera_y)
                pygame.draw.circle(surface, (245, 205, 84), (sx + TILE_SIZE // 2, sy + TILE_SIZE // 2), 13, 2)
                surface.blit(sprite("flower_yellow", (22, 22)), (sx + 5, sy + 5))

        self._draw_dialogue(surface)
        pygame.draw.rect(surface, self.game.colors["ink"], (0, self.VIEW_HEIGHT, WIDTH, HEIGHT - self.VIEW_HEIGHT))
        pygame.draw.rect(surface, self.game.colors["gold"], (0, self.VIEW_HEIGHT, WIDTH, 4))
        pygame.draw.rect(surface, self.game.colors["panel"], (8, 520, 784, 72))
        pygame.draw.rect(surface, self.game.colors["gold"], (8, 520, 784, 72), 2)
        self.text(surface, f"슬롯 {self.game.active_slot}  ·  Lv.{self.level}  HP {self.hp}/{self.max_hp}  MP {self.mp}/{self.max_mp}  금화 {self.gold}", (20, 526), 18)
        self.text(surface, self.message, (20, 558), 16, self.game.colors["muted"])
        self.button(surface, pygame.Rect(686, 536, 92, 38), "저장", False, 17)

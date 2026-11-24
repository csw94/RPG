"""The Starlight Library (lore books) and four requests from the new villagers."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from gameplay.achievements import ACHIEVEMENTS, check_achievements
from gameplay.enemies import ENEMIES
from gameplay.quests import QUESTS
from scenes.library_scene import BOOKS, LibraryScene
from scenes.status_scene import StatusScene
from scenes.village_scene import VillageScene


class FakeGame:
    active_slot = 1
    colors = {"gold": (210, 166, 78), "cream": (242, 222, 177), "panel": (57, 43, 33),
              "ink": (25, 31, 28), "muted": (190, 170, 133), "red": (181, 68, 51),
              "green": (73, 139, 91), "blue": (92, 156, 205)}

    def __init__(self):
        self.field = None
        self.scene = None
        self.scene_name = "village"
        self.shop = None

    def save_game(self):
        pass

    def open_shop(self, shop="logan"):
        self.shop = shop

    def font(self, size):
        return pygame.font.Font(None, size)


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


def village(**state):
    game = FakeGame()
    scene = VillageScene(game, {"world": "village", "x": 15, "y": 15, **state})
    game.field = game.scene = scene
    return game, scene


ROOMS = {"inn": "village_inn", "smithy": "village_smithy", "library": "village_library",
         "apothecary": "village_apothecary"}


def keeper_room(name, **state):
    """The keeper now waits inside the building: open that room with the hero at the counter."""
    from scenes.house_scene import HouseInteriorScene

    game = FakeGame()
    room = HouseInteriorScene(game, {"world": ROOMS[name], "x": 12, "y": 7, **state})
    game.field = game.scene = room
    return game, room


def talk_keeper(room):
    room.player.update(x=12.0, y=7.0)
    room._interact()
    while room.dialogue_lines:
        room._advance_dialogue()


def talk(scene, position):
    scene.player.update(x=float(position[0] - 1), y=float(position[1]))
    if scene._blocked(position[0] - 1, position[1]):
        scene.player.update(x=float(position[0] + 1), y=float(position[1]))
    scene._interact()
    while scene.dialogue_lines:
        scene._advance_dialogue()


class LibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_six_books_with_pages(self):
        self.assertEqual(len(BOOKS), 6)
        for book in BOOKS.values():
            self.assertTrue(book["title"])
            self.assertGreaterEqual(len(book["pages"]), 2)

    def test_reading_to_the_last_page_marks_a_book_read(self):
        game, scene = village()
        library = LibraryScene(game, scene)
        first = list(BOOKS)[0]
        for _ in range(len(BOOKS[first]["pages"]) - 1):
            self.assertNotIn(first, scene.books_read)
            library.handle_events([key(pygame.K_RIGHT)])
        self.assertIn(first, scene.books_read)
        library.handle_events([key(pygame.K_DOWN)])
        self.assertEqual(library.page, 0)
        library.draw(pygame.Surface((800, 600)))

    def test_reading_every_book_earns_the_scholar(self):
        _, scene = village(books_read=list(BOOKS))
        self.assertIn("scholar", ACHIEVEMENTS)
        self.assertIn("scholar", check_achievements(scene))
        self.assertEqual(scene.serialize()["books_read"], sorted(BOOKS))

    def test_edel_opens_the_library_when_no_request_is_due(self):
        game, scene = keeper_room("library", sub_quests={"sq_library": {"status": "COMPLETED", "progress": 12}})
        talk_keeper(scene)
        self.assertIsInstance(game.scene, LibraryScene)
        game.scene.handle_events([key(pygame.K_ESCAPE)])
        self.assertIs(game.scene, scene)


class RequestTests(unittest.TestCase):
    def test_four_new_requests_in_the_table(self):
        for quest_id in ("sq_inn_stew", "sq_smith_ore", "sq_library", "sq_tomi"):
            self.assertIn(quest_id, QUESTS)
        self.assertEqual(len(QUESTS), 11)

    def test_kill_requests_from_rosa_bron_and_tomi(self):
        cases = (("sq_smith_ore", "smithy", "scorpion", {}),
                 ("sq_inn_stew", "inn", "snow_wolf", {"quest_flags": {"shrine_wind": 1, "shrine_earth": 1}}),)
        for quest_id, place, enemy, state in cases:
            game, scene = keeper_room(place, **state)
            talk_keeper(scene)
            self.assertEqual(scene.sub_quests[quest_id]["status"], "IN_PROGRESS", quest_id)
            for _ in range(QUESTS[quest_id]["target"]):
                scene.resolve_battle_victory(enemy)
            talk_keeper(scene)
            self.assertEqual(scene.sub_quests[quest_id]["status"], "COMPLETED", quest_id)
        game, scene = village()
        talk(scene, scene.RESIDENTS["tomi"]["pos"])
        self.assertEqual(scene.sub_quests["sq_tomi"]["status"], "IN_PROGRESS")

    def test_rosa_waits_until_the_north_is_open(self):
        game, scene = keeper_room("inn")
        talk_keeper(scene)
        self.assertEqual(scene.sub_quests["sq_inn_stew"]["status"], "NOT_STARTED")

    def test_library_request_counts_the_bestiary(self):
        game, scene = keeper_room("library")
        talk_keeper(scene)
        quest = scene.sub_quests["sq_library"]
        self.assertEqual(quest["status"], "IN_PROGRESS")
        scene.bestiary.update({enemy: 1 for enemy in list(ENEMIES)[:12]})
        game.scene = scene
        talk_keeper(scene)
        self.assertEqual(quest["status"], "COMPLETED")
        self.assertIn("sage_glasses", scene.owned_accessories)

    def test_status_screen_fits_eleven_requests(self):
        pygame.init()
        pygame.display.set_mode((1, 1))
        game, scene = village()
        status = StatusScene(game)
        self.assertEqual(len(status.quest_rows()), 11)
        status.draw(pygame.Surface((800, 600)))
        status.page = "achievements"
        status.draw(pygame.Surface((800, 600)))


if __name__ == "__main__":
    unittest.main()

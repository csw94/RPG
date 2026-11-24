"""Hero walk cycle: 4 frames per direction with distinct front, back and side bodies."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from utils import pixel_art
from utils.pixel_art import hero_sprite, walk_frame

DIRECTIONS = ("down", "up", "left", "right")


def pixels(surface):
    w, h = surface.get_size()
    return [tuple(surface.get_at((x, y))) for y in range(h) for x in range(w)]


def base(direction, frame=0):
    return pixel_art._player("rusty_sword", "traveler_clothes", direction, frame)


class HeroWalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_walk_frame_cycles_through_four_poses(self):
        self.assertEqual(walk_frame(0.0), 0)
        self.assertEqual([walk_frame(t + 0.5) for t in range(5)], [0, 1, 2, 3, 0])

    def test_each_direction_has_two_distinct_step_poses(self):
        for direction in DIRECTIONS:
            stand, left, mid, right = (pixels(base(direction, f)) for f in range(4))
            self.assertEqual(stand, mid, direction)
            self.assertNotEqual(stand, left, direction)
            self.assertNotEqual(stand, right, direction)
            self.assertNotEqual(left, right, direction)

    def test_back_view_hides_the_face(self):
        ink = pixel_art.PALETTE["ink"]
        face = [(x, y) for x in range(16) for y in range(5, 12)]
        front, back = base("down"), base("up")
        self.assertTrue(any(tuple(front.get_at(p))[:3] == ink for p in face))
        self.assertFalse(any(tuple(back.get_at(p))[:3] == ink for p in face))

    def test_side_view_body_differs_from_front_and_left_mirrors_right(self):
        front, side = base("down"), base("right")
        body = lambda s: [tuple(s.get_at((x, y))) for x in range(16) for y in range(12, 24)]
        self.assertNotEqual(body(front), body(side))
        for frame in range(4):
            flipped = pygame.transform.flip(base("right", frame), True, False)
            self.assertEqual(pixels(flipped), pixels(base("left", frame)))

    def test_every_frame_is_outlined_and_hero_sized(self):
        outline = pixel_art.PALETTE["outline"]
        for direction in DIRECTIONS:
            for frame in range(4):
                surface = base(direction, frame)
                self.assertEqual(surface.get_size(), (16, 24))
                self.assertIn(outline, [p[:3] for p in pixels(surface)], (direction, frame))

    def test_hero_sprite_caches_all_four_frames(self):
        frames = {id(hero_sprite(size=(32, 48), direction="down", frame=f)) for f in range(4)}
        self.assertEqual(len(frames), 4)



NPCS = ("chief", "old_knight", "merchant", "shopkeeper", "villager", "townsfolk")


class NpcIdleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_idle_poses_differ_from_the_rest_pose(self):
        for name in NPCS:
            rest = pixels(pixel_art.npc_pose(name, "rest"))
            self.assertNotEqual(rest, pixels(pixel_art.npc_pose(name, "breath")), name)
            self.assertNotEqual(rest, pixels(pixel_art.npc_pose(name, "blink")), name)

    def test_blink_closes_the_eyes(self):
        ink = pixel_art.PALETTE["ink"]
        for name in NPCS:
            blink = pixel_art.npc_pose(name, "blink")
            self.assertNotEqual(tuple(blink.get_at((6, 8)))[:3], ink, name)

    def test_idle_cycle_breathes_and_blinks_over_time(self):
        poses = {pixel_art.idle_pose(t / 20, seed=0) for t in range(200)}
        self.assertEqual(poses, {"rest", "breath", "blink"})
        # Different NPCs are out of step with each other.
        a = [pixel_art.idle_pose(t / 20, seed=0) for t in range(100)]
        b = [pixel_art.idle_pose(t / 20, seed=3) for t in range(100)]
        self.assertNotEqual(a, b)

    def test_npc_sprite_scales_to_npc_size(self):
        image = pixel_art.npc_sprite("chief", pixel_art.NPC_SIZE, clock=0.0)
        self.assertEqual(image.get_size(), pixel_art.NPC_SIZE)


class EnemyIdleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_every_enemy_moves_while_idle(self):
        from gameplay.enemies import ENEMIES

        for enemy in ENEMIES.values():
            states = set()
            for t in range(60):
                image, dy = pixel_art.enemy_idle(enemy["sprite"], enemy["size"], t / 20)
                states.add((image.get_size(), dy, pygame.image.tobytes(image, "RGBA")))
            self.assertGreater(len(states), 1, enemy["id"])

    def test_idle_styles_match_the_creature(self):
        self.assertEqual(pixel_art.IDLE_STYLES["slime"], "squash")
        self.assertEqual(pixel_art.IDLE_STYLES["bat"], "hover")
        self.assertEqual(pixel_art.IDLE_STYLES.get("golem", "breathe"), "breathe")

    def test_squash_keeps_pixels_on_the_sprite_grid(self):
        base = pixel_art.fit_sprite("slime", (112, 84))
        factor = base.get_width() // pixel_art.sprite("slime", None).get_width()
        for t in range(40):
            image, _ = pixel_art.enemy_idle("slime", (112, 84), t / 20)
            self.assertEqual((image.get_width() - base.get_width()) % factor, 0)
            self.assertEqual((image.get_height() - base.get_height()) % factor, 0)


if __name__ == "__main__":
    unittest.main()

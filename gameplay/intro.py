"""New game opening: little Tomi runs up to the hero and leads them to the chief's hall.

Pure script logic (no pygame) so it can be tested; VillageScene draws it and shows the lines.
Phases: fade -> run_in -> talk -> lead -> wait. The hero is held still until Tomi has spoken.
"""

FADE_TIME = 1.2
RUN_SPEED = 5.0   # tiles per second
LEAD_SPEED = 4.0

LINES = [
    "토미: 헉, 헉... 찾았다! 여기 계셨네요!",
    "토미: 촌장님이 급하게 찾으세요! 별빛 분수 빛이 이상하게 약해졌대요.",
    "토미: 촌장님 댁은 분수 바로 위쪽 빨간 지붕 집이에요. 제가 먼저 가서 기다릴게요!",
]
DOOR_LINES = ["토미: 여기가 촌장님 댁이에요! 문 앞에서 SPACE를 눌러 들어가 보세요."]
LEAD_MESSAGE = "토미를 따라 광장 북쪽 촌장 집으로 가 보세요."


class ChiefCallIntro:
    START = (2.0, 10.0)                     # just off the west edge of the opening view
    RUN_PATH = ((12.0, 10.0), (14.0, 11.0), (14.0, 15.0))
    MEET = (14.0, 15.0)                     # beside the hero, who starts at (15, 15)
    LEAD_PATH = ((14.0, 11.0), (16.0, 10.0), (17.0, 10.0))
    WAIT = (17.0, 10.0)                     # beside the chief's door at (15, 9)

    def __init__(self, waiting=False):
        self.clock = 0.0
        self.walking = False
        if waiting:
            self.phase, self.tomi, self.path = "wait", self.WAIT, []
        else:
            self.phase, self.tomi, self.path = "fade", self.START, list(self.RUN_PATH)

    @property
    def locks_player(self):
        return self.phase in ("fade", "run_in", "talk")

    @property
    def fade(self):
        """Black overlay strength (0..1) for the opening fade-in."""
        return max(0.0, 1.0 - self.clock / FADE_TIME) if self.phase == "fade" else 0.0

    def update(self, dt):
        """Advance the script; returns "talk" on the frame Tomi reaches the hero."""
        self.clock += dt
        if self.phase == "fade" and self.clock >= FADE_TIME:
            self.phase = "run_in"
        if self.phase == "run_in":
            if self._walk(RUN_SPEED * dt):
                self.phase = "talk"
                return "talk"
        elif self.phase == "lead" and self._walk(LEAD_SPEED * dt):
            self.phase = "wait"
        return None

    def skip(self):
        """Action key during the run-in: Tomi arrives at once."""
        if self.phase in ("fade", "run_in"):
            self.tomi, self.path, self.walking, self.phase = self.MEET, [], False, "talk"
            return "talk"
        return None

    def finish_talk(self):
        if self.phase == "talk":
            self.phase, self.path = "lead", list(self.LEAD_PATH)

    def _walk(self, distance):
        """Move Tomi along the path; True once the last point is reached."""
        while self.path and distance > 0:
            tx, ty = self.path[0]
            x, y = self.tomi
            gap = ((tx - x) ** 2 + (ty - y) ** 2) ** 0.5
            if gap <= distance:
                self.tomi = (tx, ty)
                self.path.pop(0)
                distance -= gap
            else:
                self.tomi = (x + (tx - x) * distance / gap, y + (ty - y) * distance / gap)
                distance = 0
        self.walking = bool(self.path)
        return not self.path

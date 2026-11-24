"""Chiptune sound made in code: square/triangle/noise voices, no audio files.

``render_sfx`` / ``render_music`` build 16-bit mono samples (``array('h')``) with nothing but
the standard library. ``Audio`` turns them into pygame sounds, plays effects, loops the
background track on a reserved channel and keeps quiet when no audio device exists.
Music is rendered in a background thread at start-up so switching tracks never stalls.
"""

import math
import random
import threading
from array import array

import pygame

RATE = 22050
MAX_SFX_VOLUME = 0.8    # volume at setting level 10
MAX_MUSIC_VOLUME = 0.45


# --- synthesis --------------------------------------------------------------------------
def _note_freq(name):
    """'A4' -> 440.0, 'C#5' -> 554.4."""
    steps = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    semis = steps[name[0]] + (1 if "#" in name else 0)
    octave = int(name[-1])
    return 440.0 * 2 ** ((semis + (octave - 4) * 12) / 12)


def _voice(freq, dur, wave="square", vol=0.3, attack=0.004, release=0.04, slide=1.0, duty=0.5,
           seed=0, rate=RATE):
    """One note as floats in -1..1 with a linear attack/release envelope.

    ``slide`` is the frequency ratio reached at the end (0.5 = drop an octave)."""
    count = max(1, int(dur * rate))
    out = [0.0] * count
    attack_n, release_n = max(1, int(attack * rate)), max(1, int(release * rate))
    rng = random.Random(seed)
    phase, noise_val, noise_step = 0.0, 0.0, 0
    for i in range(count):
        t = i / count
        f = freq * (slide ** t)
        phase = (phase + f / rate) % 1.0
        if wave == "square":
            v = 1.0 if phase < duty else -1.0
        elif wave == "triangle":
            v = 4.0 * abs(phase - 0.5) - 1.0
        else:  # noise, re-sampled at roughly ``freq`` Hz for a pitched hiss
            noise_step += 1
            if noise_step >= max(1, int(rate / max(f, 1))):
                noise_step, noise_val = 0, rng.uniform(-1, 1)
            v = noise_val
        env = min(1.0, i / attack_n, (count - 1 - i) / release_n)
        out[i] = v * vol * env
    return out


def _seq(*parts):
    """Concatenate voices (or silence given as a float number of seconds)."""
    out = []
    for part in parts:
        out.extend([0.0] * int(part * RATE) if isinstance(part, float) else part)
    return out


def _mix(*tracks):
    length = max(len(t) for t in tracks)
    out = [0.0] * length
    for track in tracks:
        for i, v in enumerate(track):
            out[i] += v
    return out


def _to_int16(samples):
    return array("h", (max(-32768, min(32767, int(v * 32767))) for v in samples))


def _arp(notes, step, wave="square", vol=0.22, tail=0.0):
    return _seq(*[_voice(_note_freq(n), step + (tail if i == len(notes) - 1 else 0), wave, vol)
                  for i, n in enumerate(notes)])


SFX = {
    "cursor": lambda: _voice(880, 0.035, "square", 0.16, duty=0.25),
    "confirm": lambda: _seq(_voice(660, 0.05, "square", 0.2), _voice(990, 0.08, "square", 0.2)),
    "talk": lambda: _voice(1180, 0.025, "square", 0.08, duty=0.25),
    "hit": lambda: _mix(_voice(1800, 0.09, "noise", 0.35, release=0.07, seed=1),
                        _voice(180, 0.09, "square", 0.25, slide=0.5)),
    "crit": lambda: _mix(_voice(2400, 0.16, "noise", 0.45, release=0.12, seed=2),
                         _voice(260, 0.16, "square", 0.3, slide=0.3)),
    "weak": lambda: _mix(_voice(1800, 0.1, "noise", 0.35, seed=3),
                         _seq(_voice(196, 0.08, "square", 0.25, slide=0.5), _voice(1320, 0.08, "square", 0.18))),
    "hurt": lambda: _mix(_voice(900, 0.12, "noise", 0.3, seed=4), _voice(220, 0.12, "square", 0.28, slide=0.45)),
    "miss": lambda: _voice(700, 0.14, "triangle", 0.3, slide=0.45),
    "skill": lambda: _arp(("C5", "E5", "G5", "C6", "E6"), 0.035, "triangle", 0.32, 0.06),
    "heal": lambda: _arp(("G5", "C6", "E6", "G6"), 0.06, "triangle", 0.3, 0.12),
    "guard": lambda: _mix(_voice(330, 0.18, "square", 0.18, duty=0.25), _voice(495, 0.18, "triangle", 0.2)),
    "status": lambda: _seq(*[_voice(f, 0.06, "square", 0.18, duty=0.25) for f in (330, 280, 330, 250)]),
    "level_up": lambda: _arp(("C5", "E5", "G5", "C6", "G5", "C6"), 0.07, "square", 0.22, 0.25),
    "victory": lambda: _arp(("G4", "C5", "E5", "G5", "E5", "G5"), 0.09, "square", 0.22, 0.3),
    "defeat": lambda: _arp(("G4", "E4", "C4", "G3"), 0.16, "triangle", 0.35, 0.3),
    "flee": lambda: _voice(600, 0.25, "noise", 0.25, slide=4.0, seed=5),
    "encounter": lambda: _seq(*[_voice(f, 0.05, "square", 0.2, duty=0.25) for f in (220, 440, 220, 440, 660)]),
    "chest": lambda: _arp(("G5", "C6", "E6", "G6"), 0.055, "square", 0.2, 0.18),
    "coin": lambda: _seq(_voice(1319, 0.05, "square", 0.18), _voice(1760, 0.14, "square", 0.18)),
    "save": lambda: _seq(_voice(660, 0.07, "triangle", 0.3), _voice(880, 0.12, "triangle", 0.3)),
    "phase": lambda: _mix(_voice(140, 0.9, "noise", 0.4, release=0.5, slide=0.4, seed=6),
                          _voice(330, 0.9, "square", 0.22, release=0.4, slide=0.25, duty=0.25),
                          _voice(220, 0.9, "triangle", 0.3, release=0.4, slide=0.25)),
}


def render_sfx(name):
    return _to_int16(SFX[name]())


# --- music ------------------------------------------------------------------------------
# Each track: tempo, melody and bass as "NOTE:beats" tokens ('.' = rest), optional hi-hat.
# All melodies are original, written for this game.
MUSIC = {
    "title": {"bpm": 84, "hat": False,
              "melody": "E5:2 G5:1 A5:1 B5:2 A5:2 G5:2 E5:1 D5:1 E5:4",
              "bass": "E3:4 C3:4 D3:4 E3:4"},
    "village": {"bpm": 108, "hat": False,
                "melody": "C5:1 E5:1 G5:1 E5:1 A5:2 G5:2 F5:1 E5:1 D5:1 E5:1 C5:4",
                "bass": "C3:2 G3:2 A2:2 E3:2 F2:2 G2:2 C3:4"},
    "field": {"bpm": 126, "hat": True,
              "melody": "A4:1 C5:1 E5:1 A5:1 G5:1 E5:1 D5:2 C5:1 D5:1 E5:1 G5:1 E5:2 A4:2",
              "bass": "A2:2 A3:2 F2:2 F3:2 C3:2 C4:2 G2:2 G3:2"},
    "dungeon": {"bpm": 92, "hat": False,
                "melody": "D5:2 .:1 F5:1 E5:2 .:2 C5:2 .:1 D5:1 A4:4",
                "bass": "D3:4 D3:4 A2:4 D3:4"},
    "battle": {"bpm": 150, "hat": True,
               "melody": "E5:.5 E5:.5 G5:1 E5:.5 D5:.5 C5:1 D5:.5 E5:.5 D5:1 B4:2 "
                         "E5:.5 E5:.5 G5:1 A5:1 G5:1 E5:2 .:2",
               "bass": " ".join(["E3:.5 E4:.5"] * 4 + ["C3:.5 C4:.5"] * 4
                                + ["D3:.5 D4:.5"] * 4 + ["B2:.5 B3:.5"] * 4)},
    "final": {"bpm": 172, "hat": True,
              "melody": "D5:.5 F5:.5 A5:.5 D6:.5 C#6:1 A5:1 A#5:.5 A5:.5 G5:.5 F5:.5 E5:2 "
                        "D5:.5 E5:.5 F5:.5 A5:.5 G5:1 F5:1 E5:1 C#5:1 D5:2",
              "bass": " ".join(["D2:.5 D3:.5"] * 4 + ["A#2:.5 A#3:.5"] * 4
                               + ["G2:.5 G3:.5"] * 4 + ["A2:.5 A3:.5"] * 4)},
    "boss": {"bpm": 160, "hat": True,
             "melody": "A4:.5 C5:.5 E5:.5 A5:.5 G#5:1 E5:1 F5:.5 E5:.5 D5:.5 C5:.5 B4:2 "
                       "A4:.5 B4:.5 C5:.5 E5:.5 D5:1 C5:1 B4:2 G#4:2",
             "bass": " ".join(["A2:.5 A3:.5"] * 4 + ["F2:.5 F3:.5"] * 4
                              + ["D2:.5 D3:.5"] * 4 + ["E2:.5 E3:.5"] * 4)},
}


def _line(tokens, beat, wave, vol, duty=0.5):
    out = []
    for token in tokens.split():
        note, beats = token.split(":")
        dur = float(beats) * beat
        if note == ".":
            out.extend([0.0] * int(dur * RATE))
        else:
            out.extend(_voice(_note_freq(note), dur, wave, vol, attack=0.006,
                              release=min(0.06, dur * 0.4), duty=duty))
    return out


def render_music(name):
    track = MUSIC[name]
    beat = 60.0 / track["bpm"]
    melody = _line(track["melody"], beat, "square", 0.13, duty=0.25)
    bass = _line(track["bass"], beat, "triangle", 0.24)
    parts = [melody, bass]
    if track["hat"]:
        hat_count = int(len(bass) / (beat * RATE))
        parts.append(_seq(*[_seq(_voice(7000, 0.03, "noise", 0.07, release=0.025, seed=9), beat - 0.03)
                            for _ in range(hat_count)]))
    return _to_int16(_mix(*parts))


def music_for(scene_name, enemy_id):
    """Background track for a scene, or None to keep the current one (shop, status...)."""
    if scene_name == "title":
        return "title"
    if scene_name == "battle":
        bosses = ("shrine_wind", "shrine_earth", "shrine_fire", "shrine_ice", "final_boss", "abyss_lord")
        return "boss" if enemy_id in bosses else "battle"
    if scene_name in ("village", "village_north_shrine", "epilogue") or scene_name.startswith("village_house") \
            or scene_name == "village_chief_house":
        return "village"
    if scene_name.startswith("field"):
        return "field"
    if scene_name.startswith("shrine_"):
        return "dungeon"
    return None


# --- playback ---------------------------------------------------------------------------
class Audio:
    def __init__(self, enabled=True):
        self.enabled = False
        self.muted = False
        self.music_volume = MAX_MUSIC_VOLUME * 0.7
        self.sfx_volume = MAX_SFX_VOLUME * 0.7
        self.current = None
        self._sounds = {}
        self._rendered = {}
        self._music_channel = None
        self._channels = 1
        if enabled:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init(RATE, -16, 1, 512)
                self._channels = pygame.mixer.get_init()[2]
                pygame.mixer.set_reserved(1)
                self._music_channel = pygame.mixer.Channel(0)
                self.enabled = True
            except (pygame.error, TypeError):
                self.enabled = False
        if self.enabled:
            threading.Thread(target=self._prerender, daemon=True).start()

    def _prerender(self):
        for name in MUSIC:
            self._rendered[("music", name)] = render_music(name)

    def _sound(self, kind, name):
        key = (kind, name)
        if key not in self._sounds:
            samples = self._rendered.get(key)
            if samples is None:
                if kind == "music":
                    return None  # still rendering in the background; try again next frame
                samples = render_sfx(name)
            if self._channels == 2:
                stereo = array("h", [0]) * (len(samples) * 2)
                stereo[0::2], stereo[1::2] = samples, samples
                samples = stereo
            self._sounds[key] = pygame.mixer.Sound(buffer=samples.tobytes())
        return self._sounds[key]

    def play(self, name):
        if not self.enabled or self.muted or name not in SFX:
            return
        if self.sfx_volume <= 0:
            return
        sound = self._sound("sfx", name)
        sound.set_volume(self.sfx_volume)
        sound.play()

    def play_music(self, name):
        if not self.enabled or name not in MUSIC or name == self.current:
            return
        sound = self._sound("music", name)
        if sound is None:
            return
        self.current = name
        self._music_channel.stop()
        self._music_channel.set_volume(0.0 if self.muted else self.music_volume)
        self._music_channel.play(sound, loops=-1, fade_ms=400)

    def update(self, track):
        """Call every frame with ``music_for(...)``; None keeps the current track."""
        if track:
            self.play_music(track)

    def toggle_mute(self):
        self.muted = not self.muted
        self._apply_music_volume()
        return self.muted

    def set_volumes(self, music_level, sfx_level):
        """Volume levels 0-10 from the settings screen."""
        self.music_volume = MAX_MUSIC_VOLUME * max(0, min(10, music_level)) / 10
        self.sfx_volume = MAX_SFX_VOLUME * max(0, min(10, sfx_level)) / 10
        self._apply_music_volume()

    def _apply_music_volume(self):
        if self.enabled:
            self._music_channel.set_volume(0.0 if self.muted else self.music_volume)

"""New game plus: start the story again with the same hero; each cycle makes enemies tougher."""

# What the hero carries into the next cycle. Everything else (story flags, requests, opened
# chests, picked herbs, key items, position) starts fresh.
CARRIED = ("level", "xp", "max_hp", "max_mp", "atk", "defense", "evasion_bonus", "gold",
           "potions", "high_potions", "weapon", "armor", "accessory", "owned_weapons", "owned_armors",
           "owned_accessories", "bestiary", "achievements", "play_time", "stats", "difficulty",
           "layout_version")

# Per extra cycle: enemy HP +160%, damage taken +60%, gold and experience +30%.
# (Simulated: the carried-over hero still sweeps the shrines, the final boss ~75% wins.)
CYCLE_STEP = {"enemy_hp": 1.6, "damage": 0.6, "gold": 0.3, "xp": 0.3}


def cycle_multipliers(cycle):
    extra = max(0, int(cycle) - 1)
    return {key: 1 + step * extra for key, step in CYCLE_STEP.items()}


def new_game_plus_state(state):
    carried = {key: state[key] for key in CARRIED if key in state}
    carried.update(world="village", x=15, y=15,
                   hp=state.get("max_hp", 100), mp=state.get("max_mp", 10),
                   cycle=int(state.get("cycle", 1)) + 1,
                   # The chief already knows the hero: skip the prologue (and its rusty sword).
                   quest_flags={"prologue_done": 1})
    return carried

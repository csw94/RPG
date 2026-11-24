"""Static map graph and route-specific overworld layouts for Oak Valley."""


# The four shrines whose seals awaken the star sword. The northern road (Frost Highlands)
# thaws once NORTH_UNLOCK of the others are cleared.
SHRINES = ("shrine_wind", "shrine_earth", "shrine_fire", "shrine_ice")
NORTH_UNLOCK = 2

MAP_GRAPH = {
    "village_square": ("village_chief_house", "village_house_1", "village_house_2",
                       "village_north_shrine", "field_east", "field_west", "field_south"),
    "village_chief_house": ("village_square",),
    "village_north_shrine": ("village_square", "shrine_abyss_1f", "field_north"),
    "field_north": ("village_north_shrine", "shrine_ice_1f"),
    "shrine_ice_1f": ("field_north", "shrine_ice_2f"),
    "shrine_ice_2f": ("shrine_ice_1f",),
    "village_house_1": ("village_square",),
    "village_house_2": ("village_square",),
    "field_east": ("village_square", "shrine_wind_1f"),
    "shrine_wind_1f": ("field_east", "shrine_wind_2f"),
    "shrine_wind_2f": ("shrine_wind_1f",),
    "field_west": ("village_square", "shrine_earth_1f"),
    "shrine_earth_1f": ("field_west", "shrine_earth_2f"),
    "shrine_earth_2f": ("shrine_earth_1f",),
    "field_south": ("village_square", "shrine_fire_1f"),
    "shrine_fire_1f": ("field_south", "shrine_fire_2f"),
    "shrine_fire_2f": ("shrine_fire_1f",),
    # Post-game: the Starlight Abyss below the north altar.
    "shrine_abyss_1f": ("village_north_shrine", "shrine_abyss_2f"),
    "shrine_abyss_2f": ("shrine_abyss_1f", "shrine_abyss_3f"),
    "shrine_abyss_3f": ("shrine_abyss_2f",),
}


# Route fields are 52x31 tiles (about 30% larger than the original 40x24 layout).
FIELD_ROUTES = {
    "field_east": {
        "name": "바람 부는 숲길", "theme": "forest", "shrine": "shrine_wind",
        "village_portal": (1, 16), "village_spawn": (2, 16), "return_village": (30, 10),
        "dungeon_portal": (47, 6), "dungeon_spawn": (3, 14), "return_dungeon": (46, 6),
        "path": ((2, 16), (10, 13), (20, 14), (27, 10), (36, 10), (47, 6)),
        "groves": ((10, 3, 9, 7), (23, 3, 8, 5), (31, 13, 8, 7), (42, 2, 7, 3),
                   (4, 21, 10, 6), (18, 20, 9, 7), (36, 20, 10, 7), (46, 12, 4, 10)),
        "herbs": ((17, 13), (29, 10), (39, 9)),
        "chests": {(22, 14): "potion", (43, 7): "gold"},
        "enemy_pool": ("slime", "wolf", "mushroom", "goblin"), "encounter_rate": 0.09,
    },
    "field_west": {
        "name": "붉은 바위 협곡", "theme": "canyon", "shrine": "shrine_earth",
        "village_portal": (50, 16), "village_spawn": (49, 16), "return_village": (1, 10),
        "dungeon_portal": (5, 6), "dungeon_spawn": (11, 14), "return_dungeon": (6, 6),
        "path": ((49, 16), (40, 18), (33, 14), (25, 12), (17, 14), (10, 9), (5, 6)),
        "groves": (), "herbs": (),
        "toby": (43, 17),
        "chests": {(36, 14): "gold", (16, 10): "potion"},
        "enemy_pool": ("scorpion", "bandit", "goblin"), "encounter_rate": 0.12,
    },
    "field_south": {
        "name": "메마른 화산 기슭", "theme": "volcanic", "shrine": "shrine_fire",
        # Enter at the top (the village is to the north) and head downhill to the temple.
        "village_portal": (16, 1), "village_spawn": (16, 3), "return_village": (15, 19),
        "dungeon_portal": (29, 27), "dungeon_spawn": (21, 14), "return_dungeon": (29, 25),
        "path": ((16, 2), (14, 8), (21, 12), (17, 17), (23, 21), (29, 27)),
        "groves": (), "herbs": (),
        "chests": {(23, 14): "high_potion", (9, 10): "gold"},
        "enemy_pool": ("salamander", "magma_slime", "goblin"), "encounter_rate": 0.14,
    },
    # Reached through the north altar clearing once two shrines are cleared; you climb
    # from the bottom edge up through snowfields and frozen lakes to the Ice Shrine.
    "field_north": {
        "name": "서리 고원", "theme": "snow", "shrine": "shrine_ice", "home": "village_north_shrine",
        "village_portal": (26, 29), "village_spawn": (26, 28), "return_village": (15, 2),
        "dungeon_portal": (9, 3), "dungeon_spawn": (12, 13), "return_dungeon": (9, 4),
        "path": ((26, 28), (22, 22), (31, 17), (24, 12), (14, 10), (9, 4)),
        "groves": ((3, 18, 9, 8), (36, 20, 10, 7), (40, 4, 8, 7), (17, 2, 8, 5), (30, 25, 6, 4)),
        "herbs": (),
        "chests": {(33, 17): "high_potion", (14, 7): "gold"},
        "npc": {"pos": (24, 20), "sprite": "hunter", "quest": "sq_frost_hunt"},
        "enemy_pool": ("snow_wolf", "ice_slime", "frost_wisp"), "encounter_rate": 0.12,
    },
}

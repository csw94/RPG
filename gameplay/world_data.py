"""Static map graph and route-specific overworld layouts for Oak Valley."""


MAP_GRAPH = {
    "village_square": ("village_chief_house", "village_house_1", "village_house_2",
                       "village_north_shrine", "field_east", "field_west", "field_south"),
    "village_chief_house": ("village_square",),
    "village_north_shrine": ("village_square",),
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
}


FIELD_ROUTES = {
    "field_east": {
        "name": "바람 부는 숲길", "theme": "forest", "shrine": "shrine_wind",
        "village_portal": (1, 12), "village_spawn": (2, 12), "return_village": (23, 8),
        "dungeon_portal": (36, 5), "dungeon_spawn": (3, 14), "return_dungeon": (35, 5),
        "path": ((2, 12), (8, 10), (15, 11), (21, 8), (28, 8), (36, 5)),
        "groves": ((8, 2, 7, 5), (18, 2, 6, 4), (24, 10, 6, 5), (32, 2, 5, 5)),
        "herbs": ((13, 10), (22, 8), (30, 7)),
        "chests": {(17, 11): "potion", (33, 5): "gold"},
        "enemy_pool": ("slime", "goblin"), "encounter_rate": 0.09,
    },
    "field_west": {
        "name": "붉은 바위 협곡", "theme": "canyon", "shrine": "shrine_earth",
        "village_portal": (38, 12), "village_spawn": (37, 12), "return_village": (1, 8),
        "dungeon_portal": (4, 5), "dungeon_spawn": (11, 14), "return_dungeon": (5, 5),
        "path": ((37, 12), (31, 14), (25, 11), (19, 9), (13, 11), (8, 7), (4, 5)),
        "groves": (), "herbs": (),
        "toby": (33, 12),
        "chests": {(28, 11): "gold", (12, 8): "potion"},
        "enemy_pool": ("goblin",), "encounter_rate": 0.12,
    },
    "field_south": {
        "name": "메마른 화산 기슭", "theme": "volcanic", "shrine": "shrine_fire",
        "village_portal": (12, 22), "village_spawn": (12, 21), "return_village": (12, 14),
        "dungeon_portal": (22, 2), "dungeon_spawn": (21, 14), "return_dungeon": (22, 3),
        "path": ((12, 21), (11, 17), (16, 14), (13, 10), (18, 7), (22, 2)),
        "groves": (), "herbs": (),
        "chests": {(18, 12): "high_potion", (7, 15): "gold"},
        "enemy_pool": ("goblin", "slime"), "encounter_rate": 0.14,
    },
}

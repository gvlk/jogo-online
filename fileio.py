from settings import MAP_DATA_PATH, MAP_OBSTACLES_PATH, ABILITIES_PATH, SPRITES_PATH
from os import listdir
from typing import List, Dict
from csv import reader
from json import loads
from pygame.image import load
from pygame.surface import Surface


def get_map_surface(map_id: int) -> Surface:
    return load(MAP_DATA_PATH + f"{map_id}/main.png").convert()


def get_map_layout(map_id: int) -> Dict[str, List]:
    layout = {
        "details": list(),
        "obstacles": list(),
        "entities": list(),
        "barrier": list()
    }
    with open(MAP_DATA_PATH + f"{map_id}/main_Details.csv") as level_map:
        layout["details"] = list(reader(level_map, delimiter=","))
    with open(MAP_DATA_PATH + f"{map_id}/main_Obstacles.csv") as level_map:
        layout["obstacles"] = list(reader(level_map, delimiter=","))
    with open(MAP_DATA_PATH + f"{map_id}/main_Entities.csv") as level_map:
        layout["entities"] = list(reader(level_map, delimiter=","))
    with open(MAP_DATA_PATH + f"{map_id}/main_Barrier.csv") as level_map:
        layout["barrier"] = list(reader(level_map, delimiter=","))

    return layout


def get_obstacle_surfaces():
    surfaces = list()
    for file in listdir(MAP_OBSTACLES_PATH):
        surfaces.append(load(MAP_OBSTACLES_PATH + file).convert_alpha())
    return surfaces


def get_sheet(entity_id):
    return load(SPRITES_PATH + entity_id[0:3] + "spritesheet.png").convert_alpha()


def get_abilities_dict() -> dict:
    with open(ABILITIES_PATH, "r") as abilities_file:
        abilities_data = loads(abilities_file.read())
    return abilities_data

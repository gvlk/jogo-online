from typing import List, Type
from settings import TILESIZE, CHUNK_SIZE
from fileio import get_map_surface, get_map_layout, get_obstacle_surfaces
from math import ceil

from pygame.sprite import Group
from pygame.surface import Surface

from client.modules.obstacle import StaticObstacle


class World:
    def __init__(self, map_id: int):
        self.ground_surface = get_map_surface(map_id)
        self.ground_rect = self.ground_surface.get_rect(topleft=(0, 0))

        self.chunks: List[List[Group]] = list()
        self.chunk_pxsize = TILESIZE * CHUNK_SIZE
        self.nx_chunks = ceil(self.ground_surface.get_width() / self.chunk_pxsize)
        self.ny_chunks = ceil(self.ground_surface.get_height() / self.chunk_pxsize)
        self.x_max_bound = self.nx_chunks - 1
        self.y_max_bound = self.ny_chunks - 1
        for row in range(self.nx_chunks):
            self.chunks.append(list())
            for column in range(self.ny_chunks):
                self.chunks[row].append(Group())

        self.map_layout = get_map_layout(map_id)
        self.generate_obstacle_spritegroup()

    # noinspection PyTypeChecker
    def generate_obstacle_spritegroup(self) -> None:
        surfaces = get_obstacle_surfaces()
        for tile_type, layout in self.map_layout.items():
            if tile_type not in ("obstacles", "barrier"):
                continue
            for row_index, row in enumerate(layout):
                for col_index, tile_id in enumerate(row):
                    if tile_id == "-1":
                        continue
                    x = col_index * TILESIZE
                    y = row_index * TILESIZE
                    chunk = self.get_chunk((x, y))
                    if tile_type == "obstacles":
                        chunk.add(StaticObstacle((x, y), surfaces[int(tile_id)]))
                    elif tile_type == "barrier":
                        chunk.add(StaticObstacle((x, y), Surface((TILESIZE, TILESIZE))))

    def get_chunk(self, pos: tuple) -> Group:
        row = pos[0] // self.chunk_pxsize
        col = pos[1] // self.chunk_pxsize
        return self.chunks[row][col]

    def get_chunks(self, pos: tuple, x_amp, y_amp) -> Group:
        row = pos[0] // self.chunk_pxsize
        col = pos[1] // self.chunk_pxsize
        x_min = (row - x_amp) * (row - x_amp >= 0) + 0 * (row - x_amp < 0)
        x_max = (row + x_amp) * (row + x_amp <= self.x_max_bound) + self.x_max_bound * (row + x_amp > self.x_max_bound)
        y_min = (col - y_amp) * (col - y_amp >= 0) + 0 * (col - y_amp < 0)
        y_max = (col + y_amp) * (col + y_amp <= self.y_max_bound) + self.y_max_bound * (col + y_amp > self.y_max_bound)

        chunks = Group()
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                chunks.add(self.chunks[x][y])
        return chunks

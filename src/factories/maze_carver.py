# src/factories/maze_carver.py
import random
from typing import List, Tuple

class MazeCarver:
    """
    Encapsula la lógica de carving de caminos tipo laberinto dentro de un chunk.
    """

    def __init__(self, chunk_size: int, path_width_range: Tuple[int, int] = (1, 2)):
        self.chunk_size = chunk_size
        self.path_width_range = path_width_range

    # -------------------------
    # Carving principal
    # -------------------------
    def carve_maze(self, chunk: List[List[Tuple[str, ...]]], start_pos: Tuple[int, int] = None) -> List[List[Tuple[str, ...]]]:
        if not start_pos:
            start_pos = (self.chunk_size // 2, self.chunk_size // 2)

        start_x, start_y = start_pos
        self.carve_center(chunk, start_x, start_y, width=max(1, random.randint(*self.path_width_range)))

        stack = [(start_x, start_y)]
        directions = [(2, 0), (0, 2), (-2, 0), (0, -2)]
        path_cells = 1
        target_path_cells = (self.chunk_size * self.chunk_size) // 2

        while stack and path_cells < target_path_cells:
            current_x, current_y = stack[-1]
            random.shuffle(directions)
            found = False
            for dx, dy in directions:
                nx, ny = current_x + dx, current_y + dy
                if 0 <= nx < self.chunk_size and 0 <= ny < self.chunk_size and chunk[ny][nx][0] == "TREE":
                    width = random.randint(*self.path_width_range)
                    self.carve_between(chunk, current_x, current_y, nx, ny, width)
                    path_cells += 2
                    stack.append((nx, ny))
                    found = True
                    break
            if not found:
                stack.pop()

        self.add_extra_paths(chunk, path_cells, target_path_cells)
        return chunk

    # -------------------------
    # Métodos de carving
    # -------------------------
    def carve_center(self, chunk: List[List[Tuple[str, ...]]], x: int, y: int, width: int = 1):
        half = width // 2
        for dy in range(-half, half + 1):
            for dx in range(-half, half + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.chunk_size and 0 <= ny < self.chunk_size:
                    chunk[ny][nx] = ("GRASS",)

    def carve_between(self, chunk: List[List[Tuple[str, ...]]], x1: int, y1: int, x2: int, y2: int, width: int = 1):
        dx, dy = x2 - x1, y2 - y1
        half = width // 2
        wx, wy = x1 + dx // 2, y1 + dy // 2
        if dx != 0:
            for off in range(-half, half + 1):
                yy = y1 + off
                for xx in (x1, wx, x2):
                    if 0 <= xx < self.chunk_size and 0 <= yy < self.chunk_size:
                        chunk[yy][xx] = ("GRASS",)
        else:
            for off in range(-half, half + 1):
                xx = x1 + off
                for yy in (y1, wy, y2):
                    if 0 <= xx < self.chunk_size and 0 <= yy < self.chunk_size:
                        chunk[yy][xx] = ("GRASS",)

    def add_extra_paths(self, chunk: List[List[Tuple[str, ...]]], current_path_cells: int, target_path_cells: int):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        attempts = 0
        while current_path_cells < target_path_cells and attempts < 200:
            x = random.randint(1, self.chunk_size - 2)
            y = random.randint(1, self.chunk_size - 2)
            if chunk[y][x][0] == "TREE":
                adjacent_paths = sum(
                    1 for dx, dy in directions
                    if 0 <= x + dx < self.chunk_size and 0 <= y + dy < self.chunk_size and chunk[y + dy][x + dx][0] == "GRASS"
                )
                if adjacent_paths >= 2:
                    self.carve_center(chunk, x, y, 1)
                    current_path_cells += 1
            attempts += 1
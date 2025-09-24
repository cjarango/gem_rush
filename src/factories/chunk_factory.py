# src/factories/chunk_factory.py
import random
from typing import List, Tuple
from .maze_carver import MazeCarver

class ChunkFactory:
    """
    Fábrica de chunks para el mapa.
    """

    def __init__(self, chunk_size: int = 11, path_width_range: Tuple[int, int] = (1, 2)):
        self.chunk_size = chunk_size if chunk_size % 2 == 1 else chunk_size + 1
        self.path_width_range = path_width_range
        self.maze_carver = MazeCarver(self.chunk_size, path_width_range)

    # -------------------------
    # Constructores de tiles
    # -------------------------
    def make_tree(self) -> Tuple[str, int]:
        return ("TREE", 0)

    def make_grass(self) -> Tuple[str]:
        return ("GRASS",)

    def make_clear(self) -> Tuple[str]:
        return ("CLEAR",)

    # -------------------------
    # Generación de chunks
    # -------------------------
    def generate_maze_chunk(self, start_pos: Tuple[int, int] = None) -> List[List[Tuple]]:
        chunk = [[self.make_tree() for _ in range(self.chunk_size)] for _ in range(self.chunk_size)]
        return self.maze_carver.carve_maze(chunk, start_pos)

    def generate_clearing_chunk(self) -> List[List[Tuple]]:
        chunk = [[self.make_clear() for _ in range(self.chunk_size)] for _ in range(self.chunk_size)]
        num_trees = random.randint(0, max(0, self.chunk_size // 8))
        for _ in range(num_trees):
            x, y = random.randint(2, self.chunk_size - 3), random.randint(2, self.chunk_size - 3)
            chunk[y][x] = self.make_tree()
        return chunk
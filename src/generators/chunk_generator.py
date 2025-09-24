import random
from typing import List, Tuple
from factories.chunk_factory import ChunkFactory

class ChunkGenerator:
    """
    Genera chunks del mapa: clearing o maze.
    Solo decide tipo y delega a ChunkFactory.
    """

    def __init__(self, chunk_size: int = 11, path_width_range: Tuple[int, int] = (1, 2)):
        self.chunk_size = chunk_size if chunk_size % 2 == 1 else chunk_size + 1
        self.path_width_range = path_width_range
        self.chunk_factory = ChunkFactory(chunk_size, path_width_range)

    def generate_chunk(self, chunk_type: str = None) -> List[List[Tuple]]:
        """
        Genera un chunk completo.
        chunk_type puede ser "maze", "clearing" o None para random.
        """
        if chunk_type is None:
            chunk_type = "clearing" if random.random() < 0.3 else "maze"  # 30% claros, 70% maze

        if chunk_type == "clearing":
            return self.chunk_factory.generate_clearing_chunk()
        elif chunk_type == "maze":
            return self.chunk_factory.generate_maze_chunk()
        else:
            raise ValueError(f"Tipo de chunk desconocido: {chunk_type}")
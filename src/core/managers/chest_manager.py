import random
from collections import defaultdict
from factories import ChestFactory
from core.interfaces.i_chest import IChest
from typing import List, Optional, Tuple

class ChestManager:
    """
    Gestiona cofres en el mapa:
    - Los cofres solo se generan en tiles CLEAR.
    - Evita superposición con otros cofres.
    - Usa ChestFactory para generar cofres (devuelve IChest).
    """

    def __init__(self, chunk_size: int, chest_probability: float = 0.005, drop_prob: float = 0.5):
        self.chunk_size = chunk_size
        self.chests: defaultdict[int, defaultdict[int, List[List[Optional[IChest]]]]] = \
            defaultdict(lambda: defaultdict(lambda: None))
        self.chest_probability = chest_probability
        self.chest_factory = ChestFactory(drop_prob)

    def place_chests_in_chunk(self, chunk_x: int, chunk_y: int, chunk: List[List[Tuple]]):
        """Genera cofres dentro de un chunk dado, solo en tiles CLEAR."""
        # Inicializamos la matriz de cofres
        self.chests[chunk_y][chunk_x] = [[None for _ in range(self.chunk_size)] for _ in range(self.chunk_size)]

        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                if chunk[y][x][0] == "CLEAR" and random.random() < self.chest_probability:
                    self.chests[chunk_y][chunk_x][y][x] = self.chest_factory.create_chest()

    def get_chest(self, chunk_x: int, chunk_y: int, local_x: int, local_y: int) -> Optional[IChest]:
        """Devuelve el cofre en una posición local dentro del chunk, o None."""
        chest_chunk = self.chests.get(chunk_y, {}).get(chunk_x)
        if chest_chunk:
            return chest_chunk[local_y][local_x]
        return None
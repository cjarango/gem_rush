# src/factories/gem_loot_factory.py
import random
from typing import List, Tuple
from resources.gem_data import GEM_NAMES

class GemLootFactory:
    """
    Fábrica que genera loot en forma de gemas.
    Cada gema tiene chance de caer, con cantidad aleatoria.
    """

    def __init__(self, drop_prob: float = 0.5):
        self.drop_prob = drop_prob

    def generate_loot(self) -> List[Tuple[int, str, int]]:
        """
        Retorna lista de tuplas: (poder, nombre, cantidad).
        """
        loot: List[Tuple[int, str, int]] = []
        for poder, name in GEM_NAMES.items():
            if random.random() < self.drop_prob:
                cantidad = random.randint(1, 5)
                loot.append((poder, name, cantidad))
        return loot
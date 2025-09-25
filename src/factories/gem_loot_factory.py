# src/factories/gem_loot_factory.py
import random
from typing import List, Tuple
from resources.gem_data import GEM_NAMES

class GemLootFactory:
    """
    Fábrica que genera loot en forma de gemas.
    Cada gema tiene chance de caer, con cantidad aleatoria.
    La probabilidad depende del poder de la gema: más poder = más rara.
    """

    def __init__(self, base_drop_prob: float = 0.5):
        self.base_drop_prob = base_drop_prob

    def generate_loot(self) -> List[Tuple[int, str, int]]:
        """
        Retorna lista de tuplas: (poder, nombre, cantidad).
        Garantiza al menos una gema.
        """
        loot: List[Tuple[int, str, int]] = []
        for poder, name in GEM_NAMES.items():
            prob = self.base_drop_prob / (poder / 5)
            if random.random() < prob:
                max_cantidad = max(1, 6 - (poder // 10))
                cantidad = random.randint(1, max_cantidad)
                loot.append((poder, name, cantidad))

        # Garantizar al menos una gema
        if not loot:
            poder, name = random.choice(list(GEM_NAMES.items()))
            cantidad = 1
            loot.append((poder, name, cantidad))

        return loot

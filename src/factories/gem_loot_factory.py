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
        """
        loot: List[Tuple[int, str, int]] = []
        for poder, name in GEM_NAMES.items():
            # Escalamos probabilidad según el poder
            prob = self.base_drop_prob / (poder / 5)  
            # Ejemplo: poder=5 → prob=0.5, poder=50 → prob=0.05
            if random.random() < prob:
                # Cantidad también puede escalar inversamente: gemas raras salen de a 1
                max_cantidad = max(1, 6 - (poder // 10))
                cantidad = random.randint(1, max_cantidad)
                loot.append((poder, name, cantidad))
        return loot
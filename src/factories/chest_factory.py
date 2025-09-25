# src/factories/chest_factory.py
import random
from core.chest import Chest
from core.interfaces.i_chest import IChest
from .gem_loot_factory import GemLootFactory

class ChestFactory:
    """
    Fábrica de cofres:
    - Usa GemLootFactory para definir contenido.
    - Decide tamaño del cofre (small/large) según probabilidad.
    - Genera un costo de apertura (`open_cost`) basado en una gema del contenido.
    - Cofres grandes tienen costo mayor que pequeños.
    - Algunos cofres pueden ser mimics según probabilidad.
    - Los mimics tienen un costo adicional (`mimic_cost`) más alto.
    """

    def __init__(self, drop_prob: float = 0.5, large_chest_prob: float = 0.05, mimic_prob: float = 0.9):
        self.loot_factory = GemLootFactory(drop_prob)
        self.large_chest_prob = large_chest_prob
        self.mimic_prob = mimic_prob

    def create_chest(self, is_mimic: bool | None = None) -> IChest:
        if is_mimic is None:
            is_mimic = random.random() < self.mimic_prob

        contents = self.loot_factory.generate_loot()
        is_large = random.random() < self.large_chest_prob

        # -------------------
        # open_cost (visible)
        # -------------------
        open_cost = {}
        if contents:
            poder, _, cantidad = random.choice(contents)
            factor = random.uniform(0.8, 1.5) if is_large else random.uniform(0.5, 1.0)
            open_cost[poder] = max(1, int(cantidad * factor))
        else:
            # Cofre vacío, asignar costo mínimo
            open_cost[1] = 1

        # -------------------
        # mimic_cost (solo si es mimic)
        # -------------------
        mimic_cost = {}
        if is_mimic:
            if contents:
                poder, _, cantidad = random.choice(contents)
                factor = random.uniform(1.5, 2.5)
                mimic_cost[poder] = max(1, int(cantidad * factor))
            else:
                # Cofre vacío, asignar costo mínimo
                mimic_cost[1] = 2

        # Crear cofre
        chest: IChest = Chest(contents, open_cost, mimic_cost, is_mimic)
        chest._is_large = is_large
        return chest

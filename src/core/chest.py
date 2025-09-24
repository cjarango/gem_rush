from typing import List, Any, Optional
from core.interfaces import IChest
from core.interfaces import IInventory

class Chest(IChest):
    def __init__(self, contents: List[Any], open_cost: dict, mimic_cost: dict = None, is_mimic: bool = False):
        self._opened = False
        self._contents = contents
        self._open_cost = open_cost
        self._mimic_cost = mimic_cost or {}
        self._is_mimic = is_mimic
        self._is_large = False

    def is_opened(self) -> bool:
        return self._opened

    def get_open_cost(self) -> dict:
        return self._open_cost

    def get_mimic_cost(self) -> dict:
        return self._mimic_cost

    def is_mimic(self) -> bool:
        return self._is_mimic

    def get_contents(self) -> List[Any]:
        return self._contents

    def mark_opened(self):
        self._opened = True

    def can_open(self, inventory: IInventory, mimic_phase: bool = False) -> bool:
        """Verifica si el jugador tiene gemas suficientes para abrir."""
        cost_to_check = self._mimic_cost if (mimic_phase and self._is_mimic) else self._open_cost
        for poder, cantidad in cost_to_check.items():
            node = inventory.search(poder)
            if not node or node.getCantidad() < cantidad:
                return False
        return True
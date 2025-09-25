import random
from typing import Dict
from core.interfaces.i_inventory import IInventory

class Portal:
    """
    Representa un portal que aparece en el mapa.
    El jugador puede activarlo entregando gemas de Obsidiana.
    """
    OBSIDIAN_POWER = 50  # poder asociado a la Obsidiana

    def __init__(self):
        required = random.randint(50, 100)
        self._activated = False
        self._activation_cost: Dict[int, int] = {self.OBSIDIAN_POWER: required}

    def is_activated(self) -> bool:
        return self._activated

    def get_activation_cost(self) -> Dict[int, int]:
        return self._activation_cost

    def can_activate(self, inventory: IInventory) -> bool:
        for poder, cantidad in self._activation_cost.items():
            node = inventory.search(poder)
            if not node or node.getCantidad() < cantidad:
                return False
        return True

    def activate(self, inventory: IInventory) -> bool:
        if not self.can_activate(inventory):
            return False
        for poder, cantidad in self._activation_cost.items():
            node = inventory.search(poder)
            if node:
                node.setCantidad(node.getCantidad() - cantidad)
        self._activated = True
        return True

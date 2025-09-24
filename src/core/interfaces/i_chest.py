from typing import Protocol, List, Any

class IChest(Protocol):
    """Interfaz mínima para cofres."""

    def is_opened(self) -> bool:
        ...

    def open(self, inventory) -> List[Any]:
        """Intenta abrir el cofre usando el inventario del jugador"""
        ...

    def peek_contents(self) -> List[Any]:
        ...

    def is_mimic(self) -> bool:
        ...

    def get_cost(self) -> dict:
        """Devuelve el costo de apertura {poder: cantidad}"""
        ...
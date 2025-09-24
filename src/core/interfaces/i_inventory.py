# src/core/interfaces/i_inventory.py
from typing import Protocol, Optional, List
from core.binary_node import Node


class IInventory(Protocol):
    """
    Interfaz mínima para el inventario.
    Define operaciones esenciales sobre el árbol de gemas.
    """

    def insert(self, poder: int, cantidad: int = 1) -> None:
        """Inserta una gema en el inventario (si ya existe, aumenta la cantidad)."""
        ...

    def search(self, poder: int) -> Optional[Node]:
        """Busca un nodo por poder y devuelve el Node o None si no existe."""
        ...

    def delete(self, poder: int, cantidad: int = 1) -> None:
        """Elimina una cantidad de gemas del inventario; elimina el nodo si llega a cero."""
        ...

    def inorder(self) -> List[Node]:
        """Devuelve los nodos en orden ascendente según poder."""
        ...
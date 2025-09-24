from abc import ABC, abstractmethod
from typing import Tuple, Any

class IMap(ABC):
    """Interfaz para el mapa del juego."""

    @abstractmethod
    def get_tile(self, x: int, y: int) -> Tuple[str, Any]:
        """Devuelve el tipo de tile y datos adicionales en la posición (x, y)."""
        pass

    @abstractmethod
    def get_sprite(self, x: int, y: int):
        """Devuelve la imagen correspondiente al tile o cofre en la posición (x, y)."""
        pass

    @abstractmethod
    def collect_gem(self, x: int, y: int):
        """Recoge la gema en la posición (x, y) si existe, y la elimina del mapa."""
        pass

    @abstractmethod
    def interact_with_chest(self, player) -> dict | None:
        """Interactúa con un cofre en la posición del jugador, devolviendo el resultado."""
        pass

    @abstractmethod
    def is_blocked(self, x: int, y: int) -> bool:
        """Indica si la posición está bloqueada por un obstáculo o cofre."""
        pass

    @abstractmethod
    def is_clearing(self, x: int, y: int) -> bool:
        """Devuelve True si la posición pertenece a un clearing."""
        pass
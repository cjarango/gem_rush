from core.interfaces.i_inventory import IInventory

class Player:
    def __init__(self, x: int, y: int, inventory: IInventory):
        self.x = x
        self.y = y
        self._alive = True
        self.move_cooldown = 0
        self.normal_speed = 5
        self.clearing_speed = 2
        self.inventory = inventory  # inyectado, no dependemos de clase concreta

    # --------------------------
    # Métodos de estado
    # --------------------------
    def get_state(self) -> bool:
        """Devuelve True si el jugador sigue vivo, False si ha muerto."""
        return self._alive

    def die(self) -> None:
        """Mata al jugador (cambia el estado a muerto)."""
        self._alive = False
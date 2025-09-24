from core import Player
from core.interfaces import IMap
from controllers.chest_controller import ChestController
from typing import List, Any

class PlayerInteractionController:
    def __init__(self, player: Player, game_map: IMap):
        self.player = player
        self.game_map = game_map

    def collect_gem(self):
        if not self.player.get_state():
            return

        gem_value = self.game_map.collect_gem(self.player.x, self.player.y)
        if gem_value is not None:
            self.player.inventory.insert(gem_value, 1)

    def interact_with_chest(self) -> List[Any]:
        """
        Revisa tile actual, 4 adyacentes ortogonales y 4 diagonales.
        Intenta abrir el cofre si hay y agrega loot al inventario si se cumple el costo.
        """
        if not self.player.get_state():
            return []

        # Coordenadas relativas: ortogonales + diagonales
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = self.player.x + dx, self.player.y + dy
                ichest = self.game_map.get_chest(nx, ny)
                if ichest:
                    controller = ChestController(self.player, ichest)
                    result = controller.try_open()

                    # Opcional: mostrar mensaje flotante según resultado
                    if result["success"]:
                        print(f"Chest opened! {result['message']}")
                    else:
                        print(f"Cannot open chest: {result['message']}")

                    return result["items"]  # devuelve loot si se abrió, [] si no
        return []

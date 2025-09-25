from core import Player
from core.interfaces import IMap
from controllers.chest_controller import ChestController
from controllers.portal_controller import PortalController
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
        Checks current tile, 4 orthogonal and 4 diagonal neighbors.
        Tries to open the chest if present and adds loot to inventory if requirements are met.
        """
        if not self.player.get_state():
            return []

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = self.player.x + dx, self.player.y + dy
                ichest = self.game_map.get_chest(nx, ny)
                if ichest:
                    controller = ChestController(self.player, ichest)
                    result = controller.try_open()

                    if result["success"]:
                        print(f"Chest opened! {result['message']}")
                    else:
                        print(f"Cannot open chest: {result['message']}")

                    return result["items"]
        return []

    def interact_with_portal(self) -> dict:
        """
        Checks if the player is standing on a portal and tries to activate it.
        """
        if not self.player.get_state():
            return {"success": False, "message": "Player is not active"}

        portal = self.game_map.get_portal(self.player.x, self.player.y)
        if portal:
            controller = PortalController(self.player, portal)
            result = controller.try_activate()

            if result["success"]:
                print("Portal activated! You won the game 🎉")
            elif "message" in result:
                print(result["message"])

            return result

        return {"success": False, "message": "No portal here"}

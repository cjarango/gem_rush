from typing import Any, List
import random
from core import Player
from core.interfaces import IChest

class ChestController:
    def __init__(self, player: Player, chest: IChest, mimic_controller=None):
        self.player = player
        self.chest = chest
        self.mimic_controller = mimic_controller
        self.decision_active = False  # Nuevo flag para controlar bloqueo de movimiento

    def try_open(self, fight: bool = None) -> dict:
        if self.chest.is_opened():
            return {"success": False, "message": "Chest already opened", "items": []}

        # Pago normal del cofre
        if not self.chest.can_open(self.player.inventory, mimic_phase=False):
            return {"success": False, "message": "Not enough gems to open", "items": []}
        for poder, cantidad in self.chest.get_open_cost().items():
            self.player.inventory.delete(poder, cantidad)

        # Si es mimic
        if self.chest.is_mimic():
            if fight is None:
                if self.mimic_controller:
                    self.mimic_controller.start_decision(self.chest)
                    self.decision_active = True  # Activamos bloqueo de movimiento
                    return {"success": None, "message": "Mimic decision started"}
                else:
                    return {"success": False, "message": "Mimic controller missing", "items": []}

            # Se resuelve la decisión: liberamos flag
            self.decision_active = False
            if fight:
                if random.random() < 0.9:
                    self.player.die()
                    self.chest.mark_opened()
                    return {"success": False, "message": "You fought the mimic and were devoured!", "items": []}
                else:
                    contents: List[Any] = self.chest.get_contents()
                    for poder, name, cantidad in contents:
                        self.player.inventory.insert(poder, cantidad)
                    self.chest.mark_opened()
                    return {"success": True, "message": f"You fought the mimic and obtained {len(contents)} gem types!", "items": contents}

            # Pagar mimic_cost
            if not self.chest.can_open(self.player.inventory, mimic_phase=True):
                self.player.die()
                self.chest.mark_opened()
                return {"success": False, "message": "Mimic attacked! You died.", "items": []}
            for poder, cantidad in self.chest.get_mimic_cost().items():
                self.player.inventory.delete(poder, cantidad)
            contents: List[Any] = self.chest.get_contents()
            for poder, name, cantidad in contents:
                self.player.inventory.insert(poder, cantidad)
            self.chest.mark_opened()
            return {"success": True, "message": f"You paid {len(contents)} gem types from the mimic and survived!", "items": contents}

        # Cofre normal
        contents: List[Any] = self.chest.get_contents()
        for poder, name, cantidad in contents:
            self.player.inventory.insert(poder, cantidad)
        self.chest.mark_opened()
        return {"success": True, "message": f"Obtained {len(contents)} gem types", "items": contents}

    # -----------------------------
    # Getter para saber si hay decisión activa
    # -----------------------------
    def is_decision_active(self) -> bool:
        return self.decision_active

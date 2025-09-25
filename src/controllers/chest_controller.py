from typing import Any, List
import random
from core import Player
from core.interfaces import IChest

class ChestController:
    def __init__(self, player: Player, chest: IChest, mimic_controller=None):
        self.player = player
        self.chest = chest
        self.mimic_controller = mimic_controller
        self.decision_active = False  # Flag para bloquear movimiento durante la decisión

    def try_open(self, fight: bool = None) -> dict:
        # --------------------------
        # Cofre ya abierto
        # --------------------------
        if self.chest.is_opened():
            return {"success": False, "message": "Chest already opened", "items": []}

        # --------------------------
        # Pago normal del cofre
        # --------------------------
        if not self.chest.can_open(self.player.inventory, mimic_phase=False):
            return {"success": False, "message": "Not enough gems to open", "items": []}

        for poder, cantidad in self.chest.get_open_cost().items():
            self.player.inventory.delete(poder, cantidad)

        # --------------------------
        # Si es Mimic
        # --------------------------
        if self.chest.is_mimic():
            # Activar decisión Mimic si no se ha hecho todavía
            if fight is None:
                if self.mimic_controller:
                    self.mimic_controller.start_decision(self.chest)
                    self.decision_active = True
                    return {"success": None, "message": "Mimic decision started"}
                else:
                    return {"success": False, "message": "Mimic controller missing", "items": []}

            # Resolviendo la decisión: liberamos flag
            self.decision_active = False

            # Jugador decide pelear
            if fight:
                if random.random() < 0.9:  # 90% de morir
                    self.player.die()
                    self.chest.mark_opened()
                    return {"success": False, "message": "You fought the mimic and were devoured!", "items": []}
                else:
                    contents = self.chest.get_contents()
                    for poder, name, cantidad in contents:
                        self.player.inventory.insert(poder, cantidad)
                    self.chest.mark_opened()
                    return {"success": True, "message": f"You fought the mimic and obtained {len(contents)} gem types!", "items": contents}

            # Jugador decide pagar
            if not self.chest.can_open(self.player.inventory, mimic_phase=True):
                self.player.die()
                self.chest.mark_opened()
                return {"success": False, "message": "Mimic attacked! You died.", "items": []}

            for poder, cantidad in self.chest.get_mimic_cost().items():
                self.player.inventory.delete(poder, cantidad)
            contents = self.chest.get_contents()
            for poder, name, cantidad in contents:
                self.player.inventory.insert(poder, cantidad)
            self.chest.mark_opened()
            return {"success": True, "message": f"You paid {len(contents)} gem types from the mimic and survived!", "items": contents}

        # --------------------------
        # Cofre normal
        # --------------------------
        contents = self.chest.get_contents()
        for poder, name, cantidad in contents:
            self.player.inventory.insert(poder, cantidad)
        self.chest.mark_opened()
        return {"success": True, "message": f"Obtained {len(contents)} gem types", "items": contents}

    # -----------------------------
    # Getter para saber si hay decisión activa
    # -----------------------------
    def is_decision_active(self) -> bool:
        return self.decision_active

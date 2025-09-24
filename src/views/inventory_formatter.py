from resources.gem_data import GEM_NAMES
from core.inventory import Inventory

class InventoryFormatter:
    """Se encarga de formatear el inventario para mostrarlo al jugador."""

    @staticmethod
    def summary(inventory: Inventory) -> str:
        elements = inventory.inorder()
        if not elements:
            return "Inventario vacío"

        lines = []
        for node in elements:
            # Convertimos el poder en nombre de gema
            nombre = GEM_NAMES.get(int(node.poder), f"Gema {node.poder}")
            lines.append(f"{nombre} × {node.cantidad}")

        return "\n".join(lines)
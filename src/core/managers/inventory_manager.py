import os
from core.interfaces.i_inventory import IInventory

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

class InventoryManager:
    """Maneja la persistencia del inventario del jugador."""

    def __init__(self, inventory: IInventory, filename: str = "save_inventory.txt"):
        self.inventory = inventory
        self.filename = os.path.join(DATA_DIR, filename)

    def save(self):
        """Guarda el inventario en archivo usando preorder (power;quantity)."""
        preorder_list = self.inventory.preorder()
        with open(self.filename, "w") as f:
            for node_str in preorder_list:
                f.write(node_str + "\n")

    def load(self):
        """Carga el inventario desde archivo. Reinicia el BST antes de cargar."""
        if hasattr(self.inventory, "root"):
            self.inventory.root = None  # Reiniciar árbol

        try:
            with open(self.filename, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        power_str, qty_str = line.split(";")
                        self.inventory.insert(int(power_str), int(qty_str))
        except FileNotFoundError:
            # No existe archivo, inventario queda vacío
            pass

    def has_saved_inventory(self) -> bool:
        """Devuelve True si hay un archivo de inventario guardado con contenido."""
        return os.path.exists(self.filename) and os.path.getsize(self.filename) > 0
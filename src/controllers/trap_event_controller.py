import random
from resources.gem_data import GEM_NAMES

class TrapEventController:
    def __init__(self, player):
        self.player = player
        self.active = False
        self.gem_lost_name = None
        self.gem_lost_qty = 0

    # ====================
    # Activar trampa
    # ====================
    def trigger_trap(self):
        inv_nodes = self.player.inventory.inorder()
        if not inv_nodes:
            # Inventario vacío → nada que perder
            return None

        # Elegir nodo aleatorio del inventario
        lost_node = random.choice(inv_nodes)
        # Cantidad aleatoria entre 1 y la que tiene
        self.gem_lost_qty = random.randint(1, lost_node.getCantidad())
        self.gem_lost_name = lost_node.poder

        # Eliminar la gema del inventario
        self.player.inventory.delete(lost_node.poder, self.gem_lost_qty)

        # Marcar evento como activo temporalmente si quieres mostrar mensaje
        self.active = True
        return {"gem": self.gem_lost_name,
                "name": GEM_NAMES.get(self.gem_lost_name, str(self.gem_lost_name)),
                "qty": self.gem_lost_qty}

    # ====================
    # Finalizar evento
    # ====================
    def reset(self):
        self.active = False
        self.gem_lost_name = None
        self.gem_lost_qty = 0

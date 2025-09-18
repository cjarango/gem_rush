from inventory import Inventory

class Player:
    def __init__(self, x, y, game_map):
        self.x = x
        self.y = y
        self.game_map = game_map
        self.move_cooldown = 0
        self.normal_speed = 5
        self.clearing_speed = 2
        self._alive = True  # cambiar a _alive para usar getter/setter
        
        # Inventario usando BST
        self.inventory = Inventory()
    
    # --------------------------
    # Getters y Setters para alive
    # --------------------------
    @property
    def alive(self):
        """Getter para alive."""
        return self._alive
    
    @alive.setter
    def alive(self, value):
        """Setter para alive; asegura que solo sea booleano."""
        if not isinstance(value, bool):
            raise ValueError("alive debe ser un valor booleano")
        self._alive = value

    # --------------------------
    # Movimiento y recolección
    # --------------------------
    def move(self, dx, dy):
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return
            
        new_x, new_y = self.x + dx, self.y + dy

        # 1. Bloquear si es pared
        if self.game_map.is_wall(new_x, new_y):
            return

        # 2. Bloquear si hay un cofre cerrado
        chest = self.game_map.get_chest(new_x, new_y)
        if chest and not chest.opened:
            return

        # 3. Si no hay pared ni cofre, mover jugador
        self.x = new_x
        self.y = new_y

        # Velocidad según tipo de terreno
        self.move_cooldown = (
            self.clearing_speed if self.game_map.is_clearing(self.x, self.y)
            else self.normal_speed
        )

        # Pre-generar chunks adyacentes
        chunk_x, chunk_y = self.game_map.get_chunk_key(self.x, self.y)
        for dx_chunk in [-1, 0, 1]:
            for dy_chunk in [-1, 0, 1]:
                self.game_map.ensure_chunk(chunk_x + dx_chunk, chunk_y + dy_chunk)

        # Recoger gema automáticamente
        gem_value = self.game_map.collect_gem(self.x, self.y)
        if gem_value is not None:
            self.collect_gem(gem_value)
    
    def collect_gem(self, gem_value, cantidad=1):
        """Agregar gema al inventario (BST)."""
        self.inventory.insert(gem_value, cantidad)

    def interact_with_chest(self):
        """Intenta abrir un cofre en la posición actual y recoger los items."""
        chest = self.game_map.get_chest(self.x, self.y)
        if chest:
            items = chest.open()  # obtiene las gemas si no ha sido abierto
            for gem_value in items:
                self.collect_gem(gem_value)
            return items  # devuelve lo que se recogió
        return []  # no hay cofre en esta celda

    # Métodos para consultar el inventario delegando en Inventory
    def get_sorted_inventory(self):
        return self.inventory.inorder()

    def get_inventory_summary(self):
        return self.inventory.summary()

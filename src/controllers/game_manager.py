from controllers.chest_controller import ChestController
from core.managers import InventoryManager

class GameManager:
    def __init__(self, chunk_size, tile_size, hud=None, mimic_controller=None):
        self.chunk_size = chunk_size
        self.tile_size = tile_size
        self.hud = hud
        self.mimic_controller = mimic_controller
        self.paused = False
        self.pause_screen = None
        self.reset_game()

    def reset_game(self):
        from core.map import Map
        from core.player import Player
        from core.inventory import Inventory
        from core.managers.gem_manager import GemManager
        from controllers.player_movement_controller import PlayerMovementController
        from controllers.player_interaction_controller import PlayerInteractionController

        # Mapa
        self.game_map = Map(self.chunk_size, path_width_range=(1, 2), tile_size=self.tile_size)
        for cx in (-1, 0, 1):
            for cy in (-1, 0, 1):
                self.game_map.ensure_chunk(cx, cy)

        # Jugador e inventario
        self.player_inventory = Inventory()
        self.player = Player(self.chunk_size//2, self.chunk_size//2, self.player_inventory)
        self.inventory_manager = InventoryManager(self.player_inventory)

        # Controladores
        self.movement_ctrl = PlayerMovementController(self.player, self.game_map)
        self.interaction_ctrl = PlayerInteractionController(self.player, self.game_map)

        # Gem Manager
        self.gem_manager = GemManager(self.chunk_size)

        # Limpiar HUD si existe
        if self.hud:
            self.hud.clear_messages()

        # Reset pausa
        self.paused = False
        self.pause_screen = None

    def open_chest(self, chest, fight: bool = None):
        """
        Intenta abrir un cofre:
        - Si es mimic y fight=None → inicia MimicDecisionController.
        - Si no es mimic → abre normalmente.
        """
        controller = ChestController(self.player, chest, mimic_controller=self.mimic_controller)
        return controller.try_open(fight=fight)

    # ----------------------------
    # Métodos para pausa
    # ----------------------------
    def resume_game(self):
        """Cierra la pausa y vuelve a GameScreen."""
        self.paused = False
        self.pause_screen = None

    def quit_game(self, change_screen_callback):
        """Salir de la pausa y volver al menú principal."""
        self.paused = False
        self.pause_screen = None
        change_screen_callback("menu")

    # ----------------------------
    # Métodos públicos para guardar y cargar inventario
    # ----------------------------
    def save_inventory(self):
        """Guarda el inventario del jugador en disco."""
        self.inventory_manager.save()

    def load_inventory(self):
        """Carga el inventario del jugador desde disco."""
        self.inventory_manager.load()
        
    def has_saved_inventory(self) -> bool:
        """Devuelve True si existe un archivo de inventario guardado."""
        return self.inventory_manager.has_saved_inventory()
from controllers.chest_controller import ChestController

class GameManager:
    def __init__(self, chunk_size, tile_size, hud=None, mimic_controller=None):
        self.chunk_size = chunk_size
        self.tile_size = tile_size
        self.hud = hud
        self.mimic_controller = mimic_controller
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
        for cx in (-1,0,1):
            for cy in (-1,0,1):
                self.game_map.ensure_chunk(cx, cy)

        # Jugador
        self.player_inventory = Inventory()
        self.player = Player(self.chunk_size//2, self.chunk_size//2, self.player_inventory)

        # Controladores
        self.movement_ctrl = PlayerMovementController(self.player, self.game_map)
        self.interaction_ctrl = PlayerInteractionController(self.player, self.game_map)

        # Gem Manager
        self.gem_manager = GemManager(self.chunk_size)

        # Limpiar HUD si existe
        if self.hud:
            self.hud.clear_messages()

    def open_chest(self, chest, fight: bool = None):
        """
        Intenta abrir un cofre:
        - Si es mimic y fight=None → inicia MimicDecisionController.
        - Si no es mimic → abre normalmente.
        """
        controller = ChestController(self.player, chest, mimic_controller=self.mimic_controller)
        result = controller.try_open(fight=fight)
        return result

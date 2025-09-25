from controllers.chest_controller import ChestController
from core.managers import InventoryManager
from controllers.portal_controller import PortalController

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
        from core.managers.portal_manager import PortalManager
        from controllers.player_movement_controller import PlayerMovementController
        from controllers.player_interaction_controller import PlayerInteractionController
        from core.portal import Portal

        # ----------------------------
        # Mapa
        # ----------------------------
        self.game_map = Map(self.chunk_size, path_width_range=(1, 2), tile_size=self.tile_size)
        for cx in (-1, 0, 1):
            for cy in (-1, 0, 1):
                self.game_map.ensure_chunk(cx, cy)

        # ----------------------------
        # Jugador e inventario
        # ----------------------------
        self.player_inventory = Inventory()
        self.player = Player(self.chunk_size // 2, self.chunk_size // 2, self.player_inventory)
        self.inventory_manager = InventoryManager(self.player_inventory)

        # ----------------------------
        # Controladores
        # ----------------------------
        self.movement_ctrl = PlayerMovementController(self.player, self.game_map)
        self.interaction_ctrl = PlayerInteractionController(self.player, self.game_map)

        # ----------------------------
        # Managers
        # ----------------------------
        self.gem_manager = GemManager(self.chunk_size)
        self.portal_manager = PortalManager(self.chunk_size)

        # ----------------------------
        # Aseguramos que haya un portal inicial
        # ----------------------------
        chunk = self.game_map.chunks[0][0]
        self.portal_manager.try_spawn_portal(0, 0, chunk)

        # Obtenemos el portal desde PortalManager
        portal_info = self.portal_manager.get_portal_info(0, 0)
        if portal_info:
            _, _, portal = portal_info
        else:
            # Si no hay portal, creamos uno manualmente y lo colocamos en el diccionario interno
            portal = Portal()
            self.portal_manager.portals[(0, 0)] = (0, 0, portal)

        self.portal = portal
        self.portal_ctrl = PortalController(self.player, self.portal)

        # ----------------------------
        # HUD y pausa
        # ----------------------------
        if self.hud:
            self.hud.clear_messages()

        self.paused = False
        self.pause_screen = None

    # ----------------------------
    # Cofres
    # ----------------------------
    def open_chest(self, chest, fight: bool = None):
        controller = ChestController(self.player, chest, mimic_controller=self.mimic_controller)
        return controller.try_open(fight=fight)

    # ----------------------------
    # Portal
    # ----------------------------
    def try_activate_portal(self) -> dict:
        return self.portal_ctrl.try_activate()

    # ----------------------------
    # Pausa
    # ----------------------------
    def resume_game(self):
        self.paused = False
        self.pause_screen = None

    def quit_game(self, change_screen_callback):
        self.paused = False
        self.pause_screen = None
        change_screen_callback("menu")

    # ----------------------------
    # Inventario
    # ----------------------------
    def save_inventory(self):
        self.inventory_manager.save()

    def load_inventory(self):
        self.inventory_manager.load()
        
    def has_saved_inventory(self) -> bool:
        return self.inventory_manager.has_saved_inventory()

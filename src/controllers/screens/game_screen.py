import pygame
from resources.gem_data import GEM_NAMES
from views.inventory_formatter import InventoryFormatter
from controllers import GameManager, HUDController, MimicDecisionController
from controllers.screens.pause_screen import PauseScreen

class GameScreen:
    def __init__(self, screen, game: GameManager, hud: HUDController, mimic_controller: MimicDecisionController, change_screen_callback):
        self.screen = screen
        self.game = game
        self.hud = hud
        self.mimic_controller = mimic_controller
        self.change_screen_callback = change_screen_callback

        self.move_directions = {"up": 0, "down": 0, "left": 0, "right": 0}
        self.inventory_open = False
        self.current_chest_in_range = None
        self.current_cost_text = ""

        self.TILE = game.tile_size
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.COLOR_PLAYER = (0, 255, 0)
        self.COLOR_BG = (0, 0, 0)
        self.COLOR_TEXT = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 24)

        # Estado de pausa
        self.is_paused = False
        self.pause_screen = PauseScreen(screen, self, change_screen_callback, game_manager=self.game)

    def handle_event(self, event):
        if self.is_paused:
            self.pause_screen.handle_event(event)
            return

        if event.type == pygame.QUIT:
            self.change_screen_callback("quit")
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.is_paused = True  # activamos pausa
            elif event.key == pygame.K_w: self.move_directions["up"] = 1
            elif event.key == pygame.K_s: self.move_directions["down"] = 1
            elif event.key == pygame.K_a: self.move_directions["left"] = 1
            elif event.key == pygame.K_d: self.move_directions["right"] = 1
            elif event.key == pygame.K_TAB:
                self.inventory_open = not self.inventory_open
            elif event.key == pygame.K_e and self.current_chest_in_range:
                result = self.game.open_chest(self.current_chest_in_range)
                if result["success"] is not None:
                    self.hud.add_message(result["message"], duration_seconds=3.0)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w: self.move_directions["up"] = 0
            elif event.key == pygame.K_s: self.move_directions["down"] = 0
            elif event.key == pygame.K_a: self.move_directions["left"] = 0
            elif event.key == pygame.K_d: self.move_directions["right"] = 0

        self.mimic_controller.handle_event(event)

    def update(self, dt: float):
        if self.is_paused:
            self.pause_screen.update(dt)
            return

        # Actualizamos HUD
        self.hud.update(dt)

        # Movimiento del jugador
        dx = self.move_directions["right"] - self.move_directions["left"]
        dy = self.move_directions["down"] - self.move_directions["up"]
        if dx != 0 or dy != 0:
            self.game.movement_ctrl.move(dx, dy, dt)
            gem_value = self.game.interaction_ctrl.collect_gem()
            if gem_value:
                self.hud.add_message(f"Collected {GEM_NAMES.get(gem_value, f'Gema {gem_value}')}!", duration_seconds=2.0)

        # Cofres
        self.current_chest_in_range = None
        self.current_cost_text = ""
        for dx_c in [-1,0,1]:
            for dy_c in [-1,0,1]:
                nx, ny = self.game.player.x + dx_c, self.game.player.y + dy_c
                ichest = self.game.game_map.get_chest(nx, ny)
                if ichest and not ichest.is_opened():
                    self.current_chest_in_range = ichest
                    cost = ichest.get_open_cost()
                    if cost:
                        self.current_cost_text = ", ".join(f"{c}x {GEM_NAMES.get(g, g)}" for g,c in cost.items())
                    break
            if self.current_chest_in_range:
                break

        # Mimic
        mimic_result = self.mimic_controller.update()
        if mimic_result:
            fight = mimic_result["choice"] == "fight"
            result = self.game.open_chest(mimic_result["chest"], fight=fight)
            self.hud.add_message(result["message"], duration_seconds=3.0)

    def render(self):
        # Render normal del juego
        self.screen.fill(self.COLOR_BG)
        self.screen.blit(
            self.font.render("TAB: Inventory | E: Open Chest | ESC: Pause", True, self.COLOR_TEXT),
            (10, 10)
        )

        tiles_x, tiles_y = self.WIDTH//self.TILE, self.HEIGHT//self.TILE
        start_x, start_y = self.game.player.x - tiles_x//2, self.game.player.y - tiles_y//2

        for sy in range(tiles_y+1):
            for sx in range(tiles_x+1):
                mx, my = start_x+sx, start_y+sy
                sprite = self.game.game_map.get_sprite(mx,my)
                self.screen.blit(sprite,(sx*self.TILE,sy*self.TILE))
                gem_value = self.game.game_map.get_gem(mx,my)
                if gem_value is not None:
                    color = self.game.gem_manager.get_gem_color(gem_value)
                    pygame.draw.circle(self.screen, color, (sx*self.TILE+self.TILE//2, sy*self.TILE+self.TILE//2), self.TILE//4)

        pygame.draw.rect(self.screen, self.COLOR_PLAYER, (tiles_x//2*self.TILE, tiles_y//2*self.TILE, self.TILE, self.TILE))

        self.hud.draw_floating_messages()
        self.hud.draw_chest_cost(self.current_cost_text)
        self.hud.draw_inventory(self.game.player.inventory, self.inventory_open, InventoryFormatter)
        self.mimic_controller.draw()

        # Render de pausa encima si está pausado
        if self.is_paused:
            self.pause_screen.render()

        pygame.display.flip()

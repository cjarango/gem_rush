import pygame
import random
from resources.gem_data import GEM_NAMES
from views.inventory_formatter import InventoryFormatter
from controllers import GameManager, HUDController, MimicDecisionController
from controllers.screens.pause_screen import PauseScreen
from controllers.thief_event_controller import ThiefEventController

class GameScreen:
    def __init__(self, screen, game: GameManager, hud: HUDController,
                 mimic_controller: MimicDecisionController, change_screen_callback):
        self.screen = screen
        self.game = game
        self.hud = hud
        self.mimic_controller = mimic_controller
        self.change_screen_callback = change_screen_callback

        # Movimiento e inventario
        self.move_directions = {"up": 0, "down": 0, "left": 0, "right": 0}
        self.inventory_open = False
        self.current_chest_in_range = None
        self.current_portal_in_range = None
        self.current_cost_text = ""
        self.current_portal_cost_text = ""

        # Configuración visual
        self.TILE = game.tile_size
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.COLOR_PLAYER = (0, 255, 0)
        self.COLOR_BG = (0, 0, 0)
        self.COLOR_TEXT = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 24)

        # Pausa
        self.is_paused = False
        self.pause_screen = PauseScreen(screen, self, change_screen_callback, game_manager=self.game)

        # Evento ladrón
        self.thief_controller = ThiefEventController(
            player=game.player,
            screen=screen,
            font=self.font,
            width=self.WIDTH,
            height=self.HEIGHT
        )

        # Posición anterior del jugador (para recalcular probabilidad solo al moverse)
        self.prev_player_pos = (game.player.x, game.player.y)

        # Flag para evitar que el mimic sobrescriba mensajes de Game Over
        self.player_dead_by_thief = False

    # ----------------------------
    # Gestión de eventos
    # ----------------------------
    def handle_event(self, event):
        if self.is_paused:
            self.pause_screen.handle_event(event)
            return

        if self.thief_controller.active:
            self.thief_controller.handle_event(event)
            return

        if event.type == pygame.QUIT:
            self.change_screen_callback("quit")
        elif event.type == pygame.KEYDOWN:
            self._handle_keydown(event.key)
        elif event.type == pygame.KEYUP:
            self._handle_keyup(event.key)

        self.mimic_controller.handle_event(event)

    def _handle_keydown(self, key):
        if key == pygame.K_ESCAPE:
            self.is_paused = True
        elif not self.thief_controller.active:
            if key == pygame.K_w: self.move_directions["up"] = 1
            elif key == pygame.K_s: self.move_directions["down"] = 1
            elif key == pygame.K_a: self.move_directions["left"] = 1
            elif key == pygame.K_d: self.move_directions["right"] = 1
        if key == pygame.K_TAB:
            self.inventory_open = not self.inventory_open
        elif key == pygame.K_e:
            self._interact()

    def _handle_keyup(self, key):
        if not self.thief_controller.active:
            if key == pygame.K_w: self.move_directions["up"] = 0
            elif key == pygame.K_s: self.move_directions["down"] = 0
            elif key == pygame.K_a: self.move_directions["left"] = 0
            elif key == pygame.K_d: self.move_directions["right"] = 0

    # ----------------------------
    # Interacción con objetos
    # ----------------------------
    def _interact(self):
        if self.thief_controller.active:
            return

        px, py = self.game.player.x, self.game.player.y

        if self.current_chest_in_range:
            result = self.game.open_chest(self.current_chest_in_range)
            if result.get("success") is not None:
                self.hud.add_message(result["message"], duration_seconds=3.0)
            return

        if self.current_portal_in_range:
            portal = self.current_portal_in_range
            self.game.portal = portal
            result = self.game.try_activate_portal()
            message = result.get("message", "Portal activated!" if result.get("success") else "Cannot activate portal")
            self.hud.add_message(message, duration_seconds=3.0)
            if result.get("success"):
                self.change_screen_callback("win")

    # ----------------------------
    # Actualización del juego
    # ----------------------------
    def update(self, dt: float):
        if self.is_paused:
            self.pause_screen.update(dt)
            return

        self.hud.update(dt)

        # ==============================
        # Evento ladrón
        # ==============================
        if self.thief_controller.active:
            self.move_directions = {k:0 for k in self.move_directions}
            result = self.thief_controller.update()
            if result:
                if result["choice"] == "fight" and result.get("result") == "killed":
                    death_messages = [
                        "The thief's dagger found its mark. Your journey ends here...",
                        "Caught off guard, the thief claims your gems and your life!",
                        "A shadow strikes! You fall to the thief's cunning attack.",
                        "The thief laughs as your adventure comes to an untimely end."
                    ]
                    message = random.choice(death_messages)
                    self.hud.add_message(message, duration_seconds=3.0)
                    self.player_dead_by_thief = True
                    self.change_screen_callback("game_over", game_over_message=message)
                    return
                elif result["choice"] == "fight":
                    survive_messages = [
                        "You fought bravely and survived the thief's assault!",
                        "The thief lunges, but you dodge and strike back!",
                        "A narrow escape! You live to see another gem."
                    ]
                    message = random.choice(survive_messages)
                    self.hud.add_message(message, duration_seconds=3.0)
                elif result["choice"] == "pay":
                    pay_messages = [
                        f"You reluctantly hand over {result['qty']} of {result['name']} to the thief.",
                        f"The thief snatches {result['qty']} {result['name']} from you. Ouch!",
                        f"You part with {result['qty']} {result['name']} to save your skin."
                    ]
                    message = random.choice(pay_messages)
                    self.hud.add_message(message, duration_seconds=3.0)
        else:
            current_pos = (self.game.player.x, self.game.player.y)
            if current_pos != self.prev_player_pos:
                self.prev_player_pos = current_pos

                # Probabilidad de ladrón
                total = self.game.get_inventory_total_value()
                k_thief = 0.00005
                chance_thief = min(total * k_thief, 0.05)
                if random.random() < chance_thief:
                    self.thief_controller.start_event(duration_frames=600)
                    self.move_directions = {k:0 for k in self.move_directions}

                # Probabilidad de trampa
                self._check_trap()

            # Movimiento normal
            self._update_player_movement(dt)
            self._update_chest_in_range()
            self._update_portal_in_range()
            self._update_mimic()

            # -----------------------------
            # Comprobar si murió de otra forma (Mimic u otra)
            # -----------------------------
            if not self.game.player.get_state() and not self.player_dead_by_thief:
                message = getattr(self, 'last_death_message', "You have met your fate!")
                self.change_screen_callback("game_over", game_over_message=message)

    # -----------------------------
    # Movimiento del jugador
    # -----------------------------
    def _update_player_movement(self, dt):
        dx = self.move_directions["right"] - self.move_directions["left"]
        dy = self.move_directions["down"] - self.move_directions["up"]
        if dx != 0 or dy != 0:
            self.game.movement_ctrl.move(dx, dy, dt)
            gem_value = self.game.interaction_ctrl.collect_gem()
            if gem_value:
                self.hud.add_message(f"Collected {GEM_NAMES.get(gem_value, f'Gem {gem_value}')}!", duration_seconds=2.0)

    # -----------------------------
    # Evento trampa
    # -----------------------------
    def _check_trap(self):
        inv = self.game.player.inventory
        if not inv.root:
            return

        total_value = self.game.get_inventory_total_value()
        k_trap = 0.00002
        chance = min(total_value * k_trap, 0.03)
        if random.random() < chance:
            nodes = inv.inorder()
            if nodes:
                gem_node = random.choice(nodes)
                qty = random.randint(1, gem_node.getCantidad())
                inv.delete(gem_node.poder, qty)
                self.hud.add_message(
                    f"You fell into a trap and lost {qty} of {GEM_NAMES.get(gem_node.poder, gem_node.poder)}!",
                    duration_seconds=3.0
                )

    # -----------------------------
    # Chequeo de cofres y portales
    # -----------------------------
    def _update_chest_in_range(self):
        self.current_chest_in_range = None
        self.current_cost_text = ""
        px, py = self.game.player.x, self.game.player.y
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                nx, ny = px+dx, py+dy
                chest = self.game.game_map.get_chest(nx, ny)
                if chest and not chest.is_opened():
                    self.current_chest_in_range = chest
                    cost = chest.get_open_cost()
                    if cost:
                        self.current_cost_text = ", ".join(f"{c}x {GEM_NAMES.get(g,g)}" for g,c in cost.items())
                    return

    def _update_portal_in_range(self):
        self.current_portal_in_range = None
        self.current_portal_cost_text = ""
        px, py = self.game.player.x, self.game.player.y
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                nx, ny = px+dx, py+dy
                portal, pos = self.game.game_map.get_portal(nx, ny)
                if portal and pos == (nx, ny) and not portal.is_activated():
                    self.current_portal_in_range = portal
                    cost = portal.get_activation_cost()
                    if cost:
                        self.current_portal_cost_text = ", ".join(f"{c}x {GEM_NAMES.get(g, g)}" for g, c in cost.items())
                    return

    # -----------------------------
    # Mimic
    # -----------------------------
    def _update_mimic(self):
        # Evitamos que mimic sobrescriba mensaje de Game Over por ladrón
        if self.player_dead_by_thief:
            return

        mimic_result = self.mimic_controller.update()
        if mimic_result:
            fight = mimic_result["choice"] == "fight"
            result = self.game.open_chest(mimic_result["chest"], fight=fight)
            self.hud.add_message(result["message"], duration_seconds=3.0)
            # Guardamos mensaje de muerte en caso de que el Mimic mate al jugador
            if result.get("result") == "killed":
                self.last_death_message = result["message"]
                
    # -----------------------------
    # Renderizado
    # -----------------------------
    def render(self):
        self.screen.fill(self.COLOR_BG)
        self.screen.blit(
            self.font.render("TAB: Inventory | E: Interact | ESC: Pause", True, self.COLOR_TEXT),
            (10, 10)
        )

        self._render_map()
        self._render_player()
        self._render_hud()
        self.thief_controller.draw()

        if self.is_paused:
            self.pause_screen.render()

        pygame.display.flip()

    def _render_map(self):
        tiles_x, tiles_y = self.WIDTH//self.TILE, self.HEIGHT//self.TILE
        start_x = self.game.player.x - tiles_x//2
        start_y = self.game.player.y - tiles_y//2

        for sy in range(tiles_y+1):
            for sx in range(tiles_x+1):
                mx, my = start_x+sx, start_y+sy
                sprite = self.game.game_map.get_sprite(mx, my)
                self.screen.blit(sprite, (sx*self.TILE, sy*self.TILE))

                gem_value = self.game.game_map.get_gem(mx, my)
                if gem_value is not None:
                    color = self.game.gem_manager.get_gem_color(gem_value)
                    pygame.draw.circle(self.screen, color,
                                       (sx*self.TILE+self.TILE//2, sy*self.TILE+self.TILE//2), self.TILE//4)

    def _render_player(self):
        tiles_x, tiles_y = self.WIDTH//self.TILE, self.HEIGHT//self.TILE
        pygame.draw.rect(self.screen, self.COLOR_PLAYER,
                         (tiles_x//2*self.TILE, tiles_y//2*self.TILE, self.TILE, self.TILE))

    def _render_hud(self):
        self.hud.draw_floating_messages()
        self.hud.draw_chest_cost(self.current_cost_text)
        if self.current_portal_cost_text:
            self.hud.draw_chest_cost(self.current_portal_cost_text)
        self.hud.draw_inventory(self.game.player.inventory, self.inventory_open, InventoryFormatter)
        self.mimic_controller.draw()

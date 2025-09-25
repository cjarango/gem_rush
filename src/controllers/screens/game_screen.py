import pygame
import random
import os
from resources.gem_data import GEM_NAMES
from views.inventory_formatter import InventoryFormatter
from controllers import GameManager, HUDController, MimicDecisionController
from controllers.screens.pause_screen import PauseScreen
from controllers.thief_event_controller import ThiefEventController
from audio_manager import AudioManager
class GameScreen:
    screen: pygame.Surface
    WIDTH: int
    HEIGHT: int
    TILE: int
    
    def __init__(self, screen, game: GameManager, hud: HUDController,
                 mimic_controller: MimicDecisionController, change_screen_callback):
        self.screen = screen
        self.game = game
        self.hud = hud
        self.mimic_controller = mimic_controller
        self.change_screen_callback = change_screen_callback
        self.TILE = game.tile_size
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.audio_manager = AudioManager()
        self.audio_manager.load_and_play_music("src/audio/ambient.mp3")
        # Movimiento e inventario
        self.move_directions = {"up": 0, "down": 0, "left": 0, "right": 0}
        self.inventory_open = False
        self.current_chest_in_range = None
        self.current_portal_in_range = None
        self.current_cost_text = ""
        self.current_portal_cost_text = ""

        # Configuración visual
        self.COLOR_PLAYER = (0, 255, 0)
        self.COLOR_BG = (0, 0, 0)
        self.COLOR_TEXT = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 24)
        
        # --- SISTEMA DE SPRITES DEL JUGADOR ---
        self.player_direction = "down"      # Última dirección
        self.player_anim_index = 0
        self.player_anim_timer_ms = 0
        self._last_anim_tick = pygame.time.get_ticks()
        self.PLAYER_ANIM_SPEED_MS = 200     # Cambia frame cada 200ms
        
        # Cargar sprites del jugador
        self.player_sprites = self._load_player_sprites()
        
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

        # Posición anterior del jugador
        self.prev_player_pos = (game.player.x, game.player.y)
        self.player_dead_by_thief = False

    def _load_player_sprites(self):
        """Carga todos los sprites del jugador desde archivos PNG"""
        def load_sprite(path, fallback_color=(0, 255, 0)):
            """Carga un sprite individual con fallback en caso de error"""
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    return pygame.transform.scale(img, (self.TILE, self.TILE))
                else:
                    print(f"Archivo no encontrado: {path}")
            except pygame.error as e:
                print(f"Error cargando sprite: {path} - {e}")
            
            # Fallback: crear sprite simple
            surf = pygame.Surface((self.TILE, self.TILE), pygame.SRCALPHA)
            surf.fill(fallback_color)
            return surf

        # Estructura de carpetas: textures/player/
        base_path = os.path.join("textures", "player")
        
        sprites = {
            "idle": {},
            "walk": {"down": [], "up": [], "left": [], "right": []}
        }

        # Direcciones disponibles
        directions = ["down", "up", "left", "right"]
        
        # Cargar sprites IDLE (estructura exacta de tus archivos)
        print("Cargando sprites de idle...")
        for direction in directions:
            path = os.path.join(base_path, f"player_idle_{direction}.png")
            sprites["idle"][direction] = load_sprite(path)
            print(f"Cargado idle {direction}")

        # Cargar sprites WALK (3 frames: 0, 1, 2 para cada dirección)
        print("Cargando sprites de walk...")
        for direction in directions:
            frames = []
            # Cargar exactamente 3 frames (0, 1, 2) según tu estructura
            for frame_num in range(3):
                path = os.path.join(base_path, f"player_walk_{direction}_{frame_num}.png")
                frame_sprite = load_sprite(path)
                frames.append(frame_sprite)
                print(f"Cargado walk {direction} frame {frame_num}")
            
            sprites["walk"][direction] = frames

        print(f"Sprites cargados completamente:")
        for anim_type in sprites:
            for direction in sprites[anim_type]:
                if anim_type == "walk":
                    print(f"  {anim_type} {direction}: {len(sprites[anim_type][direction])} frames")
                else:
                    print(f"  {anim_type} {direction}: OK")

        return sprites

    def _render_player(self):
        """Renderiza el sprite animado del jugador en el centro de la pantalla"""
        # Centro de la pantalla en coordenadas de tiles
        tiles_x = self.WIDTH // self.TILE
        tiles_y = self.HEIGHT // self.TILE

        # Posición del jugador en pantalla (centrado)
        player_screen_x = (tiles_x // 2) * self.TILE
        player_screen_y = (tiles_y // 2) * self.TILE

        # ¿Se está moviendo?
        moving = any(self.move_directions.values())

        # Actualizar dirección según teclas presionadas
        if self.move_directions.get("right"):
            self.player_direction = "right"
        elif self.move_directions.get("left"):
            self.player_direction = "left"
        elif self.move_directions.get("down"):
            self.player_direction = "down"
        elif self.move_directions.get("up"):
            self.player_direction = "up"

        # Sistema de animación basado en tiempo
        now = pygame.time.get_ticks()
        dt = now - self._last_anim_tick
        self._last_anim_tick = now

        sprite = None

        try:
            if moving:
                # Animación de caminar
                self.player_anim_timer_ms += dt
                if self.player_anim_timer_ms >= self.PLAYER_ANIM_SPEED_MS:
                    self.player_anim_timer_ms = 0
                    # Avanzar al siguiente frame
                    walk_frames = self.player_sprites["walk"][self.player_direction]
                    if len(walk_frames) > 0:
                        self.player_anim_index = (self.player_anim_index + 1) % len(walk_frames)
                
                # Obtener sprite actual de walk
                walk_frames = self.player_sprites["walk"][self.player_direction]
                if len(walk_frames) > 0 and self.player_anim_index < len(walk_frames):
                    sprite = walk_frames[self.player_anim_index]
            else:
                # Estado idle (sin movimiento)
                self.player_anim_index = 0
                self.player_anim_timer_ms = 0
                sprite = self.player_sprites["idle"][self.player_direction]

        except (KeyError, IndexError) as e:
            print(f"Error accediendo a sprite del jugador: {e}")
            sprite = None

        # Dibujar el sprite del jugador
        if sprite is not None:
            self.screen.blit(sprite, (player_screen_x, player_screen_y))
        else:
            # Fallback: rectángulo verde simple
            pygame.draw.rect(self.screen, self.COLOR_PLAYER, 
                           (player_screen_x, player_screen_y, self.TILE, self.TILE))

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

    def update(self, dt: float):
        if self.is_paused:
            self.pause_screen.update(dt)
            return

        self.hud.update(dt)

        # Gestión del evento ladrón
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

            # Comprobar si murió de otra forma (Mimic u otra)
            if not self.game.player.get_state() and not self.player_dead_by_thief:
                message = getattr(self, 'last_death_message', "You have met your fate!")
                self.change_screen_callback("game_over", game_over_message=message)

    def _update_player_movement(self, dt):
        dx = self.move_directions["right"] - self.move_directions["left"]
        dy = self.move_directions["down"] - self.move_directions["up"]
        if dx != 0 or dy != 0:
            self.game.movement_ctrl.move(dx, dy, dt)
            gem_value = self.game.interaction_ctrl.collect_gem()
            if gem_value:
                self.hud.add_message(f"Collected {GEM_NAMES.get(gem_value, f'Gem {gem_value}')}!", duration_seconds=2.0)

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

    def _render_hud(self):
        self.hud.draw_floating_messages()
        self.hud.draw_chest_cost(self.current_cost_text)
        if self.current_portal_cost_text:
            self.hud.draw_chest_cost(self.current_portal_cost_text)
        self.hud.draw_inventory(self.game.player.inventory, self.inventory_open, InventoryFormatter)
        self.mimic_controller.draw()
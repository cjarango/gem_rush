import pygame
import random
import os
from resources.gem_data import GEM_NAMES
from views.inventory_formatter import InventoryFormatter
from controllers import GameManager, HUDController, MimicDecisionController, ThiefEventController
from controllers.screens import PauseScreen
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
        
        # Movement and inventory
        self.move_directions = {"up": 0, "down": 0, "left": 0, "right": 0}
        self.inventory_open = False
        self.current_chest_in_range = None
        self.current_portal_in_range = None
        self.current_cost_text = ""
        self.current_portal_cost_text = ""

        # Visual configuration
        self.COLOR_PLAYER = (0, 255, 0)
        self.COLOR_BG = (0, 0, 0)
        self.COLOR_TEXT = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 24)
        
        # --- PLAYER SPRITES SYSTEM ---
        self.player_direction = "down"
        self.player_anim_index = 0
        self.player_anim_timer_ms = 0
        self._last_anim_tick = pygame.time.get_ticks()
        self.PLAYER_ANIM_SPEED_MS = 200
        
        # Load player sprites
        self.player_sprites = self._load_player_sprites()
        
        # Pause
        self.is_paused = False
        self.pause_screen = PauseScreen(screen, self, change_screen_callback, game_manager=self.game)
        
        # Thief event
        self.thief_controller = ThiefEventController(
            player=game.player,
            screen=screen,
            font=self.font,
            width=self.WIDTH,
            height=self.HEIGHT
        )

        # Previous player position
        self.prev_player_pos = (game.player.x, game.player.y)
        self.player_dead_by_thief = False

    # -----------------------------
    # Load player sprites
    # -----------------------------
    def _load_player_sprites(self):
        """Loads all player sprites from PNG files"""
        def load_sprite(path, fallback_color=(0, 255, 0)):
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    return pygame.transform.scale(img, (self.TILE, self.TILE))
            except pygame.error as e:
                print(f"Error loading sprite: {path} - {e}")
            surf = pygame.Surface((self.TILE, self.TILE), pygame.SRCALPHA)
            surf.fill(fallback_color)
            return surf

        base_path = os.path.join("textures", "player")
        sprites = {"idle": {}, "walk": {"down": [], "up": [], "left": [], "right": []}}
        directions = ["down", "up", "left", "right"]

        # Load idle sprites
        for direction in directions:
            path = os.path.join(base_path, f"player_idle_{direction}.png")
            sprites["idle"][direction] = load_sprite(path)

        # Load walk sprites (3 frames)
        for direction in directions:
            frames = []
            for frame_num in range(3):
                path = os.path.join(base_path, f"player_walk_{direction}_{frame_num}.png")
                frames.append(load_sprite(path))
            sprites["walk"][direction] = frames

        return sprites

    # -----------------------------
    # Render player
    # -----------------------------
    def _render_player(self):
        tiles_x = self.WIDTH // self.TILE
        tiles_y = self.HEIGHT // self.TILE
        player_screen_x = (tiles_x // 2) * self.TILE
        player_screen_y = (tiles_y // 2) * self.TILE
        moving = any(self.move_directions.values())

        if self.move_directions.get("right"):
            self.player_direction = "right"
        elif self.move_directions.get("left"):
            self.player_direction = "left"
        elif self.move_directions.get("down"):
            self.player_direction = "down"
        elif self.move_directions.get("up"):
            self.player_direction = "up"

        now = pygame.time.get_ticks()
        dt = now - self._last_anim_tick
        self._last_anim_tick = now

        sprite = None
        try:
            if moving:
                self.player_anim_timer_ms += dt
                if self.player_anim_timer_ms >= self.PLAYER_ANIM_SPEED_MS:
                    self.player_anim_timer_ms = 0
                    walk_frames = self.player_sprites["walk"][self.player_direction]
                    if walk_frames:
                        self.player_anim_index = (self.player_anim_index + 1) % len(walk_frames)
                walk_frames = self.player_sprites["walk"][self.player_direction]
                if walk_frames and self.player_anim_index < len(walk_frames):
                    sprite = walk_frames[self.player_anim_index]
            else:
                self.player_anim_index = 0
                self.player_anim_timer_ms = 0
                sprite = self.player_sprites["idle"][self.player_direction]
        except (KeyError, IndexError) as e:
            print(f"Error accessing player sprite: {e}")
            sprite = None

        if sprite:
            self.screen.blit(sprite, (player_screen_x, player_screen_y))
        else:
            pygame.draw.rect(self.screen, self.COLOR_PLAYER, (player_screen_x, player_screen_y, self.TILE, self.TILE))

    # -----------------------------
    # Event handling
    # -----------------------------
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

    # -----------------------------
    # Update and game logic
    # -----------------------------
    def update(self, dt: float):
        if self.is_paused:
            self.pause_screen.update(dt)
            return

        self.hud.update(dt)

        if self.thief_controller.active:
            self.move_directions = {k:0 for k in self.move_directions}
            result = self.thief_controller.update()
            if result:
                # Thief results handled here...
                pass
        else:
            current_pos = (self.game.player.x, self.game.player.y)
            if current_pos != self.prev_player_pos:
                self.prev_player_pos = current_pos
                self._check_thief_chance()
                self._check_trap()

            self._update_player_movement(dt)
            self._update_chest_in_range()
            self._update_portal_in_range()
            self._update_mimic()

            # Check if player died by other causes (Mimic or other)
            if not self.game.player.get_state() and not self.player_dead_by_thief:
                message = getattr(self, 'last_death_message', "You have met your fate!")
                self.change_screen_callback("game_over", game_over_message=message)

    # -----------------------------
    # Rendering
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

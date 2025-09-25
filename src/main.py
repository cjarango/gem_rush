import pygame
from controllers.screens import MenuScreen, GameScreen, GameOverScreen, WinScreen
from controllers import GameManager, HUDController, MimicDecisionController

# --------------------------
# Configuración
# --------------------------
TILE = 32
CHUNK_SIZE = 21
WIDTH, HEIGHT = 1000, 700
COLOR_TEXT = (255, 255, 255)
FPS = 120

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Progressive Maze Enhanced")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# --------------------------
# Inicializar gestores
# --------------------------
mimic_controller = MimicDecisionController(None, screen, font, WIDTH, HEIGHT)
game_manager = GameManager(CHUNK_SIZE, TILE, mimic_controller=mimic_controller)
mimic_controller.player = game_manager.player
hud = HUDController(screen, font, WIDTH, HEIGHT, COLOR_TEXT)

# --------------------------
# Sistema de pantallas
# --------------------------
current_screen = None

def change_screen(screen_name):
    global current_screen, game_manager
    if screen_name == "menu":
        current_screen = MenuScreen(screen, change_screen, game_manager)
    elif screen_name == "game":
        current_screen = GameScreen(screen, game_manager, hud, mimic_controller, change_screen)
    elif screen_name == "game_over":
        current_screen = GameOverScreen(screen, change_screen)
    elif screen_name == "win":
        current_screen = WinScreen(screen, change_screen)
    elif screen_name == "restart_game":
        # --- RESET GAME ---
        game_manager.reset_game()
        mimic_controller.player = game_manager.player
        hud.clear_messages()
        current_screen = GameScreen(screen, game_manager, hud, mimic_controller, change_screen)
    elif screen_name == "quit":
        pygame.quit()
        exit()

# Empezar con el menú
change_screen("menu")

# --------------------------
# Loop principal
# --------------------------
running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # delta time en segundos

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            # Enviar eventos a la pantalla actual
            if hasattr(current_screen, "is_paused") and current_screen.is_paused:
                current_screen.pause_screen.handle_event(event)
            else:
                current_screen.handle_event(event)

    # Actualizar
    if hasattr(current_screen, "is_paused") and current_screen.is_paused:
        current_screen.pause_screen.update(dt)
    else:
        current_screen.update(dt)

        # Comprobar Game Over
        if hasattr(current_screen, "game") and not current_screen.game.player.get_state():
            change_screen("game_over")

    # Renderizar
    if hasattr(current_screen, "is_paused") and current_screen.is_paused:
        # Renderiza el juego de fondo y encima la pausa
        current_screen.render()
    else:
        current_screen.render()

pygame.quit()

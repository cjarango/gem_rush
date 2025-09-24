import pygame
from resources.gem_data import GEM_NAMES
from views.inventory_formatter import InventoryFormatter
from controllers import GameManager, HUDController, MimicDecisionController

# --------------------------
# Configuración
# --------------------------
TILE = 32
CHUNK_SIZE = 21
WIDTH, HEIGHT = 1000, 700

COLOR_PLAYER = (0, 255, 0)
COLOR_BG = (0, 0, 0)
COLOR_TEXT = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Progressive Maze Enhanced")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# --------------------------
# Inicializar gestores
# --------------------------
mimic_controller = MimicDecisionController(None, screen, font, WIDTH, HEIGHT)
game = GameManager(CHUNK_SIZE, TILE, mimic_controller=mimic_controller)
mimic_controller.player = game.player  # Asociar jugador al mimic
hud = HUDController(screen, font, WIDTH, HEIGHT, COLOR_TEXT)

# Estado de juego
move_directions = {"up": False, "down": False, "left": False, "right": False}
inventory_open = False
current_chest_in_range = None
current_cost_text = ""

# --------------------------
# Función de texto multilínea centrado
# --------------------------
def draw_multiline_text_centered(text, font, color, y, max_width, line_spacing=5):
    words = text.split(" ")
    lines, current_line = [], ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        text_x = WIDTH // 2 - text_surface.get_width() // 2
        screen.blit(text_surface, (text_x, y + i*(font.get_height() + line_spacing)))

# --------------------------
# Loop principal
# --------------------------
running = True
while running:
    # --------------------------
    # Pantalla Game Over
    # --------------------------
    if not game.player.get_state():
        waiting_for_input = True
        while waiting_for_input:
            screen.fill(COLOR_BG)
            draw_multiline_text_centered("GAME OVER", pygame.font.SysFont(None, 72, bold=True), (255,0,0), HEIGHT//2-100, WIDTH)
            draw_multiline_text_centered("The mimic's feast is over. You were the main course.", font, COLOR_TEXT, HEIGHT//2, WIDTH)
            draw_multiline_text_centered("Press R to restart", font, COLOR_TEXT, HEIGHT//2+50, WIDTH)
            draw_multiline_text_centered("Press H to quit", font, COLOR_TEXT, HEIGHT//2+80, WIDTH)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting_for_input = False
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h:
                        waiting_for_input = False
                        running = False
                    elif event.key == pygame.K_r:
                        # --- RESET GAME ---
                        game.reset_game()
                        mimic_controller.player = game.player
                        move_directions = {k: False for k in move_directions}
                        inventory_open = False
                        current_chest_in_range = None
                        current_cost_text = ""
                        
                        # Limpiar pantalla y mensajes flotantes inmediatamente
                        screen.fill(COLOR_BG)
                        hud.clear_messages()
                        pygame.display.flip()

                        waiting_for_input = False
            clock.tick(60)
        continue

    # --------------------------
    # Manejo de eventos
    # --------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Teclado movimiento
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
            elif event.key == pygame.K_w: move_directions["up"] = True
            elif event.key == pygame.K_s: move_directions["down"] = True
            elif event.key == pygame.K_a: move_directions["left"] = True
            elif event.key == pygame.K_d: move_directions["right"] = True
            elif event.key == pygame.K_TAB: inventory_open = not inventory_open
            elif event.key == pygame.K_e:
                if current_chest_in_range:
                    result = game.open_chest(current_chest_in_range)
                    if result["success"] is not None:
                        hud.add_message(result["message"], 180)

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w: move_directions["up"] = False
            elif event.key == pygame.K_s: move_directions["down"] = False
            elif event.key == pygame.K_a: move_directions["left"] = False
            elif event.key == pygame.K_d: move_directions["right"] = False

        # Eventos mimic
        mimic_controller.handle_event(event)

    # --------------------------
    # Movimiento
    # --------------------------
    dx = move_directions["right"] - move_directions["left"]
    dy = move_directions["down"] - move_directions["up"]
    if dx != 0 or dy != 0:
        game.movement_ctrl.move(dx, dy)
        gem_value = game.interaction_ctrl.collect_gem()
        if gem_value:
            hud.add_message(f"Collected {GEM_NAMES.get(gem_value, f'Gema {gem_value}')}!", 60)

    # --------------------------
    # Buscar cofre cercano
    # --------------------------
    current_chest_in_range = None
    current_cost_text = ""
    for dx in [-1,0,1]:
        for dy in [-1,0,1]:
            nx, ny = game.player.x + dx, game.player.y + dy
            ichest = game.game_map.get_chest(nx, ny)
            if ichest and not ichest.is_opened():
                current_chest_in_range = ichest
                cost = ichest.get_open_cost()
                if cost:
                    current_cost_text = ", ".join(f"{c}x {GEM_NAMES.get(g, g)}" for g,c in cost.items())
                break
        if current_chest_in_range:
            break

    # --------------------------
    # Update mimic
    # --------------------------
    mimic_result = mimic_controller.update()
    if mimic_result:
        fight = mimic_result["choice"] == "fight"
        result = game.open_chest(mimic_result["chest"], fight=fight)
        hud.add_message(result["message"], 180)

    # --------------------------
    # Render
    # --------------------------
    screen.fill(COLOR_BG)
    screen.blit(font.render("TAB: Inventory | E: Open Chest", True, COLOR_TEXT), (10,10))

    tiles_x, tiles_y = WIDTH//TILE, HEIGHT//TILE
    render_start_x, render_start_y = game.player.x - tiles_x//2, game.player.y - tiles_y//2
    for sy in range(tiles_y+1):
        for sx in range(tiles_x+1):
            mx, my = render_start_x+sx, render_start_y+sy
            sprite = game.game_map.get_sprite(mx,my)
            screen.blit(sprite,(sx*TILE,sy*TILE))
            gem_value = game.game_map.get_gem(mx,my)
            if gem_value is not None:
                color = game.gem_manager.get_gem_color(gem_value)
                pygame.draw.circle(screen, color, (sx*TILE+TILE//2, sy*TILE+TILE//2), TILE//4)

    pygame.draw.rect(screen, COLOR_PLAYER, (tiles_x//2*TILE, tiles_y//2*TILE, TILE, TILE))

    hud.draw_floating_messages()
    hud.draw_chest_cost(current_cost_text)
    hud.draw_inventory(game.player.inventory, inventory_open, InventoryFormatter)
    mimic_controller.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("Game Over")

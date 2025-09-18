# main.py
import pygame
from Map import Map
from Player import Player
from gem_data import GEM_NAMES
import random

# --------------------------
# Configuration
# --------------------------
TILE = 32
CHUNK_SIZE = 21
WIDTH, HEIGHT = 1000, 700

COLOR_PLAYER = (0, 255, 0)
COLOR_BG = (0, 0, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_HIGHLIGHT = (255, 215, 0)
COLOR_DECISION_BG = (0, 0, 0, 180)  # fondo semi-transparente

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Progressive Maze Enhanced")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# --------------------------
# Map settings
# --------------------------
game_map = Map(CHUNK_SIZE, path_width_range=(1, 2), tile_size=TILE)
game_map.chest_probability = 0.02

# Pre-generate initial chunks
for cx in (-1, 0, 1):
    for cy in (-1, 0, 1):
        game_map.ensure_chunk(cx, cy)

# Player
player_start_x = CHUNK_SIZE // 2
player_start_y = CHUNK_SIZE // 2
player = Player(player_start_x, player_start_y, game_map)

# Movement
move_directions = {"up": False, "down": False, "left": False, "right": False}

# Inventory and messages
inventory_open = False
floating_messages = []

# Decision system
decision_active = False
decision_chest = None
MAX_DECISION_TIMER = 600
decision_timer = MAX_DECISION_TIMER

# --------------------------
# Helper function: multiline text
# --------------------------
def draw_multiline_text(text, font, color, x, y, max_width, line_spacing=5):
    words = text.split(" ")
    lines = []
    current_line = ""
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
        line_surf = font.render(line, True, color)
        screen.blit(line_surf, (x - line_surf.get_width()//2, y + i*(font.get_height() + line_spacing)))

# --------------------------
# Main loop
# --------------------------
running = True
while running:
    if not player.alive:
        # Game over screen
        waiting_for_input = True
        while waiting_for_input:
            screen.fill(COLOR_BG)

            # Fuentes predeterminadas
            title_font = pygame.font.SysFont(None, 72, bold=True)
            font_big = pygame.font.SysFont(None, 30)
            font_small = pygame.font.SysFont(None, 25)

            # Mensajes en orden
            title_text = title_font.render("GAME OVER", True, (255, 0, 0))
            reason_text = font_big.render("You could not satisfy the mimic's hunger", True, COLOR_TEXT)
            restart_text = font_small.render("Press R to restart", True, COLOR_TEXT)
            quit_text = font_small.render("Press H to quit", True, COLOR_TEXT)

            # Calcular alturas con espacios adicionales
            space_small = 10
            space_large = 30  # espacio extra entre bloques

            total_height = (
                title_text.get_height()
                + space_large
                + reason_text.get_height()
                + space_large
                + restart_text.get_height()
                + space_small
                + quit_text.get_height()
            )
            start_y = HEIGHT // 2 - total_height // 2

            # Dibujar en pantalla centrado
            y = start_y
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, y))
            y += title_text.get_height() + space_large

            screen.blit(reason_text, (WIDTH // 2 - reason_text.get_width() // 2, y))
            y += reason_text.get_height() + space_large

            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, y))
            y += restart_text.get_height() + space_small

            screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, y))

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
                        # Reset map and player
                        game_map = Map(CHUNK_SIZE, path_width_range=(1, 2), tile_size=TILE)
                        game_map.chest_probability = 0.02
                        for cx in (-1, 0, 1):
                            for cy in (-1, 0, 1):
                                game_map.ensure_chunk(cx, cy)
                        player = Player(player_start_x, player_start_y, game_map)
                        move_directions = {"up": False, "down": False, "left": False, "right": False}
                        inventory_open = False
                        floating_messages.clear()
                        waiting_for_input = False
            clock.tick(60)
        continue

    # --------------------------
    # Events
    # --------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if not decision_active:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_w:
                    move_directions["up"] = True
                elif event.key == pygame.K_s:
                    move_directions["down"] = True
                elif event.key == pygame.K_a:
                    move_directions["left"] = True
                elif event.key == pygame.K_d:
                    move_directions["right"] = True
                elif event.key == pygame.K_TAB:
                    inventory_open = not inventory_open
                elif event.key == pygame.K_e:
                    # Check nearby chests
                    interacted = False
                    for dx in [-1,0,1]:
                        for dy in [-1,0,1]:
                            cx, cy = player.x + dx, player.y + dy
                            chest = game_map.get_chest(cx, cy)
                            if chest and not chest.opened:
                                # Intentar abrir (la función interact ahora exige y descuenta 'cost')
                                result = chest.interact(player)

                                # Si devuelve decision -> reveal mimic (no lo marcamos abierto aún)
                                if result.get("decision"):
                                    if result.get("usado"):
                                        floating_messages.append({"text": result["usado"], "timer": 180})
                                    decision_active = True
                                    decision_chest = chest
                                    decision_timer = MAX_DECISION_TIMER
                                else:
                                    # cofre normal o mensajes de error
                                    if result.get("usado"):
                                        floating_messages.append({"text": result["usado"], "timer": 180})
                                    if result.get("obtenido"):
                                        floating_messages.append({"text": result["obtenido"], "timer": 180})
                                interacted = True
                                break
                        if interacted:
                            break
                    if not interacted:
                        floating_messages.append({"text": "No chests nearby", "timer": 180})

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                move_directions["up"] = False
            elif event.key == pygame.K_s:
                move_directions["down"] = False
            elif event.key == pygame.K_a:
                move_directions["left"] = False
            elif event.key == pygame.K_d:
                move_directions["right"] = False

        elif event.type == pygame.MOUSEBUTTONDOWN and decision_active:
            mx, my = pygame.mouse.get_pos()
            button_width, button_height = 200, 60
            gap = 100
            total_width = button_width*2 + gap
            left_x = (WIDTH - total_width)//2
            right_x = left_x + button_width + gap
            top_y = HEIGHT//2 + 50  # debe coincidir con UI
            left_rect = pygame.Rect(left_x, top_y, button_width, button_height)
            right_rect = pygame.Rect(right_x, top_y, button_width, button_height)

            if left_rect.collidepoint(mx, my):
                # Fight
                if random.random() < 0.6:
                    floating_messages.append({"text":"You survived the fight!", "timer":180})
                    # after winning fight consider the mimic 'defeated' and chest opened
                    decision_chest.opened = True
                else:
                    player.alive = False
                    floating_messages.append({"text":"You died fighting the mimic!", "timer":180})
                decision_active = False

            elif right_rect.collidepoint(mx, my):
                # Satisfy
                nodo = player.inventory.search(decision_chest.poder)
                cantidad_actual = nodo.getCantidad() if nodo else 0
                demand = getattr(decision_chest, "mimic_demand", 0)
                if cantidad_actual >= demand:
                    player.inventory.delete(decision_chest.poder, demand)
                    floating_messages.append({
                        "text": f"You satisfied the mimic! Lost {demand} {GEM_NAMES.get(decision_chest.poder)}",
                        "timer":180
                    })
                    # mimic satisfied -> chest considered opened/resolved
                    decision_chest.opened = True
                else:
                    player.alive = False
                    floating_messages.append({
                        "text": f"You could not satisfy the mimic and died! Needed {demand} {GEM_NAMES.get(decision_chest.poder)}",
                        "timer":180
                    })
                decision_active = False

    # --------------------------
    # Movement
    # --------------------------
    if not decision_active:
        dx, dy = 0,0
        if move_directions["up"]:
            dy -= 1
        if move_directions["down"]:
            dy += 1
        if move_directions["left"]:
            dx -= 1
        if move_directions["right"]:
            dx += 1
        if dx !=0 or dy !=0:
            player.move(dx, dy)

    # --------------------------
    # Rendering
    # --------------------------
    screen.fill(COLOR_BG)
    screen.blit(font.render("TAB: Inventory | E: Open Chest", True, COLOR_TEXT), (10,10))

    # Tiles
    tiles_x = WIDTH//TILE
    tiles_y = HEIGHT//TILE
    render_start_x = player.x - tiles_x//2
    render_start_y = player.y - tiles_y//2
    for sy in range(tiles_y+1):
        for sx in range(tiles_x+1):
            mx, my = render_start_x+sx, render_start_y+sy
            sprite = game_map.get_sprite(mx,my)
            screen.blit(sprite,(sx*TILE,sy*TILE))
            gem_value = game_map.get_gem(mx,my)
            if gem_value is not None:
                gem_color = game_map.get_gem_color(gem_value)
                pygame.draw.circle(screen, gem_color,(sx*TILE+TILE//2,sy*TILE+TILE//2),TILE//4)

    # Player
    player_screen_x = tiles_x//2 * TILE
    player_screen_y = tiles_y//2 * TILE
    pygame.draw.rect(screen,COLOR_PLAYER,(player_screen_x,player_screen_y,TILE,TILE))

    # Chest cost message (always show when no decision active)
    if not decision_active:
        chest_message = ""
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                cx, cy = player.x+dx, player.y+dy
                chest = game_map.get_chest(cx,cy)
                if chest and not chest.opened:
                    gem_name = GEM_NAMES.get(chest.poder,f"Gem {chest.poder}")
                    chest_message = f"Use {gem_name} × {getattr(chest,'cost',0)} to open the chest"
                    break
            if chest_message:
                break
        if chest_message:
            chest_text_surface = font.render(chest_message, True, COLOR_HIGHLIGHT)
            screen.blit(chest_text_surface,(WIDTH//2 - chest_text_surface.get_width()//2,10))

    # Floating messages
    if not decision_active:
        y_offset = 50
        for msg in floating_messages[:]:
            msg_surface = font.render(msg["text"], True, COLOR_HIGHLIGHT)
            screen.blit(msg_surface,(WIDTH//2-msg_surface.get_width()//2,y_offset))
            y_offset += 25
            msg["timer"] -= 1
            if msg["timer"] <=0:
                floating_messages.remove(msg)

    # --------------------------
    # Decision UI
    # --------------------------
    if decision_active:
        # Fondo
        pygame.draw.rect(screen, COLOR_DECISION_BG, (0, HEIGHT//2-120, WIDTH, 300))

        # Mensaje
        main_msg = "A wild mimic appeared! What will you do?"
        draw_multiline_text(main_msg, font, COLOR_HIGHLIGHT, WIDTH//2, HEIGHT//2 - 100, max_width=WIDTH-100)

        # Barra
        bar_width, bar_height = 400, 25
        bar_x = WIDTH//2 - bar_width//2
        bar_y = HEIGHT//2 - 40
        pygame.draw.rect(screen, (50,50,50), (bar_x, bar_y, bar_width, bar_height), border_radius=12)
        time_ratio = decision_timer / MAX_DECISION_TIMER
        fill_width = int(bar_width * time_ratio)
        for i in range(fill_width):
            color_ratio = i / bar_width
            red = int(255 * (1 - color_ratio))
            green = int(255 * color_ratio)
            pygame.draw.line(screen, (red, green, 0), (bar_x + i, bar_y), (bar_x + i, bar_y + bar_height - 1))
        pygame.draw.rect(screen, (255,255,255), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=12)

        # Timer
        timer_text = font.render(f"Time: {decision_timer//60}", True, COLOR_HIGHLIGHT)
        screen.blit(timer_text, (WIDTH//2 - timer_text.get_width()//2, bar_y - 30))

        # Botones
        button_width, button_height = 200, 60
        gap = 100
        total_width = button_width*2 + gap
        left_x = (WIDTH - total_width)//2
        right_x = left_x + button_width + gap
        top_y = HEIGHT//2 + 50
        left_rect = pygame.Rect(left_x, top_y, button_width, button_height)
        right_rect = pygame.Rect(right_x, top_y, button_width, button_height)
        pygame.draw.rect(screen, (200,0,0), left_rect, border_radius=10)
        pygame.draw.rect(screen, (0,0,200), right_rect, border_radius=10)
        fight_text = font.render("Fight", True, COLOR_TEXT)
        satisfy_text = font.render("Satisfy", True, COLOR_TEXT)
        screen.blit(fight_text, (left_rect.x + (button_width - fight_text.get_width())//2,
                                 left_rect.y + (button_height - fight_text.get_height())//2))
        screen.blit(satisfy_text, (right_rect.x + (button_width - satisfy_text.get_width())//2,
                                   right_rect.y + (button_height - satisfy_text.get_height())//2))

        # Decrement timer
        decision_timer -= 1
        if decision_timer <= 0:
            player.alive = False
            decision_active = False

    # Inventory
    if inventory_open:
        inventory_summary = player.get_inventory_summary()
        lines = inventory_summary.split("\n")
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, COLOR_TEXT)
            screen.blit(text_surface, (WIDTH - 300, 50 + i*20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("Game Over")

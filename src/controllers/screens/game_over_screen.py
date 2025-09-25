import pygame
from controllers.screens.screen_base import ScreenBase

class GameOverScreen(ScreenBase):
    def __init__(self, screen, change_screen_callback, game_over_message=None):
        super().__init__(screen)
        self.change_screen_callback = change_screen_callback

        self.title_font = pygame.font.SysFont(None, 72, bold=True)
        self.font = pygame.font.SysFont(None, 36)
        self.COLOR_BG = (0, 0, 0)
        self.COLOR_TEXT = (255, 255, 255)

        # Mensaje de Game Over personalizable
        self.game_over_message = game_over_message or "The mimic's feast is over. You were the main course."

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.change_screen_callback("quit")
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                self.change_screen_callback("menu")  # Volver al menú principal
            elif event.key == pygame.K_r:
                self.change_screen_callback("restart_game")  # Reiniciar juego

    def update(self, dt=0):  # dt opcional por compatibilidad
        pass  # No hay animaciones por ahora

    def render(self):
        self.screen.fill(self.COLOR_BG)

        # Título
        self.draw_multiline_text_centered(
            "GAME OVER", self.title_font, (255, 0, 0), self.screen.get_height() // 2 - 100
        )

        # Mensaje principal
        self.draw_multiline_text_centered(
            self.game_over_message, 
            self.font, self.COLOR_TEXT, self.screen.get_height() // 2
        )

        # Espacio adicional antes de las instrucciones
        instruction_start_y = self.screen.get_height() // 2 + 70

        self.draw_multiline_text_centered(
            "Press R to restart", self.font, self.COLOR_TEXT, instruction_start_y
        )
        self.draw_multiline_text_centered(
            "Press H to return to menu", self.font, self.COLOR_TEXT, instruction_start_y + 40
        )

        pygame.display.flip()

    def draw_multiline_text_centered(self, text, font, color, y, max_width=None, line_spacing=5):
        if max_width is None:
            max_width = self.screen.get_width()
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
            text_x = self.screen.get_width() // 2 - text_surface.get_width() // 2
            self.screen.blit(text_surface, (text_x, y + i * (font.get_height() + line_spacing)))

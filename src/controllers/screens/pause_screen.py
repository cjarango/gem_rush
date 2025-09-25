import pygame
from controllers.screens.screen_base import ScreenBase

class PauseScreen(ScreenBase):
    def __init__(self, screen, game_screen, change_screen_callback, game_manager):
        super().__init__(screen)
        self.game_screen = game_screen
        self.change_screen_callback = change_screen_callback
        self.game_manager = game_manager  # <-- acceso al GameManager

        self.options = ["Resume", "Quit"]
        self.selected_index = 0
        self.font = pygame.font.SysFont("Arial", 36)
        self.option_rects = []

        self.active_color = (255, 255, 255)
        self.inactive_color = (200, 200, 200)
        self.highlight_bg = (50, 50, 50)

        self.center_y = screen.get_height() // 2
        self.spacing = 300

        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.title_text = "Game Paused"

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_RIGHT:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                self.activate_option()

        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(event.pos):
                    self.selected_index = i
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(event.pos):
                    self.selected_index = i
                    self.activate_option()
                    break

    def activate_option(self):
        option = self.options[self.selected_index]
        if option == "Resume":
            self.game_screen.is_paused = False
        elif option == "Quit":
            # Guardamos inventario antes de salir
            self.game_manager.save_inventory()
            self.change_screen_callback("menu")

    def update(self, dt=0):
        pass

    def render(self):
        w, h = self.screen.get_size()

        # Overlay semitransparente
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Mensaje superior centrado (blanco)
        title_surf = self.title_font.render(self.title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(w//2, h//2 - 100))
        self.screen.blit(title_surf, title_rect)

        # Dibujar opciones horizontalmente y centradas
        self.option_rects = []
        total_width = sum(self.font.size(opt)[0] for opt in self.options) + self.spacing * (len(self.options) - 1)
        start_x = w // 2 - total_width // 2

        current_x = start_x
        for i, option in enumerate(self.options):
            color = self.active_color if i == self.selected_index else self.inactive_color
            text_surf = self.font.render(option, True, color)
            text_rect = text_surf.get_rect(midtop=(current_x + text_surf.get_width()//2, self.center_y))
            
            # Fondo de selección
            if i == self.selected_index:
                highlight_rect = text_rect.copy()
                highlight_rect.inflate_ip(30, 15)
                pygame.draw.rect(self.screen, self.highlight_bg, highlight_rect)

            self.screen.blit(text_surf, text_rect)
            self.option_rects.append(text_rect)
            current_x += text_surf.get_width() + self.spacing

        pygame.display.flip()

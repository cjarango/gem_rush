import pygame
from controllers.screens.screen_base import ScreenBase


class MenuScreen(ScreenBase):
    def __init__(self, screen, change_screen_callback, game_manager):
        super().__init__(screen)
        self.change_screen_callback = change_screen_callback
        self.game_manager = game_manager

        # Opciones de menú
        self.options = ["Nuevo Juego", "Continuar", "Salir"]
        self.selected_index = 0

        # Fuentes y colores
        self.font = pygame.font.SysFont("Arial", 36)
        self.active_color = (255, 255, 255)    # Texto seleccionado
        self.inactive_color = (200, 200, 200)  # Texto no seleccionado
        self.disabled_color = (100, 100, 100)  # Continuar desactivado
        self.highlight_bg = (50, 50, 50)       # Fondo hover

        # Posición inicial de las opciones
        self.start_x = 50
        self.start_y = 200
        self.line_height = 60

        # Animación de hover
        self.current_y = self.start_y
        self.target_y = self.start_y
        self.animation_speed = 15  # pixeles por frame

        # Estado ventana de error
        self.error_message = None
        self.error_timer = 0  # ms

    def handle_event(self, event):
        if self.error_message:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                # Cierra ventana de error con cualquier tecla o click
                self.error_message = None
            return

        if event.type == pygame.KEYDOWN:
            previous_index = self.selected_index
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self.select_option()

            if self.selected_index != previous_index:
                self.target_y = self.start_y + self.selected_index * self.line_height

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for i, _ in enumerate(self.options):
                rect = pygame.Rect(self.start_x, self.start_y + i * self.line_height,
                                   300, self.font.get_height())
                if rect.collidepoint(mx, my):
                    self.selected_index = i
                    self.target_y = self.start_y + self.selected_index * self.line_height

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, _ in enumerate(self.options):
                rect = pygame.Rect(self.start_x, self.start_y + i * self.line_height,
                                   300, self.font.get_height())
                if rect.collidepoint(mx, my):
                    self.selected_index = i
                    self.select_option()

    def select_option(self):
        option = self.options[self.selected_index]
        if option == "Nuevo Juego":
            self.game_manager.reset_game()
            self.change_screen_callback("game")

        elif option == "Continuar":
            if self.game_manager.has_saved_inventory():
                try:
                    self.game_manager.load_inventory()
                    self.change_screen_callback("game")
                except Exception:
                    self.show_error("No se pudo cargar el inventario.")
            else:
                self.show_error("No hay datos guardados.")

        elif option == "Salir":
            self.change_screen_callback("quit")

    def show_error(self, message: str):
        """Muestra una ventana emergente de error con un mensaje."""
        self.error_message = message
        self.error_timer = pygame.time.get_ticks()  # guarda tiempo de inicio

    def update(self, dt=0):
        # Animación suave de hover
        if self.current_y < self.target_y:
            self.current_y = min(self.current_y + self.animation_speed, self.target_y)
        elif self.current_y > self.target_y:
            self.current_y = max(self.current_y - self.animation_speed, self.target_y)

    def render(self):
        self.screen.fill((30, 30, 30))  # Fondo gris oscuro

        for i, option in enumerate(self.options):
            # Colores según estado
            if option == "Continuar" and not self.game_manager.has_saved_inventory():
                color = self.disabled_color
            elif i == self.selected_index:
                color = self.active_color
            else:
                color = self.inactive_color

            text_surface = self.font.render(option, True, color)
            rect = text_surface.get_rect(topleft=(self.start_x, self.start_y + i * self.line_height))

            # Fondo hover
            if i == self.selected_index and not (option == "Continuar" and not self.game_manager.has_saved_inventory()):
                highlight_rect = rect.copy()
                highlight_rect.y = self.current_y
                highlight_rect.inflate_ip(20, 10)
                pygame.draw.rect(self.screen, self.highlight_bg, highlight_rect)

            self.screen.blit(text_surface, rect)

        # Si hay error -> dibujar ventana emergente
        if self.error_message:
            self.draw_error_window()

        pygame.display.flip()

    def draw_error_window(self):
        """Dibuja una ventana emergente en el centro de la pantalla."""
        width, height = self.screen.get_size()
        box_width, box_height = 400, 200
        box_rect = pygame.Rect((width - box_width) // 2, (height - box_height) // 2,
                               box_width, box_height)

        # Fondo negro semitransparente
        overlay = pygame.Surface((width, height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Ventana
        pygame.draw.rect(self.screen, (60, 0, 0), box_rect, border_radius=10)
        pygame.draw.rect(self.screen, (200, 0, 0), box_rect, 3, border_radius=10)

        # Texto mensaje
        error_font = pygame.font.SysFont("Arial", 28, bold=True)
        text_surface = error_font.render(self.error_message, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=box_rect.center)
        self.screen.blit(text_surface, text_rect)

        # Texto instrucción
        small_font = pygame.font.SysFont("Arial", 20)
        instr_surface = small_font.render("Presiona una tecla o clic para continuar", True, (220, 220, 220))
        instr_rect = instr_surface.get_rect(midbottom=(box_rect.centerx, box_rect.bottom - 15))
        self.screen.blit(instr_surface, instr_rect)

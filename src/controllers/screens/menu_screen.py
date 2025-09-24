import pygame
from controllers.screens.screen_base import ScreenBase

class MenuScreen(ScreenBase):
    def __init__(self, screen, change_screen_callback):
        super().__init__(screen)
        self.change_screen_callback = change_screen_callback

        self.options = ["Nuevo Juego", "Continuar", "Salir"]
        self.selected_index = 0

        # Fuentes y colores
        self.font = pygame.font.SysFont("Arial", 36)
        self.active_color = (255, 255, 255)    # Texto seleccionado
        self.inactive_color = (200, 200, 200)  # Texto no seleccionado
        self.disabled_color = (100, 100, 100)  # Continuar desactivado
        self.highlight_bg = (50, 50, 50)       # Fondo de hover

        # Posición inicial de las opciones
        self.start_x = 50
        self.start_y = 200
        self.line_height = 60

        # Para animación de hover
        self.current_y = self.start_y
        self.target_y = self.start_y
        self.animation_speed = 15  # pixeles por frame

    def handle_event(self, event):
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
            for i, option in enumerate(self.options):
                rect = pygame.Rect(self.start_x, self.start_y + i * self.line_height,
                                   300, self.font.get_height())
                if rect.collidepoint(mx, my):
                    self.selected_index = i
                    self.target_y = self.start_y + self.selected_index * self.line_height

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, option in enumerate(self.options):
                rect = pygame.Rect(self.start_x, self.start_y + i * self.line_height,
                                   300, self.font.get_height())
                if rect.collidepoint(mx, my):
                    self.selected_index = i
                    self.select_option()

    def select_option(self):
        option = self.options[self.selected_index]
        if option == "Nuevo Juego":
            self.change_screen_callback("game")
        elif option == "Salir":
            self.change_screen_callback("quit")
        # Continuar queda desactivada por ahora

    def update(self, dt=0):  # dt opcional por compatibilidad
        # Animación suave: mover current_y hacia target_y
        if self.current_y < self.target_y:
            self.current_y = min(self.current_y + self.animation_speed, self.target_y)
        elif self.current_y > self.target_y:
            self.current_y = max(self.current_y - self.animation_speed, self.target_y)

    def render(self):
        self.screen.fill((30, 30, 30))  # Fondo gris oscuro

        for i, option in enumerate(self.options):
            if option == "Continuar":
                color = self.disabled_color
            elif i == self.selected_index:
                color = self.active_color
            else:
                color = self.inactive_color

            text_surface = self.font.render(option, True, color)
            rect = text_surface.get_rect(topleft=(self.start_x, self.start_y + i * self.line_height))

            if i == self.selected_index and option != "Continuar":
                highlight_rect = rect.copy()
                highlight_rect.y = self.current_y
                highlight_rect.inflate_ip(20, 10)
                pygame.draw.rect(self.screen, self.highlight_bg, highlight_rect)

            self.screen.blit(text_surface, rect)

        pygame.display.flip()

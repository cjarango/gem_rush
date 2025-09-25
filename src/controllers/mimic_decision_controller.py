import pygame

class MimicDecisionController:
    def __init__(self, player, screen, font, width, height):
        self.player = player
        self.screen = screen
        self.font = font
        self.width = width
        self.height = height
        self.active = False
        self.choice = None
        self.timer = 0
        self.duration = 0
        self.chest = None

        self.btn_w, self.btn_h = 220, 60
        self.spacing = 40
        self.fight_rect = pygame.Rect(0,0,self.btn_w,self.btn_h)
        self.pay_rect = pygame.Rect(0,0,self.btn_w,self.btn_h)

    def start_decision(self, chest, duration_frames=200):
        self.active = True
        self.chest = chest
        self.choice = None
        self.timer = duration_frames
        self.duration = duration_frames
        self.fight_rect.topleft = (self.width//2 - self.btn_w - self.spacing//2, self.height//2 - self.btn_h//2)
        self.pay_rect.topleft = (self.width//2 + self.spacing//2, self.height//2 - self.btn_h//2)

    def handle_event(self, event):
        if not self.active:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l: self.choice = "fight"
            elif event.key == pygame.K_p: self.choice = "pay"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.fight_rect.collidepoint(mx, my): self.choice = "fight"
            elif self.pay_rect.collidepoint(mx, my): self.choice = "pay"

    def update(self):
        if not self.active:
            return None

        # Reducir el contador de tiempo
        self.timer -= 1

        # Si el jugador no elige y el tiempo llega a cero, decisión automática "pay"
        if self.choice is None and self.timer <= 0:
            self.choice = "pay"

        # Devolver resultado si hay elección
        if self.choice:
            result = {"choice": self.choice, "chest": self.chest}
            self.active = False
            return result

        return None

    def draw(self):
        if not self.active: return

        # Fondo semitransparente
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        self.screen.blit(overlay, (0,0))

        # Texto principal
        text = "A MIMIC APPEARED! What will you do?"
        text_surface = self.font.render(text, True, (255, 50, 50))
        x = self.width // 2 - text_surface.get_width() // 2
        y = self.height // 2 - 120
        self.screen.blit(text_surface, (x,y))

        # Botones
        pygame.draw.rect(self.screen, (220,50,50), self.fight_rect, border_radius=12)
        pygame.draw.rect(self.screen, (50,220,50), self.pay_rect, border_radius=12)

        fight_text = self.font.render("FIGHT (L)", True, (255,255,255))
        pay_text = self.font.render("PAY (P)", True, (255,255,255))
        self.screen.blit(fight_text, (self.fight_rect.centerx - fight_text.get_width()//2,
                                      self.fight_rect.centery - fight_text.get_height()//2))
        self.screen.blit(pay_text, (self.pay_rect.centerx - pay_text.get_width()//2,
                                    self.pay_rect.centery - pay_text.get_height()//2))

        # Barra de tiempo
        bar_width, bar_height = 400, 20
        bar_x = self.width // 2 - bar_width // 2
        bar_y = self.height//2 + self.btn_h
        time_ratio = max(self.timer / self.duration, 0)

        # Cambia a rojo si queda menos del 25% del tiempo
        bar_color = (255,200,0) if time_ratio > 0.25 else (255,50,50)

        pygame.draw.rect(self.screen, (100,100,100), (bar_x, bar_y, bar_width, bar_height), border_radius=10)
        pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, int(bar_width * time_ratio), bar_height), border_radius=10)

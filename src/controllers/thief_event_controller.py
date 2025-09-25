import pygame
import random
from resources.gem_data import GEM_NAMES

class ThiefEventController:
    def __init__(self, player, screen, font, width, height):
        self.player = player
        self.screen = screen
        self.font = font
        self.width = width
        self.height = height

        # Estado del evento
        self.active = False
        self.choice = None
        self.timer = 0
        self.duration = 0
        self.gem_name = None       # poder usado en el BST
        self.gem_display_name = "" # nombre para mostrar
        self.gem_qty = 0

        # Botones
        self.btn_w, self.btn_h = 220, 60
        self.spacing = 40
        self.fight_rect = pygame.Rect(0, 0, self.btn_w, self.btn_h)
        self.pay_rect = pygame.Rect(0, 0, self.btn_w, self.btn_h)

    # ====================
    # Iniciar evento
    # ====================
    def start_event(self, duration_frames=600):
        self.active = True
        self.choice = None
        self.timer = duration_frames
        self.duration = duration_frames

        # Elegir gema aleatoria de GEM_NAMES
        self.gem_name = random.choice(list(GEM_NAMES.keys()))
        self.gem_qty = random.randint(1, 3)  # Cantidad pedida aleatoria
        self.gem_display_name = GEM_NAMES[self.gem_name]

        # Posicionar botones
        self.fight_rect.topleft = (self.width//2 - self.btn_w - self.spacing//2, self.height//2 - self.btn_h//2)
        self.pay_rect.topleft = (self.width//2 + self.spacing//2, self.height//2 - self.btn_h//2)
        return True

    # ====================
    # Manejar eventos
    # ====================
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

    # ====================
    # Actualizar evento
    # ====================
    def update(self):
        if not self.active:
            return None

        self.timer -= 1

        # Si se acabó el tiempo y el jugador no ha decidido, siempre paga
        if self.choice is None and self.timer <= 0:
            self.choice = "pay"

        if self.choice:
            result = self.resolve_choice()
            self.active = False
            return result

        return None

    # ====================
    # Resolver decisión
    # ====================
    def resolve_choice(self):
        inv = self.player.inventory

        if self.choice == "pay":
            node = inv.search(self.gem_name)

            if node:
                # Caso 1: tiene la gema pedida
                removed_qty = min(self.gem_qty, node.getCantidad())
                inv.delete(node.poder, removed_qty)
                return {"choice": "pay", "gem": node.poder, "name": self.gem_display_name, "qty": removed_qty}

            else:
                # Caso 2: no tiene la gema pedida → predecesora
                pred_node = inv.predecessor(self.gem_name)
                if pred_node:
                    removed_qty = random.randint(1, pred_node.getCantidad())  # cantidad aleatoria
                    inv.delete(pred_node.poder, removed_qty)
                    return {"choice": "pay", "gem": pred_node.poder,
                            "name": GEM_NAMES.get(pred_node.poder, str(pred_node.poder)), "qty": removed_qty}
                else:
                    # Usar la gema mínima
                    min_node = inv.min_value()
                    if min_node:
                        removed_qty = random.randint(1, min_node.getCantidad())  # cantidad aleatoria
                        inv.delete(min_node.poder, removed_qty)
                        return {"choice": "pay", "gem": min_node.poder,
                                "name": GEM_NAMES.get(min_node.poder, str(min_node.poder)), "qty": removed_qty}
                    else:
                        # Inventario vacío → se considera pelea
                        self.choice = "fight"

        if self.choice == "fight":
            if random.random() < 0.5:  # 50% chance de morir
                self.player.alive = False
                return {"choice": "fight", "result": "killed"}
            return {"choice": "fight", "result": "won"}

    # ====================
    # Dibujar evento
    # ====================
    def draw(self):
        if not self.active:
            return

        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        self.screen.blit(overlay, (0,0))

        text = f"A thief appears! He asks for {self.gem_qty} of {self.gem_display_name}."
        text_surface = self.font.render(text, True, (255, 50, 50))
        x = self.width // 2 - text_surface.get_width() // 2
        y = self.height // 2 - 120
        self.screen.blit(text_surface, (x, y))

        # Botones
        pygame.draw.rect(self.screen, (220,50,50), self.fight_rect, border_radius=12)
        pygame.draw.rect(self.screen, (50,220,50), self.pay_rect, border_radius=12)

        fight_text = self.font.render("FIGHT (L)", True, (255,255,255))
        pay_text = self.font.render("PAY (P)", True, (255,255,255))
        self.screen.blit(fight_text, (self.fight_rect.centerx - fight_text.get_width()//2, self.fight_rect.centery - fight_text.get_height()//2))
        self.screen.blit(pay_text, (self.pay_rect.centerx - pay_text.get_width()//2, self.pay_rect.centery - pay_text.get_height()//2))

        # Barra de tiempo
        bar_width, bar_height = 400, 20
        bar_x = self.width // 2 - bar_width // 2
        bar_y = self.height//2 + self.btn_h
        time_ratio = max(self.timer / self.duration, 0)
        pygame.draw.rect(self.screen, (100,100,100), (bar_x, bar_y, bar_width, bar_height), border_radius=10)
        pygame.draw.rect(self.screen, (255,200,0), (bar_x, bar_y, int(bar_width * time_ratio), bar_height), border_radius=10)

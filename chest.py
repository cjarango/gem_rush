import random
import pygame
from gem_data import GEM_NAMES

class Chest:
    def __init__(self, small_gem_threshold=10, mimic_prob=0.4):
        self.mimic_prob = mimic_prob
        self.small_gem_threshold = small_gem_threshold
        self.opened = False

        gem_options = list(GEM_NAMES.keys())
        self.poder = random.choice(gem_options)
        self.is_mimic = random.random() < mimic_prob

        # Siempre definir cost y cantidad según poder
        if self.poder < self.small_gem_threshold:
            self.cost = random.randint(5, 10)
            self.cantidad = random.randint(10, 20)
            self.sprite_closed = pygame.image.load("textures/Chests1closed.png").convert_alpha()
            self.sprite_open = pygame.image.load("textures/Chests1open.png").convert_alpha()
        else:
            self.cost = random.randint(2, 5)
            self.cantidad = random.randint(1, 5)
            self.sprite_closed = pygame.image.load("textures/Chests2closed.png").convert_alpha()
            self.sprite_open = pygame.image.load("textures/Chests2open.png").convert_alpha()

        # Escalar los sprites al tamaño correcto (ej: 32x32 píxeles)
        self.sprite_closed = pygame.transform.scale(self.sprite_closed, (32, 32))
        self.sprite_open = pygame.transform.scale(self.sprite_open, (32, 32))

        if self.is_mimic:
            self.mimic_demand = random.randint(1, 5)

    def interact(self, player):
        if self.opened:
            return {"usado": None, "obtenido": "Chest already opened"}

        gem_name = GEM_NAMES.get(self.poder, f"Gem {self.poder}")
        nodo = player.inventory.search(self.poder)
        cantidad_actual = nodo.getCantidad() if nodo else 0

        if cantidad_actual < self.cost:
            return {"usado": None, "obtenido": f"You don't have enough {gem_name} to open the chest"}

        # Pagar coste
        player.inventory.delete(self.poder, self.cost)
        usado_msg = f"You used {gem_name} × {self.cost}"

        if self.is_mimic:
            return {
                "decision": True,
                "usado": usado_msg,
                "poder": self.poder,
                "mimic_demand": self.mimic_demand,
                "cantidad": getattr(self, "cantidad", 1)
            }

        # Cofre normal
        player.collect_gem(self.poder, self.cantidad)
        self.opened = True
        return {
            "usado": usado_msg,
            "obtenido": f"You obtained {self.cantidad} {gem_name}"
        }

    def info(self):
        gem_name = GEM_NAMES.get(self.poder, f"Gem {self.poder}")
        return f"Use {gem_name} × {getattr(self, 'cost', 0)} to open the chest"

    def get_sprite(self):
        return self.sprite_open if self.opened else self.sprite_closed

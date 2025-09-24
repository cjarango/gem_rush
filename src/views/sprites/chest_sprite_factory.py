# src/views/sprites/chest_sprite_factory.py
import os
import pygame
from core.interfaces import IChest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
TEXTURE_DIR = os.path.join(BASE_DIR, "textures")

def load_texture(name, size=(32, 32)):
    path = os.path.join(TEXTURE_DIR, name)
    surf = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(surf, size)

class ChestSpriteFactory:
    """Renderiza cofres según su estado (abierto/cerrado) y tamaño (small/large)."""

    def __init__(self, tile_size=32):
        self.tile_size = tile_size
        self.sprites = {
            "small_closed": load_texture("Chests1closed.png", (tile_size, tile_size)),
            "small_open": load_texture("Chests1open.png", (tile_size, tile_size)),
            "large_closed": load_texture("Chests2closed.png", (tile_size, tile_size)),
            "large_open": load_texture("Chests2open.png", (tile_size, tile_size)),
        }

    def get_sprite(self, chest: IChest):
        # Usamos el atributo interno _is_large para decidir tamaño
        is_large = getattr(chest, "_is_large", False)
        if is_large:
            return self.sprites["large_open"] if chest.is_opened() else self.sprites["large_closed"]
        else:
            return self.sprites["small_open"] if chest.is_opened() else self.sprites["small_closed"]

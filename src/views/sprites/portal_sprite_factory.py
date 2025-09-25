import os
import pygame
from core.portal import Portal

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
TEXTURE_DIR = os.path.join(BASE_DIR, "textures")

def load_texture(name, size=(32,32)):
    path = os.path.join(TEXTURE_DIR, name)
    surf = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(surf, size)

class PortalSpriteFactory:
    """Renderiza el sprite del portal."""

    def __init__(self, tile_size=32):
        self.tile_size = tile_size
        self.sprite = load_texture("portal.png", (tile_size, tile_size))

    def get_sprite(self, portal: Portal):
        return self.sprite

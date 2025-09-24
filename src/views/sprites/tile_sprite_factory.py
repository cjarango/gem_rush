import os
import pygame

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
TEXTURE_DIR = os.path.join(BASE_DIR, "textures")

def load_texture(name, tile_size):
    path = os.path.join(TEXTURE_DIR, name)
    surf = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(surf, (tile_size, tile_size))

class TileSpriteFactory:
    def __init__(self, tile_size=32, num_tree_variants=4):
        self.tile_size = tile_size
        self.num_tree_variants = num_tree_variants
        self.sprites = {
            "GRASS": self._load_grass(),
            "CLEAR": self._load_clear(),
            "TREE": self._load_trees()
        }

    def _load_grass(self):
        surf = load_texture("grass.png", self.tile_size)
        surf.fill((200, 200, 255, 180), special_flags=pygame.BLEND_RGBA_MULT)
        return surf

    def _load_clear(self):
        surf = load_texture("grass.png", self.tile_size)
        surf.fill((100, 100, 100, 200), special_flags=pygame.BLEND_RGBA_MULT)
        return surf

    def _load_trees(self):
        trees = []
        for i in range(self.num_tree_variants):
            img = load_texture(f"trees{i}.png", self.tile_size)
            trees.append(img)
        return trees

    def get_sprite(self, tile_type, variant=0):
        if tile_type == "TREE":
            return self.sprites["TREE"][variant]
        return self.sprites.get(tile_type, self._load_grass())

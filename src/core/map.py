import random
from collections import defaultdict
from views.sprites import TileSpriteFactory, ChestSpriteFactory, PortalSpriteFactory
from core.managers.gem_manager import GemManager
from core.managers.chest_manager import ChestManager
from core.managers.portal_manager import PortalManager
from generators import ChunkGenerator

class Map:
    def __init__(self, chunk_size, path_width_range=(1, 2), num_tree_variants=4, tile_size=32):
        self.chunk_size = chunk_size if chunk_size % 2 == 1 else chunk_size + 1
        self.chunks = defaultdict(lambda: defaultdict(lambda: None))
        self.generated_chunks = set()
        self.clear_chunks = set()
        self.clearing_probability = 0.2
        self.path_width_range = path_width_range
        self.num_tree_variants = num_tree_variants
        self.tile_size = tile_size
        self.tree_variant_map = {}

        # ====================
        # Factories de Sprites
        # ====================
        self.tile_sprite_factory = TileSpriteFactory(tile_size, num_tree_variants)
        self.chest_sprite_factory = ChestSpriteFactory(tile_size)
        self.portal_sprite_factory = PortalSpriteFactory(tile_size)

        # ====================
        # Managers
        # ====================
        self.gem_manager = GemManager(self.chunk_size)
        self.chest_manager = ChestManager(self.chunk_size)
        self.portal_manager = PortalManager(self.chunk_size)

        # ====================
        # Generador de Chunks
        # ====================
        self.chunk_generator = ChunkGenerator(chunk_size, path_width_range)

    # ====================
    # Constructores de celdas
    # ====================
    def make_tree(self):
        return ("TREE", random.randint(0, self.num_tree_variants - 1))

    def make_grass(self):
        return ("GRASS",)

    def make_clear(self):
        return ("CLEAR",)

    # ====================
    # Acceso a tiles y sprites
    # ====================
    def get_tile(self, x, y):
        chunk_x, chunk_y = self.get_chunk_key(x, y)
        self.ensure_chunk(chunk_x, chunk_y)
        local_x, local_y = x % self.chunk_size, y % self.chunk_size
        tile = self.chunks[chunk_y][chunk_x][local_y][local_x]
        return tile if tile else ("TREE", 0)

    def get_sprite(self, x, y):
        # Cofres
        chest = self.get_chest(x, y)
        if chest:
            return self.chest_sprite_factory.get_sprite(chest)

        # Portal
        portal, _ = self.get_portal(x, y)
        if portal:
            # Obtenemos el sprite desde el factory
            return self.portal_sprite_factory.get_sprite(portal)

        # Tile normal
        tile = self.get_tile(x, y)
        if tile[0] == "TREE":
            variant = self.get_tree_variant(x, y)
            return self.tile_sprite_factory.get_sprite("TREE", variant)
        elif tile[0] == "CLEAR":
            return self.tile_sprite_factory.get_sprite("CLEAR")
        return self.tile_sprite_factory.get_sprite("GRASS")

    # ====================
    # Gemas y cofres
    # ====================
    def get_gem(self, x, y):
        chunk_x, chunk_y = self.get_chunk_key(x, y)
        local_x, local_y = x % self.chunk_size, y % self.chunk_size
        return self.gem_manager.get_gem(chunk_x, chunk_y, local_x, local_y)

    def collect_gem(self, x, y):
        chunk_x, chunk_y = self.get_chunk_key(x, y)
        local_x, local_y = x % self.chunk_size, y % self.chunk_size
        return self.gem_manager.collect_gem(chunk_x, chunk_y, local_x, local_y)

    def get_chest(self, x, y):
        chunk_x, chunk_y = self.get_chunk_key(x, y)
        local_x, local_y = x % self.chunk_size, y % self.chunk_size
        return self.chest_manager.get_chest(chunk_x, chunk_y, local_x, local_y)

    def interact_with_chest(self, player):
        chest = self.get_chest(player.x, player.y)
        if chest:
            return chest.interact(player)
        return None

    # ====================
    # Portales
    # ====================
    def get_portal(self, x, y):
        chunk_x, chunk_y = self.get_chunk_key(x, y)
        portal_info = self.portal_manager.get_portal_info(chunk_x, chunk_y)
        if portal_info:
            lx, ly, portal = portal_info
            if (x % self.chunk_size, y % self.chunk_size) == (lx, ly):
                global_x, global_y = chunk_x*self.chunk_size + lx, chunk_y*self.chunk_size + ly
                return portal, (global_x, global_y)
        return None, None

    # ====================
    # Métodos auxiliares y chunks
    # ====================
    def get_chunk_key(self, x, y):
        return (x // self.chunk_size, y // self.chunk_size)

    def ensure_chunk(self, chunk_x, chunk_y):
        key = (chunk_x, chunk_y)
        if key not in self.generated_chunks:
            # Generamos chunk
            chunk = self.chunk_generator.generate_chunk()
            self.chunks[chunk_y][chunk_x] = chunk
            self.generated_chunks.add(key)

            # Colocamos gemas, cofres y portales
            self.gem_manager.place_gems_in_chunk(chunk_x, chunk_y, chunk)
            self.chest_manager.place_chests_in_chunk(chunk_x, chunk_y, chunk)
            self.portal_manager.try_spawn_portal(chunk_x, chunk_y, chunk)

    def is_clearing_chunk(self, chunk):
        return all(tile[0] == "CLEAR" for row in chunk for tile in row)

    # ====================
    # Métodos de consulta
    # ====================
    def is_wall(self, x, y):
        return self.get_tile(x, y)[0] == "TREE"

    def is_clearing(self, x, y):
        chunk_x, chunk_y = self.get_chunk_key(x, y)
        return (chunk_x, chunk_y) in self.clear_chunks

    def get_tree_variant(self, x, y):
        key = (x, y)
        if key not in self.tree_variant_map:
            self.tree_variant_map[key] = random.randint(0, self.num_tree_variants - 1)
        return self.tree_variant_map[key]

    def is_blocked(self, x, y):
        return self.is_wall(x, y) or self.get_chest(x, y) is not None or self.get_portal(x, y)[0] is not None

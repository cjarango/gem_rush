import random
import pygame
from chest import Chest
from collections import defaultdict

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
        # Cargar sprites
        # ====================
        self.sprites = {}
        # Grass
        grass_surface = pygame.image.load("textures/grass.png").convert_alpha()
        grass_surface = pygame.transform.scale(grass_surface, (tile_size, tile_size))
        grass_surface = grass_surface.copy()
        grass_surface.fill((200, 200, 255, 180), special_flags=pygame.BLEND_RGBA_MULT)
        self.sprites["GRASS"] = grass_surface
        # Clear
        clear_surface = pygame.image.load("textures/grass.png").convert_alpha()
        clear_surface = pygame.transform.scale(clear_surface, (tile_size, tile_size))
        clear_surface = clear_surface.copy()
        clear_surface.fill((100, 100, 100, 200), special_flags=pygame.BLEND_RGBA_MULT)
        self.sprites["CLEAR"] = clear_surface
        # Trees
        self.sprites["TREE"] = []
        for i in range(num_tree_variants):
            img = pygame.image.load(f"textures/trees{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (tile_size, tile_size))
            self.sprites["TREE"].append(img)

        # ====================
        # GEMS
        # ====================
        self.gems = defaultdict(lambda: defaultdict(lambda: None))
        self.gem_values = [5, 10, 15, 20, 30]
        self.gem_colors = {
            5: (0, 255, 255),
            10: (0, 255, 0),
            15: (255, 255, 0),
            20: (255, 165, 0),
            30: (255, 0, 0)
        }
        self.gem_probability = 0.005

        # ====================
        # CHESTS
        # ====================
        self.chests = defaultdict(lambda: defaultdict(lambda: None))
        self.chest_probability = 0.0005  # probabilidad de aparecer en un clearing

    # ======================
    # Constructores de celdas
    # ======================
    def make_tree(self):
        return ("TREE", random.randint(0, self.num_tree_variants - 1))

    def make_grass(self):
        return ("GRASS",)

    def make_clear(self):
        return ("CLEAR",)

    # ======================
    # MÉTODOS DE GEMAS
    # ======================
    def place_gems_in_chunk(self, chunk_x, chunk_y):
        if self.gems[chunk_y][chunk_x] is not None:
            return
        chunk = self.chunks[chunk_y][chunk_x]
        self.gems[chunk_y][chunk_x] = [[None for _ in range(self.chunk_size)] for _ in range(self.chunk_size)]
        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                if chunk[y][x][0] == "GRASS" and random.random() < self.gem_probability:
                    self.gems[chunk_y][chunk_x][y][x] = random.choice(self.gem_values)

    def get_gem(self, x, y):
        chunk_x, chunk_y = self.get_chunk_key(x, y)
        local_x, local_y = x % self.chunk_size, y % self.chunk_size
        if chunk_y in self.gems and chunk_x in self.gems[chunk_y]:
            return self.gems[chunk_y][chunk_x][local_y][local_x]
        return None

    def collect_gem(self, x, y):
        chunk_x, chunk_y = self.get_chunk_key(x, y)
        local_x, local_y = x % self.chunk_size, y % self.chunk_size
        gem = self.get_gem(x, y)
        if gem is not None:
            self.gems[chunk_y][chunk_x][local_y][local_x] = None
        return gem

    def get_gem_color(self, value):
        return self.gem_colors.get(value, (255, 255, 255))

    # ======================
    # MÉTODOS DE CHESTS
    # ======================
    def place_chests_in_chunk(self, chunk_x, chunk_y):
        if (chunk_x, chunk_y) not in self.clear_chunks:
            return
        chunk = self.chunks[chunk_y][chunk_x]
        self.chests[chunk_y][chunk_x] = [[None for _ in range(self.chunk_size)] for _ in range(self.chunk_size)]

        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                if chunk[y][x][0] == "CLEAR":
                    if self.is_area_free(chunk, x, y, 1) and random.random() < self.chest_probability:
                        self.chests[chunk_y][chunk_x][y][x] = Chest()
                        # ✅ ahora el cofre ocupa la celda, pero NO reemplaza el tile
                        # el bloqueo lo manejamos en is_blocked()

    def is_area_free(self, chunk, x, y, radius=1):
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < self.chunk_size and 0 <= ny < self.chunk_size):
                    return False
                if chunk[ny][nx][0] != "CLEAR":
                    return False
        return True

    def get_chest(self, x, y):
        chunk_x, chunk_y = self.get_chunk_key(x, y)
        local_x, local_y = x % self.chunk_size, y % self.chunk_size
        chest_chunk = self.chests.get(chunk_y, {}).get(chunk_x)
        if chest_chunk:
            return chest_chunk[local_y][local_x]
        return None

    # ======================
    # Interacción con cofres
    # ======================
    def interact_with_chest(self, player):
        chest = self.get_chest(player.x, player.y)
        if chest:
            return chest.interact(player)
        return None

    # ======================
    # Acceso a celdas y sprites
    # ======================
    def get_tile(self, x, y):
        chunk_x, chunk_y = self.get_chunk_key(x, y)
        self.ensure_chunk(chunk_x, chunk_y)
        local_x, local_y = x % self.chunk_size, y % self.chunk_size
        tile = self.chunks[chunk_y][chunk_x][local_y][local_x]
        return tile if tile else ("TREE", 0)

    def get_sprite(self, x, y):
        chest = self.get_chest(x, y)
        if chest:
            return chest.get_sprite()

        tile = self.get_tile(x, y)
        if tile[0] == "TREE":
            variant = self.get_tree_variant(x, y)
            return self.sprites["TREE"][variant]
        elif tile[0] == "CLEAR":
            return self.sprites["CLEAR"]
        return self.sprites["GRASS"]

    # ======================
    # Métodos auxiliares
    # ======================
    def get_chunk_key(self, x, y):
        return (x // self.chunk_size, y // self.chunk_size)

    def ensure_chunk(self, chunk_x, chunk_y):
        key = (chunk_x, chunk_y)
        if key not in self.generated_chunks:
            self.generate_chunk(chunk_x, chunk_y)
            self.generated_chunks.add(key)
            self.place_gems_in_chunk(chunk_x, chunk_y)
            self.place_chests_in_chunk(chunk_x, chunk_y)

    # ======================
    # Generación de chunks
    # ======================
    def generate_chunk(self, chunk_x, chunk_y):
        is_clearing = random.random() < self.clearing_probability
        if is_clearing:
            self.clear_chunks.add((chunk_x, chunk_y))
            chunk = self.generate_clearing()
        else:
            chunk = self.generate_maze_chunk(chunk_x, chunk_y)
        self.chunks[chunk_y][chunk_x] = chunk

    def generate_maze_chunk(self, chunk_x, chunk_y):
        chunk = [[self.make_tree() for _ in range(self.chunk_size)] for _ in range(self.chunk_size)]
        if chunk_x == 0 and chunk_y == 0:
            start_x, start_y = self.chunk_size // 2, self.chunk_size // 2
        else:
            start_x, start_y = self.get_start_position_for_chunk(chunk_x, chunk_y)

        chunk[start_y][start_x] = self.make_grass()
        self.carve_center(chunk, start_x, start_y,
                          max(1, random.randint(self.path_width_range[0], self.path_width_range[1]) // 2))

        stack = [(start_x, start_y)]
        directions = [(2, 0), (0, 2), (-2, 0), (0, -2)]
        path_cells, target_path_cells = 1, (self.chunk_size * self.chunk_size) // 2

        while stack and path_cells < target_path_cells:
            current_x, current_y = stack[-1]
            random.shuffle(directions)
            found = False
            for dx, dy in directions:
                nx, ny = current_x + dx, current_y + dy
                if 0 <= nx < self.chunk_size and 0 <= ny < self.chunk_size and chunk[ny][nx][0] == "TREE":
                    width = random.randint(self.path_width_range[0], self.path_width_range[1])
                    self.carve_between(chunk, current_x, current_y, nx, ny, width)
                    path_cells += 2
                    stack.append((nx, ny))
                    found = True
                    break
            if not found:
                stack.pop()

        self.add_extra_paths(chunk, path_cells, target_path_cells)
        self.connect_to_adjacent_chunks(chunk, chunk_x, chunk_y)
        return chunk

    # ======================
    # Métodos de carving
    # ======================
    def carve_center(self, chunk, x, y, width=1):
        half = width // 2
        for dy in range(-half, half + 1):
            for dx in range(-half, half + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.chunk_size and 0 <= ny < self.chunk_size:
                    chunk[ny][nx] = self.make_grass()

    def carve_between(self, chunk, x1, y1, x2, y2, width=1):
        dx, dy = x2 - x1, y2 - y1
        half = width // 2
        wx, wy = x1 + dx // 2, y1 + dy // 2
        if dx != 0:
            for off in range(-half, half + 1):
                yy = y1 + off
                for xx in (x1, wx, x2):
                    if 0 <= xx < self.chunk_size and 0 <= yy < self.chunk_size:
                        chunk[yy][xx] = self.make_grass()
        else:
            for off in range(-half, half + 1):
                xx = x1 + off
                for yy in (y1, wy, y2):
                    if 0 <= xx < self.chunk_size and 0 <= yy < self.chunk_size:
                        chunk[yy][xx] = self.make_grass()

    def add_extra_paths(self, chunk, current_path_cells, target_path_cells):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        attempts = 0
        while current_path_cells < target_path_cells and attempts < 200:
            x = random.randint(1, self.chunk_size - 2)
            y = random.randint(1, self.chunk_size - 2)
            if chunk[y][x][0] == "TREE":
                adjacent_paths = sum(
                    1 for dx, dy in directions
                    if 0 <= x + dx < self.chunk_size and 0 <= y + dy < self.chunk_size and chunk[y + dy][x + dx][0] == "GRASS"
                )
                if adjacent_paths >= 2:
                    self.carve_center(chunk, x, y, 1)
                    current_path_cells += 1
            attempts += 1

    def generate_clearing(self):
        chunk = [[self.make_clear() for _ in range(self.chunk_size)] for _ in range(self.chunk_size)]
        for _ in range(random.randint(0, max(0, self.chunk_size // 8))):
            x, y = random.randint(2, self.chunk_size - 3), random.randint(2, self.chunk_size - 3)
            chunk[y][x] = self.make_tree()
        return chunk

    def get_start_position_for_chunk(self, chunk_x, chunk_y):
        if chunk_x > 0 and (chunk_x - 1, chunk_y) in self.generated_chunks:
            return 1, self.chunk_size // 2
        elif chunk_x < 0 and (chunk_x + 1, chunk_y) in self.generated_chunks:
            return self.chunk_size - 2, self.chunk_size // 2
        elif chunk_y > 0 and (chunk_x, chunk_y - 1) in self.generated_chunks:
            return self.chunk_size // 2, 1
        elif chunk_y < 0 and (chunk_x, chunk_y + 1) in self.generated_chunks:
            return self.chunk_size // 2, self.chunk_size - 2
        return self.chunk_size // 2, self.chunk_size // 2

    def connect_to_adjacent_chunks(self, chunk, chunk_x, chunk_y):
        center = self.chunk_size // 2
        if (chunk_x - 1, chunk_y) in self.generated_chunks:
            left_chunk = self.chunks[chunk_y][chunk_x - 1]
            if left_chunk and left_chunk[center][self.chunk_size - 2][0] == "GRASS":
                w = random.randint(self.path_width_range[0], self.path_width_range[1])
                half = w // 2
                for off in range(-half, half + 1):
                    yy = center + off
                    if 0 <= yy < self.chunk_size:
                        chunk[yy][0] = self.make_grass()
                        chunk[yy][1] = self.make_grass()

    def is_wall(self, x, y):
        tile = self.get_tile(x, y)
        return tile[0] == "TREE"

    def is_clearing(self, x, y):
        chunk_x, chunk_y = self.get_chunk_key(x, y)
        return (chunk_x, chunk_y) in self.clear_chunks

    def get_tree_variant(self, x, y):
        key = (x, y)
        if key not in self.tree_variant_map:
            self.tree_variant_map[key] = random.randint(0, self.num_tree_variants - 1)
        return self.tree_variant_map[key]

    # ======================
    # 🚫 BLOQUEO DE MUROS Y COFRES
    # ======================
    def is_blocked(self, x, y):
        """True si el tile está bloqueado por un árbol o un cofre."""
        if self.is_wall(x, y):
            return True
        if self.get_chest(x, y) is not None:
            return True
        return False

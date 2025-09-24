import random
from collections import defaultdict

class GemManager:
    def __init__(self, chunk_size, gem_values=None, gem_probability=0.005):
        self.chunk_size = chunk_size
        self.gems = defaultdict(lambda: defaultdict(lambda: None))
        self.gem_values = gem_values or [5, 10, 15, 20, 30]
        self.gem_colors = {
            5: (0, 255, 255),
            10: (0, 255, 0),
            15: (255, 255, 0),
            20: (255, 165, 0),
            30: (255, 0, 0)
        }
        self.gem_probability = gem_probability

    def place_gems_in_chunk(self, chunk_x, chunk_y, chunk):
        if self.gems[chunk_y][chunk_x] is not None:
            return
        self.gems[chunk_y][chunk_x] = [[None for _ in range(self.chunk_size)] for _ in range(self.chunk_size)]
        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                if chunk[y][x][0] == "GRASS" and random.random() < self.gem_probability:
                    self.gems[chunk_y][chunk_x][y][x] = random.choice(self.gem_values)

    def get_gem(self, chunk_x, chunk_y, local_x, local_y):
        return self.gems.get(chunk_y, {}).get(chunk_x, [[None]*self.chunk_size]*self.chunk_size)[local_y][local_x]

    def collect_gem(self, chunk_x, chunk_y, local_x, local_y):
        gem = self.get_gem(chunk_x, chunk_y, local_x, local_y)
        if gem is not None:
            self.gems[chunk_y][chunk_x][local_y][local_x] = None
        return gem

    def get_gem_color(self, value):
        return self.gem_colors.get(value, (255, 255, 255))

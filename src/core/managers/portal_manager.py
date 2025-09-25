import random
from collections import defaultdict
from typing import List, Optional, Tuple
from core.portal import Portal

class PortalManager:
    def __init__(self, chunk_size: int, portal_probability: float = 1.0):
        self.chunk_size = chunk_size
        self.portal_probability = portal_probability
        self.portals: defaultdict[int, defaultdict[int, Optional[Tuple[int,int,Portal]]]] = \
            defaultdict(lambda: defaultdict(lambda: None))

    def place_portal_in_chunk(self, chunk_x: int, chunk_y: int, chunk: List[List[Tuple]]):
        if self.portals[chunk_y][chunk_x] is not None:
            return
        if random.random() < self.portal_probability:
            clear_positions = [
                (x, y) for y in range(self.chunk_size) for x in range(self.chunk_size)
                if chunk[y][x][0] == "CLEAR"
            ]
            if clear_positions:
                x, y = random.choice(clear_positions)
                self.portals[chunk_y][chunk_x] = (x, y, Portal())

    def try_spawn_portal(self, chunk_x: int, chunk_y: int, chunk: List[List[Tuple]]):
        self.place_portal_in_chunk(chunk_x, chunk_y, chunk)

    def get_portal(self, chunk_x: int, chunk_y: int) -> Optional[Portal]:
        p = self.portals.get(chunk_y, {}).get(chunk_x)
        return p[2] if p else None

    def get_portal_info(self, chunk_x: int, chunk_y: int) -> Optional[Tuple[int,int,Portal]]:
        return self.portals.get(chunk_y, {}).get(chunk_x)

    def get_portal_position(self, chunk_x: int, chunk_y: int) -> Optional[Tuple[int,int]]:
        p = self.portals.get(chunk_y, {}).get(chunk_x)
        return (p[0], p[1]) if p else None
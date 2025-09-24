from core import Player
from core.interfaces import IMap
from core.interfaces.i_chest import IChest

class PlayerMovementController:
    def __init__(self, player: Player, game_map: IMap, speed=5.0):
        self.player = player
        self.game_map = game_map
        self.speed = speed  # tiles por segundo

        # Posición interna con float para movimiento suave
        self.pos_x = float(player.x)
        self.pos_y = float(player.y)

    def move(self, dx: int, dy: int, dt: float):
        if not self.player.get_state():
            return  # no se mueve si está "muerto"

        # Movimiento proporcional a dt
        self.pos_x += dx * self.speed * dt
        self.pos_y += dy * self.speed * dt

        new_x, new_y = int(round(self.pos_x)), int(round(self.pos_y))

        # Bloqueado por muro
        if self.game_map.is_wall(new_x, new_y):
            self.pos_x, self.pos_y = self.player.x, self.player.y
            return

        # Bloqueado por cofre cerrado
        chest: IChest | None = self.game_map.get_chest(new_x, new_y)
        if chest and not chest.is_opened():
            self.pos_x, self.pos_y = self.player.x, self.player.y
            return

        # actualizar posición del jugador
        self.player.x, self.player.y = new_x, new_y

        # pre-generar chunks vecinos
        chunk_x, chunk_y = self.game_map.get_chunk_key(new_x, new_y)
        for dx_chunk in [-1, 0, 1]:
            for dy_chunk in [-1, 0, 1]:
                self.game_map.ensure_chunk(chunk_x + dx_chunk, chunk_y + dy_chunk)

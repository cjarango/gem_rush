class HUDController:
    def __init__(self, screen, font, width, height, color_text, max_messages=5):
        self.screen = screen
        self.font = font
        self.width = width
        self.height = height
        self.color_text = color_text
        self.floating_messages = []
        self.max_messages = max_messages

    def add_message(self, text, duration_seconds=3.0):
        """Agrega un mensaje flotante con duración en segundos"""
        self.floating_messages.append({"text": text, "timer": duration_seconds})
        # Limitar a los últimos max_messages mensajes
        if len(self.floating_messages) > self.max_messages:
            self.floating_messages = self.floating_messages[-self.max_messages:]

    def update(self, dt: float):
        """Actualiza timers de los mensajes y elimina los expirados"""
        for msg in self.floating_messages:
            msg["timer"] -= dt
        self.floating_messages = [m for m in self.floating_messages if m["timer"] > 0]

    def draw_floating_messages(self):
        y_offset = 50
        for msg in self.floating_messages:
            text_surface = self.font.render(msg["text"], True, self.color_text)
            text_x = self.width // 2 - text_surface.get_width() // 2
            self.screen.blit(text_surface, (text_x, y_offset))
            y_offset += 25

    def draw_chest_cost(self, current_cost_text):
        if current_cost_text:
            text_surface = self.font.render(f"Chest cost: {current_cost_text}", True, self.color_text)
            text_x = self.width // 2 - text_surface.get_width() // 2
            self.screen.blit(text_surface, (text_x, 30))

    def draw_inventory(self, inventory, inventory_open, inventory_formatter):
        if inventory_open:
            summary = inventory_formatter.summary(inventory)
            for i, line in enumerate(summary.split("\n")):
                self.screen.blit(self.font.render(line, True, self.color_text), (self.width-300, 50 + i*20))

    def clear_messages(self):
        self.floating_messages.clear()

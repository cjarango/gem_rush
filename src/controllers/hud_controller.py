class HUDController:
    def __init__(self, screen, font, width, height, color_text):
        self.screen = screen
        self.font = font
        self.width = width
        self.height = height
        self.color_text = color_text
        self.floating_messages = []

    def add_message(self, text, timer=180):
        self.floating_messages.append({"text": text, "timer": timer})

    def draw_floating_messages(self):
        y_offset = 50
        for msg in self.floating_messages[:]:
            text_surface = self.font.render(msg["text"], True, self.color_text)
            text_x = self.width // 2 - text_surface.get_width() // 2
            self.screen.blit(text_surface, (text_x, y_offset))
            y_offset += 25
            msg["timer"] -= 1
            if msg["timer"] <= 0:
                self.floating_messages.remove(msg)

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
        """Limpia todos los mensajes flotantes"""
        self.floating_messages.clear()
from abc import ABC, abstractmethod

class ScreenBase(ABC):
    def __init__(self, screen):
        self.screen = screen

    @abstractmethod
    def handle_event(self, event):
        pass

    @abstractmethod
    def update(self, dt=0):  # dt opcional por compatibilidad
        pass

    @abstractmethod
    def render(self):
        pass

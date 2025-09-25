

import pygame
import os

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.music_volume = 0.7  
        
    def load_and_play_music(self, music_path):
        """Carga y reproduce música de fondo en loop"""
        try:
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)  # -1 = loop infinito
                print(f"Música ambiental iniciada: {music_path}")
            else:
                print(f"Archivo de música no encontrado: {music_path}")
                print("Verifica que el archivo esté en la carpeta 'audio/'")
        except pygame.error as e:
            print(f"Error con la música: {e}")
            print("Verifica que el archivo MP3 sea válido")
    
    def pause_music(self):
        """Pausa la música"""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Resume la música"""
        pygame.mixer.music.unpause()
    
    def set_volume(self, volume):
        """Cambia volumen (0.0 a 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def stop_music(self):
        """Detiene la música"""
        pygame.mixer.music.stop()
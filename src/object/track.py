import os
import pygame as pg

# Naik 2 level dari src/object/ ke root project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

TRACK_DIR = os.path.join(ASSETS_DIR, "tracks")

class Track:
    def __init__(self, name: str, screen_width: int = 1920, screen_height: int = 1440):
        """
        Inisialisasi track dengan nama dan resolusi layar
        Args:
            name: nama file track (tanpa ekstensi)
            screen_width: lebar layar (default 1920)
            screen_height: tinggi layar (default 1440)
        """
        self.name = name
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.image_path = os.path.join(TRACK_DIR, f"{name}.png")
        
        # Load gambar trek
        if os.path.exists(self.image_path):
            original_image = pg.image.load(self.image_path)
            self.image = pg.transform.scale(original_image, (self.screen_width, self.screen_height))
        else:
            raise FileNotFoundError(f"Track image not found: {self.image_path}")
        
        self.width = self.screen_width
        self.height = self.screen_height
    
    def draw(self, screen, camera, x=0, y=0):
        screen.blit(self.image, (x - camera.x, y - camera.y))
    
    def get_size(self):
        return (self.width, self.height)
    
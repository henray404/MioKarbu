import pygame
from .base import ScreenBase
import os
import sys

class MainMenuScreen(ScreenBase):
    def __init__(self, manager, screen_size, asset_root):
        super().__init__(manager, screen_size)
        
        self.asset_root = asset_root
        self.result = None

        bg_path = os.path.join(self.asset_root, "lobby.png")
        self.bg = pygame.image.load(bg_path).convert()
        self.bg = pygame.transform.scale(self.bg, screen_size)
        
        self.btn_play = self._load_img("btn_play.png")
        self.btn_settings = self._load_img("btn_settings.png")
        self.btn_quit = self._load_img("btn_quit.png")

        self.btn_play.set_alpha(0)
        self.btn_settings.set_alpha(0)
        self.btn_quit.set_alpha(0)

        center_x = self.screen_width - 150
        self.rect_play = self.btn_play.get_rect(center=(center_x, self.screen_height- 380))
        self.rect_settings = self.btn_settings.get_rect(center=(center_x, self.screen_height - 290))
        self.rect_quit = self.btn_quit.get_rect(center=(center_x, self.screen_height - 200))

    def _load_img(self, filename):
        path = os.path.join(self.asset_root, filename)
        if os.path.exists(path):
            return pygame.image.load(path).convert_alpha()
        return pygame.Surface((190, 60)) # Fallback merah jika gambar tidak ada

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = event.pos
                if self.rect_play.collidepoint(pos):
                    self.result = "PLAY"
                elif self.rect_settings.collidepoint(pos):
                    print("Settings clicked")
                elif self.rect_quit.collidepoint(pos):
                    self.result = "EXIT"

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.blit(self.bg, (0, 0))
        surface.blit(self.btn_play, self.rect_play)
        surface.blit(self.btn_settings, self.rect_settings)
        surface.blit(self.btn_quit, self.rect_quit)
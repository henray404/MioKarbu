import pygame
import os
from .base import ScreenBase
from ui.components import HoverButton, SettingsPopup 

class MainMenuScreen(ScreenBase):
    def __init__(self, manager, screen_size, asset_root):
        super().__init__(manager, screen_size)
        self.asset_root = asset_root
        self.result = None
        
        # --- BACKGROUND ---
        bg_path = os.path.join(asset_root, "ui", "lobby-2.png")
        self.bg = pygame.image.load(bg_path).convert()
        self.bg = pygame.transform.scale(self.bg, screen_size)
        
        # --- AUDIO ---
        music_path = os.path.join(asset_root, "audio", "lobby.mp3")
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.2)
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)

        # --- SETUP TOMBOL (Dengan Scaling) ---
        SCALE_PLAY = 1.0
        SCALE_SETTINGS = 1.0
        SCALE_QUIT = 1.0
        
        # Posisi relatif ke layar (kanan bawah)
        sw, sh = screen_size
        btn_x = int(sw * 0.85)  # 85% dari lebar layar
        
        # Play Button
        self.btn_play = HoverButton(
            btn_x, int(sh * 0.6),
            os.path.join(asset_root, "ui", "btn-play.png"), 
            base_scale=SCALE_PLAY
        )
        
        # Settings Button
        self.btn_settings = HoverButton(
            btn_x, int(sh * 0.70),
            os.path.join(asset_root, "ui", "btn-settings.png"), 
            base_scale=SCALE_SETTINGS
        )
        
        # Quit Button
        self.btn_quit = HoverButton(
            btn_x, int(sh * 0.80), 
            os.path.join(asset_root, "ui", "btn-exit.png"), 
            base_scale=SCALE_QUIT
        )
        
        # --- POPUP ---
        self.popup = SettingsPopup(screen_size, max_volume=0.4, curr_volume=0.2)
        self.popup.is_visible = False

    def handle_event(self, event):
        # 1. Popup
        if self.popup.is_visible:
            should_close = self.popup.handle_event(event)
            if should_close:
                self.popup.is_visible = False
            return 

        # 2. Menu Utama
        if self.btn_play.is_clicked(event):
            pygame.mixer.music.stop()
            self.result = "PLAY"
            
        elif self.btn_settings.is_clicked(event):
            self.popup.is_visible = True
            
        elif self.btn_quit.is_clicked(event):
            pygame.mixer.music.stop()
            self.result = "EXIT"

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.blit(self.bg, (0, 0))

        self.btn_play.draw(surface)
        self.btn_settings.draw(surface)
        self.btn_quit.draw(surface)

        self.popup.draw(surface)
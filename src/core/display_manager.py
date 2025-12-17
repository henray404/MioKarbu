

import pygame
from typing import List, Optional, Tuple


class DisplayManager:
    """
    Manager untuk display dan rendering.
    
    Menangani:
    - Pygame initialization
    - Screen setup
    - Camera management
    - Rendering track, motors, UI
    """
    
    def __init__(self, fullscreen: bool = True, 
                 width: int = 1280, height: int = 960):
        """
        Initialize DisplayManager.
        
        Args:
            fullscreen: True untuk fullscreen, False untuk windowed
            width, height: Ukuran window jika tidak fullscreen
        """
        self.fullscreen = fullscreen
        self.width = width
        self.height = height
        
        # Pygame objects
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        
        # Fonts
        self.font_large: Optional[pygame.font.Font] = None
        self.font_small: Optional[pygame.font.Font] = None
        
        # Camera
        self.camera_x: float = 0
        self.camera_y: float = 0
        self.camera_smoothness: float = 0.15
    
    def init(self, title: str = "Mio Karbu", headless: bool = False):
        """
        Initialize pygame dan display.
        
        Args:
            title: Window title
            headless: True untuk mode tanpa display (training)
        """
        if headless:
            import os
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
        
        pygame.init()
        
        if headless:
            self.screen = pygame.display.set_mode((1, 1))
            print("[HEADLESS MODE] Training tanpa visualisasi")
        else:
            if self.fullscreen:
                info = pygame.display.Info()
                self.width = info.current_w
                self.height = info.current_h
            
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption(title)
        
        self.clock = pygame.time.Clock()
        
        # Fonts
        if not headless:
            self.font_large = pygame.font.Font(None, 48)
            self.font_small = pygame.font.Font(None, 32)
    
    def update_camera(self, target_x: float, target_y: float,
                      map_width: int, map_height: int):
        """
        Update camera position dengan smooth follow.
        
        Args:
            target_x, target_y: Posisi target (biasanya player)
            map_width, map_height: Ukuran map untuk clamping
        """
        # Target camera position (center on target)
        target_cam_x = target_x - self.width / 2
        target_cam_y = target_y - self.height / 2
        
        # Smooth interpolation (lerp)
        self.camera_x += (target_cam_x - self.camera_x) * self.camera_smoothness
        self.camera_y += (target_cam_y - self.camera_y) * self.camera_smoothness
        
        # Clamp to map bounds
        self.camera_x = max(0, min(map_width - self.width, self.camera_x))
        self.camera_y = max(0, min(map_height - self.height, self.camera_y))
    
    def render_track(self, track_surface: pygame.Surface):
        """
        Render track dengan camera offset.
        
        Args:
            track_surface: Surface track yang sudah di-scale
        """
        self.screen.blit(
            track_surface, 
            (-int(self.camera_x), -int(self.camera_y))
        )
    
    def render_motor(self, motor, show_radar: bool = False):
        """
        Render satu motor.
        
        Args:
            motor: Motor instance
            show_radar: True untuk menampilkan radar lines
        """
        motor.draw(
            self.screen, 
            int(self.camera_x), 
            int(self.camera_y)
        )
        
        if show_radar and hasattr(motor, 'radar'):
            motor.radar.draw(
                self.screen,
                int(self.camera_x),
                int(self.camera_y),
                motor.x,
                motor.y
            )
    
    def render_motors(self, motors: List, show_radar: bool = False):
        """
        Render multiple motors.
        
        Args:
            motors: List of Motor instances
            show_radar: True untuk menampilkan radar lines
        """
        for motor in motors:
            if motor.alive:
                self.render_motor(motor, show_radar)
    
    def render_countdown(self, countdown_seconds: int):
        """
        Render countdown overlay.
        
        Args:
            countdown_seconds: Detik tersisa (3, 2, 1)
        """
        if countdown_seconds <= 0:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))
        
        # Countdown number
        text = str(countdown_seconds)
        font = pygame.font.Font(None, 200)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text_surface, text_rect)
    
    def render_go(self):
        """Render 'GO!' text."""
        font = pygame.font.Font(None, 150)
        text_surface = font.render("GO!", True, (0, 255, 0))
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text_surface, text_rect)
    
    def render_speedometer(self, speed_kmh: int, x: int = None, y: int = None):
        """
        Render speedometer.
        
        Args:
            speed_kmh: Kecepatan dalam km/h
            x, y: Posisi (default: kanan bawah)
        """
        if x is None:
            x = self.width - 200
        if y is None:
            y = self.height - 80
        
        # Background
        pygame.draw.rect(self.screen, (30, 30, 30), (x, y, 180, 60), border_radius=10)
        
        # Speed text
        if self.font_large:
            speed_text = self.font_large.render(f"{speed_kmh}", True, (255, 255, 255))
            self.screen.blit(speed_text, (x + 10, y + 10))
            
            kmh_text = self.font_small.render("km/h", True, (150, 150, 150))
            self.screen.blit(kmh_text, (x + 80, y + 20))
        
        # Speed bar
        max_speed = 150
        bar_width = int((speed_kmh / max_speed) * 160)
        bar_width = min(160, bar_width)
        
        # Color gradient: green -> yellow -> red
        if speed_kmh < 50:
            color = (0, 255, 0)
        elif speed_kmh < 100:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
        
        pygame.draw.rect(self.screen, color, (x + 10, y + 45, bar_width, 8), border_radius=4)
    
    def render_lap_counter(self, current_lap: int, target_lap: int,
                           x: int = 20, y: int = 20):
        """
        Render lap counter.
        
        Args:
            current_lap: Lap saat ini
            target_lap: Target lap
            x, y: Posisi
        """
        if self.font_large:
            text = f"Lap {current_lap}/{target_lap}"
            text_surface = self.font_large.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (x, y))
    
    def render_winner(self, winner_name: str):
        """
        Render winner screen.
        
        Args:
            winner_name: Nama pemenang
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Winner text
        font = pygame.font.Font(None, 100)
        text = f"{winner_name} WINS!"
        text_surface = font.render(text, True, (255, 215, 0))
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(text_surface, text_rect)
        
        # Instruction
        if self.font_small:
            instruction = "Press R to restart, ESC to quit"
            inst_surface = self.font_small.render(instruction, True, (200, 200, 200))
            inst_rect = inst_surface.get_rect(center=(self.width // 2, self.height // 2 + 50))
            self.screen.blit(inst_surface, inst_rect)
    
    def tick(self, fps: int = 60) -> float:
        """
        Update display dan maintain FPS.
        
        Args:
            fps: Target FPS
            
        Returns:
            Delta time dalam detik
        """
        pygame.display.flip()
        return self.clock.tick(fps) / 1000.0
    
    def quit(self):
        """Cleanup pygame."""
        pygame.quit()

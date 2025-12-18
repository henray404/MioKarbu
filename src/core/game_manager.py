"""
Game Manager Module
====================

Mengelola loading dan setup game assets (track, masking, spawn).
Digunakan oleh main.py dan trainer.py.
"""

import os
import pygame
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class GameConfig:
    """Konfigurasi game yang bisa di-customize"""
    # Track
    track_name: str = "new-4"
    track_scale: float = 3.0
    
    # Original track dimensions (untuk kalkulasi spawn)
    original_track_width: int = 2624
    original_track_height: int = 1632
    
    # Spawn
    spawn_x: int = 1800
    spawn_y: int = 1380
    spawn_angle: float = 0.0
    
    # Masking
    masking_file: str = "ai_masking-4.png"
    masking_subfolder: str = "masking"
    
    # Display
    fullscreen: bool = True
    screen_width: int = 1280
    screen_height: int = 960


class GameManager:
    """
    Manager untuk game assets dan setup.
    
    Menangani:
    - Loading track surface
    - Loading masking surface
    - Kalkulasi spawn position
    - Create Motor instances
    """
    
    def __init__(self, base_dir: str, config: GameConfig = None):
        """
        Initialize GameManager.
        
        Args:
            base_dir: Root directory project
            config: GameConfig instance, atau None untuk default
        """
        self.base_dir = base_dir
        self.assets_dir = os.path.join(base_dir, "assets")
        self.config = config or GameConfig()
        
        # Surfaces
        self.track_surface: Optional[pygame.Surface] = None
        self.masking_surface: Optional[pygame.Surface] = None
        
        # Map dimensions (setelah scaling)
        self.map_width: int = 0 
        self.map_height: int = 0
    
    def load_track(self, track_name: str = None) -> pygame.Surface:
        """
        Load dan scale track surface.
        
        Args:
            track_name: Nama track (tanpa .png), atau None untuk pakai config
            
        Returns:
            Scaled track surface
        """
        if track_name is None:
            track_name = self.config.track_name
            
        track_path = os.path.join(self.assets_dir, "tracks", f"{track_name}.png")
        
        if not os.path.exists(track_path):
            raise FileNotFoundError(f"Track tidak ditemukan: {track_path}")
        
        # Load dan scale
        self.track_surface = pygame.image.load(track_path)
        original_w, original_h = self.track_surface.get_size()
        
        self.map_width = int(original_w * self.config.track_scale)
        self.map_height = int(original_h * self.config.track_scale)
        
        self.track_surface = pygame.transform.scale(
            self.track_surface,
            (self.map_width, self.map_height)
        )
        
        print(f"Track      : {track_name}.png")
        print(f"Map Size   : {self.map_width}x{self.map_height} (scaled {self.config.track_scale}x)")
        
        return self.track_surface
    
    def load_masking(self, masking_file: str = None) -> Optional[pygame.Surface]:
        """
        Load dan scale masking surface.
        
        Args:
            masking_file: Nama file masking, atau None untuk pakai config
            
        Returns:
            Scaled masking surface, atau None jika tidak ditemukan
        """
        if masking_file is None:
            masking_file = self.config.masking_file
        
        masking_path = os.path.join(
            self.assets_dir, 
            "tracks", 
            self.config.masking_subfolder,
            masking_file
        )
        
        if not os.path.exists(masking_path):
            print(f"Masking    : Not found at {masking_path}")
            return None
        
        self.masking_surface = pygame.image.load(masking_path)
        self.masking_surface = pygame.transform.scale(
            self.masking_surface,
            (self.map_width, self.map_height)
        )
        
        print(f"Masking    : Loaded ({self.map_width}x{self.map_height})")
        
        return self.masking_surface
    
    def get_spawn_position(self) -> Tuple[int, int]:
        """
        Hitung spawn position berdasarkan map size.
        
        Returns:
            Tuple (spawn_x, spawn_y) yang sudah di-scale
        """
        if self.map_width == 0 or self.map_height == 0:
            raise ValueError("Track belum di-load! Panggil load_track() dulu.")
        
        spawn_x = int(
            self.config.spawn_x * 
            (self.map_width / self.config.original_track_width)
        )
        spawn_y = int(
            self.config.spawn_y * 
            (self.map_height / self.config.original_track_height)
        )
        
        return spawn_x, spawn_y
    
    def create_motor(self, x: int, y: int, color: str = "pink", 
                     invincible: bool = True):
        """
        Create Motor dengan setup standard.
        
        Args:
            x, y: Posisi spawn
            color: Warna motor
            invincible: Apakah motor invincible
            
        Returns:
            Motor instance yang sudah di-setup
        """
        # Import di sini untuk menghindari circular import
        from core.motor import Motor
        
        motor = Motor(x, y, color=color)
        motor.angle = self.config.spawn_angle
        motor.start_angle = motor.angle
        
        if self.track_surface is not None:
            motor.set_track_surface(self.track_surface)
        
        if self.masking_surface is not None:
            motor.set_masking_surface(self.masking_surface)
        
        motor.invincible = invincible
        
        return motor
    
    def setup_all(self, track_name: str = None, masking_file: str = None):
        """
        Shortcut untuk setup lengkap: load track + masking.
        
        Args:
            track_name: Nama track (optional)
            masking_file: Nama file masking (optional)
        """
        self.load_track(track_name)
        self.load_masking(masking_file)

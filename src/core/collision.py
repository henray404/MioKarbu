"""
Collision Module untuk Motor
============================

Mengandung logic untuk collision detection.
Digunakan dengan composition pattern oleh Motor class.
"""

import math
from typing import List, Tuple, Optional
import pygame


class CollisionHandler:
    """
    Handler untuk collision detection.
    
    Supports:
    - Track-based pixel collision
    - Masking-based collision (multi-zone)
    - Corner-based collision box
    """
    
    def __init__(self, length: float = 140, width: float = 80):
        """
        Args:
            length: Panjang motor (untuk collision box)
            width: Lebar motor (untuk collision box)
        """
        self.length = length
        self.width = width
        
        # Surfaces
        self.track = None
        self.track_surface: Optional[pygame.Surface] = None
        self.masking_surface: Optional[pygame.Surface] = None
    
    def set_track(self, track) -> None:
        """Set Track object untuk collision detection."""
        self.track = track
    
    def set_track_surface(self, surface: pygame.Surface) -> None:
        """Set pygame.Surface langsung untuk collision."""
        self.track_surface = surface
    
    def set_masking_surface(self, surface: pygame.Surface) -> None:
        """
        Set masking surface untuk advanced collision.
        
        Masking colors:
        - Black (R,G,B < 50): Track/jalan
        - White (R,G,B > 200): Slow zone
        - Gray (50-200): Wall/tembok
        - Red: Wall (bounce/explode)
        - Green/Cyan/Yellow/Magenta: Checkpoints
        """
        self.masking_surface = surface
    
    def get_collision_corners(self, x: float, y: float, angle: float) -> List[Tuple[float, float]]:
        """
        Get 4 corner points untuk collision detection.
        
        Args:
            x, y: Posisi center motor
            angle: Sudut motor (radians)
            
        Returns:
            List of 4 corner positions
        """
        # Smaller hitbox (40% of actual size)
        length = self.length * 0.4
        width = self.width * 0.4
        
        corners = []
        for dx, dy in [(-length/2, -width/2), (length/2, -width/2),
                       (length/2, width/2), (-length/2, width/2)]:
            rx = dx * math.cos(angle) - dy * math.sin(angle)
            ry = dx * math.sin(angle) + dy * math.cos(angle)
            corners.append((x + rx, y + ry))
        
        return corners
    
    def check_track_collision(self, x: float, y: float) -> bool:
        """
        Check collision menggunakan Track object.
        
        Returns:
            True jika collision
        """
        if self.track is None:
            return False
        
        collision_size = min(self.length, self.width) * 0.6
        return self.track.check_collision(x, y, collision_size, collision_size)
    
    def check_masking_collision(self, x: float, y: float, angle: float) -> dict:
        """
        Check collision menggunakan masking surface.
        
        Returns dict dengan info:
        - 'collided': True jika nabrak wall
        - 'out_of_bounds': True jika keluar map
        - 'slow_zone': True jika di slow zone
        - 'checkpoint': 0-4 (0 = bukan checkpoint)
        - 'on_track': True jika di track hitam
        """
        result = {
            'collided': False,
            'out_of_bounds': False,
            'slow_zone': False,
            'checkpoint': 0,
            'on_track': True
        }
        
        if self.masking_surface is None:
            return result
        
        corners = self.get_collision_corners(x, y, angle)
        
        for corner in corners:
            cx, cy = int(corner[0]), int(corner[1])
            
            # Boundary check
            if cx < 0 or cx >= self.masking_surface.get_width() or \
               cy < 0 or cy >= self.masking_surface.get_height():
                result['out_of_bounds'] = True
                result['collided'] = True
                return result
            
            # Get color
            color = self.masking_surface.get_at((cx, cy))
            r, g, b = color[0], color[1], color[2]
            zone = self._classify_color(r, g, b)
            
            if zone == 'wall':
                result['collided'] = True
                return result
            elif zone == 'slow':
                result['slow_zone'] = True
            elif zone.startswith('cp'):
                result['checkpoint'] = int(zone[2])
            elif zone == 'track':
                pass  # OK
        
        return result
    
    def _classify_color(self, r: int, g: int, b: int) -> str:
        """
        Klasifikasi warna dari masking.
        
        Returns:
            'track', 'wall', 'slow', 'cp1', 'cp2', 'cp3', 'cp4'
        """
        avg = (r + g + b) / 3
        
        # Track (black)
        if avg < 50:
            return 'track'
        
        # Wall (red)
        if r > 150 and g < 100 and b < 100:
            return 'wall'
        
        # Checkpoints (sequential colors)
        # CP1: Green
        if g > 150 and r < 150 and b < 150 and g > r and g > b:
            return 'cp1'
        # CP2: Cyan
        if g > 150 and b > 150 and r < 150:
            return 'cp2'
        # CP3: Yellow
        if r > 150 and g > 150 and b < 150:
            return 'cp3'
        # CP4: Magenta
        if r > 150 and b > 150 and g < 150:
            return 'cp4'
        
        # Slow zone (white/gray)
        return 'slow'
    
    def get_surface_for_radar(self) -> Optional[pygame.Surface]:
        """Get surface yang dipakai untuk radar (masking preferred)."""
        return self.masking_surface or self.track_surface

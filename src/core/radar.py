"""
Radar Module untuk Motor AI
===========================

Mengandung sistem radar untuk AI sensing dan fitness calculation.
Digunakan dengan composition pattern oleh Motor class.
"""

import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Set
import pygame


@dataclass
class RadarConfig:
    """Konfigurasi radar."""
    num_radars: int = 5
    radar_angles: List[int] = field(default_factory=lambda: [-90, -45, 0, 45, 90])
    max_length: int = 300


@dataclass 
class AIState:
    """State untuk AI tracking dan fitness."""
    time_spent: int = 0
    distance_traveled: float = 0
    unique_positions: Set[Tuple[int, int]] = field(default_factory=set)
    last_grid_pos: Optional[Tuple[int, int]] = None
    consecutive_same_pos: int = 0
    max_distance_reached: float = 0
    stuck_timer: int = 0
    collision_count: int = 0
    total_rotation: float = 0
    prev_x: float = 0
    prev_y: float = 0


class Radar:
    """
    Sistem radar untuk AI motor.
    
    Features:
    - Raycast-based distance sensing
    - Masking-aware (stops at walls only)
    - Normalized output for neural network
    """
    
    def __init__(self, config: RadarConfig = None):
        self.config = config or RadarConfig()
        self.radars: List[Tuple[Tuple[int, int], int]] = []
    
    def update(self, x: float, y: float, angle: float, 
               surface: pygame.Surface, masking_mode: bool = True) -> None:
        """
        Update semua radar rays.
        
        Args:
            x, y: Posisi motor
            angle: Sudut motor (radians)
            surface: Surface untuk raycast
            masking_mode: True jika pakai masking (stop di merah only)
        """
        self.radars.clear()
        
        if surface is None:
            return
        
        # Convert angle dari radians ke degrees (360-system)
        angle_deg = 360 - math.degrees(angle)
        
        for degree in self.config.radar_angles:
            length = 0
            end_x = int(x)
            end_y = int(y)
            
            while length < self.config.max_length:
                # Calculate radar position
                radar_angle = math.radians(360 - (angle_deg + degree))
                end_x = int(x + math.cos(radar_angle) * length)
                end_y = int(y + math.sin(radar_angle) * length)
                
                try:
                    # Boundary check
                    if end_x < 0 or end_x >= surface.get_width() or \
                       end_y < 0 or end_y >= surface.get_height():
                        break
                    
                    pixel = surface.get_at((end_x, end_y))
                    r, g, b = pixel[0], pixel[1], pixel[2]
                    
                    if masking_mode:
                        # Only stop at red (wall)
                        is_red = (r > 150 and g < 100 and b < 100)
                        if is_red:
                            break
                    else:
                        # Legacy mode
                        avg = (r + g + b) / 3
                        is_gray = (abs(r - g) < 50 and abs(g - b) < 50 and abs(r - b) < 50)
                        is_white = (r > 200 and g > 200 and b > 200)
                        is_red = (r > 150 and g < 100 and b < 100)
                        is_green = (g > r + 30 and g > b + 30)
                        
                        if is_green or not (is_gray or is_white or is_red):
                            break
                except:
                    break
                
                length += 5  # Step 5 pixels for performance
            
            dist = int(math.sqrt((end_x - x)**2 + (end_y - y)**2))
            self.radars.append(((end_x, end_y), dist))
    
    def get_data(self) -> List[int]:
        """
        Get normalized radar data untuk neural network.
        
        Returns:
            List of values (0-10 scale)
        """
        data = [0] * self.config.num_radars
        for i, radar in enumerate(self.radars):
            if i < len(data):
                data[i] = int(radar[1] / 30)  # Normalize to 0-10
        return data
    
    def draw(self, screen: pygame.Surface, camera_x: int, camera_y: int,
             x: float, y: float) -> None:
        """Draw radar lines untuk debug."""
        for (end_pos, dist) in self.radars:
            color = (0, 255, 0) if dist > 50 else (255, 0, 0)
            pygame.draw.line(
                screen, color,
                (int(x - camera_x), int(y - camera_y)),
                (end_pos[0] - camera_x, end_pos[1] - camera_y),
                2
            )


class FitnessCalculator:
    """
    Calculator untuk fitness score AI.
    """
    
    def __init__(self, start_x: float = 0, start_y: float = 0):
        self.state = AIState(prev_x=start_x, prev_y=start_y)
    
    def update(self, x: float, y: float, angle_change: float) -> None:
        """
        Update tracking data setiap frame.
        
        Args:
            x, y: Posisi motor
            angle_change: Perubahan angle frame ini
        """
        self.state.time_spent += 1
        
        # Calculate distance traveled
        dx = x - self.state.prev_x
        dy = y - self.state.prev_y
        distance = math.sqrt(dx*dx + dy*dy)
        self.state.distance_traveled += distance
        self.state.max_distance_reached = max(self.state.max_distance_reached, 
                                               self.state.distance_traveled)
        
        # Track unique positions (grid-based)
        grid_pos = (int(x // 50), int(y // 50))
        if grid_pos != self.state.last_grid_pos:
            self.state.unique_positions.add(grid_pos)
            self.state.consecutive_same_pos = 0
            self.state.stuck_timer = 0
        else:
            self.state.consecutive_same_pos += 1
            self.state.stuck_timer += 1
        self.state.last_grid_pos = grid_pos
        
        # Track rotation
        self.state.total_rotation += abs(math.degrees(angle_change))
        
        # Update previous position
        self.state.prev_x = x
        self.state.prev_y = y
    
    def calculate(self, lap_count: int = 0) -> float:
        """
        Calculate fitness score.
        
        Args:
            lap_count: Jumlah lap yang sudah complete
            
        Returns:
            Fitness value
        """
        if lap_count == 0:
            # Belum complete lap: fokus exploration
            novelty_score = len(self.state.unique_positions)
            if novelty_score < 5:
                return -100
            
            base_reward = novelty_score * 10
            rotation_reward = min(self.state.total_rotation / 2.0, 200)
            distance_reward = self.state.distance_traveled / 50.0
            repetition_penalty = self.state.consecutive_same_pos * -20
            
            return base_reward + rotation_reward + distance_reward + repetition_penalty
        else:
            # Sudah complete lap: optimize
            lap_bonus = (lap_count ** 2) * 1000
            efficiency = self.state.distance_traveled / max(self.state.time_spent, 1)
            efficiency_bonus = efficiency * 50
            novelty_bonus = len(self.state.unique_positions) * 3
            
            return lap_bonus + efficiency_bonus + novelty_bonus
    
    def is_stuck(self, threshold: int = 120) -> bool:
        """Check apakah motor stuck."""
        return self.state.stuck_timer > threshold
    
    def reset(self, start_x: float = 0, start_y: float = 0) -> None:
        """Reset semua tracking state."""
        self.state = AIState(prev_x=start_x, prev_y=start_y)

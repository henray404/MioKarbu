"""
AI Car untuk NEAT Training (DEPRECATED)
=======================================

⚠️ DEPRECATED: Class ini sudah deprecated.
Gunakan `Motor` dari `core.motor` yang sudah unified dengan semua fitur:
- Player control (WASD)
- AI control (steer, get_radar_data, get_fitness)
- Lap detection
- Collision detection

Contoh:
    from core.motor import Motor
    ai = Motor(x, y, color="pink")
    ai.set_track_surface(track_surface)
    ai.velocity = ai.max_speed
    ai.steer(1)  # Belok kiri
    ai.update()
    
Class ini masih disimpan untuk backward compatibility dengan
model training lama. Untuk project baru, gunakan Motor.
"""

import pygame
import math
import os
from typing import List, Tuple, Optional

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


class AICar:
    """
    Car untuk NEAT AI training.
    
    Attributes:
        pos: [x, y] posisi
        angle: sudut hadap (derajat)
        speed: kecepatan tetap
        is_alive: status hidup
        lap_count: jumlah lap selesai
    """
    
    def __init__(self, start_x: float = 1300, start_y: float = 500, 
                 start_angle: float = 90, speed: float = 6):
        """
        Inisialisasi AI Car.
        
        Args:
            start_x, start_y: posisi awal
            start_angle: sudut awal (derajat)
            speed: kecepatan tetap
        """
        # Load sprite
        sprite_path = os.path.join(ASSETS_DIR, "motor", "pink-1.png")
        if os.path.exists(sprite_path):
            self.surface = pygame.image.load(sprite_path)
            self.surface = pygame.transform.scale(self.surface, (30, 60))
            self.surface = pygame.transform.rotate(self.surface, -90)
        else:
            # Fallback surface
            self.surface = pygame.Surface((60, 30), pygame.SRCALPHA)
            self.surface.fill((255, 100, 100))
        
        self.rotate_surface = self.surface
        
        # Position & movement
        self.pos = [float(start_x), float(start_y)]
        self.start_pos = [float(start_x), float(start_y)]
        self.angle = start_angle
        self.speed = speed
        
        # Center point for collision/radar
        self.center = [self.pos[0] + 23, self.pos[1] + 23]
        self.four_points = []
        
        # Sensor/radar
        self.radars: List[Tuple[Tuple[int, int], int]] = []
        self.num_radars = 5
        self.radar_angles = [-90, -45, 0, 45, 90]  # Derajat relatif ke arah hadap
        self.max_radar_length = 300
        
        # Status
        self.is_alive = True
        self.distance = 0
        self.time_spent = 0
        
        # Lap tracking
        self.lap_count = 0
        self.total_rotation = 0
        self.has_left_start = False
        self.min_distance_to_leave = 300
        self.lap_cooldown = 0  # Cooldown agar lap tidak terhitung ganda
        
        # Anti-stuck
        self.prev_pos = self.pos.copy()
        self.stuck_timer = 0
        self.collision_count = 0
        
        # Novelty tracking
        self.unique_positions = set()
        self.last_grid_pos = None
        self.consecutive_same_pos = 0
        self.max_distance = 0
    
    def reset(self, x: Optional[float] = None, y: Optional[float] = None, 
              angle: Optional[float] = None):
        """Reset car ke posisi awal"""
        self.pos = [x or self.start_pos[0], y or self.start_pos[1]]
        self.angle = angle or 0
        self.is_alive = True
        self.distance = 0
        self.time_spent = 0
        self.lap_count = 0
        self.total_rotation = 0
        self.has_left_start = False
        self.stuck_timer = 0
        self.collision_count = 0
        self.unique_positions.clear()
        self.consecutive_same_pos = 0
        self.max_distance = 0
        self.radars.clear()
    
    def steer(self, direction: int):
        """
        Belokkan car.
        
        Args:
            direction: -1 (kanan), 0 (lurus), 1 (kiri)
        """
        prev_angle = self.angle
        
        if direction == 1:
            self.angle += 7  # Belok kiri (clockwise)
        elif direction == -1:
            self.angle -= 7  # Belok kanan (counter-clockwise)
        # direction == 0: lurus
        
        # Track rotation untuk lap detection
        angle_change = self.angle - prev_angle
        if angle_change > 0:
            self.total_rotation += angle_change
    
    def update(self, track_surface: pygame.Surface):
        """
        Update posisi, collision, dan radar.
        
        Args:
            track_surface: Surface track untuk collision detection
        """
        if not self.is_alive:
            return
        
        # Update position
        self.rotate_surface = pygame.transform.rotate(self.surface, self.angle)
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        
        # Update stats
        self.distance += self.speed
        self.time_spent += 1
        self.max_distance = max(self.max_distance, self.distance)
        
        # Update center
        self.center = [int(self.pos[0]) + 23, int(self.pos[1]) + 23]
        
        # Calculate collision points
        self._update_collision_points()
        
        # Check collision
        self._check_collision(track_surface)
        
        # Update radars
        self._update_radars(track_surface)
        
        # Lap detection
        self._check_lap()
        
        # Stuck detection
        self._check_stuck()
        
        # Novelty tracking
        self._track_novelty()
        
        self.prev_pos = self.pos.copy()
    
    def _update_collision_points(self):
        """Calculate 4 corner points untuk collision"""
        length = 30
        self.four_points = [
            [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length,
             self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length],
            [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length,
             self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length],
            [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length,
             self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length],
            [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length,
             self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length],
        ]
    
    def _check_collision(self, track_surface: pygame.Surface):
        """Check collision dengan track"""
        for point in self.four_points:
            try:
                x, y = int(point[0]), int(point[1])
                if x < 0 or y < 0:
                    self.is_alive = False
                    self.collision_count += 1
                    return
                
                pixel = track_surface.get_at((x, y))
                r, g, b = pixel[0], pixel[1], pixel[2]
                
                # Valid: hitam (track), putih (finish), merah (finish alt)
                # Valid: hitam (track), putih (finish), merah (finish alt)
                # Widen range to handle antialiasing (gray pixels) - with overlap
                is_black = (r < 120 and g < 120 and b < 120)
                is_white = (r > 100 and g > 100 and b > 100)
                is_red = (r > 150 and g < 100 and b < 100)
                
                if not (is_black or is_white or is_red):
                    self.is_alive = False
                    self.collision_count += 1
                    return
            except:
                self.is_alive = False
                self.collision_count += 1
                return
    
    def _update_radars(self, track_surface: pygame.Surface):
        """Update sensor radar"""
        self.radars.clear()
        
        for degree in self.radar_angles:
            length = 0
            x = int(self.center[0])
            y = int(self.center[1])
            
            # Raycast sampai ketemu batas atau max length
            while length < self.max_radar_length:
                x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
                y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)
                
                try:
                    pixel = track_surface.get_at((x, y))
                    r, g, b = pixel[0], pixel[1], pixel[2]
                    
                    is_black = (r < 120 and g < 120 and b < 120)
                    is_white = (r > 100 and g > 100 and b > 100)
                    is_red = (r > 150 and g < 100 and b < 100)
                    
                    if not (is_black or is_white or is_red):
                        break
                except:
                    break
                
                length += 1
            
            dist = int(math.sqrt((x - self.center[0])**2 + (y - self.center[1])**2))
            self.radars.append(((x, y), dist))
    
    def _check_lap(self):
        """Check lap completion"""
        # Kurangi cooldown
        if self.lap_cooldown > 0:
            self.lap_cooldown -= 1
            return
            
        dist_from_start = math.sqrt(
            (self.pos[0] - self.start_pos[0])**2 + 
            (self.pos[1] - self.start_pos[1])**2
        )
        
        # Sudah keluar dari area start?
        if dist_from_start > self.min_distance_to_leave:
            self.has_left_start = True
        
        # Kembali ke start = lap selesai
        elif self.has_left_start and dist_from_start < 80:
            if self.total_rotation >= 300:  # Minimal 300 derajat rotasi
                self.lap_count += 1
                print(f"Lap {self.lap_count} completed! Distance: {int(self.distance)}")
                self.lap_cooldown = 60  # Cooldown 60 frame (~1 detik) sebelum bisa lap lagi
            self.has_left_start = False
            self.total_rotation = 0
    
    def _check_stuck(self):
        """Check jika car stuck"""
        dist_from_start = math.sqrt(
            (self.pos[0] - self.start_pos[0])**2 + 
            (self.pos[1] - self.start_pos[1])**2
        )
        near_finish = dist_from_start < 120
        
        pos_change = math.sqrt(
            (self.pos[0] - self.prev_pos[0])**2 + 
            (self.pos[1] - self.prev_pos[1])**2
        )
        
        if pos_change < 3 and not near_finish:
            self.stuck_timer += 1
            if self.stuck_timer > 30:
                self.is_alive = False
        else:
            self.stuck_timer = 0
    
    def _track_novelty(self):
        """Track novelty untuk fitness"""
        if self.time_spent % 10 == 0:
            grid_pos = (int(self.pos[0] / 50), int(self.pos[1] / 50))
            self.unique_positions.add(grid_pos)
            
            dist_from_start = math.sqrt(
                (self.pos[0] - self.start_pos[0])**2 + 
                (self.pos[1] - self.start_pos[1])**2
            )
            near_finish = dist_from_start < 120
            
            if grid_pos == self.last_grid_pos and not near_finish:
                self.consecutive_same_pos += 1
                if self.consecutive_same_pos > 5:
                    self.is_alive = False
            else:
                self.consecutive_same_pos = 0
            
            self.last_grid_pos = grid_pos
    
    def get_radar_data(self) -> List[int]:
        """
        Get normalized radar data untuk neural network.
        
        Returns:
            List of 5 values (0-10 scale)
        """
        data = [0] * self.num_radars
        for i, radar in enumerate(self.radars):
            if i < len(data):
                data[i] = int(radar[1] / 30)
        return data
    
    def get_fitness(self) -> float:
        """
        Calculate fitness score.
        
        Returns:
            Fitness value
        """
        # Belum complete lap: fokus exploration
        if self.lap_count == 0:
            novelty_score = len(self.unique_positions)
            if novelty_score < 5:
                return -100
            
            base_reward = novelty_score * 10
            rotation_reward = min(self.total_rotation / 2.0, 200)
            distance_reward = self.distance / 50.0
            repetition_penalty = self.consecutive_same_pos * -20
            
            return base_reward + rotation_reward + distance_reward + repetition_penalty
        
        # Sudah complete lap: optimize
        else:
            lap_bonus = (self.lap_count ** 2) * 1000
            efficiency = self.distance / max(self.time_spent, 1)
            efficiency_bonus = efficiency * 50
            novelty_bonus = len(self.unique_positions) * 3
            
            return lap_bonus + efficiency_bonus + novelty_bonus
    
    def draw(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0):
        """
        Draw car dan radar.
        
        Args:
            screen: Pygame surface
            camera_x, camera_y: Camera offset
        """
        # Draw car
        screen.blit(self.rotate_surface, 
                   (self.pos[0] - camera_x, self.pos[1] - camera_y))
        
        # Draw radar
        for radar in self.radars:
            pos, dist = radar
            pygame.draw.line(screen, (0, 255, 0),
                           (self.center[0] - camera_x, self.center[1] - camera_y),
                           (pos[0] - camera_x, pos[1] - camera_y), 1)
            pygame.draw.circle(screen, (0, 255, 0),
                             (pos[0] - camera_x, pos[1] - camera_y), 5)

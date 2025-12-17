"""
Motor Class - Refactored dengan Modular Components
===================================================

Class utama untuk motor (player & AI) menggunakan composition pattern.
Modul-modul yang digunakan:
- PhysicsEngine: Fisika pergerakan, steering, drift
- CollisionHandler: Deteksi tabrakan
- CheckpointTracker: Lap dan checkpoint tracking
- Radar: AI sensing system
- FitnessCalculator: AI fitness calculation
"""

import pygame
import math
import os
from typing import Optional, List, Tuple

from core.distance_sensor import DistanceSensor
from core.physics import PhysicsConfig, PhysicsEngine
from core.collision import CollisionHandler
from core.checkpoint import CheckpointTracker
from core.radar import Radar, FitnessCalculator, RadarConfig

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


class Motor:
    """
    Motor dengan modular architecture.
    
    Menggunakan composition pattern untuk memisahkan concerns:
    - physics: PhysicsEngine untuk movement & steering
    - collision: CollisionHandler untuk collision detection
    - checkpoint: CheckpointTracker untuk lap tracking
    - radar: Radar untuk AI sensing
    - fitness: FitnessCalculator untuk AI training
    """
    
    def __init__(self, x: float, y: float, color: str = "pink"):
        """
        Inisialisasi Motor.
        
        Args:
            x, y: Posisi awal
            color: Nama warna motor (untuk sprite sheet)
        """
        # Position & angle
        self.x = x
        self.y = y
        self.angle = 0
        self.color = color
        
        # Dimensions
        self.length = 140
        self.width = 80
        
        # =================================================================
        # COMPOSITION: Modular Components
        # =================================================================
        
        # Physics engine
        self.physics = PhysicsEngine(PhysicsConfig(
            length=self.length,
            width=self.width
        ))
        
        # Collision handler
        self.collision = CollisionHandler(length=self.length, width=self.width)
        
        # Checkpoint tracker
        self.checkpoint = CheckpointTracker(start_x=x, start_y=y)
        
        # AI Radar
        self.radar = Radar(RadarConfig())
        
        # Fitness calculator
        self.fitness_calc = FitnessCalculator(start_x=x, start_y=y)
        
        # =================================================================
        # SPRITE & ANIMATION
        # =================================================================
        
        self.current_frame = 0
        self.animation_speed = 0.15
        self.animation_counter = 0
        self.frames: List[pygame.Surface] = []
        self.total_frames = 0
        self.use_sprite = False
        self.surface = None
        
        self._load_sprites(color)
        
        # =================================================================
        # STATE
        # =================================================================
        
        self.alive = True
        self.is_alive = True  # Compatibility alias
        self.invincible = False  # Player mode
        
        # Start position (untuk reset)
        self.start_x = x
        self.start_y = y
        self.start_angle = 0
        
        # Input
        self.steering_input = 0
        
        # Respawn state (untuk animasi kelap-kelip dan stun)
        self.respawning = False
        self.respawn_timer = 0  # Frame counter untuk stun
        self.respawn_duration = 60  # 1 detik = 60 frame (60 FPS)
        self.blink_interval = 6  # Kelap-kelip setiap 6 frame
        
        # External sensor (optional, for compatibility)
        self.sensor: Optional[DistanceSensor] = None
        
        # Track references
        self.track = None
        self.track_surface: Optional[pygame.Surface] = None
        self.masking_surface: Optional[pygame.Surface] = None
        
        # Rect for collision (updated in draw)
        self.rect = None
    
    def _load_sprites(self, color: str) -> None:
        """Load sprite frames untuk animasi."""
        frame_index = 1
        while True:
            frame_path = os.path.join(ASSETS_DIR, "motor", f"{color}-{frame_index}.png")
            if os.path.exists(frame_path):
                frame = pygame.image.load(frame_path).convert_alpha()
                rotated = pygame.transform.rotate(frame, -90)
                scaled = pygame.transform.scale(rotated, (self.length, self.width))
                self.frames.append(scaled)
                self.total_frames += 1
                frame_index += 1
            else:
                break
        
        if self.total_frames > 0:
            self.use_sprite = True
        else:
            self.surface = pygame.Surface((self.length, self.width), pygame.SRCALPHA)
            self.surface.fill((255, 192, 203))
            self.use_sprite = False
    
    # =================================================================
    # PROPERTY ACCESSORS (backward compatibility)
    # =================================================================
    
    @property
    def velocity(self) -> float:
        return self.physics.state.velocity
    
    @velocity.setter
    def velocity(self, value: float):
        self.physics.state.velocity = value
    
    @property
    def max_speed(self) -> float:
        return self.physics.config.max_speed
    
    @property
    def distance_traveled(self) -> float:
        return self.fitness_calc.state.distance_traveled
    
    @distance_traveled.setter
    def distance_traveled(self, value: float):
        self.fitness_calc.state.distance_traveled = value
    
    @property
    def lap_count(self) -> int:
        return self.checkpoint.state.lap_count
    
    @lap_count.setter
    def lap_count(self, value: int):
        self.checkpoint.state.lap_count = value
    
    @property
    def checkpoint_count(self) -> int:
        return self.checkpoint.state.checkpoint_count
    
    @checkpoint_count.setter
    def checkpoint_count(self, value: int):
        self.checkpoint.state.checkpoint_count = value
    
    @property
    def time_spent(self) -> int:
        return self.fitness_calc.state.time_spent
    
    @time_spent.setter
    def time_spent(self, value: int):
        self.fitness_calc.state.time_spent = value
    
    @property
    def last_checkpoint_time(self) -> int:
        return self.checkpoint.state.last_checkpoint_time
    
    @last_checkpoint_time.setter
    def last_checkpoint_time(self, value: int):
        self.checkpoint.state.last_checkpoint_time = value
    
    @property
    def radars(self) -> List:
        return self.radar.radars
    
    @property
    def drift_angle(self) -> float:
        return self.physics.state.drift_angle
    
    @property
    def is_drifting(self) -> bool:
        return self.physics.state.is_drifting
    
    @property
    def total_rotation(self) -> float:
        return self.fitness_calc.state.total_rotation
    
    @property
    def expected_checkpoint(self) -> int:
        return self.checkpoint.state.expected_checkpoint
    
    @property
    def on_checkpoint(self) -> bool:
        return self.checkpoint.state.on_checkpoint
    
    # =================================================================
    # TRACK & COLLISION SETUP
    # =================================================================
    
    def set_track(self, track) -> None:
        """Set Track object untuk collision detection."""
        self.track = track
        self.collision.set_track(track)
        if self.sensor is not None:
            self.sensor.set_track(track)
    
    def set_track_surface(self, surface: pygame.Surface) -> None:
        """Set pygame.Surface untuk collision detection."""
        self.track_surface = surface
        self.collision.set_track_surface(surface)
    
    def set_masking_surface(self, surface: pygame.Surface) -> None:
        """Set masking surface untuk advanced collision."""
        self.masking_surface = surface
        self.collision.set_masking_surface(surface)
    
    # =================================================================
    # SENSOR METHODS
    # =================================================================
    
    def set_sensor(self, sensor: DistanceSensor) -> None:
        """Attach external sensor ke motor."""
        self.sensor = sensor
        if self.track is not None:
            self.sensor.set_track(self.track)
    
    def create_sensor(self, num_sensors: int = 5, fov: float = 180, 
                      max_distance: float = 200) -> DistanceSensor:
        """Buat dan attach sensor baru."""
        sensor = DistanceSensor(num_sensors, fov, max_distance)
        self.set_sensor(sensor)
        return sensor
    
    def get_sensor_data(self, num_sensors: int = 5, fov: float = 180,
                        max_distance: float = 200) -> List[float]:
        """Get normalized sensor data untuk AI."""
        if self.sensor is None:
            self.create_sensor(num_sensors, fov, max_distance)
        self.sensor.update(self.x, self.y, self.angle)
        return self.sensor.get_normalized()
    
    def get_radar_data(self) -> List[int]:
        """Get normalized radar data untuk neural network."""
        return self.radar.get_data()
    
    def draw_sensors(self, screen, camera) -> None:
        """Draw sensor visualization."""
        if self.sensor is not None:
            self.sensor.draw(screen, camera, self.x, self.y, self.angle)
    
    # =================================================================
    # AI INPUT
    # =================================================================
    
    def set_ai_input(self, steering: float, throttle: float) -> None:
        """
        Input dari AI controller.
        
        Args:
            steering: -1 (kiri) to 1 (kanan)
            throttle: -1 (mundur) to 1 (maju)
        """
        self.steering_input = max(-1, min(1, steering))
        self.physics.apply_acceleration(throttle)
        angle_change = self.physics.apply_steering(self.steering_input)
        self.angle += angle_change
    
    def steer(self, direction: int) -> None:
        """
        Steering untuk AI (simplified).
        
        Args:
            direction: -1 (kanan), 0 (lurus), 1 (kiri)
        """
        angle_change = self.physics.apply_steering(direction)
        self.angle += angle_change
    
    # =================================================================
    # STATE METHODS
    # =================================================================
    
    def get_state(self) -> Tuple[float, float, float, float, bool]:
        """Get state untuk AI: (x, y, angle, velocity, alive)"""
        return (self.x, self.y, self.angle, self.velocity, self.alive)
    
    def get_fitness(self) -> float:
        """Calculate fitness score."""
        return self.fitness_calc.calculate(self.lap_count)
    
    def get_speed_kmh(self) -> int:
        """Get speed in km/h untuk display."""
        return self.physics.get_speed_kmh()
    
    def reset(self, x: float = None, y: float = None, angle: float = None) -> None:
        """Reset motor ke posisi awal."""
        self.x = x if x is not None else self.start_x
        self.y = y if y is not None else self.start_y
        self.angle = angle if angle is not None else self.start_angle
        
        self.alive = True
        self.is_alive = True
        
        self.physics.reset()
        self.checkpoint.reset(self.x, self.y)
        self.fitness_calc.reset(self.x, self.y)
        self.radar.radars.clear()
    
    # =================================================================
    # PLAYER INPUT
    # =================================================================
    
    def handle_input(self, keys) -> None:
        """Handle keyboard input untuk player."""
        # Jika sedang respawning (stun), blokir input
        if self.respawning:
            return
        
        # Acceleration/braking
        if keys[pygame.K_w]:
            self.physics.apply_acceleration(1.0)
        elif keys[pygame.K_s]:
            self.physics.apply_acceleration(-1.0)
        else:
            self.physics.apply_acceleration(0)
        
        # Steering
        steering = 0
        if keys[pygame.K_a]:
            steering = -1
        elif keys[pygame.K_d]:
            steering = 1
        
        # Drift
        is_drift = keys[pygame.K_SPACE] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        angle_change = self.physics.apply_steering(steering, is_drift)
        self.angle += angle_change
    
    # =================================================================
    # UPDATE
    # =================================================================
    
    def update(self, walls=None) -> None:
        """Update motor position dan state."""
        if not self.alive:
            return
        
        # Update respawn timer
        if self.respawning:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.respawning = False
                self.respawn_timer = 0
            return  # Skip movement update saat respawning
        
        prev_x, prev_y = self.x, self.y
        prev_angle = self.angle
        
        # Calculate movement
        dx, dy = self.physics.calculate_movement(self.angle)
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Animation update
        if abs(self.velocity) > 0.1 and self.use_sprite:
            self.animation_counter += abs(self.velocity) * self.animation_speed
            if self.animation_counter >= 1:
                self.animation_counter = 0
                self.current_frame = (self.current_frame + 1) % self.total_frames
        
        # =================================================================
        # COLLISION DETECTION
        # =================================================================
        
        collided = False
        
        if self.track is not None:
            # Track-based collision
            if self.collision.check_track_collision(new_x, new_y):
                collided = True
                # Try X only
                if not self.collision.check_track_collision(new_x, self.y):
                    self.x = new_x
                # Try Y only
                elif not self.collision.check_track_collision(self.x, new_y):
                    self.y = new_y
                else:
                    self.physics.state.velocity *= 0.5
            else:
                self.x, self.y = new_x, new_y
                
        elif self.masking_surface is not None:
            # Masking-based collision
            self.x, self.y = new_x, new_y
            result = self.collision.check_masking_collision(self.x, self.y, self.angle)
            
            if result['out_of_bounds']:
                if not self.invincible:
                    self.alive = False
                    self.is_alive = False
                else:
                    self.x, self.y = prev_x, prev_y
                    self.physics.state.velocity *= -0.3
                collided = True
                
            elif result['collided']:
                # Wall collision
                if abs(self.velocity) > self.physics.config.wall_explode_speed:
                    if not self.invincible:
                        self.alive = False
                        self.is_alive = False
                    else:
                        # Respawn mundur berdasarkan angle
                        respawn_distance = 150
                        # Mundur = arah berlawanan dari angle
                        self.x = prev_x - math.cos(self.angle) * respawn_distance
                        self.y = prev_y - math.sin(self.angle) * respawn_distance
                        self.physics.state.velocity = 0  # Reset velocity
                        # Aktifkan respawn state (stun + blink)
                        self.respawning = True
                        self.respawn_timer = self.respawn_duration
                else:
                    self.physics.state.velocity *= -0.4
                    self.x, self.y = prev_x, prev_y
                collided = True
                
            elif result['slow_zone']:
                self.physics.state.velocity *= 0.99
                
            elif result['checkpoint'] > 0:
                # Process checkpoint
                cp_valid = self.checkpoint.process_checkpoint(
                    self.x, self.y, 
                    result['checkpoint'],
                    self.time_spent
                )
                if cp_valid:
                    print(f"[CP OK] CP{result['checkpoint']} passed! Count: {self.checkpoint_count}/4")
            else:
                self.checkpoint.clear_checkpoint_flag()
                
        elif self.track_surface is not None:
            # Legacy surface collision
            self.x, self.y = new_x, new_y
            result = self.collision.check_masking_collision(self.x, self.y, self.angle)
            if result['collided'] or result['out_of_bounds']:
                if not self.invincible:
                    self.alive = False
                    self.is_alive = False
                else:
                    self.physics.state.velocity *= 0.945
                collided = True
        else:
            self.x, self.y = new_x, new_y
        
        # =================================================================
        # AI TRACKING
        # =================================================================
        
        # Update fitness calculator
        angle_change = self.angle - prev_angle
        self.fitness_calc.update(self.x, self.y, angle_change)
        
        # Check lap
        lap_result = self.checkpoint.check_lap(
            self.x, self.y, 
            self.time_spent,
            self.invincible,
            "AI"
        )
        if lap_result['should_die']:
            self.alive = False
            self.is_alive = False
        
        # Update radar
        surface = self.collision.get_surface_for_radar()
        if surface is not None:
            self.radar.update(self.x, self.y, self.angle, surface)
        
        # Stuck detection (AI only)
        if self.fitness_calc.is_stuck(30) and not self.invincible:
            self.alive = False
            self.is_alive = False
        
        # Sync alias
        self.is_alive = self.alive
    
    # =================================================================
    # DRAWING
    # =================================================================
    
    def draw(self, screen, camera_or_x, camera_y: int = None) -> None:
        """Render motor."""
        # Skip render saat respawn blink (kelap-kelip)
        if self.respawning:
            # Blink: visible setiap setengah interval
            if (self.respawn_timer // self.blink_interval) % 2 == 0:
                return  # Skip render = invisible
        
        if camera_y is not None:
            cam_x, cam_y = camera_or_x, camera_y
        else:
            cam_x, cam_y = camera_or_x.x, camera_or_x.y
        
        if self.use_sprite:
            current_surface = self.frames[self.current_frame]
        else:
            current_surface = self.surface
        
        rotated = pygame.transform.rotate(current_surface, -math.degrees(self.angle))
        rect = rotated.get_rect(center=(self.x - cam_x, self.y - cam_y))
        screen.blit(rotated, rect)
        
        self.rect = rect
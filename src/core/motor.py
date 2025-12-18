
import pygame
import math
import os
from typing import Optional, List, Tuple

from core.physics import PhysicsConfig, PhysicsEngine
from core.collision import CollisionHandler
from core.checkpoint import CheckpointTracker
from core.radar import Radar, FitnessCalculator, RadarConfig

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

class Motor:
    def __init__(self, x: float, y: float, color: str = "pink"):
        # Position
        self.x = x
        self.y = y
        self.angle = 0
        self.color = color
        
        # Dimensions
        self.length = 140 // 1.5
        self.width = 80//1.5
        
        # [AUDIO STATE]
        self.snd_gas = None
        self.snd_idle = None
        self.chan_gas = None
        self.chan_idle = None
        
        self.target_gas_vol = 0.0
        self.current_gas_vol = 0.0
        self.fade_speed = 0.05 
        
        # Modules
        self.physics = PhysicsEngine(PhysicsConfig(length=self.length, width=self.width))
        self.collision = CollisionHandler(length=self.length, width=self.width)
        self.checkpoint = CheckpointTracker(start_x=x, start_y=y)
        self.radar = Radar(RadarConfig())
        self.fitness_calc = FitnessCalculator(start_x=x, start_y=y)
        
        # Sprite Setup (Single Image)
        self.frames: List[pygame.Surface] = []
        self.current_frame = 0
        self.use_sprite = False
        self.surface = None
        self.total_frames = 0
        
        self._load_single_sprite(color)
        
        # State
        self.alive = True
        self.is_alive = True
        self.invincible = False
        self.start_x = x
        self.start_y = y
        self.start_angle = 0
        self.steering_input = 0
        
        # Respawn state (untuk animasi kelap-kelip dan stun)
        self.respawning = False
        self.respawn_timer = 0  # Frame counter untuk stun
        self.respawn_duration = 60  # 1 detik = 60 frame (60 FPS)
        self.blink_interval = 6  # Kelap-kelip setiap 6 frame
        
        self.track = None
        self.track_surface = None
        self.masking_surface = None
        self.rect = None
    
    def _load_single_sprite(self, color: str) -> None:
        """
        Load SATU gambar saja (misal: pink.png).
        Tidak ada loop animasi.
        """
        self.frames = []
        self.use_sprite = False
        
        # Path: assets/motor/pink.png
        sprite_path = os.path.join(ASSETS_DIR, "motor", f"{color}.png")
        
        if os.path.exists(sprite_path):
            try:
                # Load & Process
                frame = pygame.image.load(sprite_path).convert_alpha()
                rotated = pygame.transform.rotate(frame, -90) # Sesuaikan rotasi asli asset
                scaled = pygame.transform.scale(rotated, (self.length, self.width))
                
                self.frames.append(scaled)
                self.use_sprite = True
                self.total_frames = 1
            except Exception as e:
                print(f"[ERROR] Gagal load sprite {color}: {e}")
        else:
            print(f"[WARN] Sprite tidak ditemukan: {sprite_path}")
            
        # Fallback jika gagal load
        if not self.use_sprite:
            self.surface = pygame.Surface((self.length, self.width), pygame.SRCALPHA)
            self.surface.fill((255, 0, 255)) # Magenta kotak
    
    def configure_sounds(self, gas_sound, idle_sound):
        self.snd_gas = gas_sound
        self.snd_idle = idle_sound

    def start_engine(self):
        if self.snd_gas and self.snd_idle:
            self.chan_gas = self.snd_gas.play(loops=-1)
            self.chan_idle = self.snd_idle.play(loops=-1)
            
            # Start: Idle Nyala, Gas Mati
            if self.chan_gas: self.chan_gas.set_volume(0.0)
            if self.chan_idle: self.chan_idle.set_volume(1.0)

    def stop_all_sounds(self):
        if self.snd_gas: self.snd_gas.stop()
        if self.snd_idle: self.snd_idle.stop()
        self.chan_gas = None
        self.chan_idle = None

    def update_audio(self):
        if not self.chan_gas or not self.chan_idle: return

        # Smooth transition (Lerp)
        if self.current_gas_vol < self.target_gas_vol:
            self.current_gas_vol += self.fade_speed
            if self.current_gas_vol > 1.0: self.current_gas_vol = 1.0
        elif self.current_gas_vol > self.target_gas_vol:
            self.current_gas_vol -= self.fade_speed
            if self.current_gas_vol < 0.0: self.current_gas_vol = 0.0

        self.chan_gas.set_volume(self.current_gas_vol)
        self.chan_idle.set_volume(1.0 - self.current_gas_vol)
    
    def handle_input(self, keys) -> None:
        """Handle keyboard input untuk player."""
        # Jika sedang respawning (stun), blokir input
        if self.respawning:
            return
        
        # Acceleration/braking
        if keys[pygame.K_w]:
            self.physics.apply_acceleration(1.0)
            self.target_gas_vol = 1.0
        elif keys[pygame.K_s]:
            self.physics.apply_acceleration(-1.0)
            self.target_gas_vol = 0.0
        else:
            self.physics.apply_acceleration(0)
            self.target_gas_vol = 0.0
        
        # Steering
        steering = 0
        if keys[pygame.K_a]: steering = -1
        elif keys[pygame.K_d]: steering = 1
        
        # Drift
        is_drift = keys[pygame.K_SPACE] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        angle_change = self.physics.apply_steering(steering, is_drift)
        self.angle += angle_change
    
    def update(self, walls=None) -> None:
        if not self.alive: return
        
        self.update_audio()
        
        # Update respawn timer
        if self.respawning:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.respawning = False
                self.respawn_timer = 0
            return  # Skip movement update saat respawning
        
        prev_x, prev_y = self.x, self.y
        prev_angle = self.angle
        
        dx, dy = self.physics.calculate_movement(self.angle)
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Collision Logic
        collided = False
        if self.track is not None:
             if self.collision.check_track_collision(new_x, new_y):
                collided = True
                if not self.collision.check_track_collision(new_x, self.y): self.x = new_x
                elif not self.collision.check_track_collision(self.x, new_y): self.y = new_y
                else: self.physics.state.velocity *= 0.5
             else: self.x, self.y = new_x, new_y
        elif self.masking_surface is not None:
            self.x, self.y = new_x, new_y
            result = self.collision.check_masking_collision(self.x, self.y, self.angle)
            if result['out_of_bounds']:
                if not self.invincible: self.alive = False; self.is_alive = False
                else: self.x, self.y = prev_x, prev_y; self.physics.state.velocity *= -0.3
            elif result['collided']:
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
                self.checkpoint.process_checkpoint(self.x, self.y, result['checkpoint'], self.time_spent)
            else: self.checkpoint.clear_checkpoint_flag()
        else: self.x, self.y = new_x, new_y
        
        # AI Update
        self.fitness_calc.update(self.x, self.y, self.angle - prev_angle)
        lap_result = self.checkpoint.check_lap(self.x, self.y, self.time_spent, self.invincible, "AI")
        if lap_result['should_die']: self.alive = False; self.is_alive = False
        
        surface = self.collision.get_surface_for_radar()
        if surface: self.radar.update(self.x, self.y, self.angle, surface)
        if self.fitness_calc.is_stuck(30) and not self.invincible: self.alive = False; self.is_alive = False
        self.is_alive = self.alive

    def reset(self, x: float = None, y: float = None, angle: float = None) -> None:
        self.x = x if x is not None else self.start_x
        self.y = y if y is not None else self.start_y
        self.angle = angle if angle is not None else self.start_angle
        self.alive = True; self.is_alive = True
        self.physics.reset()
        self.checkpoint.reset(self.x, self.y)
        self.fitness_calc.reset(self.x, self.y)
        self.radar.radars.clear()
        self.stop_all_sounds()
        self.start_engine()
    
    @property
    def velocity(self) -> float: return self.physics.state.velocity
    
    @velocity.setter
    def velocity(self, value: float): self.physics.state.velocity = value
    
    @property
    def distance_traveled(self) -> float: return self.fitness_calc.state.distance_traveled
    
    @distance_traveled.setter
    def distance_traveled(self, value: float): self.fitness_calc.state.distance_traveled = value
    
    @property
    def lap_count(self) -> int: return self.checkpoint.state.lap_count
    
    @lap_count.setter
    def lap_count(self, value: int): self.checkpoint.state.lap_count = value
    
    @property
    def checkpoint_count(self) -> int: return self.checkpoint.state.checkpoint_count
    
    @checkpoint_count.setter
    def checkpoint_count(self, value: int): self.checkpoint.state.checkpoint_count = value
    
    @property
    def time_spent(self) -> int: return self.fitness_calc.state.time_spent
    
    @time_spent.setter
    def time_spent(self, value: int): self.fitness_calc.state.time_spent = value
    
    @property
    def last_checkpoint_time(self) -> int: return self.checkpoint.state.last_checkpoint_time
    
    @last_checkpoint_time.setter
    def last_checkpoint_time(self, value: int): self.checkpoint.state.last_checkpoint_time = value
    
    @property
    def max_speed(self) -> float: return self.physics.config.max_speed
    @property
    def radars(self) -> List: return self.radar.radars
    @property
    def drift_angle(self) -> float: return self.physics.state.drift_angle
    @property
    def is_drifting(self) -> bool: return self.physics.state.is_drifting
    @property
    def total_rotation(self) -> float: return self.fitness_calc.state.total_rotation
    @property
    def expected_checkpoint(self) -> int: return self.checkpoint.state.expected_checkpoint
    @property
    def on_checkpoint(self) -> bool: return self.checkpoint.state.on_checkpoint

    def set_track(self, t): self.track = t; self.collision.set_track(t); 
    def set_track_surface(self, s): self.track_surface = s; self.collision.set_track_surface(s)
    def set_masking_surface(self, s): self.masking_surface = s; self.collision.set_masking_surface(s)
    def get_state(self): return (self.x, self.y, self.angle, self.velocity, self.alive)
    def get_radar_data(self): return self.radar.get_data()
    def get_speed_kmh(self): return self.physics.get_speed_kmh()
    def set_ai_input(self, s, t): 
        self.steering_input = max(-1, min(1, s))
        self.physics.apply_acceleration(t)
        self.angle += self.physics.apply_steering(self.steering_input)

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
        
        if self.use_sprite and self.frames:
            current_surface = self.frames[0]
        else:
            current_surface = self.surface
        
        rotated = pygame.transform.rotate(current_surface, -math.degrees(self.angle))
        rect = rotated.get_rect(center=(self.x - cam_x, self.y - cam_y))
        screen.blit(rotated, rect)
        self.rect = rect
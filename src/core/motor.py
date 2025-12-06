import pygame
import math
import os
from typing import Optional, List, Tuple
from core.distance_sensor import DistanceSensor


# Naik 2 level dari src/object/ ke root project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


class Motor:
    def __init__(self, x, y, color="pink"):
        """
        Inisialisasi Motor dengan sprite sheet animation vertikal
        Args:
            x, y: posisi awal
            color: nama warna motor (nama file sprite sheet)
        """
        self.x = x
        self.y = y
        self.angle = 0
        self.velocity = 0
        self.color = color

        # konstanta fisika
        self.acceleration_rate = 0.56  # 30% lebih lambat (0.8 * 0.7)
        self.friction = 0.98
        self.steering_rate = 3  # derajat per frame
        self.max_speed = 2.8  # 30% lebih lambat (4 * 0.7)
        self.length = 92  # 15% lebih besar (80 * 1.15)
        self.width = 46   # 15% lebih besar (40 * 1.15)
        
        # drift mechanics
        self.drift_angle = 0  # sudut drift saat ini
        self.is_drifting = False
        self.drift_direction = 0

        # sprite animation
        self.current_frame = 0
        self.animation_speed = 0.15  # kecepatan animasi
        self.animation_counter = 0
        
        # load sprite frames (pink-1.png, pink-2.png, pink-3.png)
        self.frames = []
        self.total_frames = 0
        
        # Coba load frame dari pink-1, pink-2, pink-3, dst
        frame_index = 1
        while True:
            frame_path = os.path.join(ASSETS_DIR, "motor", f"{color}-{frame_index}.png")
            if os.path.exists(frame_path):
                frame = pygame.image.load(frame_path).convert_alpha()
                # Rotasi 90 derajat searah jarum jam agar sprite menghadap ke kanan (arah default)
                rotated_frame = pygame.transform.rotate(frame, -90)
                scaled_frame = pygame.transform.scale(rotated_frame, (self.length, self.width))
                self.frames.append(scaled_frame)
                self.total_frames += 1
                frame_index += 1
            else:
                break
        
        if self.total_frames > 0:
            self.use_sprite = True
        else:
            # fallback ke surface berwarna jika sprite tidak ada
            self.surface = pygame.Surface((self.length, self.width), pygame.SRCALPHA)
            self.surface.fill((255, 192, 203))  # pink default
            self.use_sprite = False
        
        self.input_offset = 0
        self.steering_input = 0
        
        # Track reference untuk collision
        self.track = None
        
        # Sensor untuk AI (composition pattern)
        self.sensor: Optional[DistanceSensor] = None
        
        # Status untuk AI/RL
        self.alive = True
        self.distance_traveled = 0

    def set_track(self, track):
        """Set track untuk collision detection berbasis pixel"""
        self.track = track
        # Update sensor track juga jika ada
        if self.sensor is not None:
            self.sensor.set_track(track)
    
    def set_sensor(self, sensor: DistanceSensor):
        """
        Attach sensor ke motor (composition pattern)
        Args:
            sensor: DistanceSensor instance
        """
        self.sensor = sensor
        # Sync track ke sensor
        if self.track is not None:
            self.sensor.set_track(self.track)
    
    def create_sensor(self, num_sensors: int = 5, fov: float = 180, max_distance: float = 200) -> DistanceSensor:
        """
        Buat dan attach sensor baru ke motor
        Args:
            num_sensors: jumlah sensor
            fov: field of view dalam derajat
            max_distance: jarak maksimum sensor
        Returns:
            DistanceSensor yang sudah di-attach
        """
        sensor = DistanceSensor(num_sensors, fov, max_distance)
        self.set_sensor(sensor)
        return sensor
    
    def set_ai_input(self, steering: float, throttle: float):
        """
        Input dari AI/NEAT controller
        Args:
            steering: -1 (kiri) sampai 1 (kanan)
            throttle: -1 (mundur) sampai 1 (maju)
        """
        self.steering_input = max(-1, min(1, steering))
        throttle = max(-1, min(1, throttle))
        
        if throttle > 0:
            self.velocity += self.acceleration_rate * throttle
        elif throttle < 0:
            self.velocity += self.acceleration_rate * throttle
        else:
            self.velocity *= self.friction
            
        self.velocity = max(-self.max_speed, min(self.max_speed, self.velocity))
        
        # Apply steering
        if abs(self.velocity) > 0.1:
            steering_factor = self.velocity / self.max_speed
            self.angle += math.radians(self.steering_rate) * self.steering_input * abs(steering_factor)
    
    def get_sensor_data(self, num_sensors: int = 5, fov: float = 180, max_distance: float = 200) -> List[float]:
        """
        Dapatkan data sensor untuk AI input
        Args:
            num_sensors: jumlah sensor (dipakai jika sensor belum ada)
            fov: field of view dalam derajat
            max_distance: jarak maksimum sensor
        Returns:
            List jarak ternormalisasi (0-1) untuk setiap sensor
        """
        # Auto-create sensor jika belum ada
        if self.sensor is None:
            self.create_sensor(num_sensors, fov, max_distance)
        
        # Update sensor dengan posisi dan sudut motor saat ini
        self.sensor.update(self.x, self.y, self.angle)
        
        return self.sensor.get_normalized()
    
    def draw_sensors(self, screen, camera):
        """
        Gambar visualisasi sensor (delegate ke DistanceSensor)
        """
        if self.sensor is not None:
            self.sensor.draw(screen, camera, self.x, self.y, self.angle)
    
    def get_state(self) -> Tuple[float, float, float, float, bool]:
        """
        Dapatkan state motor untuk AI
        Returns:
            (x, y, angle, velocity, alive)
        """
        return (self.x, self.y, self.angle, self.velocity, self.alive)
    
    def reset(self, x: float, y: float, angle: float = 0):
        """Reset motor ke posisi awal"""
        self.x = x
        self.y = y
        self.angle = angle
        self.velocity = 0
        self.alive = True
        self.distance_traveled = 0
        self.drift_angle = 0
        self.is_drifting = False

    def handle_input(self, keys):
        """Kendali manual player dengan kontrol relatif dan drift (standard racing game)"""
        # W/S untuk gas/rem
        if keys[pygame.K_w]:
            self.velocity += self.acceleration_rate
        elif keys[pygame.K_s]:
            self.velocity -= self.acceleration_rate
        else:
            self.velocity *= self.friction

        self.velocity = max(-self.max_speed, min(self.max_speed, self.velocity))

        # A/D untuk steering
        self.steering_input = 0
        if keys[pygame.K_a]:
            self.steering_input = -1
        elif keys[pygame.K_d]:
            self.steering_input = 1

        # Drift dengan Space atau Shift
        self.is_drifting = keys[pygame.K_SPACE] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        if abs(self.velocity) > 0.1:
            if self.is_drifting and self.steering_input != 0:
                # Mode drift - steering lebih tajam dan ada slide
                self.drift_direction = self.steering_input
                drift_steer_rate = self.steering_rate * 1.8  # 80% lebih tajam saat drift
                self.angle += math.radians(drift_steer_rate) * self.steering_input
                
                # Build up drift angle
                max_drift = 0.4  # max drift angle in radians
                self.drift_angle += self.steering_input * 0.05
                self.drift_angle = max(-max_drift, min(max_drift, self.drift_angle))
            else:
                # Normal steering
                steering_factor = self.velocity / self.max_speed
                self.angle += math.radians(self.steering_rate) * self.steering_input * abs(steering_factor)
                
                # Decay drift angle
                self.drift_angle *= 0.9

    def update(self, walls=None):
        """Update posisi + deteksi tabrakan dengan drift mechanics
        
        Args:
            walls: Legacy parameter untuk rect walls (optional)
                   Jika track sudah di-set, pakai pixel collision
        """
        if not self.alive:
            return
            
        prev_x, prev_y = self.x, self.y

        # Hitung movement angle dengan drift
        if self.is_drifting:
            # Saat drift, motor meluncur dengan angle yang berbeda dari arah hadap
            move_angle = self.angle + self.drift_angle
        else:
            # Normal movement
            move_angle = self.angle

        new_x = self.x + math.cos(move_angle) * self.velocity
        new_y = self.y + math.sin(move_angle) * self.velocity

        # update animasi berdasarkan kecepatan
        if abs(self.velocity) > 0.1 and self.use_sprite:
            self.animation_counter += abs(self.velocity) * self.animation_speed
            if self.animation_counter >= 1:
                self.animation_counter = 0
                self.current_frame = (self.current_frame + 1) % self.total_frames
        
        # Collision detection
        collided = False
        
        # Prioritas 1: Pixel-based collision dari Track
        if self.track is not None:
            # Check collision dengan pixel di posisi baru
            # Pakai collision box yang lebih kecil untuk akurasi
            collision_size = min(self.length, self.width) * 0.6
            
            if self.track.check_collision(new_x, new_y, collision_size, collision_size):
                collided = True
                # Coba gerak hanya X
                if not self.track.check_collision(new_x, self.y, collision_size, collision_size):
                    self.x = new_x
                # Coba gerak hanya Y
                elif not self.track.check_collision(self.x, new_y, collision_size, collision_size):
                    self.y = new_y
                # Tidak bisa gerak sama sekali
                else:
                    # AI mati kalau nabrak
                    self.velocity *= 0.5
                    # Uncomment line di bawah untuk mode training ketat
                    # self.alive = False
            else:
                self.x = new_x
                self.y = new_y
        
        # Prioritas 2: Legacy rect-based collision
        elif walls is not None:
            self.x = new_x
            self.y = new_y
            
            # dapatkan surface saat ini
            if self.use_sprite:
                current_surface = self.frames[self.current_frame]
            else:
                current_surface = self.surface
                
            rotated_motor = pygame.transform.rotate(current_surface, -math.degrees(self.angle))
            self.rect = rotated_motor.get_rect(center=(self.x, self.y))
            
            for wall in walls:
                if self.rect.colliderect(wall):
                    collided = True
                    # Slide along wall instead of stopping
                    overlap_left = self.rect.right - wall.left
                    overlap_right = wall.right - self.rect.left
                    overlap_top = self.rect.bottom - wall.top
                    overlap_bottom = wall.bottom - self.rect.top
                    
                    min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                    
                    if min_overlap == overlap_left:
                        self.x -= overlap_left
                    elif min_overlap == overlap_right:
                        self.x += overlap_right
                    elif min_overlap == overlap_top:
                        self.y -= overlap_top
                    elif min_overlap == overlap_bottom:
                        self.y += overlap_bottom
                    
                    # Update rect position
                    self.rect.center = (self.x, self.y)
                    
                    # Reduce velocity when hitting wall
                    self.velocity *= 0.7
                    break
        else:
            # Tidak ada collision, langsung update posisi
            self.x = new_x
            self.y = new_y
        
         # Update distance traveled (untuk fitness AI)
        if not collided:
            distance = math.sqrt((self.x - prev_x)**2 + (self.y - prev_y)**2)
            self.distance_traveled += distance
       
        # Update rect untuk drawing
        if self.use_sprite:
            current_surface = self.frames[self.current_frame]
        else:
            current_surface = self.surface
        rotated_motor = pygame.transform.rotate(current_surface, -math.degrees(self.angle))
        self.rect = rotated_motor.get_rect(center=(self.x, self.y))

    def draw(self, screen, camera):
        """Render motor dengan animasi"""
        # pilih frame saat ini
        if self.use_sprite:
            current_surface = self.frames[self.current_frame]
        else:
            current_surface = self.surface
        
        # rotasi dan render dengan offset kamera
        rotated_motor = pygame.transform.rotate(current_surface, -math.degrees(self.angle))
        rect = rotated_motor.get_rect(center=(self.x - camera.x, self.y - camera.y))
        screen.blit(rotated_motor, rect)
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
        self.max_speed = 12  # 30% lebih lambat (4 * 0.7)
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
        
        # Track reference untuk collision (Track object atau pygame.Surface)
        self.track = None
        self.track_surface = None  # Direct pygame.Surface for pixel collision
        
        # Sensor untuk AI (composition pattern)
        self.sensor: Optional[DistanceSensor] = None
        
        # Status untuk AI/RL
        self.alive = True
        self.distance_traveled = 0
        
        # Lap counting (untuk racing mode)
        self.start_x = x
        self.start_y = y
        self.start_angle = 0
        self.lap_count = 0
        self.total_rotation = 0
        self.has_left_start = False
        self.lap_cooldown = 0
        
        # AI Radar System (built-in, no external sensor needed)
        self.radars: List[Tuple[Tuple[int, int], int]] = []
        self.num_radars = 5
        self.radar_angles = [-90, -45, 0, 45, 90]  # Derajat relatif ke arah hadap
        self.max_radar_length = 300
        
        # AI Fitness tracking
        self.time_spent = 0
        self.unique_positions = set()
        self.last_grid_pos = None
        self.consecutive_same_pos = 0
        self.max_distance_reached = 0
        self.prev_x = x
        self.prev_y = y
        self.stuck_timer = 0
        self.collision_count = 0
        
        # Compatibility alias
        self.is_alive = self.alive  # For backward compatibility with AICar code
        
        # Invincible mode (untuk player - tidak mati kalau keluar track)
        self.invincible = False

    def set_track(self, track):
        """Set track untuk collision detection berbasis pixel"""
        self.track = track
        # Update sensor track juga jika ada
        if self.sensor is not None:
            self.sensor.set_track(track)
    
    def set_track_surface(self, surface: pygame.Surface):
        """Set pygame.Surface langsung untuk collision detection (alternatif dari Track object)"""
        self.track_surface = surface
    
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
    
    def reset(self, x: float = None, y: float = None, angle: float = None):
        """Reset motor ke posisi awal"""
        self.x = x if x is not None else self.start_x
        self.y = y if y is not None else self.start_y
        self.angle = angle if angle is not None else self.start_angle
        self.velocity = 0
        self.alive = True
        self.is_alive = True  # Sync alias
        self.distance_traveled = 0
        self.drift_angle = 0
        self.is_drifting = False
        # Reset lap counting
        self.lap_count = 0
        self.total_rotation = 0
        self.has_left_start = False
        self.lap_cooldown = 0
        # Reset AI tracking
        self.time_spent = 0
        self.unique_positions.clear()
        self.consecutive_same_pos = 0
        self.max_distance_reached = 0
        self.stuck_timer = 0
        self.collision_count = 0
        self.radars.clear()
    
    def steer(self, direction: int):
        """
        Belokkan motor (untuk AI control).
        Kompatibel dengan model AI yang sudah di-train dengan AICar.
        
        Args:
            direction: -1 (kanan), 0 (lurus), 1 (kiri)
        """
        prev_angle = self.angle
        steer_amount = math.radians(7)  # ~7 derajat per frame
        
        # Arah terbalik dari handle_input karena AI model di-train dengan AICar
        # yang punya sistem koordinat berbeda
        if direction == 1:
            self.angle -= steer_amount  # Belok kiri di sistem AICar
        elif direction == -1:
            self.angle += steer_amount  # Belok kanan di sistem AICar
        # direction == 0: lurus
        
        # Track rotation untuk lap detection
        angle_change = abs(self.angle - prev_angle)
        self.total_rotation += math.degrees(angle_change)
    
    def _update_radars(self, track_surface: pygame.Surface):
        """Update sensor radar (built-in, tanpa DistanceSensor)
        
        Kompatibel dengan AICar yang pakai sistem 360-angle
        """
        self.radars.clear()
        
        # Convert angle dari radians ke degrees
        # Gunakan sistem 360-angle seperti AICar untuk kompatibilitas
        angle_deg = 360 - math.degrees(self.angle)
        
        for degree in self.radar_angles:
            length = 0
            x = int(self.x)
            y = int(self.y)
            
            # Raycast sampai ketemu batas atau max length
            while length < self.max_radar_length:
                # Hitung posisi titik radar (pakai sistem 360-angle)
                radar_angle = math.radians(360 - (angle_deg + degree))
                x = int(self.x + math.cos(radar_angle) * length)
                y = int(self.y + math.sin(radar_angle) * length)
                
                try:
                    if x < 0 or x >= track_surface.get_width() or \
                       y < 0 or y >= track_surface.get_height():
                        break
                    
                    pixel = track_surface.get_at((x, y))
                    r, g, b = pixel[0], pixel[1], pixel[2]
                    
                    # Check jika pixel adalah jalan
                    is_black = (r < 120 and g < 120 and b < 120)
                    is_white = (r > 100 and g > 100 and b > 100)
                    is_red = (r > 150 and g < 100 and b < 100)
                    
                    if not (is_black or is_white or is_red):
                        break
                except:
                    break
                
                length += 5  # Step 5 pixel untuk performa
            
            dist = int(math.sqrt((x - self.x)**2 + (y - self.y)**2))
            self.radars.append(((x, y), dist))
    
    def get_radar_data(self) -> List[int]:
        """
        Get normalized radar data untuk neural network.
        
        Returns:
            List of 5 values (0-10 scale)
        """
        data = [0] * self.num_radars
        for i, radar in enumerate(self.radars):
            if i < len(data):
                data[i] = int(radar[1] / 30)  # Normalize to 0-10 range
        return data
    
    def get_fitness(self) -> float:
        """
        Calculate fitness score untuk AI training.
        
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
            distance_reward = self.distance_traveled / 50.0
            repetition_penalty = self.consecutive_same_pos * -20
            
            return base_reward + rotation_reward + distance_reward + repetition_penalty
        
        # Sudah complete lap: optimize
        else:
            lap_bonus = (self.lap_count ** 2) * 1000
            efficiency = self.distance_traveled / max(self.time_spent, 1)
            efficiency_bonus = efficiency * 50
            novelty_bonus = len(self.unique_positions) * 3
            
            return lap_bonus + efficiency_bonus + novelty_bonus
    
    def get_speed_kmh(self) -> int:
        """Get current speed in km/h for speedometer display"""
        # Convert internal velocity to km/h (scale factor for display)
        return int(abs(self.velocity) * 15)  # Scale factor for display
    
    def _get_collision_corners(self) -> List[tuple]:
        """Get 4 corner points of motor for collision detection"""
        length, width = self.length * 0.4, self.width * 0.4  # Smaller hitbox
        
        corners = []
        for dx, dy in [(-length/2, -width/2), (length/2, -width/2), 
                       (length/2, width/2), (-length/2, width/2)]:
            rx = dx * math.cos(self.angle) - dy * math.sin(self.angle)
            ry = dx * math.sin(self.angle) + dy * math.cos(self.angle)
            corners.append((self.x + rx, self.y + ry))
        
        return corners
    
    def _check_lap(self):
        """Check lap completion"""
        if self.lap_cooldown > 0:
            self.lap_cooldown -= 1
            return
        
        dist_from_start = math.sqrt(
            (self.x - self.start_x)**2 + 
            (self.y - self.start_y)**2
        )
        
        if dist_from_start > 300:
            self.has_left_start = True
        elif self.has_left_start and dist_from_start < 80:
            if self.total_rotation >= 300:
                self.lap_count += 1
                print(f"[PLAYER] Lap {self.lap_count} completed!")
                self.lap_cooldown = 60
            self.has_left_start = False
            self.total_rotation = 0

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
        
        # Prioritas 1: Pixel-based collision dari Track object
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
        
        # Prioritas 2: Pixel-based collision dari pygame.Surface langsung
        elif self.track_surface is not None:
            self.x = new_x
            self.y = new_y
            
            # Check collision di 4 sudut motor
            corners = self._get_collision_corners()
            for corner in corners:
                cx, cy = int(corner[0]), int(corner[1])
                
                # Boundary check
                if cx < 0 or cx >= self.track_surface.get_width() or \
                   cy < 0 or cy >= self.track_surface.get_height():
                    if not self.invincible:
                        self.alive = False
                    collided = True
                    break
                
                # Color check - hitam = track, putih/merah = finish
                color = self.track_surface.get_at((cx, cy))
                r, g, b = color[0], color[1], color[2]
                
                # Widen range to handle antialiasing (gray pixels)
                is_black = (r < 120 and g < 120 and b < 120)
                is_white = (r > 100 and g > 100 and b > 100)
                is_red = (r > 150 and g < 100 and b < 100)
                
                if not (is_black or is_white or is_red):
                    if not self.invincible:
                        self.alive = False
                    else:
                        # Speed penalty untuk invincible player
                        self.velocity *= 0.915
                    collided = True
                    break
        
        # Prioritas 3: Legacy rect-based collision
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
        
        # Track rotation untuk lap detection
        prev_angle_deg = math.degrees(prev_angle) if 'prev_angle' in dir() else 0
        angle_diff = math.degrees(self.angle) - prev_angle_deg
        if angle_diff > 180:
            angle_diff -= 360
        elif angle_diff < -180:
            angle_diff += 360
        self.total_rotation += abs(angle_diff)
        
        # Check lap completion
        self._check_lap()
        
        # Update radars untuk AI (jika track_surface ada)
        if self.track_surface is not None:
            self._update_radars(self.track_surface)
        
        # AI tracking: time, novelty, stuck detection
        self.time_spent += 1
        self.max_distance_reached = max(self.max_distance_reached, self.distance_traveled)
        
        # Novelty tracking (grid-based)
        if self.time_spent % 10 == 0:
            grid_pos = (int(self.x / 50), int(self.y / 50))
            self.unique_positions.add(grid_pos)
            
            dist_from_start = math.sqrt(
                (self.x - self.start_x)**2 + 
                (self.y - self.start_y)**2
            )
            near_finish = dist_from_start < 120
            
            if grid_pos == self.last_grid_pos and not near_finish:
                self.consecutive_same_pos += 1
                if self.consecutive_same_pos > 5 and not self.invincible:
                    self.alive = False
                    self.is_alive = False
            else:
                self.consecutive_same_pos = 0
            
            self.last_grid_pos = grid_pos
        
        # Stuck detection
        pos_change = math.sqrt((self.x - self.prev_x)**2 + (self.y - self.prev_y)**2)
        dist_from_start = math.sqrt((self.x - self.start_x)**2 + (self.y - self.start_y)**2)
        near_finish = dist_from_start < 120
        
        if pos_change < 3 and not near_finish:
            self.stuck_timer += 1
            if self.stuck_timer > 30 and not self.invincible:
                self.alive = False
                self.is_alive = False
        else:
            self.stuck_timer = 0
        
        self.prev_x, self.prev_y = self.x, self.y
        
        # Sync is_alive alias
        self.is_alive = self.alive
       
        # Update rect untuk drawing
        if self.use_sprite:
            current_surface = self.frames[self.current_frame]
        else:
            current_surface = self.surface
        rotated_motor = pygame.transform.rotate(current_surface, -math.degrees(self.angle))
        self.rect = rotated_motor.get_rect(center=(self.x, self.y))

    def draw(self, screen, camera_or_x, camera_y: int = None):
        """Render motor dengan animasi
        
        Args:
            screen: pygame display surface
            camera_or_x: Either a camera object with .x/.y attributes, or an int for x offset
            camera_y: If camera_or_x is int, this is the y offset
        """
        # Support both camera object and offset integers
        if camera_y is not None:
            # Called as draw(screen, camera_x, camera_y)
            cam_x, cam_y = camera_or_x, camera_y
        else:
            # Called as draw(screen, camera) where camera has .x and .y
            cam_x, cam_y = camera_or_x.x, camera_or_x.y
        
        # pilih frame saat ini
        if self.use_sprite:
            current_surface = self.frames[self.current_frame]
        else:
            current_surface = self.surface
        
        # rotasi dan render dengan offset kamera
        rotated_motor = pygame.transform.rotate(current_surface, -math.degrees(self.angle))
        rect = rotated_motor.get_rect(center=(self.x - cam_x, self.y - cam_y))
        screen.blit(rotated_motor, rect)
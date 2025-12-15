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

        # =================================================================
        # REALISTIC PHYSICS CONSTANTS
        # =================================================================
        
        # Speed & Acceleration
        self.acceleration_rate = 0.12      # Akselerasi (lebih realistis)
        self.brake_power = 0.25            # Kekuatan rem
        self.friction = 0.985              # Gesekan natural (mendekati 1 = mulus)
        self.max_speed = 15                # Kecepatan maksimum
        
        # Steering - Speed Dependent
        self.base_steering_rate = 4.5      # Steering rate saat diam/lambat (derajat/frame)
        self.min_steering_rate = 1.2       # Steering rate minimal saat kecepatan max
        self.steering_rate = self.base_steering_rate  # Dynamic, akan berubah
        
        # Grip & Traction
        self.grip = 1.0                    # Grip saat ini (0.0-1.0)
        self.base_grip = 1.0               # Grip dasar
        self.turn_grip_loss = 0.15         # Kehilangan grip saat belok tajam
        self.speed_grip_factor = 0.7       # Faktor grip di kecepatan tinggi
        
        # Turn Physics
        self.turn_speed_penalty = 0.02     # Kehilangan speed saat belok
        self.sharp_turn_threshold = 0.5    # Threshold untuk belok tajam (0-1)
        self.understeer_factor = 0.3       # Seberapa besar understeer di speed tinggi
        
        # Inertia & Weight Transfer
        self.lateral_velocity = 0          # Velocity samping (untuk slide)
        self.lateral_friction = 0.92       # Gesekan lateral
        self.weight_transfer = 0           # Weight transfer saat akselerasi/rem
        
        # Dimensions
        self.length = 140
        self.width = 80
        
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
        self.masking_surface = None  # Separate masking for advanced collision
        
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
        
        # Sequential Checkpoint system (warna berbeda = urutan berbeda)
        # Hijau (0,255,0) = CP1, Cyan (0,255,255) = CP2, Kuning (255,255,0) = CP3, Magenta (255,0,255) = CP4
        self.checkpoint_count = 0  # Jumlah checkpoint yang sudah dilalui di lap ini
        self.expected_checkpoint = 1  # Checkpoint berikutnya yang harus dilalui (1-4)
        self.total_checkpoints = 4  # Total checkpoint per lap
        self.last_checkpoint_time = 0  # Frame terakhir melewati checkpoint
        self.on_checkpoint = False  # Sedang di atas checkpoint?
        self.checkpoints_for_lap = 4  # Harus lewat semua checkpoint untuk validasi lap
        self.last_checkpoint_x = x  # Posisi X saat checkpoint terakhir
        self.last_checkpoint_y = y  # Posisi Y saat checkpoint terakhir
        self.min_checkpoint_distance = 0  # Tidak perlu jarak minimal karena sudah sequential
        self.failed_lap_checks = 0  # Counter untuk failed lap attempts
        self.max_failed_lap_checks = 5  # Mati setelah 5x gagal
        
        # Lap timing
        self.lap_start_time = 0  # Frame saat lap dimulai
        self.last_lap_time = 0  # Waktu lap terakhir (frames)
        self.best_lap_time = float('inf')  # Best lap time
        
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
        
        # Collision physics thresholds
        self.wall_explode_speed = 8  # Speed di atas ini = meledak saat nabrak tembok

    def set_track(self, track):
        """Set track untuk collision detection berbasis pixel"""
        self.track = track
        # Update sensor track juga jika ada
        if self.sensor is not None:
            self.sensor.set_track(track)
    
    def set_track_surface(self, surface: pygame.Surface):
        """Set pygame.Surface langsung untuk collision detection (alternatif dari Track object)"""
        self.track_surface = surface
    
    def set_masking_surface(self, surface: pygame.Surface):
        """Set masking surface untuk advanced collision detection
        
        Masking colors:
        - Black (R,G,B < 50): Track/jalan
        - White (R,G,B > 200): Slow zone
        - Gray (50-200): Wall/tembok (bounce/explode)
        """
        self.masking_surface = surface
    
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
        # Reset checkpoint
        self.checkpoint_count = 0
        self.expected_checkpoint = 1  # Reset urutan checkpoint
        self.on_checkpoint = False
        self.last_checkpoint_x = self.start_x
        self.last_checkpoint_y = self.start_y
        self.failed_lap_checks = 0  # Reset failed lap counter
        # Reset lap timing
        self.lap_start_time = 0
        self.last_lap_time = 0
        self.best_lap_time = float('inf')
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
        Belokkan motor (untuk AI control) dengan REALISTIC PHYSICS.
        Uses same speed-dependent steering as player.
        
        Args:
            direction: -1 (kanan), 0 (lurus), 1 (kiri)
        """
        prev_angle = self.angle
        
        # Speed-dependent steering (sama dengan player)
        speed_ratio = abs(self.velocity) / self.max_speed if self.max_speed > 0 else 0
        
        # Interpolate steering rate berdasarkan speed
        current_steer_rate = self.base_steering_rate - (
            (self.base_steering_rate - self.min_steering_rate) * speed_ratio
        )
        
        # Understeer di kecepatan tinggi
        understeer = 1.0 - (speed_ratio * self.understeer_factor)
        steer_amount = math.radians(current_steer_rate) * understeer
        
        # Apply steering
        if direction == 1:
            self.angle += steer_amount  # Belok kiri
        elif direction == -1:
            self.angle -= steer_amount  # Belok kanan
        # direction == 0: lurus
        
        # Speed penalty saat belok (sama dengan player)
        if direction != 0 and abs(self.velocity) > 1:
            turn_intensity = speed_ratio
            speed_loss = self.turn_speed_penalty * turn_intensity
            self.velocity *= (1.0 - speed_loss)
        
        # Track rotation untuk lap detection
        angle_change = abs(self.angle - prev_angle)
        self.total_rotation += math.degrees(angle_change)
    
    def _update_radars(self, track_surface: pygame.Surface):
        """Update sensor radar (built-in, tanpa DistanceSensor)
        
        Kompatibel dengan AICar yang pakai sistem 360-angle
        Uses masking_surface if available, otherwise track_surface
        """
        self.radars.clear()
        
        # Gunakan masking jika ada, otherwise fallback ke track_surface
        surface_to_use = self.masking_surface if self.masking_surface is not None else track_surface
        
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
                    if x < 0 or x >= surface_to_use.get_width() or \
                       y < 0 or y >= surface_to_use.get_height():
                        break
                    
                    pixel = surface_to_use.get_at((x, y))
                    r, g, b = pixel[0], pixel[1], pixel[2]
                    avg = (r + g + b) / 3
                    
                    # Masking mode: black = track, putih/abu = slow (OK), merah = wall (stop)
                    if self.masking_surface is not None:
                        # Hanya stop di merah (wall)
                        is_red = (r > 150 and g < 100 and b < 100)
                        if is_red:
                            break
                    else:
                        # Legacy mode: color-based
                        is_gray = (abs(r - g) < 50 and abs(g - b) < 50 and abs(r - b) < 50)
                        is_white = (r > 200 and g > 200 and b > 200)
                        is_red = (r > 150 and g < 100 and b < 100)
                        is_green = (g > r + 30 and g > b + 30)
                        
                        if is_green or not (is_gray or is_white or is_red):
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
        return int(abs(self.velocity) * 7.5)  # Scale factor for display
    
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
        """Check lap completion with checkpoint validation"""
        if self.lap_cooldown > 0:
            self.lap_cooldown -= 1
            return
        
        dist_from_start = math.sqrt(
            (self.x - self.start_x)**2 + 
            (self.y - self.start_y)**2
        )
        
        # DEBUG: show distance from start periodically
        if self.time_spent % 60 == 0 and self.checkpoint_count >= 4:
            print(f"[START AREA] dist={dist_from_start:.0f}, cp={self.checkpoint_count}, has_left={self.has_left_start}")
        
        # Area thresholds
        leave_start_dist = 300  # Harus keluar 300 pixel dulu
        return_start_dist = 200  # Kembali dalam 200 pixel = finish
        
        if dist_from_start > leave_start_dist:
            self.has_left_start = True
            # Start lap timer saat pertama kali keluar dari start
            if self.lap_start_time == 0:
                self.lap_start_time = self.time_spent
                
        elif self.has_left_start and dist_from_start < return_start_dist:
            # Debug: lihat kondisi lap
            who = "PLAYER" if self.invincible else "AI"
            print(f"[LAP CHECK] {who}: checkpoints={self.checkpoint_count}/{self.checkpoints_for_lap}")
            
            # Validasi: harus lewat semua checkpoint
            if self.checkpoint_count >= self.checkpoints_for_lap:
                # Hitung lap time
                lap_time = self.time_spent - self.lap_start_time
                self.last_lap_time = lap_time
                if lap_time < self.best_lap_time:
                    self.best_lap_time = lap_time
                
                self.lap_count += 1
                lap_time_seconds = lap_time / 60.0  # Konversi ke detik (60 FPS)
                print(f"[LAP] {who} Lap {self.lap_count} completed! Time: {lap_time_seconds:.2f}s (checkpoints: {self.checkpoint_count})")
                self.lap_cooldown = 60
                
                # Reset untuk lap berikutnya
                self.checkpoint_count = 0
                self.expected_checkpoint = 1  # Reset urutan checkpoint
                self.lap_start_time = self.time_spent  # Reset timer
                self.failed_lap_checks = 0  # Reset failed counter setelah sukses
            else:
                print(f"[LAP CHECK] {who} FAILED - need {self.checkpoints_for_lap} checkpoints, got {self.checkpoint_count}")
                self.failed_lap_checks += 1
                
                # Mati setelah 5x gagal (hanya untuk AI, bukan player)
                if not self.invincible and self.failed_lap_checks >= self.max_failed_lap_checks:
                    print(f"[AI KILLED] Too many failed lap attempts ({self.failed_lap_checks})")
                    self.alive = False
                    self.is_alive = False
            self.has_left_start = False

    def handle_input(self, keys):
        """Kendali manual player dengan REALISTIC PHYSICS
        
        Features:
        - Speed-dependent steering (semakin cepat, semakin sulit belok)
        - Grip system (kehilangan grip saat belok tajam di speed tinggi)
        - Speed penalty saat belok
        - Understeer di kecepatan tinggi
        - Drift mechanics dengan handbrake
        """
        # =====================================================================
        # 1. ACCELERATION & BRAKING
        # =====================================================================
        if keys[pygame.K_w]:
            # Akselerasi - lebih lambat di speed tinggi (drag)
            speed_ratio = abs(self.velocity) / self.max_speed
            accel_modifier = 1.0 - (speed_ratio * 0.5)  # Drag effect
            self.velocity += self.acceleration_rate * accel_modifier
            self.weight_transfer = 0.3  # Weight ke belakang
        elif keys[pygame.K_s]:
            # Rem - lebih kuat dari akselerasi
            self.velocity -= self.brake_power
            self.weight_transfer = -0.5  # Weight ke depan
        else:
            self.velocity *= self.friction
            self.weight_transfer *= 0.9  # Decay weight transfer

        # Clamp velocity
        self.velocity = max(-self.max_speed * 0.5, min(self.max_speed, self.velocity))

        # =====================================================================
        # 2. SPEED-DEPENDENT STEERING RATE
        # =====================================================================
        # Semakin cepat = semakin sulit belok (realistic motorcycle/car physics)
        speed_ratio = abs(self.velocity) / self.max_speed
        
        # Interpolate steering rate: base (saat lambat) -> min (saat max speed)
        self.steering_rate = self.base_steering_rate - (
            (self.base_steering_rate - self.min_steering_rate) * speed_ratio
        )

        # =====================================================================
        # 3. STEERING INPUT
        # =====================================================================
        self.steering_input = 0
        if keys[pygame.K_a]:
            self.steering_input = -1
        elif keys[pygame.K_d]:
            self.steering_input = 1

        # Drift/Handbrake dengan Space atau Shift
        self.is_drifting = keys[pygame.K_SPACE] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        # Simpan angle sebelum berubah untuk rotation tracking
        prev_angle = self.angle

        # =====================================================================
        # 4. APPLY STEERING WITH PHYSICS
        # =====================================================================
        if abs(self.velocity) > 0.1:
            if self.is_drifting and self.steering_input != 0:
                # =============================================================
                # DRIFT MODE - Override normal physics
                # =============================================================
                self.drift_direction = self.steering_input
                
                # Drift steering lebih tajam
                drift_steer = self.base_steering_rate * 1.5
                self.angle += math.radians(drift_steer) * self.steering_input
                
                # Build up drift angle (sliding)
                max_drift = 0.5
                self.drift_angle += self.steering_input * 0.08
                self.drift_angle = max(-max_drift, min(max_drift, self.drift_angle))
                
                # Speed penalty saat drift
                self.velocity *= 0.995
                
                # Lose grip saat drift
                self.grip = max(0.3, self.grip - 0.05)
                
                # Build lateral velocity
                self.lateral_velocity += self.steering_input * 0.5
                
            else:
                # =============================================================
                # NORMAL STEERING with realistic physics
                # =============================================================
                
                # Base steering dengan speed factor
                steer_amount = math.radians(self.steering_rate) * self.steering_input
                
                # Understeer di kecepatan tinggi
                understeer = 1.0 - (speed_ratio * self.understeer_factor)
                steer_amount *= understeer
                
                # Apply steering
                self.angle += steer_amount
                
                # Speed penalty saat belok (kehilangan speed proporsional dengan sudut belok)
                if abs(self.steering_input) > 0:
                    turn_intensity = abs(self.steering_input) * speed_ratio
                    speed_loss = self.turn_speed_penalty * turn_intensity
                    self.velocity *= (1.0 - speed_loss)
                
                # Grip recovery
                self.grip = min(self.base_grip, self.grip + 0.02)
                
                # Decay drift angle saat tidak drift
                self.drift_angle *= 0.85
                
                # Decay lateral velocity
                self.lateral_velocity *= self.lateral_friction

        # =====================================================================
        # 5. LATERAL PHYSICS (sliding/inertia)
        # =====================================================================
        # Clamp lateral velocity
        max_lateral = 3.0
        self.lateral_velocity = max(-max_lateral, min(max_lateral, self.lateral_velocity))

        # =====================================================================
        # 6. GRIP EFFECTS
        # =====================================================================
        # Grip berkurang di speed tinggi saat belok
        if abs(self.steering_input) > 0 and speed_ratio > 0.6:
            grip_loss = self.turn_grip_loss * speed_ratio * abs(self.steering_input)
            self.grip = max(0.5, self.grip - grip_loss)
        
        # Track rotation untuk lap detection
        angle_diff = math.degrees(self.angle - prev_angle)
        self.total_rotation += abs(angle_diff)

    def update(self, walls=None):
        """Update posisi + deteksi tabrakan dengan drift mechanics
        
        Args:
            walls: Legacy parameter untuk rect walls (optional)
                   Jika track sudah di-set, pakai pixel collision
        """
        if not self.alive:
            return
            
        prev_x, prev_y = self.x, self.y
        prev_angle = self.angle  # Simpan angle sebelum update untuk rotation tracking

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
        
        # Prioritas 2: Masking-based collision (3 zones: black=track, white=slow, gray=wall)
        elif self.masking_surface is not None:
            self.x = new_x
            self.y = new_y
            
            # Check collision di 4 sudut motor
            corners = self._get_collision_corners()
            for corner in corners:
                cx, cy = int(corner[0]), int(corner[1])
                
                # Boundary check
                if cx < 0 or cx >= self.masking_surface.get_width() or \
                   cy < 0 or cy >= self.masking_surface.get_height():
                    if not self.invincible:
                        self.alive = False
                    else:
                        self.x, self.y = prev_x, prev_y
                        self.velocity *= -0.3
                    collided = True
                    break
                
                # Get masking color
                color = self.masking_surface.get_at((cx, cy))
                r, g, b = color[0], color[1], color[2]
                avg = (r + g + b) / 3
                
                # Zone detection:
                # - Hitam = Track OK
                # - Putih/Abu-abu = Slow zone
                # - Merah = Tembok (bounce/explode)
                # Sequential Checkpoints:
                # - Hijau murni (g>200, r<100, b<100) = CP1
                # - Cyan (g>200, b>200, r<100) = CP2
                # - Kuning (r>200, g>200, b<100) = CP3
                # - Magenta (r>200, b>200, g<100) = CP4
                
                is_black = (avg < 50)   # Track - OK
                is_red = (r > 150 and g < 100 and b < 100)  # Wall
                
                # Checkpoint colors (sequential) - RELAXED CONDITIONS
                is_cp1_green = (g > 150 and r < 150 and b < 150 and g > r and g > b)  # Greenish
                is_cp2_cyan = (g > 150 and b > 150 and r < 150)   # Cyan-ish
                is_cp3_yellow = (r > 150 and g > 150 and b < 150)  # Yellow-ish
                is_cp4_magenta = (r > 150 and b > 150 and g < 150)  # Magenta-ish
                
                is_any_checkpoint = is_cp1_green or is_cp2_cyan or is_cp3_yellow or is_cp4_magenta
                is_white_or_gray = (avg > 50 and not is_any_checkpoint and not is_red)
                
                # DEBUG: Print any unrecognized color (not black, not white, not red, not checkpoint)
                if not is_black and not is_white_or_gray and not is_red and not is_any_checkpoint:
                    print(f"[COLOR?] RGB=({r},{g},{b}) avg={avg:.0f} - NOT RECOGNIZED")
                
                if is_black:
                    # Track OK
                    self.on_checkpoint = False
                    
                elif is_any_checkpoint:
                    # Check which checkpoint and if it's the expected one
                    detected_cp = 0
                    if is_cp1_green:
                        detected_cp = 1
                    elif is_cp2_cyan:
                        detected_cp = 2
                    elif is_cp3_yellow:
                        detected_cp = 3
                    elif is_cp4_magenta:
                        detected_cp = 4
                    
                    # Jarak dari checkpoint terakhir
                    dist_from_last_cp = math.sqrt(
                        (self.x - self.last_checkpoint_x)**2 + 
                        (self.y - self.last_checkpoint_y)**2
                    )
                    
                    # DEBUG: Print semua kondisi
                    # if not self.on_checkpoint:
                    #     print(f"[CP DEBUG] RGB=({r},{g},{b}) Det=CP{detected_cp} Exp=CP{self.expected_checkpoint} Dist={dist_from_last_cp:.0f} NeedDist={self.min_checkpoint_distance}")
                    
                    # Hanya hitung jika checkpoint yang benar DAN sudah cukup jauh
                    if not self.on_checkpoint and detected_cp == self.expected_checkpoint and dist_from_last_cp >= self.min_checkpoint_distance:
                        self.checkpoint_count += 1
                        self.last_checkpoint_time = self.time_spent
                        self.last_checkpoint_x = self.x
                        self.last_checkpoint_y = self.y
                        self.on_checkpoint = True
                        
                        print(f"[CP OK] CP{detected_cp} passed! Count: {self.checkpoint_count}/4")
                        
                        # Update expected checkpoint (wrap around)
                        self.expected_checkpoint = (self.expected_checkpoint % self.total_checkpoints) + 1
                        
                    elif not self.on_checkpoint:
                        self.on_checkpoint = True
                    
                    break  # Keluar dari loop corner
                    
                elif is_white_or_gray:
                    # Slow zone - speed penalty (putih dan abu-abu)
                    self.velocity *= 0.99
                    self.on_checkpoint = False
                    collided = True
                    
                elif is_red:
                    # Wall (merah) - bounce atau explode
                    self.on_checkpoint = False
                    if abs(self.velocity) > self.wall_explode_speed:
                        # High speed = meledak
                        if not self.invincible:
                            self.alive = False
                            self.is_alive = False
                        else:
                            # Invincible: severe penalty tapi tidak mati
                            self.velocity *= -0.2
                            self.x, self.y = prev_x, prev_y
                    else:
                        # Low speed = bounce back
                        self.velocity = -self.velocity * 0.4
                        self.x, self.y = prev_x, prev_y
                    collided = True
                    self.collision_count += 1
                    break
        
        # Prioritas 3: Pixel-based collision dari pygame.Surface langsung (legacy)
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
                
                # Color check - abu-abu = track, hijau = off-track
                color = self.track_surface.get_at((cx, cy))
                r, g, b = color[0], color[1], color[2]
                
                # Track baru: abu-abu = jalan, hijau = off-track
                is_gray = (abs(r - g) < 50 and abs(g - b) < 50 and abs(r - b) < 50)
                is_white = (r > 200 and g > 200 and b > 200)
                is_red = (r > 150 and g < 100 and b < 100)
                is_green = (g > r + 30 and g > b + 30)
                
                if is_green or not (is_gray or is_white or is_red):
                    if not self.invincible:
                        self.alive = False
                    else:
                        # Speed penalty untuk invincible player
                        self.velocity *= 0.945
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
        angle_diff = math.degrees(self.angle - prev_angle)
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
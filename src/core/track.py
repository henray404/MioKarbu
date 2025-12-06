import os
import math
import pygame as pg

# Naik 2 level dari src/object/ ke root project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

TRACK_DIR = os.path.join(ASSETS_DIR, "tracks")

class Track:
    def __init__(self, name: str, screen_width: int = 1920, screen_height: int = 1440, 
                 road_threshold: int = 100):
        """
        Inisialisasi track dengan nama dan resolusi layar
        Args:
            name: nama file track (tanpa ekstensi)
            screen_width: lebar layar (default 1920)
            screen_height: tinggi layar (default 1440)
            road_threshold: batas brightness untuk dianggap jalan (0-255)
                           pixel dengan brightness > threshold = jalan
                           pixel dengan brightness <= threshold = tembok/grass
        """
        self.name = name
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.road_threshold = road_threshold
        self.image_path = os.path.join(TRACK_DIR, f"{name}.png")
        
        # Load gambar trek
        if os.path.exists(self.image_path):
            original_image = pg.image.load(self.image_path)
            self.image = pg.transform.scale(original_image, (self.screen_width, self.screen_height))
        else:
            raise FileNotFoundError(f"Track image not found: {self.image_path}")
        
        self.width = self.screen_width
        self.height = self.screen_height
    
    def get_pixel_at(self, x: int, y: int) -> tuple:
        """
        Dapatkan warna pixel pada posisi (x, y)
        Returns: tuple (R, G, B) atau (R, G, B, A)
        """
        # Pastikan koordinat dalam bounds
        x = max(0, min(int(x), self.width - 1))
        y = max(0, min(int(y), self.height - 1))
        return self.image.get_at((x, y))
    
    def get_brightness_at(self, x: int, y: int) -> float:
        """
        Dapatkan brightness pixel pada posisi (x, y)
        Returns: float 0-255 (0 = hitam, 255 = putih)
        """
        color = self.get_pixel_at(x, y)
        # Hitung brightness dari RGB (grayscale formula)
        return (color[0] * 0.299 + color[1] * 0.587 + color[2] * 0.114)
    
    def is_road(self, x: int, y: int) -> bool:
        """
        Cek apakah posisi (x, y) adalah jalan atau tembok
        Returns: True jika jalan, False jika tembok/grass
        """
        brightness = self.get_brightness_at(x, y)
        return brightness < self.road_threshold or brightness == 250
    
    def is_wall(self, x: int, y: int) -> bool:
        """
        Cek apakah posisi (x, y) adalah tembok/grass
        Returns: True jika tembok, False jika jalan
        """
        return not self.is_road(x, y)
    
    def check_collision(self, x: float, y: float, width: float = 10, height: float = 10) -> bool:
        """
        Cek collision untuk area rectangular (misal motor)
        Args:
            x, y: center position
            width, height: ukuran area yang dicek
        Returns: True jika ada collision dengan tembok
        """
        # Cek beberapa titik di sekitar center
        half_w = width / 2
        half_h = height / 2
        
        # Check 5 titik: center, 4 corner
        check_points = [
            (x, y),  # center
            (x - half_w, y - half_h),  # top-left
            (x + half_w, y - half_h),  # top-right
            (x - half_w, y + half_h),  # bottom-left
            (x + half_w, y + half_h),  # bottom-right
        ]
        
        for px, py in check_points:
            if self.is_wall(px, py):
                return True
        return False
    
    def raycast(self, start_x: float, start_y: float, angle: float, max_distance: float = 300) -> float:
        """
        Raycast dari posisi start ke arah angle sampai ketemu tembok
        Args:
            start_x, start_y: posisi awal ray
            angle: sudut dalam radian (0 = kanan, pi/2 = bawah)
            max_distance: jarak maksimum ray
        Returns: jarak ke tembok terdekat (0 - max_distance)
        """
        # Direction vector
        dx = math.cos(angle)
        dy = math.sin(angle)
        
        # Step size (semakin kecil = lebih akurat tapi lebih lambat)
        step = 5
        
        distance = 0
        while distance < max_distance:
            # Hitung posisi saat ini
            check_x = start_x + dx * distance
            check_y = start_y + dy * distance
            
            # Cek bounds
            if check_x < 0 or check_x >= self.width or check_y < 0 or check_y >= self.height:
                return distance
            
            # Cek wall
            if self.is_wall(check_x, check_y):
                return distance
            
            distance += step
        
        return max_distance
    
    def get_sensor_distances(self, x: float, y: float, angle: float, 
                             num_sensors: int = 5, fov: float = math.pi, 
                             max_distance: float = 300) -> list:
        """
        Dapatkan jarak dari beberapa sensor (raycast)
        Args:
            x, y: posisi motor
            angle: sudut hadap motor dalam radian
            num_sensors: jumlah sensor (default 5)
            fov: field of view total dalam radian (default pi = 180 derajat)
            max_distance: jarak maksimum sensor
        Returns: list of distances untuk setiap sensor
        """
        distances = []
        
        if num_sensors == 1:
            # Hanya sensor depan
            dist = self.raycast(x, y, angle, max_distance)
            distances.append(dist)
        else:
            # Spread sensors across FOV
            # FOV centered on motor's angle
            start_angle = angle - fov / 2
            angle_step = fov / (num_sensors - 1)
            
            for i in range(num_sensors):
                sensor_angle = start_angle + i * angle_step
                dist = self.raycast(x, y, sensor_angle, max_distance)
                distances.append(dist)
        
        return distances
    
    def draw(self, screen, camera, x=0, y=0):
        screen.blit(self.image, (x - camera.x, y - camera.y))
    
    def draw_sensors(self, screen, camera, x: float, y: float, angle: float,
                     num_sensors: int = 5, fov: float = math.pi, max_distance: float = 300):
        """
        Gambar visualisasi sensor rays (untuk debugging)
        """
        distances = self.get_sensor_distances(x, y, angle, num_sensors, fov, max_distance)
        
        if num_sensors == 1:
            angles = [angle]
        else:
            start_angle = angle - fov / 2
            angle_step = fov / (num_sensors - 1)
            angles = [start_angle + i * angle_step for i in range(num_sensors)]
        
        # Warna gradient dari hijau (jauh) ke merah (dekat)
        for i, (sensor_angle, dist) in enumerate(zip(angles, distances)):
            # Hitung end point
            end_x = x + math.cos(sensor_angle) * dist
            end_y = y + math.sin(sensor_angle) * dist
            
            # Warna berdasarkan jarak (merah = dekat tembok, hijau = jauh)
            ratio = dist / max_distance
            color = (int(255 * (1 - ratio)), int(255 * ratio), 0)  # Red to Green
            
            # Convert ke screen coordinates
            screen_start = (int(x - camera.x), int(y - camera.y))
            screen_end = (int(end_x - camera.x), int(end_y - camera.y))
            
            # Draw ray line
            pg.draw.line(screen, color, screen_start, screen_end, 2)
            # Draw end point
            pg.draw.circle(screen, (255, 0, 0), screen_end, 4)
    
    def get_size(self):
        return (self.width, self.height)




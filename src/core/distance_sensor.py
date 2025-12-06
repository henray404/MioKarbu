import math
import pygame as pg
from typing import List, Tuple, Optional


class DistanceSensor:
    """
    Sensor jarak berbasis raycasting untuk deteksi tembok/obstacle.
    Bisa di-attach ke motor untuk AI/NEAT training.
    """
    
    def __init__(self, num_sensors: int = 5, fov: float = 180, max_distance: float = 200):
        """
        Inisialisasi DistanceSensor
        Args:
            num_sensors: jumlah ray sensor
            fov: field of view dalam derajat
            max_distance: jarak maksimum sensor (pixel)
        """
        self.num_sensors = num_sensors
        self.fov = math.radians(fov)  # Convert ke radian
        self.max_distance = max_distance
        self.step_size = 5  # Step size untuk raycast (pixel)
        
        # Cache hasil sensor terakhir
        self.distances: List[float] = [max_distance] * num_sensors
        self.normalized: List[float] = [1.0] * num_sensors
        self.hit_points: List[Tuple[float, float]] = []
        
        # Reference ke track untuk collision check
        self.track = None
    
    def set_track(self, track):
        """Set track untuk raycasting collision detection"""
        self.track = track
    
    def _raycast(self, start_x: float, start_y: float, angle: float) -> Tuple[float, Tuple[float, float]]:
        """
        Single raycast dari posisi start ke arah angle
        Args:
            start_x, start_y: posisi awal ray
            angle: sudut dalam radian (0 = kanan, pi/2 = bawah)
        Returns: 
            (distance, hit_point) - jarak ke tembok dan titik hit
        """
        if self.track is None:
            return self.max_distance, (start_x, start_y)
        
        dx = math.cos(angle)
        dy = math.sin(angle)
        
        distance = 0
        while distance < self.max_distance:
            check_x = start_x + dx * distance
            check_y = start_y + dy * distance
            
            # Cek bounds
            if (check_x < 0 or check_x >= self.track.width or 
                check_y < 0 or check_y >= self.track.height):
                return distance, (check_x, check_y)
            
            # Cek wall
            if self.track.is_wall(check_x, check_y):
                return distance, (check_x, check_y)
            
            distance += self.step_size
        
        # Max distance reached
        end_x = start_x + dx * self.max_distance
        end_y = start_y + dy * self.max_distance
        return self.max_distance, (end_x, end_y)
    
    def update(self, x: float, y: float, angle: float) -> List[float]:
        """
        Update semua sensor dari posisi dan sudut motor
        Args:
            x, y: posisi motor
            angle: sudut hadap motor dalam radian
        Returns:
            List jarak raw untuk setiap sensor
        """
        self.distances = []
        self.hit_points = []
        
        if self.num_sensors == 1:
            dist, hit = self._raycast(x, y, angle)
            self.distances.append(dist)
            self.hit_points.append(hit)
        else:
            # Spread sensors across FOV, centered on motor's angle
            start_angle = angle - self.fov / 2
            angle_step = self.fov / (self.num_sensors - 1)
            
            for i in range(self.num_sensors):
                sensor_angle = start_angle + i * angle_step
                dist, hit = self._raycast(x, y, sensor_angle)
                self.distances.append(dist)
                self.hit_points.append(hit)
        
        # Update normalized values
        self.normalized = [d / self.max_distance for d in self.distances]
        
        return self.distances
    
    def get_distances(self) -> List[float]:
        """Dapatkan jarak raw terakhir"""
        return self.distances
    
    def get_normalized(self) -> List[float]:
        """
        Dapatkan jarak ternormalisasi (0-1)
        0 = sangat dekat tembok, 1 = jauh/aman
        """
        return self.normalized
    
    def get_angles(self, base_angle: float) -> List[float]:
        """
        Dapatkan sudut setiap sensor ray
        Args:
            base_angle: sudut hadap motor dalam radian
        Returns:
            List sudut untuk setiap sensor
        """
        if self.num_sensors == 1:
            return [base_angle]
        
        start_angle = base_angle - self.fov / 2
        angle_step = self.fov / (self.num_sensors - 1)
        return [start_angle + i * angle_step for i in range(self.num_sensors)]
    
    def draw(self, screen, camera, x: float, y: float, angle: float):
        """
        Gambar visualisasi sensor rays (untuk debugging)
        Args:
            screen: pygame surface
            camera: camera object dengan x, y offset
            x, y: posisi motor
            angle: sudut hadap motor
        """
        # Update dulu untuk dapat hit points terbaru
        self.update(x, y, angle)
        
        angles = self.get_angles(angle)
        
        for i, (sensor_angle, dist, hit) in enumerate(zip(angles, self.distances, self.hit_points)):
            # Warna berdasarkan jarak (merah = dekat tembok, hijau = jauh)
            ratio = dist / self.max_distance
            color = (int(255 * (1 - ratio)), int(255 * ratio), 0)  # Red to Green
            
            # Convert ke screen coordinates
            screen_start = (int(x - camera.x), int(y - camera.y))
            screen_end = (int(hit[0] - camera.x), int(hit[1] - camera.y))
            
            # Draw ray line
            pg.draw.line(screen, color, screen_start, screen_end, 2)
            # Draw end point (hit marker)
            pg.draw.circle(screen, (255, 0, 0), screen_end, 4)
    
    def __repr__(self) -> str:
        return f"DistanceSensor(num={self.num_sensors}, fov={math.degrees(self.fov):.0f}°, max={self.max_distance})"
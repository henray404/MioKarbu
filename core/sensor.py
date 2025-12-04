"""
Sensor - Distance sensor untuk AI observation
Tanggung jawab: raycasting untuk deteksi jarak ke obstacles
"""
import math
from typing import List, Tuple, Optional

import pygame


class DistanceSensor:
    """
    Sensor jarak menggunakan raycasting sederhana.
    Bisa dipasang di berbagai sudut relatif terhadap mobil.
    """

    def __init__(
        self,
        angle_offset: float = 0.0,
        max_range: float = 200.0,
        color: Tuple[int, int, int] = (255, 255, 0),
    ):
        """
        Args:
            angle_offset: offset sudut dari arah mobil (dalam radian)
            max_range: jarak maksimal sensor
            color: warna garis sensor untuk debug
        """
        self.angle_offset = angle_offset
        self.max_range = max_range
        self.distance = max_range  # current measured distance
        self.color = color
        self.hit_point: Optional[Tuple[float, float]] = None

    def update_distance(
        self,
        walls: List[pygame.Rect],
        car_x: float,
        car_y: float,
        car_angle: float,
    ) -> float:
        """
        Update jarak sensor dengan raycasting
        
        Returns:
            distance: jarak terdekat ke obstacle (normalized 0-1)
        """
        # Calculate sensor angle (car angle + offset)
        sensor_angle = car_angle + self.angle_offset

        # Ray direction
        ray_dx = math.cos(sensor_angle)
        ray_dy = math.sin(sensor_angle)

        # Find closest intersection
        min_distance = self.max_range
        closest_hit = None

        # Check intersection with each wall
        for wall in walls:
            hit_point = self._ray_rect_intersection(
                car_x, car_y, ray_dx, ray_dy, wall
            )
            if hit_point:
                dist = math.hypot(hit_point[0] - car_x, hit_point[1] - car_y)
                if dist < min_distance:
                    min_distance = dist
                    closest_hit = hit_point

        self.distance = min_distance
        self.hit_point = closest_hit

        # Return normalized distance (0 = hit, 1 = max range)
        return self.distance / self.max_range

    def _ray_rect_intersection(
        self,
        rx: float,
        ry: float,
        rdx: float,
        rdy: float,
        rect: pygame.Rect,
    ) -> Optional[Tuple[float, float]]:
        """
        Simplified ray-rectangle intersection
        Returns the hit point or None
        """
        # Get rectangle edges
        edges = [
            ((rect.left, rect.top), (rect.right, rect.top)),  # top
            ((rect.right, rect.top), (rect.right, rect.bottom)),  # right
            ((rect.right, rect.bottom), (rect.left, rect.bottom)),  # bottom
            ((rect.left, rect.bottom), (rect.left, rect.top)),  # left
        ]

        closest_hit = None
        min_t = float("inf")

        for (x1, y1), (x2, y2) in edges:
            hit = self._ray_line_intersection(rx, ry, rdx, rdy, x1, y1, x2, y2)
            if hit:
                t = hit[2]  # parameter t
                if 0 < t < min_t and t < self.max_range:
                    min_t = t
                    closest_hit = (hit[0], hit[1])

        return closest_hit

    def _ray_line_intersection(
        self,
        rx: float,
        ry: float,
        rdx: float,
        rdy: float,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
    ) -> Optional[Tuple[float, float, float]]:
        """
        Ray-line segment intersection using parametric form
        Returns (hit_x, hit_y, t) or None
        """
        # Line segment direction
        ldx = x2 - x1
        ldy = y2 - y1

        # Solve: ray_origin + t*ray_dir = line_start + u*line_dir
        denominator = rdx * ldy - rdy * ldx

        if abs(denominator) < 1e-10:  # parallel
            return None

        # Calculate parameters
        t = ((x1 - rx) * ldy - (y1 - ry) * ldx) / denominator
        u = ((x1 - rx) * rdy - (y1 - ry) * rdx) / denominator

        # Check if intersection is valid
        if t > 0 and 0 <= u <= 1:
            hit_x = rx + t * rdx
            hit_y = ry + t * rdy
            return (hit_x, hit_y, t)

        return None

    def draw(self, screen: pygame.Surface, car_x: float, car_y: float, car_angle: float):
        """Draw sensor line for debugging"""
        sensor_angle = car_angle + self.angle_offset

        if self.hit_point:
            # Draw to hit point
            pygame.draw.line(
                screen,
                self.color,
                (int(car_x), int(car_y)),
                (int(self.hit_point[0]), int(self.hit_point[1])),
                2,
            )
            # Draw hit point
            pygame.draw.circle(
                screen, (255, 0, 0), (int(self.hit_point[0]), int(self.hit_point[1])), 3
            )
        else:
            # Draw to max range
            end_x = car_x + math.cos(sensor_angle) * self.max_range
            end_y = car_y + math.sin(sensor_angle) * self.max_range
            pygame.draw.line(
                screen,
                self.color,
                (int(car_x), int(car_y)),
                (int(end_x), int(end_y)),
                1,
            )

    def get_normalized_distance(self) -> float:
        """Return distance normalized to [0, 1]"""
        return self.distance / self.max_range


class SensorArray:
    """Helper class untuk manage multiple sensors"""

    def __init__(self, num_sensors: int = 5, max_range: float = 200.0):
        """
        Create sensor array dengan distribusi merata
        Default: 5 sensor dari -90° sampai +90°
        """
        self.sensors: List[DistanceSensor] = []
        
        if num_sensors == 1:
            angles = [0.0]
        else:
            # Distribute sensors evenly from -90° to +90°
            angles = [
                math.radians(-90 + (180 / (num_sensors - 1)) * i)
                for i in range(num_sensors)
            ]

        colors = [
            (255, 0, 255),
            (255, 128, 0),
            (255, 255, 0),
            (0, 255, 128),
            (0, 255, 255),
        ]

        for i, angle in enumerate(angles):
            color = colors[i % len(colors)]
            self.sensors.append(DistanceSensor(angle, max_range, color))

    def update_all(
        self, walls: List[pygame.Rect], car_x: float, car_y: float, car_angle: float
    ) -> List[float]:
        """Update semua sensor dan return array of normalized distances"""
        return [
            sensor.update_distance(walls, car_x, car_y, car_angle)
            for sensor in self.sensors
        ]

    def draw_all(
        self, screen: pygame.Surface, car_x: float, car_y: float, car_angle: float
    ):
        """Draw all sensors"""
        for sensor in self.sensors:
            sensor.draw(screen, car_x, car_y, car_angle)

    def get_readings(self) -> List[float]:
        """Get all sensor readings (normalized)"""
        return [sensor.get_normalized_distance() for sensor in self.sensors]

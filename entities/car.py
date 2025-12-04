"""
Car - Base class untuk semua mobil (Player & AI)
Menggunakan composition: PhysicsEngine, Controller, Sensors
"""
import math
from typing import List, Optional

import pygame

from core.physics_engine import PhysicsEngine
from core.controller import BaseController
from core.sensor import SensorArray


class Car:
    """
    Base class untuk mobil dengan composition pattern.
    
    Responsibilities:
    - Manage state (position, angle, velocity)
    - Coordinate physics, controller, and sensors
    - Handle rendering
    """

    def __init__(
        self,
        x: float,
        y: float,
        color: tuple[int, int, int] = (255, 165, 0),
        image: Optional[pygame.Surface] = None,
        controller: Optional[BaseController] = None,
        physics: Optional[PhysicsEngine] = None,
        enable_sensors: bool = False,
        num_sensors: int = 5,
        sensor_range: float = 200.0,
    ):
        # Position & movement state
        self._x = x
        self._y = y
        self._angle = 0.0
        self._velocity = 0.0

        # Visual
        self.color = color
        self.image = image
        self.length = 40
        self.width = 20
        self.surface = pygame.Surface((self.length, self.width), pygame.SRCALPHA)
        self.surface.fill(color)
        self.rect: Optional[pygame.Rect] = None

        # Composition: inject dependencies
        self.physics = physics or PhysicsEngine()
        self.controller = controller
        self.sensors: Optional[SensorArray] = None

        if enable_sensors:
            self.sensors = SensorArray(num_sensors, sensor_range)

        # Debug mode
        self.debug_mode = False

    # Properties for encapsulation
    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def angle(self) -> float:
        return self._angle

    @property
    def velocity(self) -> float:
        return self._velocity

    def process_input(self) -> tuple[float, float]:
        """Get input from controller (to be overridden or use controller)"""
        if self.controller:
            return self.controller.get_input()
        return 0.0, 0.0

    def update_steering(self, dx: float, dy: float):
        """Update steering based on input direction"""
        move = (dx != 0 or dy != 0)

        if move:
            # Calculate target angle from input
            target_angle = math.atan2(-dy, dx)

            # Smooth steering with physics
            self._angle = self.physics.calculate_steering(self._angle, target_angle)

            # Apply acceleration
            self._velocity = self.physics.update_velocity(self._velocity, True)
        else:
            # Apply friction
            self._velocity = self.physics.update_velocity(self._velocity, False)

        # Normalize angle
        self._angle = self.physics.normalize_angle(self._angle)

    def update_position(self):
        """Update position based on current velocity and angle"""
        self._x, self._y = self.physics.calculate_movement(
            self._x, self._y, self._angle, self._velocity
        )

        # Update collision rect
        if self.image:
            rotated = pygame.transform.rotate(self.image, -math.degrees(self._angle))
        else:
            rotated = pygame.transform.rotate(self.surface, -math.degrees(self._angle))
        self.rect = rotated.get_rect(center=(self._x, self._y))

    def check_collision(self, walls: List[pygame.Rect]) -> bool:
        """Check and resolve collisions with walls"""
        if not self.rect:
            return False

        for wall in walls:
            if self.rect.colliderect(wall):
                # Collision detected - revert position
                prev_x, prev_y = self.physics.calculate_movement(
                    self._x, self._y, self._angle, -self._velocity
                )
                self._x, self._y = prev_x, prev_y

                # Apply collision physics
                self._velocity = self.physics.resolve_collision(self._velocity)

                # Update rect after reverting
                if self.image:
                    rotated = pygame.transform.rotate(self.image, -math.degrees(self._angle))
                else:
                    rotated = pygame.transform.rotate(self.surface, -math.degrees(self._angle))
                self.rect = rotated.get_rect(center=(self._x, self._y))

                return True

        return False

    def update_sensors(self, walls: List[pygame.Rect]) -> Optional[List[float]]:
        """Update all sensors and return readings"""
        if self.sensors:
            return self.sensors.update_all(walls, self._x, self._y, self._angle)
        return None

    def update(self, walls: List[pygame.Rect]):
        """Main update cycle - separated into clear steps"""
        # 1. Get input
        dx, dy = self.process_input()

        # 2. Update steering & velocity
        self.update_steering(dx, dy)

        # 3. Update position
        self.update_position()

        # 4. Check collisions
        self.check_collision(walls)

        # 5. Update sensors
        self.update_sensors(walls)

    def draw(self, screen: pygame.Surface):
        """Render car and debug info"""
        # Draw car
        if self.image:
            rotated_car = pygame.transform.rotate(self.image, -math.degrees(self._angle))
            rect = rotated_car.get_rect(center=(self._x, self._y))
            screen.blit(rotated_car, rect)
        else:
            rotated_car = pygame.transform.rotate(self.surface, -math.degrees(self._angle))
            rect = rotated_car.get_rect(center=(self._x, self._y))
            screen.blit(rotated_car, rect)

        # Draw direction indicator
        front_x = self._x + math.cos(self._angle) * (self.length / 2)
        front_y = self._y + math.sin(self._angle) * (self.length / 2)
        pygame.draw.line(
            screen, (0, 255, 0), (self._x, self._y), (front_x, front_y), 3
        )
        pygame.draw.circle(screen, (255, 0, 0), (int(front_x), int(front_y)), 4)

        # Draw sensors if enabled and debug mode
        if self.debug_mode and self.sensors:
            self.sensors.draw_all(screen, self._x, self._y, self._angle)

    def get_sensor_readings(self) -> Optional[List[float]]:
        """Get current sensor readings (for AI)"""
        if self.sensors:
            return self.sensors.get_readings()
        return None

    def set_debug_mode(self, enabled: bool):
        """Toggle debug visualization"""
        self.debug_mode = enabled



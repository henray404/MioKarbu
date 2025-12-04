"""
AICar - Mobil yang dikontrol oleh AI agent
"""
import math
from typing import Optional, List

import pygame

from entities.car import Car
from core.controller import AIController
from core.physics_engine import PhysicsEngine


class AICar(Car):
    """
    AI-controlled car dengan AIController dan sensors
    Siap untuk RL agent integration
    """

    def __init__(
        self,
        x: float,
        y: float,
        color: tuple[int, int, int] = (0, 255, 0),
        image: Optional[pygame.Surface] = None,
        physics: Optional[PhysicsEngine] = None,
        num_sensors: int = 5,
        sensor_range: float = 200.0,
    ):
        # Create AI controller
        controller = AIController()

        # Initialize base Car with AI controller and sensors enabled
        super().__init__(
            x=x,
            y=y,
            color=color,
            image=image,
            controller=controller,
            physics=physics,
            enable_sensors=True,
            num_sensors=num_sensors,
            sensor_range=sensor_range,
        )

        # AI-specific attributes
        self.ai_mode = "simple"  # simple, rl, etc.

    def set_ai_input(self, dx: float, dy: float):
        """Set input dari AI algorithm/model"""
        if isinstance(self.controller, AIController):
            self.controller.set_input(dx, dy)

    def simple_ai_behavior(self):
        """
        Simple AI: just drive forward and turn when hitting wall
        (untuk demo - bisa diganti dengan RL agent)
        """
        if self.velocity < 2.0:
            # Drive forward
            if isinstance(self.controller, AIController):
                self.controller.set_input(0, 1)  # forward
        else:
            # Check sensors - turn if obstacle ahead
            readings = self.get_sensor_readings()
            if readings and readings[2] < 0.3:  # center sensor detects wall
                # Turn randomly
                import random
                dx = random.choice([-1, 1])
                if isinstance(self.controller, AIController):
                    self.controller.set_input(dx, 1)

    def update(self, walls: List[pygame.Rect]):
        """Override update to include AI decision making"""
        if self.ai_mode == "simple":
            self.simple_ai_behavior()
        # print position
        print(f"AI Car Position: ({self.x:.1f}, {self.y:.1f})")

        # Call parent update
        super().update(walls)

    def draw(self, screen: pygame.Surface):
        """Override draw to add AI-specific visualization"""
        super().draw(screen)

        if self.debug_mode:
            # Draw sensor readings as text
            readings = self.get_sensor_readings()
            if readings:
                font = pygame.font.Font(None, 16)
                y_offset = int(self.y) - 60

                for i, reading in enumerate(readings):
                    text = f"S{i}: {reading:.2f}"
                    surface = font.render(text, True, (0, 255, 255))
                    screen.blit(surface, (int(self.x) - 30 + i * 15, y_offset))

    def get_state(self) -> dict:
        """
        Get current state untuk RL agent
        Returns state yang bisa digunakan untuk training
        """
        return {
            "position": (self.x, self.y),
            "angle": self.angle,
            "velocity": self.velocity,
            "sensor_readings": self.get_sensor_readings() or [],
        }

    def set_rl_mode(self, enabled: bool = True):
        """Enable RL mode (untuk future integration)"""
        if enabled:
            self.ai_mode = "rl"
        else:
            self.ai_mode = "simple"

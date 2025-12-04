"""
PlayerCar - Mobil yang dikontrol oleh player via keyboard
"""
from typing import Optional

import pygame

from entities.car import Car
from core.controller import KeyboardController
from core.physics_engine import PhysicsEngine


class PlayerCar(Car):
    """
    Player-controlled car dengan KeyboardController
    """

    def __init__(
        self,
        x: float,
        y: float,
        color: tuple[int, int, int] = (255, 165, 0),
        image: Optional[pygame.Surface] = None,
        physics: Optional[PhysicsEngine] = None,
        forward_key=pygame.K_w,
        backward_key=pygame.K_s,
        left_key=pygame.K_a,
        right_key=pygame.K_d,
        enable_sensors: bool = False,
    ):
        # Create keyboard controller
        controller = KeyboardController(
            forward_key=forward_key,
            backward_key=backward_key,
            left_key=left_key,
            right_key=right_key,
        )

        # Initialize base Car with keyboard controller
        super().__init__(
            x=x,
            y=y,
            color=color,
            image=image,
            controller=controller,
            physics=physics,
            enable_sensors=enable_sensors,
        )

    def draw(self, screen: pygame.Surface):
        """Override draw to add player-specific HUD"""
        super().draw(screen)

        # Optional: Add player-specific visualization
        if self.debug_mode:
            # Draw debug info
            font = pygame.font.Font(None, 20)
            info_texts = [
                f"Pos: ({self.x:.1f}, {self.y:.1f})",
                f"Angle: {math.degrees(self.angle):.1f}°",
                f"Speed: {self.velocity:.2f}",
            ]

            y_offset = 40
            for text in info_texts:
                surface = font.render(text, True, (255, 255, 0))
                screen.blit(surface, (10, y_offset))
                y_offset += 20


# Import math for debug display
import math

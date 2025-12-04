"""
Controller - Interface untuk input (keyboard atau AI)
Tanggung jawab: menyediakan input movement (dx, dy)
"""
import math
from abc import ABC, abstractmethod
from typing import Tuple

import pygame


class BaseController(ABC):
    """Abstract base class untuk semua controller"""

    @abstractmethod
    def get_input(self) -> Tuple[float, float]:
        """
        Return (dx, dy) untuk direction input
        dx: -1 (left) to 1 (right)
        dy: -1 (backward) to 1 (forward)
        """
        pass


class KeyboardController(BaseController):
    """Controller untuk player menggunakan keyboard WASD"""

    def __init__(
        self,
        forward_key=pygame.K_w,
        backward_key=pygame.K_s,
        left_key=pygame.K_a,
        right_key=pygame.K_d,
    ):
        self.forward_key = forward_key
        self.backward_key = backward_key
        self.left_key = left_key
        self.right_key = right_key

    def get_input(self) -> Tuple[float, float]:
        """Get input from keyboard"""
        keys = pygame.key.get_pressed()
        dx, dy = 0.0, 0.0

        if keys[self.forward_key]:
            dy += 1
        if keys[self.backward_key]:
            dy -= 1
        if keys[self.left_key]:
            dx -= 1
        if keys[self.right_key]:
            dx += 1

        return dx, dy


class AIController(BaseController):
    """Controller untuk AI agent (menerima output dari AI model)"""

    def __init__(self):
        self.dx = 0.0
        self.dy = 0.0

    def set_input(self, dx: float, dy: float):
        """Set input dari AI model/algorithm"""
        self.dx = dx
        self.dy = dy

    def get_input(self) -> Tuple[float, float]:
        """Return AI input"""
        return self.dx, self.dy

    def set_target_angle(self, target_angle: float):
        """
        Alternative: AI bisa langsung set target angle
        Convert angle to dx, dy
        """
        self.dx = math.cos(target_angle)
        self.dy = math.sin(target_angle)

    def move_forward(self, should_move: bool = True):
        """Simple AI command: move forward"""
        if should_move:
            self.dy = 1.0
        else:
            self.dy = 0.0

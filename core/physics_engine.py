"""
PhysicsEngine - Menangani semua aspek fisika mobil
Tanggung jawab: acceleration, friction, velocity, collision resolution
"""
import math


class PhysicsEngine:
    def __init__(
        self,
        acceleration_rate: float = 2.9,
        friction: float = 0.98,
        steering_rate: float = 5.0,
        max_speed: float = 4.0,
    ):
        self.acceleration_rate = acceleration_rate
        self.friction = friction
        self.steering_rate = steering_rate  # degrees per frame
        self.max_speed = max_speed

    def apply_acceleration(self, velocity: float, accelerating: bool) -> float:
        """Tambah kecepatan saat akselerasi aktif"""
        if accelerating:
            velocity += self.acceleration_rate
        return velocity

    def apply_friction(self, velocity: float) -> float:
        """Kurangi kecepatan dengan friction"""
        return velocity * self.friction

    def update_velocity(self, velocity: float, accelerating: bool) -> float:
        """Update velocity dengan acceleration & friction"""
        if accelerating:
            velocity = self.apply_acceleration(velocity, True)
        else:
            velocity = self.apply_friction(velocity)
        
        # Clamp velocity
        return max(-self.max_speed, min(self.max_speed, velocity))

    def calculate_steering(
        self, current_angle: float, target_angle: float
    ) -> float:
        """Hitung sudut baru dengan steering rate limit"""
        # Normalize angle difference
        angle_diff = (target_angle - current_angle + math.pi) % (2 * math.pi) - math.pi
        max_turn = math.radians(self.steering_rate)
        
        if abs(angle_diff) < max_turn:
            return target_angle
        else:
            return current_angle + max_turn * math.copysign(1, angle_diff)

    def normalize_angle(self, angle: float) -> float:
        """Normalize angle to [-π, π]"""
        return (angle + math.pi) % (2 * math.pi) - math.pi

    def resolve_collision(self, velocity: float, bounce_factor: float = -0.4) -> float:
        """Balikkan velocity saat tabrakan"""
        return velocity * bounce_factor

    def calculate_movement(
        self, x: float, y: float, angle: float, velocity: float
    ) -> tuple[float, float]:
        """Hitung posisi baru berdasarkan angle dan velocity"""
        new_x = x + math.cos(angle) * velocity
        new_y = y + math.sin(angle) * velocity
        return new_x, new_y

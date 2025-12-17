"""
Physics Module untuk Motor
==========================

Mengandung konstanta fisika dan kalkulasi physics.
Digunakan dengan composition pattern oleh Motor class.
"""

from dataclasses import dataclass, field
from typing import Tuple
import math


@dataclass
class PhysicsConfig:
    """
    Konfigurasi konstanta fisika motor.
    
    Semua nilai default dioptimasi untuk gameplay yang fun tapi realistis.
    """
    # Speed & Acceleration
    acceleration_rate: float = 0.12      # Akselerasi
    brake_power: float = 0.25            # Kekuatan rem
    friction: float = 0.985              # Gesekan natural (mendekati 1 = mulus)
    max_speed: float = 25.0              # Kecepatan maksimum
    
    # Steering - Speed Dependent
    base_steering_rate: float = 4.5      # Steering rate saat diam/lambat (derajat/frame)
    min_steering_rate: float = 1.2       # Steering rate minimal saat kecepatan max
    
    # Grip & Traction
    base_grip: float = 1.0               # Grip dasar
    turn_grip_loss: float = 0.15         # Kehilangan grip saat belok tajam
    speed_grip_factor: float = 0.7       # Faktor grip di kecepatan tinggi
    
    # Turn Physics
    turn_speed_penalty: float = 0.02     # Kehilangan speed saat belok
    sharp_turn_threshold: float = 0.5    # Threshold untuk belok tajam (0-1)
    understeer_factor: float = 0.3       # Seberapa besar understeer di speed tinggi
    
    # Inertia
    lateral_friction: float = 0.92       # Gesekan lateral
    
    # Dimensions
    length: float = 140.0
    width: float = 80.0
    
    # Collision
    wall_explode_speed: float = 8.0      # Speed di atas ini = meledak saat nabrak


@dataclass
class PhysicsState:
    """
    State fisika motor yang berubah-ubah setiap frame.
    """
    velocity: float = 0.0
    lateral_velocity: float = 0.0
    grip: float = 1.0
    weight_transfer: float = 0.0
    steering_rate: float = 4.5  # Dynamic, akan berubah
    
    # Drift
    drift_angle: float = 0.0
    is_drifting: bool = False
    drift_direction: int = 0


class PhysicsEngine:
    """
    Engine untuk kalkulasi fisika motor.
    
    Handles:
    - Acceleration/braking
    - Speed-dependent steering
    - Grip system
    - Drift mechanics
    """
    
    def __init__(self, config: PhysicsConfig = None):
        self.config = config or PhysicsConfig()
        self.state = PhysicsState(steering_rate=self.config.base_steering_rate)
    
    def calculate_steering_rate(self) -> float:
        """
        Hitung steering rate berdasarkan kecepatan.
        Semakin cepat = semakin sulit belok.
        """
        speed_ratio = abs(self.state.velocity) / self.config.max_speed
        return self.config.base_steering_rate - (
            (self.config.base_steering_rate - self.config.min_steering_rate) * speed_ratio
        )
    
    def apply_acceleration(self, throttle: float) -> None:
        """
        Apply akselerasi atau rem.
        
        Args:
            throttle: -1 (mundur) sampai 1 (maju)
        """
        throttle = max(-1, min(1, throttle))
        
        if throttle > 0:
            # Akselerasi dengan drag di speed tinggi
            speed_ratio = abs(self.state.velocity) / self.config.max_speed
            accel_modifier = 1.0 - (speed_ratio * 0.5)
            self.state.velocity += self.config.acceleration_rate * throttle * accel_modifier
            self.state.weight_transfer = 0.3
        elif throttle < 0:
            self.state.velocity -= self.config.brake_power
            self.state.weight_transfer = -0.5
        else:
            self.state.velocity *= self.config.friction
            self.state.weight_transfer *= 0.9
        
        # Clamp velocity
        self.state.velocity = max(
            -self.config.max_speed * 0.5, 
            min(self.config.max_speed, self.state.velocity)
        )
    
    def apply_steering(self, steering_input: float, is_drifting: bool = False) -> float:
        """
        Hitung perubahan angle berdasarkan steering input.
        
        Args:
            steering_input: -1 (kiri) sampai 1 (kanan)
            is_drifting: True jika sedang drift
            
        Returns:
            Perubahan angle dalam radians
        """
        self.state.is_drifting = is_drifting
        
        if abs(self.state.velocity) <= 0.1:
            return 0.0
        
        speed_ratio = abs(self.state.velocity) / self.config.max_speed
        
        if is_drifting and steering_input != 0:
            # Drift mode
            self.state.drift_direction = int(steering_input)
            drift_steer = self.config.base_steering_rate * 1.5
            angle_change = math.radians(drift_steer) * steering_input
            
            # Build up drift angle
            max_drift = 0.5
            self.state.drift_angle += steering_input * 0.08
            self.state.drift_angle = max(-max_drift, min(max_drift, self.state.drift_angle))
            
            # Speed penalty
            self.state.velocity *= 0.995
            
            # Lose grip
            self.state.grip = max(0.3, self.state.grip - 0.05)
            
            # Build lateral velocity
            self.state.lateral_velocity += steering_input * 0.5
        else:
            # Normal steering
            self.state.steering_rate = self.calculate_steering_rate()
            steer_amount = math.radians(self.state.steering_rate) * steering_input
            
            # Understeer at high speed
            understeer = 1.0 - (speed_ratio * self.config.understeer_factor)
            angle_change = steer_amount * understeer
            
            # Speed penalty when turning
            if abs(steering_input) > 0:
                turn_intensity = abs(steering_input) * speed_ratio
                speed_loss = self.config.turn_speed_penalty * turn_intensity
                self.state.velocity *= (1.0 - speed_loss)
            
            # Grip recovery
            self.state.grip = min(self.config.base_grip, self.state.grip + 0.02)
            
            # Decay drift
            self.state.drift_angle *= 0.85
            self.state.lateral_velocity *= self.config.lateral_friction
        
        # Clamp lateral velocity
        max_lateral = 3.0
        self.state.lateral_velocity = max(-max_lateral, min(max_lateral, self.state.lateral_velocity))
        
        # Grip loss at high speed turning
        if abs(steering_input) > 0 and speed_ratio > 0.6:
            grip_loss = self.config.turn_grip_loss * speed_ratio * abs(steering_input)
            self.state.grip = max(0.5, self.state.grip - grip_loss)
        
        return angle_change
    
    def calculate_movement(self, angle: float) -> Tuple[float, float]:
        """
        Hitung delta posisi berdasarkan angle dan velocity.
        
        Args:
            angle: Sudut hadap motor (radians)
            
        Returns:
            (delta_x, delta_y)
        """
        move_angle = angle + self.state.drift_angle if self.state.is_drifting else angle
        dx = math.cos(move_angle) * self.state.velocity
        dy = math.sin(move_angle) * self.state.velocity
        return dx, dy
    
    def get_speed_kmh(self) -> int:
        """Get kecepatan dalam km/h untuk display."""
        return int(abs(self.state.velocity) * 7.5)
    
    def reset(self) -> None:
        """Reset state fisika ke default."""
        self.state = PhysicsState(steering_rate=self.config.base_steering_rate)

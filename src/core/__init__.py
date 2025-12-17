"""
Core game components
"""
# from .ai_car import AICar
from .motor import Motor
from .track import Track
# from .distance_sensor import DistanceSensor

# New modular components
from .physics import PhysicsConfig, PhysicsState, PhysicsEngine
from .collision import CollisionHandler
from .checkpoint import CheckpointState, CheckpointTracker
from .radar import RadarConfig, Radar, AIState, FitnessCalculator

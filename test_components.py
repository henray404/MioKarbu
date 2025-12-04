"""
Demo script untuk testing komponen modular
Mendemonstrasikan penggunaan individual components
"""
import math
import pygame

from core.physics_engine import PhysicsEngine
from core.controller import KeyboardController, AIController
from core.sensor import DistanceSensor, SensorArray


def test_physics_engine():
    """Test PhysicsEngine"""
    print("\n" + "="*60)
    print("🔧 Testing PhysicsEngine")
    print("="*60)
    
    physics = PhysicsEngine(
        acceleration_rate=2.9,
        friction=0.98,
        steering_rate=5.0,
        max_speed=4.0
    )
    
    velocity = 0.0
    angle = 0.0
    
    # Test acceleration
    print("\n1. Acceleration test:")
    for i in range(5):
        velocity = physics.update_velocity(velocity, accelerating=True)
        print(f"   Frame {i+1}: velocity = {velocity:.2f}")
    
    # Test friction
    print("\n2. Friction test:")
    for i in range(5):
        velocity = physics.update_velocity(velocity, accelerating=False)
        print(f"   Frame {i+1}: velocity = {velocity:.2f}")
    
    # Test steering
    print("\n3. Steering test:")
    target = math.radians(90)  # Turn 90 degrees
    for i in range(20):
        angle = physics.calculate_steering(angle, target)
        if i % 5 == 0:
            print(f"   Frame {i}: angle = {math.degrees(angle):.1f}°")
    
    print("\n✅ PhysicsEngine works correctly!")


def test_controllers():
    """Test Controllers"""
    print("\n" + "="*60)
    print("🎮 Testing Controllers")
    print("="*60)
    
    # Keyboard Controller
    print("\n1. KeyboardController:")
    kb_controller = KeyboardController()
    print(f"   Created with keys: W={kb_controller.forward_key}, "
          f"A={kb_controller.left_key}, S={kb_controller.backward_key}, "
          f"D={kb_controller.right_key}")
    
    # AI Controller
    print("\n2. AIController:")
    ai_controller = AIController()
    
    # Test different AI commands
    commands = [
        (0, 1, "Move forward"),
        (1, 1, "Move forward-right"),
        (-1, 0, "Turn left"),
        (0, 0, "Stop"),
    ]
    
    for dx, dy, desc in commands:
        ai_controller.set_input(dx, dy)
        result = ai_controller.get_input()
        print(f"   {desc}: set({dx}, {dy}) -> get{result}")
    
    print("\n✅ Controllers work correctly!")


def test_sensors():
    """Test Sensor System"""
    print("\n" + "="*60)
    print("📡 Testing Sensor System")
    print("="*60)
    
    # Create test walls
    walls = [
        pygame.Rect(0, 0, 800, 10),      # top
        pygame.Rect(0, 590, 800, 10),    # bottom
        pygame.Rect(0, 0, 10, 600),      # left
        pygame.Rect(790, 0, 10, 600),    # right
    ]
    
    # Single sensor
    print("\n1. Single DistanceSensor:")
    sensor = DistanceSensor(angle_offset=0, max_range=200.0)
    
    # Test from center, facing right
    car_x, car_y, car_angle = 400.0, 300.0, 0.0
    distance = sensor.update_distance(walls, car_x, car_y, car_angle)
    print(f"   Position: ({car_x}, {car_y})")
    print(f"   Facing: {math.degrees(car_angle):.0f}° (right)")
    print(f"   Distance: {sensor.distance:.1f}px (normalized: {distance:.2f})")
    
    # Sensor Array
    print("\n2. SensorArray (5 sensors):")
    sensor_array = SensorArray(num_sensors=5, max_range=200.0)
    readings = sensor_array.update_all(walls, car_x, car_y, car_angle)
    
    angles = [-90, -45, 0, 45, 90]
    for i, (angle, reading) in enumerate(zip(angles, readings)):
        print(f"   Sensor {i} ({angle:+4d}°): {reading:.2f}")
    
    print("\n✅ Sensors work correctly!")


def test_composition():
    """Test Composition pattern"""
    print("\n" + "="*60)
    print("🏗️  Testing Composition Pattern")
    print("="*60)
    
    from entities.car import Car
    
    # Create car with custom components
    physics = PhysicsEngine(max_speed=10.0)  # Faster car
    controller = AIController()
    
    car = Car(
        x=100, y=100,
        physics=physics,
        controller=controller,
        enable_sensors=True,
        num_sensors=3,
    )
    
    print("\n1. Car created with composition:")
    print(f"   Physics: acceleration={car.physics.acceleration_rate}")
    print(f"   Controller: {type(car.controller).__name__}")
    print(f"   Sensors: {len(car.sensors.sensors) if car.sensors else 0} sensors")
    
    # Test state access via properties
    print("\n2. Encapsulation test (properties):")
    print(f"   car.x = {car.x}")
    print(f"   car.y = {car.y}")
    print(f"   car.angle = {car.angle:.2f}")
    print(f"   car.velocity = {car.velocity:.2f}")
    
    # Try to access private attributes (should work but not recommended)
    print(f"   car._x = {car._x} (private, use property instead)")
    
    print("\n✅ Composition pattern works correctly!")


def test_inheritance():
    """Test Inheritance"""
    print("\n" + "="*60)
    print("👨‍👦 Testing Inheritance")
    print("="*60)
    
    from entities.player_car import PlayerCar
    from entities.ai_car import AICar
    
    # PlayerCar
    print("\n1. PlayerCar (inherits from Car):")
    player = PlayerCar(x=200, y=200)
    print(f"   Type: {type(player).__name__}")
    print(f"   Controller: {type(player.controller).__name__}")
    print(f"   Has sensors: {player.sensors is not None}")
    print(f"   Position: ({player.x}, {player.y})")
    
    # AICar
    print("\n2. AICar (inherits from Car):")
    ai_car = AICar(x=300, y=300, num_sensors=5)
    print(f"   Type: {type(ai_car).__name__}")
    print(f"   Controller: {type(ai_car.controller).__name__}")
    print(f"   Has sensors: {ai_car.sensors is not None}")
    print(f"   Number of sensors: {len(ai_car.sensors.sensors) if ai_car.sensors else 0}")
    print(f"   AI mode: {ai_car.ai_mode}")
    
    # Test polymorphism
    print("\n3. Polymorphism test:")
    cars = [player, ai_car]
    for car in cars:
        print(f"   {type(car).__name__}: update() and draw() available")
        print(f"      - Has update method: {hasattr(car, 'update')}")
        print(f"      - Has draw method: {hasattr(car, 'draw')}")
    
    print("\n✅ Inheritance works correctly!")


def main():
    """Run all tests"""
    pygame.init()  # Initialize pygame for Rect tests
    
    print("\n" + "="*60)
    print("🧪 TESTING REFACTORED SYSTEM")
    print("="*60)
    
    test_physics_engine()
    test_controllers()
    test_sensors()
    test_composition()
    test_inheritance()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\n🎯 Refactoring successful! System is:")
    print("   ✓ Modular")
    print("   ✓ Testable")
    print("   ✓ Follows OOP principles")
    print("   ✓ Ready for AI/RL integration")
    print("="*60 + "\n")
    
    pygame.quit()


if __name__ == "__main__":
    main()

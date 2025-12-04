# 📚 Panduan Belajar - Tabrak Bahlil

Dokumen ini berisi **roadmap lengkap** untuk memahami semua konsep yang digunakan dalam project ini, mulai dari dasar sampai advanced.

---

## 📖 Daftar Isi

1. [Konsep Dasar Programming](#1-konsep-dasar-programming)
2. [Object-Oriented Programming (OOP)](#2-object-oriented-programming-oop)
3. [Python Advanced Features](#3-python-advanced-features)
4. [Pygame Basics](#4-pygame-basics)
5. [Matematika & Fisika](#5-matematika--fisika)
6. [Algoritma & Data Structures](#6-algoritma--data-structures)
7. [AI & Machine Learning Concepts](#7-ai--machine-learning-concepts)
8. [Software Design Patterns](#8-software-design-patterns)

---

## 1. Konsep Dasar Programming

### 1.1 Variables & Data Types
**File:** Semua file  
**Konsep yang digunakan:**
- `int`, `float`, `bool`, `str`
- Type hints: `float`, `int`, `bool`, `Optional[T]`
- Collections: `list`, `tuple`, `dict`

**Contoh di code:**
```python
# core/physics_engine.py
def __init__(
    self,
    acceleration_rate: float = 2.9,  # Type hint: float
    friction: float = 0.98,
    steering_rate: float = 5.0,
    max_speed: float = 4.0,
):
```

**Apa yang perlu dipelajari:**
- [ ] Tipe data primitif (int, float, bool, str)
- [ ] Type annotations di Python 3.5+
- [ ] Collections (list, dict, tuple, set)
- [ ] Optional dan Union types
- [ ] Generic types dengan typing module

**Tujuan:**
Memahami bagaimana data disimpan dan dimanipulasi dalam program.

---

### 1.2 Functions & Methods
**File:** Semua file  
**Konsep yang digunakan:**
- Function definition
- Parameters & arguments
- Return values
- Default parameters
- `*args` dan `**kwargs`

**Contoh di code:**
```python
# core/physics_engine.py
def calculate_movement(
    self, x: float, y: float, angle: float, velocity: float
) -> tuple[float, float]:  # Return type annotation
    """Docstring menjelaskan fungsi"""
    new_x = x + math.cos(angle) * velocity
    new_y = y + math.sin(angle) * velocity
    return new_x, new_y  # Return tuple
```

**Apa yang perlu dipelajari:**
- [ ] Function syntax dan calling
- [ ] Parameters: positional, keyword, default
- [ ] Return values dan multiple returns
- [ ] Docstrings untuk dokumentasi
- [ ] `*args` dan `**kwargs` untuk flexible arguments

**Tujuan:**
Membuat kode yang reusable dan modular.

---

### 1.3 Control Flow
**File:** `entities/ai_car.py`, `core/sensor.py`  
**Konsep yang digunakan:**
- `if`, `elif`, `else`
- `for` loops
- `while` loops
- List comprehensions

**Contoh di code:**
```python
# entities/ai_car.py
def simple_ai_behavior(self):
    if self.velocity < 2.0:
        # Drive forward
        if isinstance(self.controller, AIController):
            self.controller.set_input(0, 1)
    else:
        # Check sensors
        readings = self.get_sensor_readings()
        if readings and readings[2] < 0.3:  # Center sensor
            # Turn
            dx = random.choice([-1, 1])
            self.controller.set_input(dx, 1)
```

**Apa yang perlu dipelajari:**
- [ ] Conditional statements (if/elif/else)
- [ ] Boolean logic (and, or, not)
- [ ] Loops (for, while)
- [ ] Break dan continue
- [ ] List/dict comprehensions

**Tujuan:**
Mengontrol flow eksekusi program berdasarkan kondisi.

---

## 2. Object-Oriented Programming (OOP)

### 2.1 Classes & Objects
**File:** Semua file di `entities/` dan `core/`  
**Konsep yang digunakan:**
- Class definition
- `__init__` constructor
- Instance variables (`self.x`)
- Methods

**Contoh di code:**
```python
# entities/car.py
class Car:
    """Class adalah blueprint untuk membuat object"""
    
    def __init__(self, x: float, y: float):
        """Constructor dipanggil saat object dibuat"""
        self._x = x  # Instance variable (private)
        self._y = y
    
    def update(self, walls):
        """Method adalah function milik class"""
        # Process logic here
        pass
```

**Apa yang perlu dipelajari:**
- [ ] Class definition dengan `class` keyword
- [ ] `__init__` constructor
- [ ] `self` parameter
- [ ] Instance variables vs class variables
- [ ] Methods vs functions
- [ ] Creating instances (objects)

**Tujuan:**
Mengelompokkan data dan behavior terkait dalam satu unit.

---

### 2.2 Encapsulation
**File:** `entities/car.py`  
**Konsep yang digunakan:**
- Private attributes (`_x`, `_y`)
- Properties dengan `@property`
- Getter/setter pattern

**Contoh di code:**
```python
# entities/car.py
class Car:
    def __init__(self, x, y):
        # Private attributes (convention: _ prefix)
        self._x = x
        self._y = y
    
    @property
    def x(self) -> float:
        """Getter: read-only access to private _x"""
        return self._x
    
    @property
    def y(self) -> float:
        """Getter: read-only access to private _y"""
        return self._y
    
    # Tidak ada setter → x dan y read-only dari luar
```

**Apa yang perlu dipelajari:**
- [ ] Public vs private members
- [ ] Naming conventions (`_private`, `__very_private`)
- [ ] `@property` decorator
- [ ] `@property.setter` untuk setters
- [ ] Information hiding principle

**Tujuan:**
Menyembunyikan detail implementasi dan mengontrol akses ke data.

**Mengapa penting:**
- Mencegah modification yang tidak valid
- Memudahkan refactoring
- Validation bisa ditambahkan di setter

---

### 2.3 Inheritance
**File:** `entities/player_car.py`, `entities/ai_car.py`  
**Konsep yang digunakan:**
- Base class (parent)
- Derived class (child)
- `super()` untuk call parent
- Method overriding

**Contoh di code:**
```python
# entities/player_car.py
class PlayerCar(Car):  # PlayerCar inherits from Car
    """Child class extends parent class"""
    
    def __init__(self, x, y, color, image):
        # Create keyboard controller
        controller = KeyboardController()
        
        # Call parent constructor
        super().__init__(
            x, y, 
            controller=controller,
            enable_sensors=False
        )
    
    def draw(self, screen):
        """Override parent method"""
        super().draw(screen)  # Call parent version
        # Add player-specific drawing
```

**Apa yang perlu dipelajari:**
- [ ] Inheritance syntax (`class Child(Parent)`)
- [ ] `super()` untuk access parent
- [ ] Method overriding
- [ ] `isinstance()` dan `issubclass()`
- [ ] Multiple inheritance (advanced)
- [ ] Method Resolution Order (MRO)

**Tujuan:**
Code reuse dan specialization tanpa duplikasi.

**Contoh real-world:**
```
Animal
  ├─ Dog (inherits from Animal)
  └─ Cat (inherits from Animal)

Car
  ├─ PlayerCar (inherits from Car)
  └─ AICar (inherits from Car)
```

---

### 2.4 Polymorphism
**File:** `core/controller.py`  
**Konsep yang digunakan:**
- Abstract base classes
- Interface pattern
- Duck typing
- Method overriding

**Contoh di code:**
```python
# core/controller.py
from abc import ABC, abstractmethod

class BaseController(ABC):
    """Abstract base class = interface"""
    
    @abstractmethod
    def get_input(self) -> Tuple[float, float]:
        """Abstract method must be implemented by children"""
        pass

class KeyboardController(BaseController):
    def get_input(self) -> Tuple[float, float]:
        """Concrete implementation for keyboard"""
        keys = pygame.key.get_pressed()
        # ... process keys
        return dx, dy

class AIController(BaseController):
    def get_input(self) -> Tuple[float, float]:
        """Concrete implementation for AI"""
        return self.dx, self.dy

# Polymorphism in action:
def process_car(car):
    # Works with ANY controller that implements get_input()
    dx, dy = car.controller.get_input()
```

**Apa yang perlu dipelajari:**
- [ ] Abstract Base Classes (ABC module)
- [ ] `@abstractmethod` decorator
- [ ] Interface vs implementation
- [ ] Duck typing di Python
- [ ] Polymorphic behavior

**Tujuan:**
Same interface, different implementations. Code yang flexible.

**Analogy:**
```
"Semua mobil punya method drive(), tapi cara implementasinya beda:
- Manual car: gear shift manually
- Automatic car: no gear shift
Tapi dari luar, tinggal panggil car.drive()"
```

---

### 2.5 Composition
**File:** `entities/car.py`  
**Konsep yang digunakan:**
- Has-a relationship
- Dependency injection
- Component-based design

**Contoh di code:**
```python
# entities/car.py
class Car:
    """Car HAS-A physics engine, controller, sensors"""
    
    def __init__(
        self,
        controller: Optional[BaseController] = None,
        physics: Optional[PhysicsEngine] = None,
        enable_sensors: bool = False,
    ):
        # Composition: Car contains other objects
        self.physics = physics or PhysicsEngine()  # Has-a
        self.controller = controller  # Has-a
        self.sensors = SensorArray(...) if enable_sensors else None  # Has-a
    
    def update(self, walls):
        # Delegate to components
        dx, dy = self.controller.get_input()  # Use controller
        self.physics.update_velocity(...)  # Use physics
        self.sensors.update_all(...)  # Use sensors
```

**Apa yang perlu dipelajari:**
- [ ] Composition vs inheritance
- [ ] "Has-a" relationship
- [ ] Dependency injection pattern
- [ ] Component-based architecture
- [ ] Delegation pattern

**Tujuan:**
Flexible code, easy to test, loosely coupled.

**Composition vs Inheritance:**
```
Inheritance (is-a):
  Dog IS-A Animal

Composition (has-a):
  Car HAS-A Engine
  Car HAS-A Wheels
  Car HAS-A Sensors
```

**Mengapa composition lebih baik:**
- Flexible: bisa swap components
- Testable: bisa inject mock objects
- Reusable: components bisa dipakai di class lain

---

## 3. Python Advanced Features

### 3.1 Decorators
**File:** `entities/car.py`, `core/controller.py`  
**Konsep yang digunakan:**
- `@property`
- `@abstractmethod`
- Function decorators

**Contoh di code:**
```python
# entities/car.py
@property
def x(self) -> float:
    """@property makes method act like attribute"""
    return self._x

# Usage:
car = Car(100, 200)
print(car.x)  # Calls the method, no () needed
# car.x = 50  # Error! No setter defined

# core/controller.py
from abc import abstractmethod

@abstractmethod
def get_input(self) -> Tuple[float, float]:
    """@abstractmethod enforces implementation in children"""
    pass
```

**Apa yang perlu dipelajari:**
- [ ] Decorator syntax (`@decorator`)
- [ ] `@property` untuk getter/setter
- [ ] `@staticmethod` dan `@classmethod`
- [ ] `@abstractmethod` dari ABC
- [ ] Custom decorators (advanced)

**Tujuan:**
Memodifikasi behavior function/method tanpa ubah code-nya.

---

### 3.2 Type Hints & Annotations
**File:** Semua file  
**Konsep yang digunakan:**
- Type annotations (PEP 484)
- `Optional`, `Union`, `List`, `Tuple`
- Return type annotations

**Contoh di code:**
```python
# core/physics_engine.py
from typing import Tuple, Optional, List

def calculate_movement(
    self, 
    x: float,  # Parameter type
    y: float, 
    angle: float, 
    velocity: float
) -> Tuple[float, float]:  # Return type
    """Type hints help IDE and type checkers"""
    new_x = x + math.cos(angle) * velocity
    new_y = y + math.sin(angle) * velocity
    return new_x, new_y

# Optional type
def __init__(
    self,
    controller: Optional[BaseController] = None,  # Can be None
):
    pass
```

**Apa yang perlu dipelajari:**
- [ ] Basic type hints (int, float, str, bool)
- [ ] Collection types (List, Dict, Tuple, Set)
- [ ] Optional dan Union
- [ ] Generic types (List[int], Dict[str, float])
- [ ] Type checking tools (mypy)

**Tujuan:**
- Better IDE autocomplete
- Catch errors before runtime
- Self-documenting code

---

### 3.3 List Comprehensions
**File:** `core/sensor.py`  
**Konsep yang digunakan:**
- List comprehensions
- Generator expressions
- Conditional comprehensions

**Contoh di code:**
```python
# core/sensor.py
class SensorArray:
    def __init__(self, num_sensors: int = 5):
        # List comprehension
        angles = [
            math.radians(-90 + (180 / (num_sensors - 1)) * i)
            for i in range(num_sensors)
        ]
        
        # Another list comprehension
        self.sensors = [
            DistanceSensor(angle, max_range) 
            for angle in angles
        ]
    
    def get_readings(self) -> List[float]:
        # List comprehension dengan method call
        return [
            sensor.get_normalized_distance() 
            for sensor in self.sensors
        ]

# Equivalent tanpa list comprehension:
angles = []
for i in range(num_sensors):
    angle = math.radians(-90 + (180 / (num_sensors - 1)) * i)
    angles.append(angle)
```

**Apa yang perlu dipelajari:**
- [ ] Basic list comprehension syntax
- [ ] Conditional comprehensions
- [ ] Nested comprehensions
- [ ] Dict comprehensions
- [ ] Generator expressions

**Tujuan:**
Concise, readable, dan often faster code.

---

## 4. Pygame Basics

### 4.1 Pygame Initialization & Game Loop
**File:** `core/game_manager.py`, `main.py`  
**Konsep yang digunakan:**
- `pygame.init()`
- Display modes
- Clock dan FPS
- Event loop

**Contoh di code:**
```python
# core/game_manager.py
import pygame

pygame.init()  # Initialize pygame

# Create window
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption(title)

# Create clock for FPS control
clock = pygame.time.Clock()

# Game loop
running = True
while running:
    # Limit FPS
    dt_ms = clock.tick(60)  # 60 FPS
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update game state
    # ...
    
    # Draw everything
    screen.fill((0, 0, 0))  # Clear screen
    # ... draw sprites
    pygame.display.flip()  # Update display

pygame.quit()
```

**Apa yang perlu dipelajari:**
- [ ] `pygame.init()` dan `pygame.quit()`
- [ ] `pygame.display.set_mode()`
- [ ] `pygame.time.Clock()` dan `tick()`
- [ ] Event handling dengan `pygame.event.get()`
- [ ] Display update dengan `flip()` atau `update()`
- [ ] FPS limiting

**Tujuan:**
Membuat window dan game loop yang stabil.

---

### 4.2 Event Handling
**File:** `core/game_manager.py`, `core/controller.py`  
**Konsep yang digunakan:**
- Event types (QUIT, KEYDOWN, KEYUP)
- Keyboard input
- `pygame.key.get_pressed()`

**Contoh di code:**
```python
# core/game_manager.py
def handle_events(self):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Window close button
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # ESC key
                self.running = False

# core/controller.py
def get_input(self):
    keys = pygame.key.get_pressed()  # Current state of all keys
    
    if keys[pygame.K_w]:  # W key pressed?
        dy += 1
    if keys[pygame.K_s]:  # S key pressed?
        dy -= 1
```

**Apa yang perlu dipelajari:**
- [ ] Event types (QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN, etc)
- [ ] `pygame.event.get()` vs `pygame.event.poll()`
- [ ] `pygame.key.get_pressed()` untuk continuous input
- [ ] Key constants (K_w, K_a, K_s, K_d, K_ESCAPE)
- [ ] Mouse events

**Tujuan:**
Handle user input untuk interactive applications.

---

### 4.3 Drawing & Rendering
**File:** `entities/car.py`, `core/sensor.py`, `main.py`  
**Konsep yang digunakan:**
- Surface objects
- `blit()` method
- Drawing shapes (line, circle, rect)
- Image rotation

**Contoh di code:**
```python
# entities/car.py
def draw(self, screen):
    # Rotate image
    rotated_car = pygame.transform.rotate(
        self.image, 
        -math.degrees(self._angle)
    )
    
    # Get rect for positioning
    rect = rotated_car.get_rect(center=(self._x, self._y))
    
    # Draw to screen
    screen.blit(rotated_car, rect)
    
    # Draw line
    pygame.draw.line(
        screen, 
        (0, 255, 0),  # Color (R, G, B)
        (self._x, self._y),  # Start point
        (front_x, front_y),  # End point
        3  # Width
    )
    
    # Draw circle
    pygame.draw.circle(
        screen, 
        (255, 0, 0), 
        (int(front_x), int(front_y)), 
        4  # Radius
    )
```

**Apa yang perlu dipelajari:**
- [ ] Surface objects
- [ ] `blit()` untuk drawing surfaces
- [ ] `pygame.draw` functions (line, circle, rect, polygon)
- [ ] `pygame.transform` (rotate, scale, flip)
- [ ] `get_rect()` untuk positioning
- [ ] Color formats (RGB, RGBA)
- [ ] Alpha transparency

**Tujuan:**
Render graphics ke screen.

---

### 4.4 Collision Detection
**File:** `entities/car.py`  
**Konsep yang digunakan:**
- Rect objects
- `colliderect()` method

**Contoh di code:**
```python
# entities/car.py
def check_collision(self, walls: List[pygame.Rect]) -> bool:
    if not self.rect:
        return False
    
    for wall in walls:
        if self.rect.colliderect(wall):  # Check collision
            # Collision detected!
            # Revert position
            self._x, self._y = prev_x, prev_y
            # Apply bounce
            self._velocity = self.physics.resolve_collision(self._velocity)
            return True
    
    return False
```

**Apa yang perlu dipelajari:**
- [ ] `pygame.Rect` object
- [ ] `colliderect()` untuk rect-rect collision
- [ ] `collidepoint()` untuk point-rect collision
- [ ] `collidelist()` untuk multiple collisions
- [ ] Collision response (bounce, stop, etc)

**Tujuan:**
Detect when objects overlap/collide.

---

## 5. Matematika & Fisika

### 5.1 Trigonometry
**File:** `entities/car.py`, `core/physics_engine.py`, `core/sensor.py`  
**Konsep yang digunakan:**
- Sine, cosine, tangent
- Radian vs degrees
- `math.atan2()` untuk angle calculation

**Contoh di code:**
```python
# entities/car.py
import math

# Convert direction to angle
dx, dy = 1, 1  # Moving right-up
target_angle = math.atan2(-dy, dx)  # Get angle in radians

# Calculate position from angle and distance
new_x = x + math.cos(angle) * velocity
new_y = y + math.sin(angle) * velocity

# Draw direction indicator
front_x = self._x + math.cos(self._angle) * (self.length / 2)
front_y = self._y + math.sin(self._angle) * (self.length / 2)

# Convert radians to degrees for display
degrees = math.degrees(angle)
# Convert degrees to radians
radians = math.radians(90)
```

**Apa yang perlu dipelajari:**
- [ ] Unit circle concept
- [ ] Sine dan cosine untuk x/y components
- [ ] `math.atan2(y, x)` untuk angle dari vector
- [ ] Radian vs degree conversion
- [ ] `math.cos()`, `math.sin()`, `math.tan()`
- [ ] Pythagorean theorem: `distance = sqrt(dx² + dy²)`

**Tujuan:**
Convert antara angles dan directions untuk movement.

**Visual explanation:**
```
      y
      ↑
      |
  sin(θ)  / hypot
      | /
      |/θ
──────●─────→ x
    cos(θ)

angle = atan2(y, x)
x = cos(angle) * distance
y = sin(angle) * distance
```

---

### 5.2 Vector Math
**File:** `core/physics_engine.py`, `core/sensor.py`  
**Konsep yang digunakan:**
- 2D vectors
- Vector addition
- Magnitude (length)
- Normalization

**Contoh di code:**
```python
# Vector representation
position = (x, y)  # 2D vector
velocity_vector = (vx, vy)

# Vector addition (movement)
new_x = x + vx
new_y = y + vy

# Vector magnitude (distance)
import math
distance = math.hypot(dx, dy)  # sqrt(dx² + dy²)

# Direction vector from angle
direction_x = math.cos(angle)
direction_y = math.sin(angle)

# Scale vector
scaled_x = direction_x * speed
scaled_y = direction_y * speed
```

**Apa yang perlu dipelajari:**
- [ ] Vector representation (tuple, list, class)
- [ ] Vector addition dan subtraction
- [ ] Magnitude/length: `sqrt(x² + y²)`
- [ ] Normalization (unit vector)
- [ ] Dot product (advanced)
- [ ] Cross product (advanced)

**Tujuan:**
Represent dan manipulate position, velocity, direction.

---

### 5.3 Physics Simulation
**File:** `core/physics_engine.py`  
**Konsep yang digunakan:**
- Acceleration
- Velocity
- Friction
- Momentum
- Collision response

**Contoh di code:**
```python
# core/physics_engine.py

# Acceleration (change in velocity)
def apply_acceleration(self, velocity, accelerating):
    if accelerating:
        velocity += self.acceleration_rate  # F = ma
    return velocity

# Friction (opposing force)
def apply_friction(self, velocity):
    return velocity * self.friction  # Exponential decay

# Update velocity (integrate acceleration)
velocity = velocity + acceleration
velocity = velocity * friction
velocity = clamp(velocity, -max_speed, max_speed)

# Update position (integrate velocity)
new_x = x + velocity_x * delta_time
new_y = y + velocity_y * delta_time

# Collision response (bounce)
def resolve_collision(self, velocity, bounce_factor=-0.4):
    return velocity * bounce_factor  # Reverse and reduce
```

**Apa yang perlu dipelajari:**
- [ ] Newton's laws of motion
- [ ] Velocity = change in position / time
- [ ] Acceleration = change in velocity / time
- [ ] Friction as exponential decay
- [ ] Collision elasticity (bounce factor)
- [ ] Integration methods (Euler, RK4)
- [ ] Delta time untuk frame-independent physics

**Tujuan:**
Realistic movement simulation.

**Physics equations used:**
```
v(t+1) = v(t) + a * dt    (acceleration)
v(t+1) = v(t) * friction   (friction)
p(t+1) = p(t) + v * dt     (position)
```

---

### 5.4 Angle Calculations
**File:** `core/physics_engine.py`, `entities/car.py`  
**Konsep yang digunakan:**
- Angle normalization
- Angle difference
- Angle interpolation (steering)

**Contoh di code:**
```python
# Normalize angle to [-π, π]
def normalize_angle(self, angle):
    return (angle + math.pi) % (2 * math.pi) - math.pi

# Calculate shortest angle difference
def calculate_steering(self, current_angle, target_angle):
    # Normalize difference to [-π, π]
    angle_diff = (target_angle - current_angle + math.pi) % (2 * math.pi) - math.pi
    
    # Limit turn rate
    max_turn = math.radians(self.steering_rate)
    
    if abs(angle_diff) < max_turn:
        return target_angle  # Can reach target in one frame
    else:
        # Turn gradually
        return current_angle + max_turn * math.copysign(1, angle_diff)
```

**Apa yang perlu dipelajari:**
- [ ] Angle wrapping/normalization
- [ ] Shortest rotation direction
- [ ] Angle interpolation (lerp)
- [ ] `math.copysign()` untuk sign transfer
- [ ] Modulo operator untuk wrapping

**Tujuan:**
Smooth steering tanpa weird 360° spins.

**Why normalize angles:**
```
Without normalization:
angle = 7.5 (> 2π) → confusing, wraps around multiple times

With normalization:
angle = 1.2 (within [-π, π]) → clear, shortest path
```

---

## 6. Algoritma & Data Structures

### 6.1 Raycasting Algorithm
**File:** `core/sensor.py`  
**Konsep yang digunakan:**
- Ray-line intersection
- Parametric line equations
- Distance calculation

**Contoh di code:**
```python
# core/sensor.py
def _ray_line_intersection(
    self, rx, ry, rdx, rdy,  # Ray origin and direction
    x1, y1, x2, y2  # Line segment endpoints
):
    """
    Solve parametric equations:
    Ray:  P = (rx, ry) + t * (rdx, rdy)
    Line: Q = (x1, y1) + u * (x2-x1, y2-y1)
    
    Find t and u where P = Q
    """
    ldx = x2 - x1
    ldy = y2 - y1
    
    # Denominator of parametric solution
    denominator = rdx * ldy - rdy * ldx
    
    if abs(denominator) < 1e-10:  # Parallel lines
        return None
    
    # Solve for t and u
    t = ((x1 - rx) * ldy - (y1 - ry) * ldx) / denominator
    u = ((x1 - rx) * rdy - (y1 - ry) * rdx) / denominator
    
    # Check if intersection is valid
    if t > 0 and 0 <= u <= 1:
        hit_x = rx + t * rdx
        hit_y = ry + t * rdy
        return (hit_x, hit_y, t)
    
    return None
```

**Apa yang perlu dipelajari:**
- [ ] Parametric line representation
- [ ] Line-line intersection formula
- [ ] Ray vs line segment
- [ ] Epsilon comparison untuk floating point
- [ ] Geometric algorithms basics

**Tujuan:**
Detect obstacles in sensor's line of sight.

**Visual:**
```
    Ray origin (rx, ry)
         ●
          \
           \ direction (rdx, rdy)
            \
             ● Hit point
              |
    Wall: ────●────
```

---

### 6.2 Spatial Queries
**File:** `core/sensor.py`  
**Konsep yang digunakan:**
- Finding closest object
- Distance calculations
- Iteration optimization

**Contoh di code:**
```python
# core/sensor.py
def update_distance(self, walls, car_x, car_y, car_angle):
    # Find closest wall in sensor direction
    min_distance = self.max_range
    closest_hit = None
    
    for wall in walls:  # O(n) search
        hit_point = self._ray_rect_intersection(...)
        
        if hit_point:
            # Calculate distance
            dist = math.hypot(hit_point[0] - car_x, hit_point[1] - car_y)
            
            # Track closest
            if dist < min_distance:
                min_distance = dist
                closest_hit = hit_point
    
    return min_distance
```

**Apa yang perlu dipelajari:**
- [ ] Linear search O(n)
- [ ] Distance formula
- [ ] Min/max finding
- [ ] Spatial partitioning (advanced: quadtree, grid)

**Tujuan:**
Efficiently find closest obstacle.

---

### 6.3 State Machine (Simple AI)
**File:** `entities/ai_car.py`  
**Konsep yang digunakan:**
- State-based behavior
- Conditional logic
- Decision making

**Contoh di code:**
```python
# entities/ai_car.py
def simple_ai_behavior(self):
    """Simple state machine for AI"""
    
    # State 1: Accelerating
    if self.velocity < 2.0:
        self.controller.set_input(0, 1)  # Drive forward
    
    # State 2: Obstacle avoidance
    else:
        readings = self.get_sensor_readings()
        if readings and readings[2] < 0.3:  # Obstacle ahead
            # Turn away
            dx = random.choice([-1, 1])
            self.controller.set_input(dx, 1)
        else:
            # Continue forward
            self.controller.set_input(0, 1)
```

**Apa yang perlu dipelajari:**
- [ ] Finite State Machines (FSM)
- [ ] State transitions
- [ ] Behavior trees (advanced)
- [ ] Decision trees

**Tujuan:**
Organize AI logic into states/behaviors.

---

### 6.4 Lists & Iteration
**File:** Semua file  
**Konsep yang digunakan:**
- List operations
- Iteration patterns
- Filtering

**Contoh di code:**
```python
# List iteration
for sensor in self.sensors:
    sensor.update_distance(...)

# List comprehension (functional style)
readings = [sensor.get_normalized_distance() for sensor in self.sensors]

# Enumerate for index
for i, reading in enumerate(readings):
    print(f"Sensor {i}: {reading}")

# Filtering
active_sensors = [s for s in self.sensors if s.distance < threshold]

# Append
self.sensors.append(new_sensor)
```

**Apa yang perlu dipelajari:**
- [ ] List methods (append, remove, pop, insert)
- [ ] Indexing dan slicing
- [ ] Iteration (for loops)
- [ ] List comprehensions
- [ ] `enumerate()`, `zip()`
- [ ] Sorting dan filtering

**Tujuan:**
Manage collections of objects efficiently.

---

## 7. AI & Machine Learning Concepts

### 7.1 Sensors as Observations
**File:** `entities/ai_car.py`, `core/sensor.py`  
**Konsep yang digunakan:**
- State representation
- Observation space
- Normalized values [0, 1]

**Contoh di code:**
```python
# entities/ai_car.py
def get_state(self) -> dict:
    """Get current state for RL agent"""
    return {
        'position': (self.x, self.y),
        'angle': self.angle,
        'velocity': self.velocity,
        'sensor_readings': self.get_sensor_readings() or [],
    }

# Observation space untuk RL:
# - 5 sensor readings (normalized 0-1)
# - 1 velocity value
# - 1 angle value
# Total: 7 continuous values
```

**Apa yang perlu dipelajari:**
- [ ] State representation in RL
- [ ] Observation space design
- [ ] Normalization importance
- [ ] Feature engineering
- [ ] Sensor fusion

**Tujuan:**
Provide AI with information about environment.

---

### 7.2 Action Space
**File:** `entities/ai_car.py`, `core/controller.py`  
**Konsep yang digunakan:**
- Discrete vs continuous actions
- Action encoding

**Contoh di code:**
```python
# Discrete action space (9 actions):
# dx ∈ {-1, 0, 1}, dy ∈ {-1, 0, 1}
# 
# 0: (-1, -1)  left-back
# 1: (-1,  0)  left
# 2: (-1,  1)  left-forward
# 3: ( 0, -1)  back
# 4: ( 0,  0)  stop
# 5: ( 0,  1)  forward
# 6: ( 1, -1)  right-back
# 7: ( 1,  0)  right
# 8: ( 1,  1)  right-forward

def action_to_input(action: int) -> Tuple[float, float]:
    actions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1), (0, 0), (0, 1),
        (1, -1), (1, 0), (1, 1)
    ]
    return actions[action]

# Usage:
action = agent.select_action(state)
dx, dy = action_to_input(action)
ai_car.set_ai_input(dx, dy)
```

**Apa yang perlu dipelajari:**
- [ ] Discrete vs continuous action spaces
- [ ] Action encoding
- [ ] Exploration vs exploitation
- [ ] Action selection strategies

**Tujuan:**
Define what actions AI can take.

---

### 7.3 Reward Function Design
**File:** Not implemented yet (untuk future RL)  
**Konsep yang digunakan:**
- Reward shaping
- Sparse vs dense rewards
- Credit assignment

**Contoh untuk future:**
```python
def calculate_reward(state, action, next_state) -> float:
    """Design reward function for RL"""
    reward = 0.0
    
    # Positive: Moving forward
    if next_state['velocity'] > 0:
        reward += 0.1
    
    # Negative: Collision
    if collision_detected:
        reward -= 10.0
    
    # Positive: Staying away from walls
    min_sensor = min(next_state['sensor_readings'])
    if min_sensor > 0.5:
        reward += 0.5
    
    # Negative: Too close to wall
    if min_sensor < 0.2:
        reward -= 1.0
    
    return reward
```

**Apa yang perlu dipelajari:**
- [ ] Reward function principles
- [ ] Reward shaping
- [ ] Sparse vs dense rewards
- [ ] Terminal conditions
- [ ] Credit assignment problem

**Tujuan:**
Guide AI learning towards desired behavior.

---

### 7.4 Reinforcement Learning Basics
**File:** Future integration  
**Konsep yang digunakan:**
- Agent, environment, state, action, reward
- Policy
- Q-learning, DQN, PPO

**Future code structure:**
```python
# Gym environment wrapper
import gym

class CarEnv(gym.Env):
    def reset(self):
        # Reset car to start position
        return initial_state
    
    def step(self, action):
        # Execute action
        self.ai_car.set_ai_input(*action)
        self.ai_car.update(self.walls)
        
        # Get new state
        next_state = self.ai_car.get_state()
        
        # Calculate reward
        reward = self.calculate_reward(...)
        
        # Check if done
        done = self.check_collision() or self.timeout
        
        return next_state, reward, done, {}

# Training loop
for episode in range(1000):
    state = env.reset()
    while not done:
        action = agent.select_action(state)
        next_state, reward, done, _ = env.step(action)
        agent.learn(state, action, reward, next_state)
        state = next_state
```

**Apa yang perlu dipelajari:**
- [ ] RL fundamentals (agent, environment, MDP)
- [ ] Q-learning algorithm
- [ ] Deep Q-Networks (DQN)
- [ ] Policy gradient methods (PPO, A3C)
- [ ] Experience replay
- [ ] Exploration strategies (ε-greedy)

**Tujuan:**
Train AI to drive autonomously through trial and error.

---

## 8. Software Design Patterns

### 8.1 Dependency Injection
**File:** `entities/car.py`  
**Konsep yang digunakan:**
- Constructor injection
- Inversion of Control (IoC)

**Contoh di code:**
```python
# entities/car.py
class Car:
    def __init__(
        self,
        controller: Optional[BaseController] = None,  # Injected
        physics: Optional[PhysicsEngine] = None,      # Injected
    ):
        # Inject dependencies instead of creating them
        self.physics = physics or PhysicsEngine()
        self.controller = controller

# Usage:
custom_physics = PhysicsEngine(max_speed=10.0)
custom_controller = AIController()

car = Car(
    controller=custom_controller,  # Inject custom controller
    physics=custom_physics  # Inject custom physics
)

# Benefits:
# 1. Easy to swap implementations
# 2. Easy to test with mocks
# 3. Loose coupling
```

**Apa yang perlu dipelajari:**
- [ ] Dependency Injection pattern
- [ ] Constructor injection vs setter injection
- [ ] Inversion of Control principle
- [ ] Dependency Inversion Principle (SOLID)

**Tujuan:**
Flexible, testable code dengan loose coupling.

---

### 8.2 Strategy Pattern
**File:** `core/controller.py`  
**Konsep yang digunakan:**
- Interchangeable algorithms
- Polymorphic behavior

**Contoh di code:**
```python
# Strategy pattern: Different strategies for input
class BaseController(ABC):  # Strategy interface
    @abstractmethod
    def get_input(self):
        pass

class KeyboardController(BaseController):  # Concrete strategy 1
    def get_input(self):
        # Keyboard strategy
        return dx, dy

class AIController(BaseController):  # Concrete strategy 2
    def get_input(self):
        # AI strategy
        return self.dx, self.dy

# Context uses strategy
class Car:
    def __init__(self, controller: BaseController):
        self.controller = controller  # Store strategy
    
    def process_input(self):
        return self.controller.get_input()  # Use strategy
```

**Apa yang perlu dipelajari:**
- [ ] Strategy pattern
- [ ] Context and strategy roles
- [ ] When to use strategy pattern

**Tujuan:**
Swap algorithms at runtime without changing client code.

---

### 8.3 Component Pattern
**File:** `entities/car.py`  
**Konsep yang digunakan:**
- Entity-component architecture
- Composition over inheritance

**Contoh di code:**
```python
# Component pattern
class Car:
    """Entity with multiple components"""
    
    def __init__(self):
        # Components
        self.physics = PhysicsEngine()      # Physics component
        self.controller = KeyboardController()  # Input component
        self.sensors = SensorArray()        # Sensor component
    
    def update(self):
        # Delegate to components
        dx, dy = self.controller.get_input()
        self.physics.update_velocity(...)
        self.sensors.update_all(...)

# Benefits:
# - Add/remove components dynamically
# - Share components between entities
# - Clear separation of concerns
```

**Apa yang perlu dipelajari:**
- [ ] Component-based design
- [ ] Entity-Component-System (ECS)
- [ ] Composition vs inheritance tradeoffs

**Tujuan:**
Flexible entities yang bisa di-customize via components.

---

### 8.4 Template Method Pattern
**File:** `entities/car.py`  
**Konsep yang digunakan:**
- Define skeleton, let subclasses fill in
- Hook methods

**Contoh di code:**
```python
# entities/car.py
class Car:
    """Template method: update() defines skeleton"""
    
    def update(self, walls):
        """Template method - defines algorithm structure"""
        # 1. Get input (can be overridden)
        dx, dy = self.process_input()
        
        # 2. Update steering
        self.update_steering(dx, dy)
        
        # 3. Update position
        self.update_position()
        
        # 4. Check collisions
        self.check_collision(walls)
        
        # 5. Update sensors
        self.update_sensors(walls)
    
    def process_input(self):
        """Hook method - subclasses can override"""
        if self.controller:
            return self.controller.get_input()
        return 0, 0

# entities/ai_car.py
class AICar(Car):
    def update(self, walls):
        """Override to add AI behavior"""
        if self.ai_mode == "simple":
            self.simple_ai_behavior()  # AI decision making
        
        super().update(walls)  # Call template method
```

**Apa yang perlu dipelajari:**
- [ ] Template Method pattern
- [ ] Hook methods
- [ ] Hollywood Principle ("Don't call us, we'll call you")

**Tujuan:**
Define common algorithm structure, allow customization.

---

### 8.5 Factory Pattern (Implicit)
**File:** `entities/player_car.py`, `entities/ai_car.py`  
**Konsep yang digunakan:**
- Object creation abstraction
- Encapsulate creation logic

**Contoh di code:**
```python
# Implicit factory pattern in constructors

class PlayerCar(Car):
    def __init__(self, x, y):
        # Factory: create appropriate controller
        controller = KeyboardController()
        super().__init__(controller=controller)

class AICar(Car):
    def __init__(self, x, y):
        # Factory: create appropriate controller
        controller = AIController()
        super().__init__(controller=controller, enable_sensors=True)

# Usage is simple:
player = PlayerCar(100, 100)  # Automatically gets keyboard
ai_car = AICar(200, 200)      # Automatically gets AI + sensors
```

**Apa yang perlu dipelajari:**
- [ ] Factory Method pattern
- [ ] Abstract Factory pattern
- [ ] Simple Factory pattern

**Tujuan:**
Simplify object creation, hide complexity.

---

## 📚 Recommended Learning Path

### Level 1: Beginner (1-2 bulan)
1. ✅ Python basics (variables, functions, control flow)
2. ✅ OOP basics (classes, objects, methods)
3. ✅ Pygame basics (window, game loop, drawing)
4. ✅ Basic math (trigonometry, vectors)

### Level 2: Intermediate (2-3 bulan)
1. ✅ OOP advanced (inheritance, polymorphism, composition)
2. ✅ Python advanced (decorators, type hints, comprehensions)
3. ✅ Physics simulation basics
4. ✅ Algorithms (raycasting, collision detection)
5. ✅ Design patterns (strategy, dependency injection)

### Level 3: Advanced (3-6 bulan)
1. ✅ Software architecture (clean code, SOLID principles)
2. ✅ Testing (unit tests, mocks)
3. ✅ AI/ML basics (state space, action space, reward)
4. ✅ Reinforcement Learning (Q-learning, DQN)
5. ✅ Advanced patterns (ECS, state machines)

---

## 📖 Recommended Resources

### Python & OOP
- [ ] "Python Crash Course" by Eric Matthes
- [ ] "Fluent Python" by Luciano Ramalho
- [ ] Real Python (realpython.com)

### Pygame
- [ ] Pygame documentation (pygame.org/docs)
- [ ] "Making Games with Python & Pygame" (free)
- [ ] Al Sweigart's pygame tutorials

### Math & Physics
- [ ] Khan Academy - Trigonometry
- [ ] "Math for Game Developers" (YouTube - Jorge Rodriguez)
- [ ] "Game Physics Engine Development" by Ian Millington

### Design Patterns
- [ ] "Head First Design Patterns"
- [ ] Refactoring Guru (refactoring.guru)
- [ ] "Design Patterns: Elements of Reusable OO Software" (Gang of Four)

### AI & Reinforcement Learning
- [ ] "Reinforcement Learning: An Introduction" (Sutton & Barto)
- [ ] OpenAI Gym documentation
- [ ] "Deep Reinforcement Learning Hands-On" by Maxim Lapan

---

## 🎯 Study Tips

1. **Hands-on Learning**
   - Don't just read - code along
   - Modify existing code
   - Break things to understand them

2. **Small Steps**
   - Focus on one concept at a time
   - Master basics before advanced topics
   - Build small projects

3. **Documentation**
   - Read official docs
   - Write your own documentation
   - Explain concepts to others

4. **Debugging Skills**
   - Use print statements
   - Learn debugger (pdb)
   - Read error messages carefully

5. **Community**
   - Join Python/Pygame communities
   - Ask questions on Stack Overflow
   - Read others' code on GitHub

---

## ✅ Self-Assessment Checklist

Mark topics you understand:

### Python Basics
- [ ] Variables dan types
- [ ] Functions
- [ ] Control flow (if/for/while)
- [ ] Lists dan dicts
- [ ] File I/O

### OOP
- [ ] Classes dan objects
- [ ] Inheritance
- [ ] Polymorphism
- [ ] Encapsulation
- [ ] Composition

### Pygame
- [ ] Game loop
- [ ] Event handling
- [ ] Drawing
- [ ] Collision detection
- [ ] Sprite management

### Math
- [ ] Basic trigonometry
- [ ] Vectors
- [ ] Angle calculations
- [ ] Distance formulas

### Physics
- [ ] Velocity dan acceleration
- [ ] Friction
- [ ] Collision response

### Advanced
- [ ] Design patterns
- [ ] Type hints
- [ ] Testing
- [ ] AI concepts

---

## 🎓 Project-Based Learning

### Mini Projects untuk Practice:
1. **Pong Game** - Collision, velocity, score
2. **Maze Solver** - Pathfinding, algorithms
3. **Particle System** - Physics, vectors
4. **Simple Car Racer** - This project!
5. **AI Snake** - Reinforcement learning

---

**Selamat belajar! 🚀 Take it step by step, dan yang penting konsisten practice.**

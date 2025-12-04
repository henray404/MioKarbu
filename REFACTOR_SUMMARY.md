# 🚗 Tabrak Bahlil - Refactored Architecture

## 📋 Ringkasan Refaktorisasi

Sistem mobil telah di-refactor dengan **modular architecture** menggunakan prinsip OOP yang kuat:
- **Separation of Concerns** - Setiap komponen punya tanggung jawab tunggal
- **Composition over Inheritance** - Car menggunakan PhysicsEngine, Controller, Sensors
- **Polymorphism** - Different controllers (Keyboard/AI) dengan interface sama
- **Encapsulation** - Properties dengan @property decorator
- **Ready for AI/RL Integration** - Sensor system dan AIController siap untuk Reinforcement Learning

---

## 🏗️ Struktur Project

```
final_project/
│
├── core/                          # Core game systems
│   ├── __init__.py
│   ├── game_manager.py           # ✅ Game loop & window management
│   ├── physics_engine.py         # ✅ BARU: Fisika (acceleration, friction, steering)
│   ├── controller.py              # ✅ BARU: Input handling (Keyboard & AI)
│   └── sensor.py                  # ✅ BARU: Distance sensors dengan raycasting
│
├── entities/                      # Game entities
│   ├── __init__.py
│   ├── car.py                     # ✅ REFACTORED: Base class dengan composition
│   ├── player_car.py              # ✅ BARU: Player-controlled car
│   └── ai_car.py                  # ✅ BARU: AI-controlled car dengan sensors
│
├── asset/                         # Game assets
│   └── car_sprite.png
│
├── main.py                        # ✅ UPDATED: Entry point
├── requirements.txt               # Dependencies
└── README.md                      # This file
```

---

## 🔧 Perubahan File per File

### 1️⃣ **core/physics_engine.py** (BARU)

**Tanggung Jawab:** Semua logika fisika mobil

**Class:** `PhysicsEngine`

**Attributes:**
- `acceleration_rate` - Kecepatan akselerasi
- `friction` - Koefisien gesekan
- `steering_rate` - Kecepatan steering (derajat per frame)
- `max_speed` - Kecepatan maksimal

**Methods:**
```python
apply_acceleration(velocity, accelerating) -> float
apply_friction(velocity) -> float
update_velocity(velocity, accelerating) -> float
calculate_steering(current_angle, target_angle) -> float
normalize_angle(angle) -> float
resolve_collision(velocity, bounce_factor) -> float
calculate_movement(x, y, angle, velocity) -> tuple[float, float]
```

**Prinsip OOP:**
- **Single Responsibility** - Hanya handle fisika
- **Reusable** - Bisa digunakan untuk mobil jenis apapun

---

### 2️⃣ **core/controller.py** (BARU)

**Tanggung Jawab:** Interface untuk input (keyboard atau AI)

**Classes:**

#### `BaseController` (Abstract)
Interface untuk semua controller:
```python
@abstractmethod
def get_input() -> Tuple[float, float]:
    pass  # Returns (dx, dy)
```

#### `KeyboardController`
Untuk player dengan keyboard:
```python
__init__(forward_key, backward_key, left_key, right_key)
get_input() -> Tuple[float, float]  # Reads pygame keys
```

#### `AIController`
Untuk AI agent:
```python
set_input(dx, dy)  # Set by AI algorithm
get_input() -> Tuple[float, float]  # Returns AI decision
set_target_angle(angle)  # Alternative: direct angle control
move_forward(should_move)  # Simple command
```

**Prinsip OOP:**
- **Polymorphism** - Same interface, different implementations
- **Dependency Injection** - Car receives controller, tidak hardcoded

---

### 3️⃣ **core/sensor.py** (BARU)

**Tanggung Jawab:** Distance sensing dengan raycasting

**Classes:**

#### `DistanceSensor`
Single sensor dengan raycasting:
```python
__init__(angle_offset, max_range, color)
update_distance(walls, car_x, car_y, car_angle) -> float
draw(screen, car_x, car_y, car_angle)
get_normalized_distance() -> float  # 0=hit, 1=no obstacle
```

**Raycasting Algorithm:**
- Ray-rectangle intersection
- Parametric line intersection
- Finds closest obstacle

#### `SensorArray`
Manage multiple sensors:
```python
__init__(num_sensors, max_range)  # Default: 5 sensors, -90° to +90°
update_all(walls, car_x, car_y, car_angle) -> List[float]
draw_all(screen, car_x, car_y, car_angle)
get_readings() -> List[float]
```

**Prinsip OOP:**
- **Encapsulation** - Sensor logic tersembunyi
- **Ready for AI** - Output normalized untuk neural networks

---

### 4️⃣ **entities/car.py** (REFACTORED)

**Tanggung Jawab:** Base class untuk semua mobil

**Perubahan Besar:**

**SEBELUM:**
```python
class Car:
    def __init__(self, x, y, ...):
        self.acceleration_rate = 2.9  # ❌ Physics hardcoded
        self.friction = 0.98
        # ... mixed responsibilities
    
    def handle_input(self, keys):  # ❌ Hardcoded keyboard
        if keys[pygame.K_w]: ...
```

**SESUDAH:**
```python
class Car:
    def __init__(
        self, x, y, 
        controller: BaseController,      # ✅ Injected
        physics: PhysicsEngine,          # ✅ Injected
        enable_sensors: bool,            # ✅ Optional sensors
    ):
        self._x, self._y = x, y          # ✅ Private attributes
        self.physics = physics           # ✅ Composition
        self.controller = controller     # ✅ Composition
        self.sensors = SensorArray(...) if enable_sensors else None
```

**Properties (Encapsulation):**
```python
@property
def x(self) -> float: return self._x

@property
def y(self) -> float: return self._y

@property
def angle(self) -> float: return self._angle

@property
def velocity(self) -> float: return self._velocity
```

**Update Cycle (Separated):**
```python
def update(self, walls):
    # 1. Get input from controller
    dx, dy = self.process_input()
    
    # 2. Update steering & velocity (via physics)
    self.update_steering(dx, dy)
    
    # 3. Update position
    self.update_position()
    
    # 4. Check collisions
    self.check_collision(walls)
    
    # 5. Update sensors
    self.update_sensors(walls)
```

**Methods:**
```python
process_input() -> tuple[float, float]
update_steering(dx, dy)
update_position()
check_collision(walls) -> bool
update_sensors(walls) -> List[float]
draw(screen)
get_sensor_readings() -> List[float]
set_debug_mode(enabled)
```

**Prinsip OOP:**
- **Composition** - Has-a relationship dengan physics, controller, sensors
- **Encapsulation** - Private attributes dengan property accessors
- **Single Responsibility** - Setiap method punya tujuan jelas

---

### 5️⃣ **entities/player_car.py** (BARU)

**Tanggung Jawab:** Player-controlled car

```python
class PlayerCar(Car):
    def __init__(self, x, y, color, image, ...):
        controller = KeyboardController(...)  # Create keyboard controller
        super().__init__(
            x, y, 
            controller=controller,  # Inject keyboard controller
            enable_sensors=False,   # Player doesn't need sensors
        )
```

**Features:**
- WASD controls (configurable keys)
- Optional debug info display
- Inherits all Car behavior

**Prinsip OOP:**
- **Inheritance** - Extends Car
- **Specialization** - Player-specific features

---

### 6️⃣ **entities/ai_car.py** (BARU)

**Tanggung Jawab:** AI-controlled car dengan sensors

```python
class AICar(Car):
    def __init__(self, x, y, color, image, num_sensors=5, ...):
        controller = AIController()  # Create AI controller
        super().__init__(
            x, y,
            controller=controller,
            enable_sensors=True,      # ✅ AI needs sensors
            num_sensors=num_sensors,
        )
        self.ai_mode = "simple"  # simple, rl, etc.
```

**Methods:**
```python
set_ai_input(dx, dy)           # Set AI decision
simple_ai_behavior()           # Simple demo AI
update(walls)                  # Override: add AI decision
get_state() -> dict            # For RL: position, angle, velocity, sensors
set_rl_mode(enabled)           # Switch to RL mode
```

**Simple AI Behavior:**
- Drive forward
- Check center sensor
- Turn if obstacle detected

**Ready for RL:**
```python
state = ai_car.get_state()
# {
#   'position': (x, y),
#   'angle': 1.57,
#   'velocity': 3.2,
#   'sensor_readings': [0.8, 0.9, 0.3, 0.9, 0.8]
# }
```

**Prinsip OOP:**
- **Inheritance** - Extends Car
- **Specialization** - AI-specific features
- **Open/Closed** - Open for extension (RL), closed for modification

---

### 7️⃣ **main.py** (UPDATED)

**Perubahan:**

**SEBELUM:**
```python
player = Car(400, 300, ...)  # ❌ Generic Car
ai_car = Car(200, 150, ...)  # ❌ Same class for AI

def custom_update():
    keys = pygame.key.get_pressed()
    player.handle_input(keys)  # ❌ Manual input handling
    player.update(walls)
```

**SESUDAH:**
```python
# ✅ Specialized classes
player = PlayerCar(
    x=400, y=300,
    enable_sensors=False,  # Player doesn't need sensors
)

ai_car = AICar(
    x=200, y=150,
    num_sensors=5,         # AI gets 5 sensors
    sensor_range=200.0,
)

# ✅ Set modes
player.set_debug_mode(True)
ai_car.set_debug_mode(True)
ai_car.ai_mode = "simple"

# ✅ Simple update - controller handled internally
def update_wrapper(*args, **kwargs):
    return original_update(walls)  # Cars handle their own input
```

**Controls:**
- `WASD` - Player car control
- `F1` - Toggle player debug
- `F2` - Toggle AI debug (sensors)
- `ESC/X` - Quit

---

## ✅ Validasi Hasil Akhir

### ✓ Struktur File
- [x] File terstruktur sesuai hierarki
- [x] Semua file di lokasi yang benar
- [x] No circular imports

### ✓ Single Responsibility
- [x] `PhysicsEngine` - Only physics
- [x] `Controller` - Only input
- [x] `Sensor` - Only distance detection
- [x] `Car` - Coordinate components

### ✓ Functionality
- [x] Player car dengan keyboard ✅
- [x] AI car dengan input buatan ✅
- [x] Sensors tampil di debug mode ✅
- [x] Collision detection works ✅
- [x] No crashes, stable FPS ✅

### ✓ OOP Principles
- [x] **Encapsulation** - Properties, private attributes
- [x] **Composition** - Car has-a Physics, Controller, Sensors
- [x] **Inheritance** - PlayerCar/AICar extends Car
- [x] **Polymorphism** - Different controllers, same interface
- [x] **Abstraction** - BaseController abstract class

### ✓ AI Ready
- [x] Sensor system dengan raycasting
- [x] AIController untuk external control
- [x] `get_state()` untuk RL observations
- [x] Normalized sensor readings (0-1)

---

## 🎮 Cara Menjalankan

```powershell
# Install dependencies
python -m pip install -r requirements.txt

# Run game
python main.py
```

**Controls:**
- `W` - Forward
- `S` - Backward
- `A` - Turn left
- `D` - Turn right
- `F1` - Toggle player debug
- `F2` - Toggle AI sensors
- `ESC` - Quit

---

## 🤖 Integrasi RL (Future)

Sistem ini **siap untuk Reinforcement Learning**:

### 1. Observation Space
```python
state = ai_car.get_state()
obs = {
    'sensor_readings': [0.8, 0.9, 0.3, 0.9, 0.8],  # 5 floats [0-1]
    'velocity': 3.2,                                 # float
    'angle': 1.57,                                   # float [0-2π]
}
```

### 2. Action Space
```python
# Discrete: 9 actions (3x3 grid)
# dx: [-1, 0, 1]
# dy: [-1, 0, 1]
action = env.action_space.sample()
dx, dy = action_to_direction(action)
ai_car.set_ai_input(dx, dy)
```

### 3. Reward Function
```python
def calculate_reward(state, action, next_state):
    # Positive: moving forward, avoiding walls
    # Negative: collision, stopping
    return reward
```

### 4. Training Loop
```python
for episode in range(1000):
    state = ai_car.get_state()
    action = agent.select_action(state)
    ai_car.set_ai_input(*action)
    ai_car.update(walls)
    next_state = ai_car.get_state()
    reward = calculate_reward(...)
    agent.learn(state, action, reward, next_state)
```

---

## 📊 Perbandingan SEBELUM vs SESUDAH

| Aspek | SEBELUM | SESUDAH |
|-------|---------|---------|
| **Physics** | Hardcoded di Car | PhysicsEngine class |
| **Input** | Hardcoded keyboard | Controller interface |
| **Sensors** | ❌ Tidak ada | ✅ Raycasting sensors |
| **Player** | Generic Car | Specialized PlayerCar |
| **AI** | Generic Car | Specialized AICar |
| **Modularity** | ❌ Low | ✅ High |
| **Testability** | ❌ Hard | ✅ Easy (inject mocks) |
| **RL Ready** | ❌ No | ✅ Yes |
| **Code Reuse** | ❌ Copy-paste | ✅ Composition |

---

## 🎯 Next Steps (Opsional)

1. **Add More AI Behaviors**
   - Pathfinding (A*)
   - Genetic Algorithm
   - Neural Network controller

2. **Gym Environment**
   ```python
   import gym
   class CarEnv(gym.Env):
       def __init__(self):
           self.ai_car = AICar(...)
       def step(self, action):
           ...
   ```

3. **Multi-Agent**
   - Multiple AI cars
   - Competition/cooperation

4. **Better Sensors**
   - LIDAR-style 360° sensors
   - Object detection (other cars)

5. **Training Dashboard**
   - Real-time metrics
   - Reward graphs
   - Best policy visualization

---

## 📝 Dependencies

```
pygame>=2.6.0
numpy>=1.26
opencv-python>=4.10
pyautogui>=0.9.54
mlxtend==0.23.4
```

---

## 🎓 Konsep OOP yang Digunakan

### 1. **Encapsulation**
- Private attributes (`_x`, `_y`, `_angle`, `_velocity`)
- Public properties (`@property`)
- Internal methods hidden

### 2. **Composition (Has-A)**
- Car **has-a** PhysicsEngine
- Car **has-a** Controller
- Car **has-a** SensorArray

### 3. **Inheritance (Is-A)**
- PlayerCar **is-a** Car
- AICar **is-a** Car
- KeyboardController **is-a** BaseController

### 4. **Polymorphism**
- Different controllers, same `get_input()` interface
- Different cars, same `update()` and `draw()` methods

### 5. **Abstraction**
- `BaseController` abstract base class
- Implementation details hidden

### 6. **Dependency Injection**
- Car receives physics, controller, sensors
- Easy to test, easy to swap implementations

---

## 👨‍💻 Author

Refactored architecture for OOP final project - modular, scalable, AI-ready car simulation system.

---

**✅ Refaktorisasi Selesai!**

Sistem sekarang:
- ✅ Modular dan scalable
- ✅ Siap untuk AI/RL
- ✅ Clean architecture
- ✅ Easy to test and extend
- ✅ OOP principles applied correctly

# 📁 motor.py

> Path: `src/core/motor.py`

## Deskripsi

**Class terpenting dalam game!** Menghandle semua logic untuk motor baik player maupun AI:

- Physics (speed, steering, drift, grip)
- Collision detection
- Checkpoint & lap counting
- AI radar system

---

## Class: `Motor`

### Constructor

```python
def __init__(self, x, y, color="pink")
```

| Parameter | Deskripsi                            |
| --------- | ------------------------------------ |
| `x, y`    | Posisi spawn awal                    |
| `color`   | Nama warna motor (untuk load sprite) |

---

## 📐 Physics Constants

### Speed & Acceleration

```python
self.acceleration_rate = 0.12      # Akselerasi per frame
self.brake_power = 0.25            # Kekuatan rem
self.friction = 0.985              # Gesekan (1.0 = tanpa gesekan)
self.max_speed = 30                # Kecepatan maksimum
```

### Steering - Speed Dependent

```python
self.base_steering_rate = 4.5      # Derajat/frame saat lambat
self.min_steering_rate = 1.2       # Derajat/frame saat max speed
```

**Rumus:**

```
steering_rate = base - (base - min) × speed_ratio

Dimana speed_ratio = velocity / max_speed (0.0 - 1.0)
```

**Contoh:**
| Speed | speed_ratio | Steering Rate |
|-------|-------------|---------------|
| 0 | 0.0 | 4.5°/frame |
| 15 | 0.5 | 2.85°/frame |
| 30 | 1.0 | 1.2°/frame |

### Grip & Traction

```python
self.grip = 1.0                    # Grip saat ini (0.0-1.0)
self.base_grip = 1.0               # Grip dasar
self.turn_grip_loss = 0.15         # Kehilangan grip saat belok tajam
self.speed_grip_factor = 0.7       # Faktor grip di speed tinggi
```

### Turn Physics

```python
self.turn_speed_penalty = 0.02     # Kehilangan speed saat belok (2%)
self.sharp_turn_threshold = 0.5    # Threshold belok tajam
self.understeer_factor = 0.3       # Understeer di speed tinggi (30%)
```

### Inertia & Weight Transfer

```python
self.lateral_velocity = 0          # Velocity samping (sliding)
self.lateral_friction = 0.92       # Gesekan lateral
self.weight_transfer = 0           # Weight transfer saat gas/rem
```

---

## 🎮 Method: `handle_input(keys)`

Kontrol player dengan physics realistis.

### 1. Acceleration & Braking

```python
if keys[K_w]:  # Gas
    speed_ratio = abs(velocity) / max_speed
    accel_modifier = 1.0 - (speed_ratio * 0.5)  # Drag effect
    velocity += acceleration_rate * accel_modifier
    weight_transfer = 0.3
elif keys[K_s]:  # Rem
    velocity -= brake_power
    weight_transfer = -0.5
```

**Drag Effect:**
Akselerasi berkurang mendekati max speed.

```
effective_accel = base_accel × (1 - speed_ratio × 0.5)

Di 100% speed: effective = base × 0.5 (50% akselerasi)
```

### 2. Speed-Dependent Steering

```python
speed_ratio = abs(velocity) / max_speed
steering_rate = base_steering_rate - (
    (base_steering_rate - min_steering_rate) * speed_ratio
)
```

### 3. Normal Steering with Understeer

```python
steer_amount = radians(steering_rate) * steering_input
understeer = 1.0 - (speed_ratio * understeer_factor)
steer_amount *= understeer
angle += steer_amount
```

**Understeer:**
Di kecepatan tinggi, motor cenderung lurus.

```
effective_steer = base_steer × (1 - speed_ratio × 0.3)

Di 100% speed: effective = base × 0.7 (70% efektivitas steering)
```

### 4. Speed Penalty saat Belok

```python
if abs(steering_input) > 0:
    turn_intensity = abs(steering_input) * speed_ratio
    speed_loss = turn_speed_penalty * turn_intensity
    velocity *= (1.0 - speed_loss)
```

### 5. Drift Mode

```python
if is_drifting and steering_input != 0:
    drift_steer = base_steering_rate * 1.5  # 50% lebih tajam
    angle += radians(drift_steer) * steering_input

    drift_angle += steering_input * 0.08
    drift_angle = clamp(drift_angle, -0.5, 0.5)  # Max ~28°

    velocity *= 0.995  # Speed penalty
    grip = max(0.3, grip - 0.05)  # Lose grip
```

---

## 🤖 Method: `steer(direction)`

Steering untuk AI dengan physics yang sama.

```python
def steer(self, direction: int):
    # direction: -1 (kanan), 0 (lurus), 1 (kiri)

    speed_ratio = abs(velocity) / max_speed

    # Speed-dependent steering rate
    current_steer_rate = base_steering_rate - (
        (base_steering_rate - min_steering_rate) * speed_ratio
    )

    # Understeer
    understeer = 1.0 - (speed_ratio * understeer_factor)
    steer_amount = radians(current_steer_rate) * understeer

    if direction == 1:
        angle += steer_amount
    elif direction == -1:
        angle -= steer_amount

    # Speed penalty
    if direction != 0:
        velocity *= (1.0 - turn_speed_penalty * speed_ratio)
```

---

## 📡 AI Radar System

### Konstanta

```python
self.radar_angles = [-90, -45, 0, 45, 90]  # Derajat relatif
self.max_radar_length = 300  # Pixel
self.num_radars = 5
```

### Method: `_update_radars(track_surface)`

**Raycast Algorithm:**

```python
for degree in radar_angles:
    length = 0
    while length < max_radar_length:
        # Hitung posisi
        radar_angle = radians(360 - (angle_deg + degree))
        x = int(self.x + cos(radar_angle) * length)
        y = int(self.y + sin(radar_angle) * length)

        # Cek wall (warna merah)
        if is_red_wall(x, y):
            break

        length += 5  # Step

    radars.append(((x, y), length))
```

**Matematika:**

```
Position(t) = Origin + Direction × t

Direction = (cos(θ), sin(θ))
t = jarak dari origin
```

### Method: `get_radar_data()`

Return data ternormalisasi untuk neural network.

```python
def get_radar_data(self):
    data = [int(radar[1] / 30) for radar in self.radars]
    return data  # 5 values, scale 0-10
```

---

## 🏁 Checkpoint System

### Warna Checkpoint (Sequential)

| CP  | Warna   | RGB Condition       |
| --- | ------- | ------------------- |
| 1   | Hijau   | g>150, r<150, b<150 |
| 2   | Cyan    | g>150, b>150, r<150 |
| 3   | Kuning  | r>150, g>150, b<150 |
| 4   | Magenta | r>150, b>150, g<150 |

### Logic

```python
# Harus sequential
if detected_cp == expected_checkpoint:
    checkpoint_count += 1
    expected_checkpoint = (expected_checkpoint % 4) + 1
    print(f"[CP OK] CP{detected_cp} passed!")
```

### Lap Validation

```python
# Di _check_lap()
if checkpoint_count >= 4:  # Semua checkpoint dilalui
    lap_count += 1
    checkpoint_count = 0
    expected_checkpoint = 1  # Reset
```

---

## 🔄 Collision Detection

### Masking Colors

| Warna     | Kondisi      | Aksi                     |
| --------- | ------------ | ------------------------ |
| Hitam     | avg < 50     | Track OK                 |
| Putih/Abu | avg > 50     | Slow zone (speed × 0.99) |
| Merah     | r>150, g<100 | Wall (bounce/explode)    |

### Wall Collision

```python
if is_red:
    if abs(velocity) > wall_explode_speed:  # > 8
        alive = False  # Meledak!
    else:
        velocity = -velocity * 0.4  # Bounce back
        x, y = prev_x, prev_y
```

---

## 📊 Speedometer

```python
def get_speed_kmh(self):
    return int(abs(velocity) * 7.5)
```

**Scale:**
| velocity | km/h |
|----------|------|
| 0 | 0 |
| 15 | 112 |
| 30 | 225 |

---

## Diagram Physics

```
┌─────────────────────────────────────────────────────────────┐
│                    MOTOR PHYSICS FLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input (W/A/S/D/Space)                                       │
│     │                                                        │
│     ├── handle_input()                                       │
│     │      ├── Acceleration with drag                        │
│     │      ├── Calculate speed_ratio                         │
│     │      ├── Calculate steering_rate (speed-dependent)    │
│     │      ├── Apply understeer                              │
│     │      ├── Apply speed penalty                           │
│     │      └── Handle drift if Space pressed                 │
│     │                                                        │
│     └── update()                                             │
│            ├── Calculate new position                        │
│            ├── Check collision                               │
│            │      ├── Slow zone → speed × 0.99               │
│            │      └── Wall → bounce or explode               │
│            ├── Update checkpoints                            │
│            └── Check lap completion                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

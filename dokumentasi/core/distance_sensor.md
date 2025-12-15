# 📁 distance_sensor.py

> Path: `src/core/distance_sensor.py`

## Deskripsi

Sensor jarak berbasis raycasting untuk AI. Bisa di-attach ke motor untuk training NEAT.

---

## Class: `DistanceSensor`

### Constructor

```python
def __init__(self, num_sensors: int = 5, fov: float = 180,
             max_distance: float = 200)
```

| Parameter      | Default | Deskripsi               |
| -------------- | ------- | ----------------------- |
| `num_sensors`  | 5       | Jumlah ray sensor       |
| `fov`          | 180     | Field of view (derajat) |
| `max_distance` | 200     | Jarak maksimum (pixel)  |

### Atribut

```python
self.num_sensors = 5
self.fov = radians(180)        # Convert ke radian
self.max_distance = 200
self.step_size = 5              # Step raycast (pixel)

# Cache hasil
self.distances = [max_distance] * num_sensors
self.normalized = [1.0] * num_sensors
self.hit_points = []

# Reference ke track
self.track = None
```

---

## Method

### `set_track(track)`

Set track untuk collision detection.

```python
def set_track(self, track):
    self.track = track
```

### `_raycast(start_x, start_y, angle)`

Single raycast ke arah tertentu.

```python
def _raycast(self, start_x, start_y, angle):
    if self.track is None:
        return self.max_distance, (start_x, start_y)

    dx = cos(angle)
    dy = sin(angle)

    distance = 0
    while distance < self.max_distance:
        check_x = start_x + dx * distance
        check_y = start_y + dy * distance

        # Bounds check
        if check_x < 0 or check_x >= track.width or \
           check_y < 0 or check_y >= track.height:
            return distance, (check_x, check_y)

        # Wall check
        if self.track.is_wall(check_x, check_y):
            return distance, (check_x, check_y)

        distance += self.step_size

    # Max distance reached
    end_x = start_x + dx * self.max_distance
    end_y = start_y + dy * self.max_distance
    return self.max_distance, (end_x, end_y)
```

### `update(x, y, angle)`

Update semua sensor dari posisi motor.

```python
def update(self, x, y, angle):
    self.distances = []
    self.hit_points = []

    # Spread sensors across FOV
    start_angle = angle - self.fov / 2
    angle_step = self.fov / (self.num_sensors - 1)

    for i in range(self.num_sensors):
        sensor_angle = start_angle + i * angle_step
        dist, hit = self._raycast(x, y, sensor_angle)
        self.distances.append(dist)
        self.hit_points.append(hit)

    # Update normalized
    self.normalized = [d / self.max_distance for d in self.distances]

    return self.distances
```

---

## 📐 Matematika

### FOV Distribution

```
num_sensors = 5
fov = 180° = π radian

start_angle = motor_angle - π/2 = motor_angle - 90°
angle_step = π / 4 = 45°

Sensor angles (relative):
[0] = -90° (kiri penuh)
[1] = -45° (kiri depan)
[2] = 0°   (depan)
[3] = +45° (kanan depan)
[4] = +90° (kanan penuh)
```

**Diagram:**

```
            [2] 0°
              ↑
     [1] -45° ↖  ↗ +45° [3]
               M
    [0] -90° ←   → +90° [4]
```

### Normalisasi

```python
normalized = distance / max_distance
```

| Distance | Normalized | Meaning              |
| -------- | ---------- | -------------------- |
| 0        | 0.0        | Sangat dekat tembok! |
| 100      | 0.5        | Setengah jarak       |
| 200      | 1.0        | Aman (max distance)  |

---

## Output Methods

### `get_distances()`

Return jarak raw (0 - max_distance).

### `get_normalized()`

Return jarak ternormalisasi (0.0 - 1.0).

```python
def get_normalized(self):
    return self.normalized  # [0.0-1.0] untuk setiap sensor
```

### `get_angles(base_angle)`

Return sudut absolut setiap sensor.

```python
def get_angles(self, base_angle):
    start_angle = base_angle - self.fov / 2
    angle_step = self.fov / (self.num_sensors - 1)
    return [start_angle + i * angle_step for i in range(num_sensors)]
```

---

## Visualisasi

### `draw(screen, camera, x, y, angle)`

Gambar visualisasi sensor untuk debugging.

```python
def draw(self, screen, camera, x, y, angle):
    self.update(x, y, angle)  # Update dulu

    angles = self.get_angles(angle)

    for sensor_angle, dist, hit in zip(angles, self.distances, self.hit_points):
        # Color gradient: merah (dekat) → hijau (jauh)
        ratio = dist / self.max_distance
        color = (int(255 * (1 - ratio)), int(255 * ratio), 0)

        # Screen coordinates
        screen_start = (int(x - camera.x), int(y - camera.y))
        screen_end = (int(hit[0] - camera.x), int(hit[1] - camera.y))

        # Draw
        pg.draw.line(screen, color, screen_start, screen_end, 2)
        pg.draw.circle(screen, (255, 0, 0), screen_end, 4)
```

---

## Penggunaan

```python
# Buat sensor
sensor = DistanceSensor(num_sensors=5, fov=180, max_distance=200)
sensor.set_track(track)

# Update dan get data untuk neural network
sensor.update(motor.x, motor.y, motor.angle)
inputs = sensor.get_normalized()  # [0.x, 0.x, 0.x, 0.x, 0.x]

# Visualisasi (optional)
sensor.draw(screen, camera, motor.x, motor.y, motor.angle)
```

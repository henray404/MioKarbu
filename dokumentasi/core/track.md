# 📁 track.py

> Path: `src/core/track.py`

## Deskripsi

Class untuk mengelola track/sirkuit racing. Handle:

- Loading gambar track
- Collision detection berbasis pixel brightness
- Raycast untuk sensor AI

---

## Class: `Track`

### Constructor

```python
def __init__(self, name: str, screen_width: int = 1920,
             screen_height: int = 1440, road_threshold: int = 100)
```

| Parameter        | Default | Deskripsi                        |
| ---------------- | ------- | -------------------------------- |
| `name`           | -       | Nama file track (tanpa .png)     |
| `screen_width`   | 1920    | Lebar tampilan                   |
| `screen_height`  | 1440    | Tinggi tampilan                  |
| `road_threshold` | 100     | Threshold brightness untuk jalan |

---

## Konsep Brightness

Track menggunakan **brightness pixel** untuk menentukan jalan vs tembok:

```
brightness = R × 0.299 + G × 0.587 + B × 0.114
```

**Standar Grayscale (Luminance):**

- Rumus ini mengikuti persepsi mata manusia
- Hijau paling sensitif (0.587), merah tengah (0.299), biru terendah (0.114)

| Brightness | Interpretasi                |
| ---------- | --------------------------- |
| < 100      | Jalan (gelap/abu-abu gelap) |
| ≥ 100      | Tembok/Grass (terang)       |

---

## Method

### `get_pixel_at(x, y)`

Dapatkan warna RGB pixel di posisi tertentu.

```python
def get_pixel_at(self, x, y):
    x = clamp(x, 0, width - 1)
    y = clamp(y, 0, height - 1)
    return self.image.get_at((x, y))  # (R, G, B, A)
```

### `get_brightness_at(x, y)`

Dapatkan brightness (0-255).

```python
def get_brightness_at(self, x, y):
    color = self.get_pixel_at(x, y)
    return color[0] * 0.299 + color[1] * 0.587 + color[2] * 0.114
```

### `is_road(x, y)`

Cek apakah posisi adalah jalan.

```python
def is_road(self, x, y):
    brightness = self.get_brightness_at(x, y)
    return brightness < self.road_threshold  # < 100
```

### `is_wall(x, y)`

Kebalikan dari `is_road()`.

```python
def is_wall(self, x, y):
    return not self.is_road(x, y)
```

---

## Collision Detection

### `check_collision(x, y, width, height)`

Cek collision untuk area rectangular.

```python
def check_collision(self, x, y, width=10, height=10):
    half_w = width / 2
    half_h = height / 2

    # Check 5 titik: center + 4 corner
    check_points = [
        (x, y),                        # center
        (x - half_w, y - half_h),      # top-left
        (x + half_w, y - half_h),      # top-right
        (x - half_w, y + half_h),      # bottom-left
        (x + half_w, y + half_h),      # bottom-right
    ]

    for px, py in check_points:
        if self.is_wall(px, py):
            return True
    return False
```

**Diagram:**

```
    ┌───────────────┐
    │ TL         TR │
    │       C       │  → Check semua 5 titik
    │ BL         BR │
    └───────────────┘
```

---

## Raycast System

### `raycast(start_x, start_y, angle, max_distance)`

Raycast untuk sensor AI - mencari jarak ke tembok terdekat.

```python
def raycast(self, start_x, start_y, angle, max_distance=300):
    dx = cos(angle)  # Direction X
    dy = sin(angle)  # Direction Y

    distance = 0
    step = 5  # Step size (pixel)

    while distance < max_distance:
        check_x = start_x + dx * distance
        check_y = start_y + dy * distance

        # Out of bounds?
        if check_x < 0 or check_x >= width or check_y < 0 or check_y >= height:
            return distance

        # Hit wall?
        if self.is_wall(check_x, check_y):
            return distance

        distance += step

    return max_distance
```

**Matematika Parametric Line:**

```
P(t) = Start + Direction × t

Dimana:
- Start = (start_x, start_y)
- Direction = (cos(θ), sin(θ))
- t = distance (0 to max_distance)
```

### `get_sensor_distances(x, y, angle, num_sensors, fov, max_distance)`

Dapatkan jarak dari multiple sensors.

```python
def get_sensor_distances(self, x, y, angle, num_sensors=5,
                         fov=π, max_distance=300):
    distances = []

    # Spread sensors across FOV
    start_angle = angle - fov / 2
    angle_step = fov / (num_sensors - 1)

    for i in range(num_sensors):
        sensor_angle = start_angle + i * angle_step
        dist = self.raycast(x, y, sensor_angle, max_distance)
        distances.append(dist)

    return distances
```

**Diagram Sensor:**

```
                    [2] depan
                      ↑
             [1] ↙         ↘ [3]
                   motor
           [0] ←           → [4]

FOV = 180° = π radian, dibagi 5 sensor
Angle step = 180° / 4 = 45° antar sensor
```

---

## Visualisasi

### `draw_sensors(...)`

Gambar rays sensor untuk debugging.

```python
def draw_sensors(self, screen, camera, x, y, angle, ...):
    for sensor_angle, dist in zip(angles, distances):
        end_x = x + cos(sensor_angle) * dist
        end_y = y + sin(sensor_angle) * dist

        # Color gradient: merah (dekat) → hijau (jauh)
        ratio = dist / max_distance
        color = (255 * (1 - ratio), 255 * ratio, 0)

        # Draw line dan endpoint
        pg.draw.line(screen, color, start, end, 2)
        pg.draw.circle(screen, (255, 0, 0), end, 4)
```

---

## Diagram Alur

```
┌─────────────────────────────────────────────────────────────┐
│                    TRACK SYSTEM                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Load track.png                                              │
│     │                                                        │
│     ├── Scale ke screen_width × screen_height                │
│     │                                                        │
│     └── Ready for queries:                                   │
│            │                                                 │
│            ├── is_road(x, y) → bool                          │
│            │      └── brightness < 100?                      │
│            │                                                 │
│            ├── check_collision(x, y, w, h) → bool            │
│            │      └── any corner on wall?                    │
│            │                                                 │
│            └── raycast(x, y, angle) → distance               │
│                   └── step until wall or max_distance        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

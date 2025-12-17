# radar.py - Radar dan Fitness Calculator

> Lokasi: `src/core/radar.py`

---

## Deskripsi Umum

Modul radar mengandung komponen untuk AI sensing dan fitness calculation:

1. **RadarConfig**: Konfigurasi radar
2. **AIState**: State untuk tracking AI
3. **Radar**: Sistem raycast untuk sensing jarak
4. **FitnessCalculator**: Penghitungan skor fitness untuk NEAT

Kedua class ini bekerja sama - Radar memberikan input untuk neural network, FitnessCalculator mengevaluasi performa untuk training.

---

## Class: RadarConfig

Konfigurasi untuk sistem radar.

```python
@dataclass
class RadarConfig:
    num_radars: int = 5
    radar_angles: List[int] = field(
        default_factory=lambda: [-90, -45, 0, 45, 90]
    )
    max_length: int = 300
```

### Penjelasan Parameter

- **num_radars**: Jumlah ray yang dicast. 5 adalah balance antara detail dan performance.
- **radar_angles**: Sudut relatif terhadap arah hadap motor (dalam derajat)
  - -90: Kiri penuh (tegak lurus)
  - -45: Kiri depan (diagonal)
  - 0: Depan (lurus)
  - 45: Kanan depan (diagonal)
  - 90: Kanan penuh (tegak lurus)
- **max_length**: Jarak maksimum raycast dalam pixel. Lebih jauh = AI bisa "melihat" lebih jauh.

### Diagram Radar Rays

```
                     [2] 0 derajat (DEPAN)
                        ^
                        |
             [1] -45    |     +45 [3]
                   \    |    /
                    \   |   /
                     \  |  /
                      \ | /
        [0] -90 <------[M]------> +90 [4]

        M = Motor (posisi center)
```

---

## Class: AIState

State untuk tracking performa AI selama training.

```python
@dataclass
class AIState:
    time_spent: int = 0              # Total frames hidup
    distance_traveled: float = 0     # Total jarak tempuh

    # Grid-based position tracking
    unique_positions: Set[Tuple[int, int]] = field(default_factory=set)
    last_grid_pos: Optional[Tuple[int, int]] = None
    consecutive_same_pos: int = 0    # Counter stuck di posisi sama

    # Progress tracking
    max_distance_reached: float = 0
    stuck_timer: int = 0
    collision_count: int = 0
    total_rotation: float = 0        # Total sudut yang di-rotate

    # Previous position untuk kalkulasi jarak
    prev_x: float = 0
    prev_y: float = 0
```

### Penjelasan Grid-based Tracking

Posisi motor dibagi ke grid 50x50 pixel. Ini memungkinkan tracking yang efisien:

```
+----+----+----+----+
|(0,0)|(1,0)|(2,0)|(3,0)|
+----+----+----+----+
|(0,1)|(1,1)|(2,1)|(3,1)|   Setiap cell = 50x50 pixel
+----+----+----+----+
|(0,2)|(1,2)|(2,2)|(3,2)|
+----+----+----+----+
```

- **unique_positions**: Set semua grid cell yang pernah dikunjungi. Lebih banyak = AI lebih eksploratif.
- **consecutive_same_pos**: Counter untuk deteksi stuck. Reset saat pindah ke cell baru.

---

## Class: Radar

Sistem raycast untuk AI sensing.

### Constructor

```python
def __init__(self, config: RadarConfig = None):
    self.config = config or RadarConfig()
    self.radars: List[Tuple[Tuple[int, int], int]] = []
    # Format: [((end_x, end_y), distance), ...]
```

### Method: update(x, y, angle, surface, masking_mode)

Melakukan raycast di semua arah radar.

```python
def update(self, x: float, y: float, angle: float,
           surface: pygame.Surface, masking_mode: bool = True) -> None:
    """
    Update semua radar rays.

    Args:
        x, y: Posisi motor
        angle: Sudut hadap motor (radian)
        surface: Surface untuk raycast (masking atau track)
        masking_mode: True = stop hanya di merah (wall)
                      False = legacy mode
    """
    self.radars.clear()

    if surface is None:
        return

    # Convert angle dari radian ke derajat
    # 360 - degrees karena pygame y-axis terbalik
    angle_deg = 360 - math.degrees(angle)

    # Cast ray untuk setiap sudut radar
    for degree in self.config.radar_angles:  # [-90, -45, 0, 45, 90]
        length = 0
        end_x, end_y = int(x), int(y)

        while length < self.config.max_length:
            # Hitung posisi ray pada jarak length
            radar_angle = math.radians(360 - (angle_deg + degree))
            end_x = int(x + math.cos(radar_angle) * length)
            end_y = int(y + math.sin(radar_angle) * length)

            try:
                # Boundary check
                if (end_x < 0 or end_x >= surface.get_width() or
                    end_y < 0 or end_y >= surface.get_height()):
                    break

                # Get pixel color
                pixel = surface.get_at((end_x, end_y))
                r, g, b = pixel[0], pixel[1], pixel[2]

                if masking_mode:
                    # Hanya stop di merah (wall)
                    is_red = (r > 150 and g < 100 and b < 100)
                    if is_red:
                        break
                else:
                    # Legacy mode - stop di border apapun
                    # ... logic lama
                    pass

            except:
                break

            length += 5  # Step 5 pixel untuk performance

        # Hitung jarak akhir
        dist = int(math.sqrt((end_x - x)**2 + (end_y - y)**2))
        self.radars.append(((end_x, end_y), dist))
```

### Penjelasan Raycast Algorithm

1. **Loop through angles**: Untuk setiap sudut radar (-90, -45, 0, 45, 90)
2. **Step forward**: Mulai dari posisi motor, step 5 pixel ke arah radar
3. **Check pixel**: Di setiap step, cek warna pixel
4. **Stop condition**: Berhenti jika menemukan wall (merah) atau boundary
5. **Record distance**: Simpan jarak akhir

Step 5 pixel dipilih untuk balance antara akurasi dan performance. Step lebih kecil = lebih akurat tapi lebih lambat.

### Method: get_data()

Mendapatkan data radar yang dinormalisasi untuk neural network.

```python
def get_data(self) -> List[int]:
    """
    Get normalized radar data untuk input neural network.

    Returns:
        List of 5 integers (0-10 scale)

    Format: [left_90, left_45, front, right_45, right_90]

    Nilai:
        0 = sangat dekat wall (DANGER!)
        5 = jarak menengah
        10 = jauh dari wall (safe)
    """
    data = [0] * self.config.num_radars

    for i, radar in enumerate(self.radars):
        if i < len(data):
            # Normalize: distance / 30 untuk range 0-10
            # max_length 300 / 30 = 10
            data[i] = int(radar[1] / 30)

    return data
```

### Tabel Normalisasi

| Jarak (pixel) | Nilai Normalized | Interpretasi              |
| ------------- | ---------------- | ------------------------- |
| 0-30          | 0-1              | BAHAYA! Sangat dekat wall |
| 30-90         | 1-3              | Dekat, perlu hati-hati    |
| 90-150        | 3-5              | Menengah                  |
| 150-210       | 5-7              | Cukup aman                |
| 210-270       | 7-9              | Aman                      |
| 270-300       | 9-10             | Sangat aman               |

### Method: draw(screen, camera_x, camera_y, x, y)

Menggambar visualisasi radar untuk debugging.

```python
def draw(self, screen: pygame.Surface, camera_x: int, camera_y: int,
         x: float, y: float) -> None:
    """
    Draw radar lines untuk debug visualization.

    Color coding:
    - Hijau = jarak > 50 (aman)
    - Merah = jarak <= 50 (bahaya)
    """
    for (end_pos, dist) in self.radars:
        # Color based on distance
        if dist > 50:
            color = (0, 255, 0)  # Hijau = aman
        else:
            color = (255, 0, 0)  # Merah = dekat

        # Draw line dari motor ke end point
        pygame.draw.line(
            screen, color,
            (int(x - camera_x), int(y - camera_y)),
            (end_pos[0] - camera_x, end_pos[1] - camera_y),
            2
        )
```

---

## Class: FitnessCalculator

Penghitungan skor fitness untuk training NEAT.

### Constructor

```python
def __init__(self, start_x: float = 0, start_y: float = 0):
    self.state = AIState(prev_x=start_x, prev_y=start_y)
```

### Method: update(x, y, angle_change)

Update tracking data setiap frame.

```python
def update(self, x: float, y: float, angle_change: float) -> None:
    """
    Update tracking data setiap frame.

    Args:
        x, y: Posisi motor saat ini
        angle_change: Perubahan angle frame ini (radian)
    """
    self.state.time_spent += 1

    # === DISTANCE TRAVELED ===
    dx = x - self.state.prev_x
    dy = y - self.state.prev_y
    distance = math.sqrt(dx*dx + dy*dy)
    self.state.distance_traveled += distance
    self.state.max_distance_reached = max(
        self.state.max_distance_reached,
        self.state.distance_traveled
    )

    # === UNIQUE POSITIONS (grid-based) ===
    # Bagi posisi ke grid 50x50 pixel
    grid_pos = (int(x // 50), int(y // 50))

    if grid_pos != self.state.last_grid_pos:
        # Pindah ke cell baru
        self.state.unique_positions.add(grid_pos)
        self.state.consecutive_same_pos = 0
        self.state.stuck_timer = 0
    else:
        # Masih di cell sama
        self.state.consecutive_same_pos += 1
        self.state.stuck_timer += 1

    self.state.last_grid_pos = grid_pos

    # === ROTATION TRACKING ===
    self.state.total_rotation += abs(math.degrees(angle_change))

    # === UPDATE PREVIOUS POSITION ===
    self.state.prev_x = x
    self.state.prev_y = y
```

### Method: calculate(lap_count)

Menghitung fitness score.

```python
def calculate(self, lap_count: int = 0) -> float:
    """
    Calculate fitness score.

    Args:
        lap_count: Jumlah lap yang sudah complete

    Returns:
        Fitness value (float)

    Fitness strategy berbeda berdasarkan lap:
    - Sebelum lap complete: Fokus pada exploration
    - Setelah lap complete: Fokus pada efficiency
    """
    if lap_count == 0:
        # === BELUM COMPLETE LAP ===
        # Fokus mendorong AI untuk explore

        novelty_score = len(self.state.unique_positions)

        # Penalti keras jika tidak bergerak
        if novelty_score < 5:
            return -100

        # Base reward dari exploration
        base_reward = novelty_score * 10

        # Rotation reward - AI yang belok dapat reward
        # Cap di 200 untuk mencegah spinning
        rotation_reward = min(self.state.total_rotation / 2.0, 200)

        # Distance reward
        distance_reward = self.state.distance_traveled / 50.0

        # Repetition penalty - stuck di tempat sama
        repetition_penalty = self.state.consecutive_same_pos * -20

        return (base_reward + rotation_reward +
                distance_reward + repetition_penalty)

    else:
        # === SUDAH COMPLETE LAP ===
        # Fokus pada optimasi lap

        # Lap bonus - exponential reward
        # 1 lap = 1000, 2 lap = 4000, 3 lap = 9000
        lap_bonus = (lap_count ** 2) * 1000

        # Efficiency bonus - distance / time
        efficiency = (self.state.distance_traveled /
                      max(self.state.time_spent, 1))
        efficiency_bonus = efficiency * 50

        # Novelty bonus (lebih kecil setelah lap)
        novelty_bonus = len(self.state.unique_positions) * 3

        return lap_bonus + efficiency_bonus + novelty_bonus
```

### Penjelasan Rumus Fitness

**Sebelum Complete Lap (lap_count = 0)**

Tujuan: Mendorong AI untuk explore track dan belajar bernavigasi

```
Fitness = (unique_positions × 10)
        + min(total_rotation / 2, 200)
        + (distance_traveled / 50)
        - (consecutive_same_pos × 20)
```

| Komponen                   | Penjelasan                                    | Rentang Tipikal |
| -------------------------- | --------------------------------------------- | --------------- |
| unique_positions × 10      | Reward untuk setiap cell baru yang dikunjungi | 0 - 500         |
| total_rotation / 2         | Reward untuk belok (capped 200)               | 0 - 200         |
| distance_traveled / 50     | Reward kecil untuk jarak                      | 0 - 100         |
| consecutive_same_pos × -20 | Penalti stuck                                 | -400 sampai 0   |

**Setelah Complete Lap (lap_count > 0)**

Tujuan: Mendorong AI untuk complete lap lebih banyak dan lebih cepat

```
Fitness = (lap_count^2 × 1000)
        + (efficiency × 50)
        + (unique_positions × 3)
```

| Komponen             | Penjelasan                 | Rentang Tipikal     |
| -------------------- | -------------------------- | ------------------- |
| lap_count^2 × 1000   | Exponential reward per lap | 1000, 4000, 9000... |
| efficiency × 50      | Bonus untuk speed          | 0 - 500             |
| unique_positions × 3 | Bonus kecil exploration    | 0 - 150             |

### Tabel Contoh Skor

| Skenario           | lap | unique | rotation | distance | stuck | Fitness        |
| ------------------ | --- | ------ | -------- | -------- | ----- | -------------- |
| Tidak bergerak     | 0   | 1      | 0        | 0        | 60    | -100 (penalti) |
| Berputar di tempat | 0   | 3      | 1000     | 50       | 30    | ~-370          |
| Explore bagus      | 0   | 30     | 500      | 3000     | 0     | ~610           |
| 1 lap complete     | 1   | 50     | 800      | 5000     | 5     | ~1250          |
| 2 lap complete     | 2   | 80     | 1200     | 10000    | 3     | ~4440          |

### Method: is_stuck(threshold)

Check apakah motor stuck.

```python
def is_stuck(self, threshold: int = 120) -> bool:
    """
    Check apakah motor stuck di tempat.

    Args:
        threshold: Frames tanpa bergerak (default 120 = 2 detik)

    Returns:
        True jika stuck
    """
    return self.state.stuck_timer > threshold
```

### Method: reset(start_x, start_y)

Reset state untuk training ulang.

```python
def reset(self, start_x: float = 0, start_y: float = 0) -> None:
    """Reset semua tracking state."""
    self.state = AIState(prev_x=start_x, prev_y=start_y)
```

---

## Penggunaan Lengkap

```python
# === SETUP ===
radar = Radar(RadarConfig())
fitness = FitnessCalculator(start_x=1000, start_y=500)

# === TRAINING LOOP ===
for frame in range(max_frames):
    # Update radar
    radar.update(motor.x, motor.y, motor.angle, masking_surface)

    # Get input untuk neural network
    # Output: [5, 8, 10, 7, 3] - 5 nilai jarak normalized
    radar_data = radar.get_data()

    # Neural network membuat keputusan
    output = network.activate(radar_data)
    action = output.index(max(output))  # 0, 1, atau 2

    # Apply action
    if action == 0:
        motor.steer(1)   # Kiri
    elif action == 1:
        pass             # Lurus
    elif action == 2:
        motor.steer(-1)  # Kanan

    # Update fitness tracking
    fitness.update(motor.x, motor.y, angle_change)

    # Check stuck
    if fitness.is_stuck(threshold=120):
        motor.alive = False

# === SETELAH SIMULASI ===
# Hitung fitness score
score = fitness.calculate(lap_count=motor.lap_count)
genome.fitness = score
```

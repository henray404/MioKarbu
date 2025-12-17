# motor.py - Class Motor

> Lokasi: `src/core/motor.py`

---

## Deskripsi Umum

Class Motor adalah entity utama dalam game yang merepresentasikan kendaraan motor baik untuk player maupun AI. Class ini menggunakan **Composition Pattern** dimana berbagai tanggung jawab dipisahkan ke komponen-komponen terpisah.

Pendekatan composition ini dipilih karena:

1. **Separation of Concerns**: Setiap komponen fokus pada satu tanggung jawab
2. **Reusability**: Komponen bisa digunakan ulang atau diganti
3. **Testability**: Lebih mudah untuk testing unit
4. **Maintainability**: Perubahan di satu area tidak mempengaruhi area lain

---

## Arsitektur Composition Pattern

```
+------------------------------------------------------------------+
|                          MOTOR CLASS                              |
|                                                                   |
|  Position & State:                                                |
|  - x, y (koordinat)                                               |
|  - angle (sudut hadap dalam radian)                               |
|  - alive (status hidup/mati)                                      |
|                                                                   |
|  +------------------------+  +---------------------------+        |
|  |    PHYSICS ENGINE      |  |    COLLISION HANDLER      |        |
|  |------------------------|  |---------------------------|        |
|  | - velocity             |  | - track_surface           |        |
|  | - steering_rate        |  | - masking_surface         |        |
|  | - grip                 |  | - collision corners       |        |
|  | - drift mechanics      |  | - zone classification     |        |
|  +------------------------+  +---------------------------+        |
|                                                                   |
|  +------------------------+  +---------------------------+        |
|  |  CHECKPOINT TRACKER    |  |     RADAR (AI Only)       |        |
|  |------------------------|  |---------------------------|        |
|  | - lap_count            |  | - 5 directional rays      |        |
|  | - checkpoint_count     |  | - masking-aware           |        |
|  | - timing               |  | - normalized output       |        |
|  +------------------------+  +---------------------------+        |
|                                                                   |
|  +------------------------+                                       |
|  |   FITNESS CALCULATOR   |                                       |
|  |------------------------|                                       |
|  | - distance_traveled    |                                       |
|  | - unique_positions     |                                       |
|  | - fitness scoring      |                                       |
|  +------------------------+                                       |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Komponen dan File Terkait

| Komponen          | File          | Tanggung Jawab                                            |
| ----------------- | ------------- | --------------------------------------------------------- |
| PhysicsEngine     | physics.py    | Semua kalkulasi fisika: akselerasi, steering, grip, drift |
| CollisionHandler  | collision.py  | Deteksi tabrakan dengan track, wall, checkpoint           |
| CheckpointTracker | checkpoint.py | Penghitungan lap dan validasi checkpoint                  |
| Radar             | radar.py      | Raycast sensing untuk input AI                            |
| FitnessCalculator | radar.py      | Penghitungan skor fitness untuk training                  |

---

## Constructor

```python
def __init__(self, x: float, y: float, color: str = "pink"):
    # Posisi dan sudut awal
    self.x = x
    self.y = y
    self.angle = 0  # dalam radian, 0 = menghadap kanan
    self.color = color

    # Dimensi motor (untuk collision box)
    self.length = 140
    self.width = 80

    # Inisialisasi komponen-komponen
    self.physics = PhysicsEngine(PhysicsConfig(
        length=self.length,
        width=self.width
    ))

    self.collision = CollisionHandler(
        length=self.length,
        width=self.width
    )

    self.checkpoint = CheckpointTracker(
        start_x=x,
        start_y=y
    )

    self.radar = Radar(RadarConfig())

    self.fitness_calc = FitnessCalculator(
        start_x=x,
        start_y=y
    )
```

### Penjelasan Parameter

- **x, y**: Koordinat spawn awal motor dalam pixel. Sistem koordinat menggunakan konvensi pygame dimana (0,0) di pojok kiri atas.
- **color**: String nama warna yang digunakan untuk memilih sprite sheet. Contoh: "pink", "hijau", dll.

---

## Property Delegation

Motor menggunakan property untuk mendelegasikan akses ke komponen-komponen internal. Ini memungkinkan kode eksternal mengakses data tanpa perlu tahu struktur internal.

```python
@property
def velocity(self):
    """Kecepatan motor saat ini dari PhysicsEngine."""
    return self.physics.state.velocity

@velocity.setter
def velocity(self, value):
    """Set kecepatan motor. Biasanya digunakan untuk AI."""
    self.physics.state.velocity = value

@property
def max_speed(self):
    """Kecepatan maksimum dari konfigurasi physics."""
    return self.physics.config.max_speed

@property
def lap_count(self):
    """Jumlah lap yang sudah diselesaikan."""
    return self.checkpoint.state.lap_count

@property
def checkpoint_count(self):
    """Jumlah checkpoint yang sudah dilewati dalam lap saat ini."""
    return self.checkpoint.state.checkpoint_count

@property
def distance_traveled(self):
    """Total jarak yang sudah ditempuh (untuk fitness)."""
    return self.fitness_calc.state.distance_traveled
```

---

## Method Utama

### handle_input(keys) - Kontrol Player

Method ini memproses input keyboard dari player dan mengaplikasikan ke physics engine.

```python
def handle_input(self, keys):
    """
    Proses input keyboard untuk kontrol player.

    Args:
        keys: pygame.key.get_pressed() result
    """
    # 1. THROTTLE
    # W = gas maju, S = rem/mundur, tidak ada = friction
    if keys[pygame.K_w]:
        self.physics.apply_acceleration(1.0)
    elif keys[pygame.K_s]:
        self.physics.apply_acceleration(-1.0)
    else:
        self.physics.apply_acceleration(0)

    # 2. STEERING
    # A = belok kiri (-1), D = belok kanan (+1)
    steering_input = 0
    if keys[pygame.K_a]:
        steering_input = -1
    elif keys[pygame.K_d]:
        steering_input = 1

    # 3. DRIFT
    # Space atau Shift = mode drift
    is_drifting = (keys[pygame.K_SPACE] or
                   keys[pygame.K_LSHIFT] or
                   keys[pygame.K_RSHIFT])

    # 4. APPLY STEERING
    # PhysicsEngine menghitung perubahan angle berdasarkan
    # steering input, kecepatan, dan mode drift
    angle_change = self.physics.apply_steering(
        steering_input,
        is_drifting
    )
    self.angle += angle_change
```

### Penjelasan Alur Input

1. **Throttle**: Input W/S dikonversi ke nilai throttle (-1 sampai 1) dan dikirim ke PhysicsEngine. Engine akan menangani akselerasi dengan drag effect dan friction.

2. **Steering**: Input A/D dikonversi ke steering input (-1 sampai 1). Tidak ada angka antara karena keyboard bersifat digital.

3. **Drift**: Jika tombol drift ditekan bersamaan dengan steering, motor memasuki mode drift dengan steering yang lebih tajam tapi speed penalty.

4. **Apply**: PhysicsEngine menghitung perubahan angle yang diperlukan dengan memperhitungkan kecepatan saat ini (speed-dependent steering).

---

### steer(direction) - Kontrol AI

Method yang lebih sederhana untuk AI karena tidak memerlukan handling throttle (AI selalu max speed).

```python
def steer(self, direction: int):
    """
    Steering untuk AI.

    Args:
        direction: -1 (kanan), 0 (lurus), 1 (kiri)

    Note:
        Arah sesuai dengan konvensi:
        - Positive angle = counter-clockwise
        - direction 1  = angle bertambah = belok kiri
        - direction -1 = angle berkurang = belok kanan
    """
    angle_change = self.physics.apply_steering(float(direction))
    self.angle += angle_change
```

---

### update() - Update Loop Utama

Method yang dipanggil setiap frame untuk mengupdate posisi dan state motor.

```python
def update(self):
    """
    Update posisi dan state motor setiap frame.

    Alur:
    1. Hitung delta posisi dari physics
    2. Check collision di posisi baru
    3. Handle hasil collision
    4. Update radar untuk AI
    5. Update fitness tracking
    6. Check dan process checkpoint/lap
    """
    # 1. MOVEMENT
    # PhysicsEngine menghitung delta posisi berdasarkan
    # angle dan velocity saat ini
    dx, dy = self.physics.calculate_movement(self.angle)
    new_x = self.x + dx
    new_y = self.y + dy

    # 2. COLLISION CHECK
    # CollisionHandler memeriksa posisi baru terhadap masking
    result = self.collision.check_masking_collision(
        new_x, new_y, self.angle
    )

    # 3. HANDLE COLLISION
    if result['collided']:
        # Nabrak wall - handle bounce/explode
        self._handle_wall_collision()
    elif result['slow_zone']:
        # Di slow zone - kurangi speed
        self.physics.state.velocity *= 0.99
        self.x = new_x
        self.y = new_y
    else:
        # OK - update posisi
        self.x = new_x
        self.y = new_y

    # 4. UPDATE RADAR
    # Untuk AI sensing (tidak berpengaruh untuk player)
    surface = self.collision.get_surface_for_radar()
    if surface:
        self.radar.update(self.x, self.y, self.angle, surface)

    # 5. FITNESS TRACKING
    # Untuk AI training
    self.fitness_calc.update(self.x, self.y, angle_change)

    # 6. CHECKPOINT
    if result['checkpoint'] > 0:
        self.checkpoint.process_checkpoint(
            self.x, self.y,
            result['checkpoint'],
            current_time
        )
    else:
        # Clear checkpoint flag jika sudah keluar
        self.checkpoint.clear_checkpoint_flag()

    # 7. LAP CHECK
    lap_result = self.checkpoint.check_lap(
        self.x, self.y, current_time, self.invincible
    )
    if lap_result['should_die']:
        self.alive = False
```

---

### get_radar_data() - Data untuk Neural Network

```python
def get_radar_data(self):
    """
    Get data sensor untuk input neural network.

    Returns:
        List[int]: 5 nilai jarak ternormalisasi (0-10)

    Format output:
        [left_90, left_45, front, right_45, right_90]

    Nilai:
        0  = sangat dekat wall (bahaya)
        10 = jauh dari wall (aman)
    """
    return self.radar.get_data()
```

---

## Penggunaan

### Untuk Player

```python
# Setup
player = Motor(spawn_x, spawn_y, color="hijau")
player.set_masking_surface(masking_surface)
player.invincible = True  # Player tidak mati saat nabrak

# Game loop
while running:
    keys = pygame.key.get_pressed()
    player.handle_input(keys)
    player.update()
    player.draw(screen, camera_x, camera_y)
```

### Untuk AI

```python
# Setup
ai = Motor(spawn_x, spawn_y, color="pink")
ai.set_masking_surface(ai_masking_surface)

# Game/Training loop
while running:
    # Maintain constant speed
    ai.velocity = ai.max_speed

    # Get sensor data
    radar_data = ai.get_radar_data()  # [5, 7, 10, 8, 4]

    # Neural network decision
    output = network.activate(radar_data)
    action = output.index(max(output))  # 0, 1, atau 2

    # Apply steering
    if action == 0:
        ai.steer(1)    # Belok kiri
    elif action == 1:
        pass           # Lurus
    elif action == 2:
        ai.steer(-1)   # Belok kanan

    ai.update()
```

---

## Lihat Juga

Untuk penjelasan detail setiap komponen:

- [physics.md](physics.md) - PhysicsEngine dengan rumus fisika lengkap
- [collision.md](collision.md) - CollisionHandler dengan masking colors
- [checkpoint.md](checkpoint.md) - CheckpointTracker dengan sequential system
- [radar.md](radar.md) - Radar dan FitnessCalculator untuk AI

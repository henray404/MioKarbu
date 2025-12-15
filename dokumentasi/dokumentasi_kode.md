# 📚 Dokumentasi Kode - Tabrak Bahlil

Dokumentasi lengkap untuk semua modul kode dalam project game racing AI.

---

## 📁 Struktur Project

```
src/
├── ai/                     # Modul AI/NEAT Training
│   ├── neat_trainer.py     # Trainer dengan visualisasi lengkap
│   └── trainer.py          # Trainer utama (dipakai train.py)
├── core/                   # Modul Core Game
│   ├── motor.py            # Class Motor (player & AI)
│   ├── track.py            # Class Track (peta/sirkuit)
│   ├── camera.py           # Sistem kamera follow
│   ├── distance_sensor.py  # Sensor jarak untuk AI
│   └── ai_car.py           # Legacy AI car (tidak dipakai)
├── screens/                # Screen management
│   ├── base.py             # Base screen class
│   └── main_menu.py        # Main menu (placeholder)
├── ui/                     # UI Components
│   └── button.py           # Button class
├── main.py                 # Entry point game (Player vs AI)
├── train.py                # Entry point training
└── play_ai.py              # Mode demo AI saja
```

---

# 🤖 Modul AI

## 1. `trainer.py` - NEAT Trainer Utama

### Deskripsi

File ini adalah **trainer utama** yang digunakan oleh `train.py`. Menghandle evolusi neural network menggunakan algoritma **NEAT (NeuroEvolution of Augmenting Topologies)**.

### Class: `NEATTrainer`

```python
class NEATTrainer:
    def __init__(self, config_path, track_name, screen_width, screen_height,
                 map_width, map_height, headless, render_interval)
```

#### Parameter Penting:

| Parameter          | Default    | Fungsi                                    |
| ------------------ | ---------- | ----------------------------------------- |
| `headless`         | `False`    | Mode tanpa visualisasi (3-5x lebih cepat) |
| `render_interval`  | `1`        | Render setiap N frame                     |
| `map_width/height` | 16512x9216 | Ukuran map (6x dari original)             |

### Method Utama:

#### `setup()`

Inisialisasi pygame dan load track/masking surfaces.

```python
def setup(self):
    if self.headless:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Untuk headless mode
    pygame.init()
    # Load track dan masking surface
```

#### `eval_genomes(genomes, config)`

**Callback utama untuk NEAT** - dipanggil setiap generasi.

**Logic Flow:**

1. Buat motor untuk setiap genome
2. Loop simulasi sampai semua mati atau timeout
3. Update fitness berdasarkan:
   - `distance_traveled` (jarak tempuh)
   - `checkpoint_count × 200` (checkpoint bonus)
   - `lap_count × 2000` (lap bonus)

```python
# Fitness calculation
fitness = car.distance_traveled
fitness += car.checkpoint_count * 200  # Checkpoint bonus
fitness += car.lap_count * 2000        # Lap bonus
genome.fitness = fitness
```

#### `run(generations)`

Jalankan evolusi NEAT.

**Flow:**

1. Load NEAT config
2. Buat populasi awal
3. Tambah reporters (StdOut, Statistics, Checkpointer)
4. Jalankan evolusi
5. Save model terbaik

---

## 2. `neat_trainer.py` - Trainer Alternatif

Versi lebih lengkap dengan fitur tambahan seperti:

- Visualisasi lebih detail
- Save/load genome
- Entry point terpisah

---

# 🏍️ Modul Core

## 1. `motor.py` - Class Motor (PALING PENTING!)

### Deskripsi

Class utama untuk **player dan AI motor**. Menghandle:

- Physics (speed, steering, drift)
- Collision detection
- Checkpoint/lap counting
- AI radar system

### 📐 Fisika & Matematika

#### A. Speed-Dependent Steering

Motor lebih sulit belok di kecepatan tinggi (realistis):

```python
# Konstanta
base_steering_rate = 4.5    # Derajat/frame saat lambat
min_steering_rate = 1.2     # Derajat/frame saat max speed

# Kalkulasi steering rate
speed_ratio = velocity / max_speed  # 0.0 - 1.0
steering_rate = base_steering_rate - (
    (base_steering_rate - min_steering_rate) * speed_ratio
)
```

**Visualisasi:**

```
Speed   | Steering Rate
--------|---------------
0%      | 4.5°/frame
50%     | 2.85°/frame
100%    | 1.2°/frame
```

#### B. Understeer

Di kecepatan tinggi, motor cenderung lurus meski belok:

```python
understeer_factor = 0.3  # 30% understeer di max speed

understeer = 1.0 - (speed_ratio * understeer_factor)
steer_amount = radians(steering_rate) * steering_input * understeer
```

**Matematika:**

```
Effective_Steer = Base_Steer × (1 - speed_ratio × understeer_factor)

Contoh di 100% speed:
Effective = Base × (1 - 1.0 × 0.3) = Base × 0.7 = 70% steering
```

#### C. Speed Penalty saat Belok

Kehilangan speed proporsional dengan intensitas belok:

```python
turn_speed_penalty = 0.02  # 2% penalty per frame

if steering_input != 0:
    turn_intensity = abs(steering_input) * speed_ratio
    speed_loss = turn_speed_penalty * turn_intensity
    velocity *= (1.0 - speed_loss)
```

#### D. Drag Effect (Akselerasi)

Akselerasi lebih lambat mendekati max speed:

```python
if keys[K_w]:
    accel_modifier = 1.0 - (speed_ratio * 0.5)  # 50% drag di max speed
    velocity += acceleration_rate * accel_modifier
```

#### E. Drift Mechanics

```python
if is_drifting and steering_input != 0:
    # Steering lebih tajam
    drift_steer = base_steering_rate * 1.5
    angle += radians(drift_steer) * steering_input

    # Build drift angle (sliding)
    drift_angle += steering_input * 0.08
    drift_angle = clamp(drift_angle, -0.5, 0.5)  # Max 28° drift

    # Speed penalty
    velocity *= 0.995
```

### 📡 AI Radar System

Motor memiliki 5 sensor radar untuk AI:

```python
radar_angles = [-90, -45, 0, 45, 90]  # Derajat relatif
max_radar_length = 300  # Pixel
```

**Raycast Algorithm:**

```python
def _update_radars(self, track_surface):
    for degree in radar_angles:
        length = 0
        while length < max_radar_length:
            # Hitung posisi titik
            radar_angle = radians(360 - (angle_deg + degree))
            x = int(self.x + cos(radar_angle) * length)
            y = int(self.y + sin(radar_angle) * length)

            # Cek collision dgn wall (warna merah)
            if is_wall(x, y):
                break
            length += 5  # Step 5 pixel
```

### 🏁 Checkpoint System

Sequential checkpoint dengan 4 warna:

| Checkpoint | Warna   | RGB Condition       |
| ---------- | ------- | ------------------- |
| CP1        | Hijau   | g>150, r<150, b<150 |
| CP2        | Cyan    | g>150, b>150, r<150 |
| CP3        | Kuning  | r>150, g>150, b<150 |
| CP4        | Magenta | r>150, b>150, g<150 |

```python
# Harus melewati checkpoint secara urut
if detected_cp == expected_checkpoint:
    checkpoint_count += 1
    expected_checkpoint = (expected_checkpoint % 4) + 1
```

### 🔄 Collision Detection

```python
# Masking colors:
# - Hitam (avg < 50): Track OK
# - Putih/Abu (avg > 50): Slow zone
# - Merah (r>150, g<100, b<100): Wall

if is_red:
    if velocity > wall_explode_speed:
        alive = False  # Meledak!
    else:
        velocity = -velocity * 0.4  # Bounce back
```

---

## 2. `track.py` - Class Track

### Deskripsi

Handle loading track image dan collision detection via pixel brightness.

### Method Utama:

#### `is_road(x, y)`

Cek apakah posisi adalah jalan:

```python
def is_road(self, x, y):
    brightness = self.get_brightness_at(x, y)
    return brightness < road_threshold  # < 100 = jalan
```

#### `raycast(start_x, start_y, angle, max_distance)`

Raycast untuk sensor:

```python
def raycast(self, start_x, start_y, angle, max_distance):
    dx = cos(angle)
    dy = sin(angle)

    distance = 0
    while distance < max_distance:
        check_x = start_x + dx * distance
        check_y = start_y + dy * distance

        if self.is_wall(check_x, check_y):
            return distance
        distance += 5  # Step

    return max_distance
```

**Matematika Raycast:**

```
Position(t) = Start + Direction × t

dimana:
- Direction = (cos(θ), sin(θ))
- t = jarak dari start point
```

---

## 3. `camera.py` - Sistem Kamera

### Smooth Camera Follow

Menggunakan **Linear Interpolation (Lerp)**:

```python
def update_camera(target_x, target_y, map_width, map_height):
    smoothness = 0.15  # 15% per frame

    # Lerp formula: new = current + (target - current) × t
    camera.x += (camera_target_x - camera.x) * smoothness
    camera.y += (camera_target_y - camera.y) * smoothness

    # Clamp ke bounds
    camera.x = clamp(camera.x, 0, map_width - camera.width)
    camera.y = clamp(camera.y, 0, map_height - camera.height)
```

**Matematika Lerp:**

```
newPosition = currentPosition + (targetPosition - currentPosition) × smoothness

Dengan smoothness = 0.15:
- Frame 1: 15% closer to target
- Frame 2: 15% of remaining 85% = 12.75% more
- ...converges over time
```

---

## 4. `distance_sensor.py` - Sensor Jarak

### Deskripsi

Sensor raycasting modular untuk AI. Bisa di-attach ke motor.

### Normalized Output

Output ternormalisasi 0-1:

- 0 = sangat dekat tembok (bahaya!)
- 1 = jauh/aman

```python
def get_normalized(self):
    return [d / self.max_distance for d in self.distances]
```

---

# 🎮 Entry Points

## 1. `main.py` - Game Utama

### Flow:

1. Load track dan masking
2. Spawn player (hijau) dan AI (dari model pkl)
3. Game loop dengan rendering
4. Hitung lap dan declare winner

### Kontrol:

| Key         | Action      |
| ----------- | ----------- |
| W           | Gas maju    |
| S           | Rem/mundur  |
| A           | Belok kiri  |
| D           | Belok kanan |
| Space/Shift | Drift       |
| R           | Reset       |
| ESC         | Quit        |

---

## 2. `train.py` - Training AI

### Command Line Arguments:

```bash
python train.py --generations 100   # Jumlah generasi
python train.py --track new         # Nama track
python train.py --laps 15           # Target lap
python train.py --headless          # Tanpa visualisasi (cepat!)
python train.py --render-interval 10  # Render setiap 10 frame
```

---

# ⚙️ Config Files

## `config.txt` - NEAT Configuration

### 🎯 Parameter Tunable Utama:

| Parameter            | Default | Efek NAIK               | Efek TURUN             |
| -------------------- | ------- | ----------------------- | ---------------------- |
| `pop_size`           | 150     | Eksplorasi luas, lambat | Cepat, bisa stuck      |
| `weight_mutate_rate` | 0.75    | Eksplorasi agresif      | Stabil, lambat improve |
| `node_add_prob`      | 0.4     | Network kompleks        | Network simpel         |
| `max_stagnation`     | 15      | Species lebih lama      | Agresif remove         |
| `elitism`            | 2       | Preserve solusi bagus   | Lebih exploratif       |

### NEAT Algorithm Overview:

```
┌─────────────────────────────────────────────────────────────┐
│                    NEAT EVOLUTION CYCLE                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. POPULATION INIT                                          │
│     └── Buat N genome dengan struktur minimal                │
│                                                              │
│  2. EVALUATE FITNESS                                         │
│     └── Jalankan simulasi, hitung score tiap genome         │
│                                                              │
│  3. SPECIATION                                               │
│     └── Kelompokkan genome mirip ke species sama             │
│                                                              │
│  4. REPRODUCTION                                             │
│     ├── Elitism: Copy genome terbaik langsung               │
│     ├── Crossover: Gabungkan 2 parent                        │
│     └── Mutation: Ubah weight/struktur                       │
│                                                              │
│  5. REPEAT until target fitness atau max generations        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

# 🧮 Ringkasan Rumus Matematika

## Physics

| Nama              | Rumus                                            |
| ----------------- | ------------------------------------------------ |
| **Steering Rate** | `rate = base - (base - min) × speed_ratio`       |
| **Understeer**    | `effective = steer × (1 - speed_ratio × factor)` |
| **Speed Penalty** | `v = v × (1 - penalty × turn_intensity)`         |
| **Drag**          | `accel = base × (1 - speed_ratio × 0.5)`         |
| **Camera Lerp**   | `pos = pos + (target - pos) × smoothness`        |

## AI/Sensor

| Nama                    | Rumus                                        |
| ----------------------- | -------------------------------------------- |
| **Raycast Position**    | `P(t) = start + (cos(θ), sin(θ)) × t`        |
| **Normalized Distance** | `normalized = distance / max_distance`       |
| **Fitness**             | `F = distance + checkpoints×200 + laps×2000` |

---

# 🔧 Tips Tuning

## Untuk Motor Lebih Mudah Dikontrol:

```python
# Di motor.py
self.min_steering_rate = 2.0    # Naikkan (default 1.2)
self.understeer_factor = 0.15   # Turunkan (default 0.3)
```

## Untuk Training Lebih Cepat:

```python
# Di config.txt
pop_size = 100                  # Turunkan
max_stagnation = 10             # Turunkan
```

## Untuk AI Lebih Pintar:

```python
# Di config.txt
pop_size = 200                  # Naikkan
weight_mutate_rate = 0.8        # Naikkan
elitism = 3                     # Preserve lebih banyak
```

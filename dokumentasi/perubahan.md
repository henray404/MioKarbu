# Dokumentasi Perubahan Sistem Racing Game dengan AI

Dokumen ini menjelaskan secara lengkap semua perubahan yang dilakukan pada sistem racing game, termasuk penjelasan fisika motor, sistem checkpoint, dan training AI menggunakan NEAT.

---

## Daftar Isi

1. [Sistem Fisika Motor](#1-sistem-fisika-motor)
2. [Sistem Masking dan Deteksi Zona](#2-sistem-masking-dan-deteksi-zona)
3. [Sistem Checkpoint Sequential](#3-sistem-checkpoint-sequential)
4. [Sistem Validasi Lap](#4-sistem-validasi-lap)
5. [Sistem Lap Timing](#5-sistem-lap-timing)
6. [Sistem Training AI dengan NEAT](#6-sistem-training-ai-dengan-neat)
7. [Fitness Calculation](#7-fitness-calculation)
8. [Anti-Exploit Mechanisms](#8-anti-exploit-mechanisms)
9. [Konfigurasi dan Parameter](#9-konfigurasi-dan-parameter)

---

## 1. Sistem Fisika Motor

### File: `src/core/motor.py`

### Parameter Dasar Motor

```python
self.acceleration_rate = 0.16  # Akselerasi per frame
self.friction = 0.98           # Gesekan (velocity *= friction setiap frame)
self.steering_rate = 3         # Derajat rotasi per frame saat belok
self.max_speed = 12            # Kecepatan maksimum (pixel per frame)
self.length = 140              # Panjang motor (pixel)
self.width = 80                # Lebar motor (pixel)
```

### Cara Kerja Pergerakan

Motor menggunakan sistem koordinat 2D dengan angle dalam radian:

```python
# Update posisi berdasarkan velocity dan angle
self.x += math.cos(self.angle) * self.velocity
self.y += math.sin(self.angle) * self.velocity
```

- `angle = 0` artinya motor menghadap ke kanan
- `angle = pi/2` artinya motor menghadap ke bawah
- Pergerakan dihitung dengan trigonometri: cos untuk sumbu X, sin untuk sumbu Y

### Sistem Steering

Steering diimplementasikan dengan mengubah angle motor:

```python
def steer(self, direction: int):
    steer_amount = math.radians(self.steering_rate)
    if direction > 0:
        self.angle += steer_amount  # Belok kiri
    elif direction < 0:
        self.angle -= steer_amount  # Belok kanan
```

- `direction = 1`: Belok kiri (angle bertambah)
- `direction = -1`: Belok kanan (angle berkurang)
- `direction = 0`: Lurus (tidak ada perubahan angle)

### Distance Tracking

Motor otomatis melacak jarak tempuh:

```python
distance_moved = math.sqrt((self.x - prev_x)**2 + (self.y - prev_y)**2)
self.distance_traveled += distance_moved
```

---

## 2. Sistem Masking dan Deteksi Zona

### Konsep Masking

Masking adalah gambar overlay yang digunakan untuk mendeteksi zona berbeda di track. Setiap warna merepresentasikan zona yang berbeda.

### File Masking

- `assets/masking.png` - Untuk player
- `assets/ai_masking.png` - Untuk AI training

### Definisi Zona Berdasarkan Warna

| Warna     | RGB Condition              | Zona         | Efek                         |
| --------- | -------------------------- | ------------ | ---------------------------- |
| Hitam     | avg < 50                   | Track        | Tidak ada efek, jalan normal |
| Putih/Abu | avg > 50, bukan warna lain | Slow Zone    | velocity \*= 0.99 per frame  |
| Merah     | r > 150, g < 100, b < 100  | Wall         | Bounce atau explode          |
| Hijau     | g > 150, r < 150, b < 150  | Checkpoint 1 | Titik checkpoint pertama     |
| Cyan      | g > 150, b > 150, r < 150  | Checkpoint 2 | Titik checkpoint kedua       |
| Kuning    | r > 150, g > 150, b < 150  | Checkpoint 3 | Titik checkpoint ketiga      |
| Magenta   | r > 150, b > 150, g < 150  | Checkpoint 4 | Titik checkpoint keempat     |

### Implementasi Deteksi Warna

```python
# Ambil warna dari masking di posisi corner motor
pixel_color = self.masking_surface.get_at((check_x, check_y))
r, g, b = pixel_color[0], pixel_color[1], pixel_color[2]
avg = (r + g + b) / 3

# Deteksi zona
is_black = (avg < 50)
is_red = (r > 150 and g < 100 and b < 100)
is_cp1_green = (g > 150 and r < 150 and b < 150 and g > r and g > b)
is_cp2_cyan = (g > 150 and b > 150 and r < 150)
is_cp3_yellow = (r > 150 and g > 150 and b < 150)
is_cp4_magenta = (r > 150 and b > 150 and g < 150)
```

### Corner Detection

Motor memiliki 4 corner yang dicek setiap frame:

```python
def _get_corners(self):
    half_length = self.length / 2
    half_width = self.width / 2

    corners = []
    for dx, dy in [(-half_length, -half_width),
                   (half_length, -half_width),
                   (half_length, half_width),
                   (-half_length, half_width)]:
        # Rotasi corner berdasarkan angle motor
        rotated_x = dx * cos_angle - dy * sin_angle
        rotated_y = dx * sin_angle + dy * cos_angle
        corners.append((self.x + rotated_x, self.y + rotated_y))
    return corners
```

---

## 3. Sistem Checkpoint Sequential

### Konsep

Checkpoint harus dilewati secara berurutan. Motor tidak bisa skip checkpoint atau melewati checkpoint yang sama berulang kali untuk farming.

### Atribut Checkpoint di Motor

```python
self.checkpoint_count = 0      # Jumlah checkpoint yang sudah dilalui
self.expected_checkpoint = 1   # Checkpoint berikutnya yang harus dilalui (1-4)
self.total_checkpoints = 4     # Total checkpoint per lap
self.checkpoints_for_lap = 4   # Minimal checkpoint untuk validasi lap
self.on_checkpoint = False     # Sedang di atas checkpoint?
self.min_checkpoint_distance = 0  # Jarak minimal (0 = tidak ada batasan)
```

### Logika Deteksi Checkpoint

```python
# Deteksi warna checkpoint yang terdeteksi
detected_cp = 0
if is_cp1_green:
    detected_cp = 1
elif is_cp2_cyan:
    detected_cp = 2
elif is_cp3_yellow:
    detected_cp = 3
elif is_cp4_magenta:
    detected_cp = 4

# Hanya hitung jika checkpoint yang benar
if not self.on_checkpoint and detected_cp == self.expected_checkpoint:
    self.checkpoint_count += 1
    self.on_checkpoint = True

    # Update expected checkpoint (wrap around setelah 4)
    self.expected_checkpoint = (self.expected_checkpoint % self.total_checkpoints) + 1
```

### Urutan Checkpoint

1. Mulai: `expected_checkpoint = 1`
2. Lewat CP1 (Hijau): `expected_checkpoint = 2`
3. Lewat CP2 (Cyan): `expected_checkpoint = 3`
4. Lewat CP3 (Kuning): `expected_checkpoint = 4`
5. Lewat CP4 (Magenta): `expected_checkpoint = 1` (wrap around)

---

## 4. Sistem Validasi Lap

### Konsep

Lap dianggap valid jika:

1. Motor sudah keluar dari area start (> 300 pixel)
2. Motor kembali ke area start (< 200 pixel)
3. Motor sudah melewati semua 4 checkpoint

### Parameter Area Start

```python
leave_start_dist = 300   # Harus keluar 300 pixel untuk dianggap "sudah pergi"
return_start_dist = 200  # Kembali dalam 200 pixel untuk finish lap
```

### Implementasi \_check_lap()

```python
def _check_lap(self):
    if self.lap_cooldown > 0:
        self.lap_cooldown -= 1
        return

    # Hitung jarak dari posisi start
    dist_from_start = math.sqrt(
        (self.x - self.start_x)**2 +
        (self.y - self.start_y)**2
    )

    # Tandai sudah keluar dari start
    if dist_from_start > leave_start_dist:
        self.has_left_start = True
        if self.lap_start_time == 0:
            self.lap_start_time = self.time_spent

    # Cek apakah kembali ke start dengan checkpoint lengkap
    elif self.has_left_start and dist_from_start < return_start_dist:
        if self.checkpoint_count >= self.checkpoints_for_lap:
            # Lap valid!
            self.lap_count += 1
            self.checkpoint_count = 0
            self.expected_checkpoint = 1
            self.lap_cooldown = 60  # Cooldown 1 detik
```

### Failed Lap Counter

Jika motor kembali ke start tanpa checkpoint lengkap, counter failed bertambah:

```python
self.failed_lap_checks = 0
self.max_failed_lap_checks = 5

# Jika gagal 5x, AI mati
if not self.invincible and self.failed_lap_checks >= self.max_failed_lap_checks:
    self.alive = False
```

---

## 5. Sistem Lap Timing

### Atribut Timing

```python
self.lap_start_time = 0        # Frame saat lap dimulai
self.last_lap_time = 0         # Waktu lap terakhir (frames)
self.best_lap_time = float('inf')  # Best lap time
```

### Kalkulasi Waktu Lap

```python
# Saat lap selesai
lap_time = self.time_spent - self.lap_start_time
self.last_lap_time = lap_time

if lap_time < self.best_lap_time:
    self.best_lap_time = lap_time

# Konversi ke detik (60 FPS)
lap_time_seconds = lap_time / 60.0
print(f"Lap completed! Time: {lap_time_seconds:.2f}s")

# Reset timer untuk lap berikutnya
self.lap_start_time = self.time_spent
```

---

## 6. Sistem Training AI dengan NEAT

### File: `src/ai/trainer.py`

### Apa itu NEAT?

NEAT (NeuroEvolution of Augmenting Topologies) adalah algoritma yang mengevolusi neural network. Tidak perlu dataset, AI belajar melalui trial and error dengan fitness function.

### Komponen NEAT

1. **Genome**: Blueprint untuk neural network
2. **Population**: Kumpulan genome (100 motor per generasi)
3. **Species**: Kelompok genome yang mirip
4. **Fitness**: Skor performa setiap genome

### Input Neural Network (5 input)

Motor memiliki 5 radar sensor:

```python
self.radar_angles = [-90, -45, 0, 45, 90]  # Derajat relatif ke arah hadap
self.max_radar_length = 300                 # Panjang maksimum radar
```

Setiap radar mengembalikan jarak ke obstacle terdekat, dinormalisasi ke 0-1.

### Output Neural Network (3 output)

```python
action = output.index(max(output))

if action == 0:
    car.steer(1)   # Belok kiri
elif action == 1:
    pass           # Lurus
elif action == 2:
    car.steer(-1)  # Belok kanan
```

### Spawn Configuration

```python
# Rasio spawn dari track original (2752x1536)
spawn_ratio_x = 400 / 2752
spawn_ratio_y = 770 / 1536

# Hitung spawn untuk map yang di-scale
self.spawn_x = int(self.map_width * spawn_ratio_x)
self.spawn_y = int(self.map_height * spawn_ratio_y)
self.spawn_angle = 0  # Menghadap kanan
```

---

## 7. Fitness Calculation

### Formula Fitness

```python
fitness = car.distance_traveled  # Base fitness = jarak tempuh

# Checkpoint bonus (200 per checkpoint)
fitness += car.checkpoint_count * 200

# Lap bonus (2000 per lap)
if car.lap_count > 0:
    fitness += car.lap_count * 2000
```

### Penjelasan

- **Distance**: Reward untuk menjelajahi track
- **Checkpoint**: Reward untuk progress yang benar
- **Lap**: Reward besar untuk menyelesaikan lap

### Contoh Perhitungan

Motor yang:

- Jarak tempuh: 5000 pixel
- 3 checkpoint
- 1 lap

Fitness = 5000 + (3 _ 200) + (1 _ 2000) = 5000 + 600 + 2000 = **7600**

---

## 8. Anti-Exploit Mechanisms

### 1. Sequential Checkpoint

Motor harus lewat CP1, CP2, CP3, CP4 secara berurutan. Tidak bisa skip atau farming satu checkpoint.

### 2. Failed Lap Counter

Motor yang kembali ke start tanpa checkpoint lengkap 5x akan mati.

### 3. Checkpoint Timeout

Motor yang tidak mencapai checkpoint berikutnya dalam 60 detik akan mati.

```python
max_time_between_checkpoints = 60 * 60  # 60 detik * 60 FPS = 3600 frames

time_since_last_checkpoint = car.time_spent - car.last_checkpoint_time
if time_since_last_checkpoint > max_time_between_checkpoints:
    car.alive = False
```

### 4. Generation Timer Reset

Ketika ada motor yang menyelesaikan lap baru, timer generasi di-reset. Ini memberikan reward waktu tambahan untuk motor yang sukses.

```python
if car.lap_count > best_lap_count:
    best_lap_count = car.lap_count
    gen_start_time = time.time()  # Reset timer ke 60 detik
```

---

## 9. Konfigurasi dan Parameter

### File: `config.txt`

```ini
[NEAT]
pop_size = 100              # Populasi per generasi
fitness_threshold = 100.0   # Threshold untuk stop training
reset_on_extinction = 1     # Reset jika semua species punah

[DefaultGenome]
num_inputs = 5              # 5 radar sensor
num_hidden = 8              # Hidden neurons
num_outputs = 3             # Kiri, lurus, kanan
```

### Training Parameters di trainer.py

```python
max_gen_time = 60           # 60 detik per generasi
target_laps = 3             # Target lap untuk menang
map_width = 16512           # Lebar map (6x scale)
map_height = 9216           # Tinggi map (6x scale)
```

---

## Ringkasan Perubahan

1. **Implementasi Sequential Checkpoint** - 4 warna berbeda untuk urutan checkpoint
2. **Perbaikan Lap Validation** - Area start yang tepat dan checkpoint validation
3. **Penambahan Lap Timing** - Tracking waktu per lap dan best lap
4. **Optimasi Fitness Function** - Distance + checkpoint + lap bonus
5. **Anti-Exploit System** - Failed counter, timeout, sequential requirement
6. **Timer Reset on Lap** - Reward waktu untuk motor yang sukses
7. **Penyesuaian Spawn Position** - Proporsional dengan ukuran map
8. **Unified Steering Logic** - AI dan player menggunakan logika yang sama
9. **Masking-Based Collision** - Deteksi zona berdasarkan warna pixel

---

## Troubleshooting

### Checkpoint Tidak Terdeteksi

Pastikan warna di masking sesuai dengan threshold:

- Hijau: g > 150, r < 150, b < 150
- Cyan: g > 150, b > 150, r < 150
- Kuning: r > 150, g > 150, b < 150
- Magenta: r > 150, b > 150, g < 150

### Lap Tidak Terhitung

Cek kondisi:

1. `has_left_start` harus True (motor keluar > 300 pixel)
2. Motor kembali < 200 pixel dari start
3. `checkpoint_count >= 4`

### AI Mati Terlalu Cepat

Tingkatkan parameter:

- `max_time_between_checkpoints` (default 60 detik)
- `max_failed_lap_checks` (default 5)

---

Dokumen ini dibuat pada 14 Desember 2024.

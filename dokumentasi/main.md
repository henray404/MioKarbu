# main.py - Entry Point Game

> Lokasi: `src/main.py`

---

## Deskripsi Umum

File main.py adalah entry point utama untuk mode game Player vs AI. Di mode ini, player berkompetisi melawan AI yang sudah dilatih sebelumnya dalam race untuk mencapai target lap.

---

## Command Line Arguments

```bash
python main.py [options]
```

### Tabel Arguments

| Argument      | Short | Type   | Default           | Deskripsi        |
| ------------- | ----- | ------ | ----------------- | ---------------- |
| --model       | -m    | string | winner_genome.pkl | File model AI    |
| --track       | -t    | string | new               | Nama file track  |
| --ai-count    | -n    | int    | 1                 | Jumlah AI lawan  |
| --target-laps | -l    | int    | 3                 | Lap untuk menang |

### Penjelasan Arguments

**--model (-m)**

File model AI yang akan digunakan. Program akan mencari di:

1. `models/{nama_file}`
2. `{nama_file}` (root project)

Pastikan sudah melakukan training dan ada file model sebelum menjalankan game.

**--track (-t)**

Nama track yang akan dimainkan. File harus ada di `assets/tracks/{nama}.png`.

**--ai-count (-n)**

Jumlah AI lawan. Semua AI menggunakan model yang sama tapi race secara independen. AI di-spawn berdampingan dengan player, bukan di belakang.

**--target-laps (-l)**

Jumlah lap yang harus dicapai untuk menang. Siapa yang pertama mencapai target menang.

---

## Contoh Penggunaan

```bash
# Default game (1 AI, 3 laps)
python main.py

# Dengan model spesifik
python main.py --model best_genome.pkl

# Race melawan 3 AI
python main.py --ai-count 3

# Race 5 lap
python main.py --target-laps 5

# Kombinasi lengkap
python main.py -m winner_genome.pkl -t mandalika -n 2 -l 5
```

---

## Alur Kerja Program

### 1. Initialization Phase

```
Program Start
    |
    +-- Parse arguments
    |
    +-- Load config.txt (NEAT config)
    |
    +-- Find dan validate model file
    |
    +-- pygame.init()
    |
    +-- Create display (1280 x 960)
    |
    +-- Load track surface
    |
    +-- Load masking surface
    |
    +-- Load AI masking (terpisah)
    |
    +-- Setup fonts
```

### 2. Entity Spawn Phase

```
Entity Creation
    |
    +-- Calculate spawn position
    |   (base_spawn_x, base_spawn_y = 1745, 275)
    |   (spawn_x, spawn_y = base * track_scale)
    |
    +-- Create Player Motor
    |   - color = "pink"
    |   - angle = 0 (menghadap kanan)
    |   - invincible = True
    |   - masking = player masking
    |
    +-- Create AI Motors (loop untuk setiap AI)
        - Offset Y = 80 * (i + 1) pixel ke bawah
        - color = "pink"
        - angle = 0
        - invincible = True
        - masking = AI masking (terpisah)
        - Load neural network dari model
```

### 3. Main Menu Phase

```
Main Menu Loop
    |
    +-- Draw MainMenuScreen
    |
    +-- Handle events
    |
    +-- Check result:
        - "PLAY" -> Lanjut ke game
        - "EXIT" -> Quit program
```

### 4. Countdown Phase

```
Countdown (3...2...1...GO!)
    |
    +-- countdown_timer = 3 * 60 frames (3 detik)
    |
    +-- Setiap frame:
        - countdown_timer -= 1
        - Draw semi-transparent overlay
        - Draw countdown number
    |
    +-- Jika timer <= 0:
        - race_started = True
        - Show "GO!" untuk 30 frames
```

### 5. Game Loop Phase

```
Game Loop (60 FPS)
    |
    +-- Handle Events
    |   - QUIT -> running = False
    |   - ESC -> running = False
    |   - R -> Reset semua entity
    |
    +-- Player Update (jika race_started)
    |   - keys = pygame.key.get_pressed()
    |   - player.handle_input(keys)
    |   - player.update()
    |   - Check win condition
    |
    +-- AI Update (untuk setiap AI)
    |   - ai.velocity = ai.max_speed (constant speed)
    |   - radar_data = ai.get_radar_data()
    |   - output = network.activate(radar_data)
    |   - action = output.index(max(output))
    |   - Apply steering berdasarkan action
    |   - ai.update()
    |   - Check win condition
    |
    +-- Camera Update
    |   - Follow player (atau AI jika player mati)
    |   - Clamp ke bounds map
    |
    +-- Render
        - Track surface
        - AI motors
        - Player motor
        - UI (lap counter, speedometer, dll)
        - Win screen jika game over
```

---

## Konfigurasi Screen dan Map

```python
# Screen (viewport)
SCREEN_WIDTH = 1280     # Lebar window
SCREEN_HEIGHT = 960     # Tinggi window

# Map (track yang sebenarnya)
MAP_SCALE = 6.0         # Faktor pembesaran track
original_width = 2752   # Lebar track asli
original_height = 1536  # Tinggi track asli

MAP_WIDTH = int(2752 * 6.0)   # = 16512 pixel
MAP_HEIGHT = int(1536 * 6.0)  # = 9216 pixel
```

### Penjelasan Scaling

Track di-scale 6x dari ukuran asli agar motor terlihat proporsional. Camera viewport (1280x960) menampilkan sebagian kecil dari map yang besar.

---

## Spawn Position System

```python
# Posisi spawn pada track asli
base_spawn_x = 1745
base_spawn_y = 275

# Posisi setelah scaling
spawn_x = int(1745 * 6.0)  # = 10470
spawn_y = int(275 * 6.0)   # = 1650

# Player spawn
player_x = spawn_x
player_y = spawn_y

# AI spawn (sejajar dengan player, bukan di belakang)
for i in range(ai_count):
    ai_x = spawn_x
    ai_y = spawn_y + 80 * (i + 1)  # 80 pixel ke bawah per AI
```

### Diagram Posisi Spawn

```
    START LINE
    ----------

    [PLAYER]     <- spawn_x, spawn_y

    [AI-1]       <- spawn_x, spawn_y + 80

    [AI-2]       <- spawn_x, spawn_y + 160

    [AI-3]       <- spawn_x, spawn_y + 240
```

---

## AI Decision Making

```python
# 1. Get sensor data
radar_data = ai.get_radar_data()
# Contoh output: [5, 8, 10, 7, 3]
# Format: [left_90, left_45, front, right_45, right_90]

# 2. Feed ke neural network
output = network.activate(radar_data)
# Contoh output: [0.2, 0.1, 0.8]
# Format: [left_steer, straight, right_steer]

# 3. Pilih action dengan value tertinggi
action = output.index(max(output))
# action = 2 (index dari 0.8)

# 4. Apply steering
if action == 0:
    ai.steer(1)    # Belok kiri
elif action == 1:
    pass           # Lurus (tidak steer)
elif action == 2:
    ai.steer(-1)   # Belok kanan
```

---

## UI Elements

### Info Panel (Kiri Atas)

```
+---------------------------+
| PLAYER [ALIVE]            |
|   Lap: 1/3                |
|                           |
| AI-1 [ALIVE]              |
|   Lap: 0/3                |
|                           |
| AI-2 [ALIVE]              |
|   Lap: 1/3                |
+---------------------------+
```

### Speedometer (Kanan Bawah)

```
+------------------------+
|  75     km/h           |
|  [==========       ]   |  <- Speed bar
+------------------------+

Bar color:
- Hijau: speed rendah
- Kuning: speed menengah
- Merah: speed tinggi
```

### Win Screen

```
+----------------------------------+
|                                  |
|         PLAYER WINS!             |
|                                  |
|   Press R to restart, ESC to quit|
|                                  |
+----------------------------------+
```

---

## Kontrol Keyboard

| Key   | Fungsi                       |
| ----- | ---------------------------- |
| W     | Gas maju (accelerate)        |
| S     | Rem / mundur (brake/reverse) |
| A     | Belok kiri                   |
| D     | Belok kanan                  |
| Space | Drift mode                   |
| Shift | Drift mode (alternatif)      |
| R     | Reset posisi semua entity    |
| ESC   | Keluar dari game             |

---

## Perbedaan Player vs AI

| Aspek      | Player                  | AI                        |
| ---------- | ----------------------- | ------------------------- |
| Input      | Keyboard (WASD)         | Neural network            |
| Speed      | Dikontrol manual        | Selalu max_speed          |
| Invincible | True (tidak mati)       | True (tidak mati)         |
| Masking    | Player masking          | AI masking (terpisah)     |
| Spawn      | Posisi spawn_x, spawn_y | Offset ke bawah           |
| Camera     | Diikuti kamera          | Tidak mempengaruhi kamera |

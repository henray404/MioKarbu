# Dokumentasi Kode - Tabrak Bahlil

Dokumentasi lengkap untuk semua modul dalam project game racing AI "Tabrak Bahlil". Dokumen ini menjelaskan arsitektur, logika, dan matematika yang digunakan dalam setiap komponen.

**Terakhir Diperbarui:** 17 Desember 2024

---

## Daftar Isi

1. [Gambaran Umum Project](#gambaran-umum-project)
2. [Struktur Dokumentasi](#struktur-dokumentasi)
3. [Arsitektur Sistem](#arsitektur-sistem)
4. [Perubahan Terbaru](#perubahan-terbaru)
5. [Panduan Membaca](#panduan-membaca)
6. [Ringkasan Rumus Matematika](#ringkasan-rumus-matematika)

---

## Gambaran Umum Project

Tabrak Bahlil adalah game racing 2D dengan fitur AI yang dilatih menggunakan algoritma NEAT (NeuroEvolution of Augmenting Topologies). Game ini memungkinkan:

1. **Mode Player vs AI**: Pemain berkompetisi melawan AI yang sudah dilatih
2. **Mode Training**: Melatih AI baru menggunakan evolutionary algorithm
3. **Mode Demo AI**: Menonton AI bermain sendiri

### Teknologi yang Digunakan

- **Pygame**: Library untuk rendering grafis dan input handling
- **NEAT-Python**: Implementasi algoritma NEAT untuk training neural network
- **Python 3.x**: Bahasa pemrograman utama

### Konsep Kunci

- **Composition Pattern**: Motor class menggunakan pattern ini untuk memisahkan tanggung jawab ke modul-modul kecil
- **Raycast Sensing**: AI menggunakan raycast untuk mendeteksi jarak ke dinding
- **Sequential Checkpoint**: Sistem lap counting yang mengharuskan melewati checkpoint secara berurutan

---

## Struktur Dokumentasi

```
dokumentasi/
│
├── README.md              <- File ini (index utama)
│
├── ai/                    <- Modul AI dan Training
│   ├── trainer.md         <- Class NEATTrainer utama
│   └── neat_trainer.md    <- Trainer alternatif dengan fitur tambahan
│
├── core/                  <- Modul Core Game (Modular)
│   ├── motor.md           <- Class Motor dengan composition pattern
│   ├── physics.md         <- PhysicsEngine untuk kalkulasi fisika
│   ├── collision.md       <- CollisionHandler untuk deteksi tabrakan
│   ├── checkpoint.md      <- CheckpointTracker untuk lap counting
│   ├── radar.md           <- Radar dan FitnessCalculator untuk AI
│   ├── track.md           <- Track loading dan raycast
│   ├── camera.md          <- Sistem kamera follow
│   └── distance_sensor.md <- Sensor jarak alternatif
│
├── main.md                <- Entry point game (Player vs AI)
├── train.md               <- Entry point training AI
└── config.md              <- Konfigurasi NEAT
```

---

## Arsitektur Sistem

### Diagram Komponen Utama

```
+------------------------------------------------------------------+
|                        TABRAK BAHLIL                              |
+------------------------------------------------------------------+
|                                                                   |
|  ENTRY POINTS:                                                    |
|  +-- main.py      : Mode Player vs AI                             |
|  +-- train.py     : Mode Training AI                              |
|  +-- play_ai.py   : Mode Demo AI                                  |
|                                                                   |
|  CORE COMPONENTS:                                                 |
|  +-- Motor (Composition Pattern)                                  |
|  |    +-- PhysicsEngine      : Kalkulasi pergerakan dan steering  |
|  |    +-- CollisionHandler   : Deteksi tabrakan dan checkpoint    |
|  |    +-- CheckpointTracker  : Penghitungan lap                   |
|  |    +-- Radar              : Sensing jarak untuk AI             |
|  |    +-- FitnessCalculator  : Penghitungan skor fitness          |
|  |                                                                |
|  +-- Track    : Loading peta dan raycast                          |
|  +-- Camera   : Smooth camera follow dengan interpolasi           |
|                                                                   |
|  AI COMPONENTS:                                                   |
|  +-- NEATTrainer  : Evolutionary training algorithm               |
|  +-- config.txt   : Parameter konfigurasi NEAT                    |
|                                                                   |
+------------------------------------------------------------------+
```

### Penjelasan Arsitektur

**Composition Pattern** digunakan pada class Motor untuk memisahkan berbagai tanggung jawab:

1. **PhysicsEngine**: Menangani semua kalkulasi fisika termasuk akselerasi, steering dengan speed-dependent rate, sistem grip, dan mekanik drift.

2. **CollisionHandler**: Menangani deteksi tabrakan menggunakan masking surface. Mendukung berbagai zone seperti track, wall, slow zone, dan checkpoint.

3. **CheckpointTracker**: Menangani sistem checkpoint sequential dan penghitungan lap. Motor harus melewati 4 checkpoint secara berurutan untuk lap yang valid.

4. **Radar**: Sistem raycast untuk AI yang mendeteksi jarak ke dinding di 5 arah berbeda. Output dinormalisasi untuk input neural network.

5. **FitnessCalculator**: Menghitung fitness score untuk training NEAT berdasarkan jarak tempuh, posisi unik yang dikunjungi, dan jumlah lap.

---

## Perubahan Terbaru

### Refactoring ke Composition Pattern

Sebelumnya, class Motor adalah satu file besar dengan semua logika. Sekarang sudah dipisah menjadi modul-modul:

| Komponen Baru     | File          | Fungsi                      |
| ----------------- | ------------- | --------------------------- |
| PhysicsEngine     | physics.py    | Steering, akselerasi, drift |
| CollisionHandler  | collision.py  | Deteksi tabrakan multi-zone |
| CheckpointTracker | checkpoint.py | Lap counting sequential     |
| Radar             | radar.py      | AI distance sensing         |
| FitnessCalculator | radar.py      | AI fitness score            |

### Fitur Baru di train.py

1. **Resume Training**: Bisa melanjutkan training dari checkpoint yang tersimpan

   ```bash
   python train.py -c neat_checkpoints/neat-checkpoint-50
   ```

2. **Auto-save on Interrupt**: Ketika menekan Ctrl+C, program akan menyimpan best genome secara otomatis ke `models/interrupted_genome.pkl`

---

## Panduan Membaca

### Untuk Memahami Game Flow

1. Baca [main.md](main.md) untuk memahami bagaimana game berjalan
2. Baca [motor.md](core/motor.md) untuk memahami entity utama
3. Baca [physics.md](core/physics.md) untuk memahami sistem fisika

### Untuk Memahami AI Training

1. Baca [trainer.md](ai/trainer.md) untuk memahami proses training
2. Baca [config.md](config.md) untuk memahami parameter NEAT
3. Baca [radar.md](core/radar.md) untuk memahami input neural network
4. Baca [checkpoint.md](core/checkpoint.md) untuk memahami sistem lap

### Untuk Memahami Fisika

1. Baca [physics.md](core/physics.md) untuk semua rumus fisika
2. Baca [collision.md](core/collision.md) untuk sistem collision
3. Baca [camera.md](core/camera.md) untuk sistem kamera

---

## Ringkasan Rumus Matematika

### Fisika Motor

| Konsep                       | Rumus                                            | Penjelasan                                                                                                               |
| ---------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| **Speed-dependent Steering** | `rate = base - (base - min) * speed_ratio`       | Steering menjadi lebih sulit saat kecepatan tinggi. Base rate 4.5 derajat/frame berkurang hingga min 1.2 saat max speed. |
| **Understeer**               | `effective = steer * (1 - speed_ratio * factor)` | Di kecepatan tinggi, motor cenderung lurus meski belok. Factor 0.3 berarti 30% understeer di max speed.                  |
| **Drag Effect**              | `accel = base * (1 - speed_ratio * 0.5)`         | Akselerasi berkurang mendekati max speed. Di 100% speed, akselerasi hanya 50%.                                           |
| **Speed Penalty**            | `velocity *= (1 - penalty * turn_intensity)`     | Kehilangan kecepatan proporsional dengan intensitas belokan.                                                             |

### Sistem Kamera

| Konsep                          | Rumus                                | Penjelasan                                                                                 |
| ------------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------ |
| **Linear Interpolation (Lerp)** | `pos += (target - pos) * smoothness` | Kamera bergerak smooth menuju target. Smoothness 0.15 berarti 15% menuju target per frame. |

### AI Sensing

| Konsep                  | Rumus                                         | Penjelasan                                             |
| ----------------------- | --------------------------------------------- | ------------------------------------------------------ |
| **Raycast Position**    | `P(t) = start + (cos(angle), sin(angle)) * t` | Posisi raycast pada jarak t dari start point.          |
| **Normalized Distance** | `normalized = distance / max_distance`        | Jarak dinormalisasi ke 0-1 untuk input neural network. |

### Fitness Calculation

| Kondisi                  | Rumus                                                                     | Penjelasan                                |
| ------------------------ | ------------------------------------------------------------------------- | ----------------------------------------- |
| **Sebelum Complete Lap** | `F = (unique_pos * 10) + (rotation / 2) + (distance / 50) - (stuck * 20)` | Fokus pada exploration dan movement.      |
| **Setelah Complete Lap** | `F = (lap^2 * 1000) + (efficiency * 50) + (unique_pos * 3)`               | Fokus pada lap completion dan efficiency. |

---

## Link ke Dokumentasi Detail

### Modul AI

- [trainer.md](ai/trainer.md) - NEAT trainer utama yang digunakan oleh train.py
- [neat_trainer.md](ai/neat_trainer.md) - Trainer alternatif dengan fitur visualisasi lengkap

### Modul Core (Arsitektur Baru)

- [motor.md](core/motor.md) - Class Motor dengan composition pattern
- [physics.md](core/physics.md) - PhysicsEngine dengan semua rumus fisika
- [collision.md](core/collision.md) - CollisionHandler dengan masking colors
- [checkpoint.md](core/checkpoint.md) - CheckpointTracker dengan sequential system
- [radar.md](core/radar.md) - Radar dan FitnessCalculator untuk AI

### Modul Core (Legacy)

- [track.md](core/track.md) - Track loading dan brightness-based collision
- [camera.md](core/camera.md) - Smooth camera follow dengan lerp
- [distance_sensor.md](core/distance_sensor.md) - Alternative sensor untuk raycast

### Entry Points

- [main.md](main.md) - Entry point game Player vs AI
- [train.md](train.md) - Entry point training AI

### Konfigurasi

- [config.md](config.md) - Parameter NEAT dengan penjelasan detail

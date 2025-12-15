# 📚 Dokumentasi Kode - Tabrak Bahlil

Dokumentasi lengkap untuk semua modul dalam project.

---

## 📁 Struktur Dokumentasi

```
dokumentasi/
├── README.md              # File ini
├── ai/
│   ├── trainer.md         # Training NEAT utama
│   └── neat_trainer.md    # Trainer alternatif
├── core/
│   ├── motor.md           # ⭐ Physics & Motor (PALING PENTING)
│   ├── track.md           # Track loading & collision
│   ├── camera.md          # Camera follow system
│   └── distance_sensor.md # Sensor raycasting
├── main.md                # Entry point game
├── train.md               # Entry point training
└── config.md              # NEAT configuration
```

---

## 🔗 Quick Links

### AI Training

| File                                  | Deskripsi                               |
| ------------------------------------- | --------------------------------------- |
| [trainer.md](ai/trainer.md)           | NEAT trainer utama (dipakai train.py)   |
| [neat_trainer.md](ai/neat_trainer.md) | Trainer alternatif dengan fitur lengkap |

### Core Components

| File                                          | Deskripsi                                         |
| --------------------------------------------- | ------------------------------------------------- |
| [motor.md](core/motor.md)                     | ⭐ **Class Motor** - physics, collision, AI radar |
| [track.md](core/track.md)                     | Track loading, brightness-based collision         |
| [camera.md](core/camera.md)                   | Smooth camera follow dengan Lerp                  |
| [distance_sensor.md](core/distance_sensor.md) | Raycast sensor untuk AI                           |

### Entry Points

| File                 | Deskripsi                            |
| -------------------- | ------------------------------------ |
| [main.md](main.md)   | Game Player vs AI                    |
| [train.md](train.md) | Training AI dengan command line args |

### Configuration

| File                   | Deskripsi                                 |
| ---------------------- | ----------------------------------------- |
| [config.md](config.md) | NEAT parameters dengan penjelasan lengkap |

---

## 🎯 Mulai dari Mana?

1. **Pahami game flow** → Baca [main.md](main.md)
2. **Pahami physics** → Baca [motor.md](core/motor.md) ⭐
3. **Pahami AI training** → Baca [trainer.md](ai/trainer.md) dan [config.md](config.md)
4. **Pahami collision** → Baca [track.md](core/track.md)

---

## 📐 Rumus Matematika Penting

| Konsep                   | Rumus                                        | File       |
| ------------------------ | -------------------------------------------- | ---------- |
| Speed-dependent steering | `rate = base - (base-min) × speed_ratio`     | motor.md   |
| Understeer               | `steer × (1 - speed_ratio × factor)`         | motor.md   |
| Camera Lerp              | `pos += (target - pos) × smoothness`         | camera.md  |
| Raycast                  | `P(t) = start + (cos(θ), sin(θ)) × t`        | track.md   |
| Fitness                  | `F = distance + checkpoints×200 + laps×2000` | trainer.md |

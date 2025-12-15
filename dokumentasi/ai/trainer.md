# 📁 trainer.py

> Path: `src/ai/trainer.py`

## Deskripsi

Trainer utama untuk evolusi AI menggunakan algoritma **NEAT (NeuroEvolution of Augmenting Topologies)**. File ini digunakan oleh `train.py` sebagai entry point training.

---

## Class: `NEATTrainer`

### Constructor

```python
def __init__(self, config_path: str, track_name: str = "mandalika",
             screen_width: int = 1280, screen_height: int = 960,
             map_width: int = 16512, map_height: int = 9216,
             headless: bool = False, render_interval: int = 1)
```

### Parameter:

| Parameter         | Type | Default     | Deskripsi                            |
| ----------------- | ---- | ----------- | ------------------------------------ |
| `config_path`     | str  | -           | Path ke file config NEAT             |
| `track_name`      | str  | "mandalika" | Nama track untuk training            |
| `screen_width`    | int  | 1280        | Lebar window pygame                  |
| `screen_height`   | int  | 960         | Tinggi window pygame                 |
| `map_width`       | int  | 16512       | Lebar map (6x scale)                 |
| `map_height`      | int  | 9216        | Tinggi map (6x scale)                |
| `headless`        | bool | False       | Mode tanpa visualisasi (lebih cepat) |
| `render_interval` | int  | 1           | Render setiap N frame                |

---

## Method Utama

### `setup()`

Inisialisasi pygame dan load resources.

**Logic:**

1. Jika `headless=True`, set `SDL_VIDEODRIVER=dummy`
2. Initialize pygame
3. Load track surface
4. Load masking surface (untuk collision)
5. Initialize fonts (jika tidak headless)

```python
def setup(self):
    if self.headless:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    # Load track dan masking...
```

---

### `eval_genomes(genomes, config)`

**Callback utama NEAT** - dipanggil setiap generasi.

**Flow:**

```
1. Increment generation counter
2. Untuk setiap genome:
   └── Buat Motor dan FeedForwardNetwork
3. Loop simulasi:
   ├── Check timeout (max 60 detik/generasi)
   ├── Untuk setiap motor hidup:
   │   ├── Get radar data (5 sensor)
   │   ├── Neural network predict action
   │   ├── Apply steering (0=kiri, 1=lurus, 2=kanan)
   │   ├── Update motor physics
   │   └── Calculate fitness
   ├── Check win condition (target laps)
   └── Render (jika tidak headless)
4. Return saat semua mati atau ada winner
```

### Fitness Calculation:

```python
fitness = car.distance_traveled           # Base: jarak tempuh
fitness += car.checkpoint_count * 200     # Bonus: checkpoint
fitness += car.lap_count * 2000            # Bonus besar: lap complete
```

**Matematika:**

```
F = D + (C × 200) + (L × 2000)

Dimana:
- D = distance traveled (pixel)
- C = checkpoint count (0-4 per lap)
- L = lap count
```

---

### `run(generations: int = 50)`

Jalankan training NEAT.

**Flow:**

1. `setup()` - init pygame
2. Load NEAT config
3. Create `neat.Population`
4. Add reporters:
   - `StdOutReporter` - print ke console
   - `StatisticsReporter` - track stats
   - `Checkpointer` - save checkpoint setiap 5 gen
5. Run evolution dengan `eval_genomes` callback
6. Save best genome ke `models/`

```python
def run(self, generations=50):
    self.setup()
    config = neat.Config(...)
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    winner = population.run(self.eval_genomes, generations)
    # Save winner...
```

---

### `_handle_winner(genome, net, car, config)`

Dipanggil saat ada motor yang mencapai target laps.

**Actions:**

1. Set `winner_found = True`
2. Print success message
3. Save `winner_genome.pkl` dan `winner_network.pkl`

---

## Diagram Alur

```
┌─────────────────────────────────────────────────────────────┐
│                    TRAINING FLOW                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  train.py                                                    │
│     │                                                        │
│     └── NEATTrainer.run(generations=50)                      │
│            │                                                 │
│            ├── setup() → Load pygame, track, masking         │
│            │                                                 │
│            └── population.run(eval_genomes, 50)              │
│                   │                                          │
│                   └── [LOOP setiap generasi]                 │
│                          │                                   │
│                          └── eval_genomes(genomes, config)   │
│                                 │                            │
│                                 ├── Create 100+ motors       │
│                                 ├── Simulate racing          │
│                                 ├── Calculate fitness        │
│                                 └── NEAT selects best        │
│                                                              │
│  Output: models/winner_genome.pkl                            │
│          models/winner_network.pkl                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Konstanta Penting

| Konstanta                      | Nilai | Deskripsi              |
| ------------------------------ | ----- | ---------------------- |
| `max_gen_time`                 | 60s   | Timeout per generasi   |
| `max_time_between_checkpoints` | 60s   | Kill AI jika stuck     |
| `checkpoint_bonus`             | 200   | Fitness per checkpoint |
| `lap_bonus`                    | 2000  | Fitness per lap        |

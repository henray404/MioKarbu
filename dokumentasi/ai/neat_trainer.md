# 📁 neat_trainer.py

> Path: `src/ai/neat_trainer.py`

## Deskripsi

Versi alternatif trainer NEAT dengan fitur lebih lengkap. Mirip dengan `trainer.py` tapi dengan:

- Visualisasi lebih detail
- Save/load genome terpisah
- Entry point standalone

---

## Class: `NEATTrainer`

### Constructor

```python
def __init__(self, config_path: str, track_name: str = "japan", visualize: bool = True)
```

| Parameter     | Default | Deskripsi               |
| ------------- | ------- | ----------------------- |
| `config_path` | -       | Path ke neat-config.txt |
| `track_name`  | "japan" | Track untuk training    |
| `visualize`   | True    | Tampilkan window pygame |

---

## Method Utama

### `create_motor(genome, config)`

Buat motor dengan neural network dari genome.

```python
def create_motor(self, genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    motor = Motor(self.spawn_x, self.spawn_y, color="pink")
    motor.set_track(self.track)
    motor.create_sensor(num_sensors=5, fov=180, max_distance=200)
    return motor, net
```

### `calculate_fitness(motor, frames_alive)`

Hitung fitness score untuk motor.

**Components:**

```python
fitness = (
    motor.distance_traveled * 1.0 +      # Jarak utama
    avg_speed * 0.1 +                     # Bonus kecepatan
    frames_alive * 0.01                    # Bonus survival
)
```

### `eval_genomes(genomes, config)`

Evaluasi semua genome. Mendelegasi ke:

- `_eval_genomes_headless()` - tanpa visual
- `_eval_genomes_visual()` - dengan pygame window

### `save_best_genome(genome, filename)`

Save genome terbaik ke file pkl.

### `load_genome(filename)` [static]

Load genome dari file pkl.

---

## Perbedaan dengan trainer.py

| Fitur           | trainer.py       | neat_trainer.py    |
| --------------- | ---------------- | ------------------ |
| Headless mode   | ✅ Flag          | ✅ visualize param |
| Render interval | ✅ Configurable  | ❌ Fixed           |
| Track loading   | Langsung surface | Via Track class    |
| Checkpointer    | ✅ Built-in      | ✅ Built-in        |
| Entry point     | Via train.py     | Standalone         |

---

## Kapan Pakai?

- **trainer.py**: Training produksi via `train.py`
- **neat_trainer.py**: Development/debugging dengan kontrol lebih

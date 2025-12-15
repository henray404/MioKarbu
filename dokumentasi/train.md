# 📁 train.py

> Path: `src/train.py`

## Deskripsi

Entry point untuk **training AI** menggunakan NEAT algorithm.

---

## Command Line Arguments

```bash
python train.py [options]
```

| Argument            | Short | Default   | Deskripsi                      |
| ------------------- | ----- | --------- | ------------------------------ |
| `--generations`     | `-g`  | 50        | Jumlah generasi training       |
| `--track`           | `-t`  | mandalika | Nama track untuk training      |
| `--laps`            | `-l`  | 15        | Target lap untuk menang        |
| `--headless`        | -     | False     | Mode tanpa visualisasi (cepat) |
| `--render-interval` | `-r`  | 1         | Render setiap N frame          |

---

## Contoh Penggunaan

```bash
# Default training
python train.py

# 100 generasi, track "new"
python train.py -g 100 --track new

# Headless mode (3-5x lebih cepat)
python train.py --headless

# Reduced render (tetap ada visualisasi, lebih cepat)
python train.py --render-interval 10

# Kombinasi lengkap
python train.py -g 200 --track new --headless
```

---

## Flow

```python
def main():
    # 1. Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--generations', '-g', type=int, default=50)
    parser.add_argument('--track', '-t', type=str, default='mandalika')
    parser.add_argument('--laps', '-l', type=int, default=15)
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--render-interval', '-r', type=int, default=1)
    args = parser.parse_args()

    # 2. Setup config path
    config_path = os.path.join(BASE_DIR, "config.txt")

    # 3. Print info
    print("=" * 60)
    print("  TABRAK BAHLIL - NEAT AI Training")
    print("=" * 60)
    print(f"Track       : {args.track}")
    print(f"Generations : {args.generations}")
    print(f"Target Laps : {args.laps}")
    print(f"Mode        : {'HEADLESS' if args.headless else 'Visual'}")

    # 4. Create trainer
    trainer = NEATTrainer(
        config_path=config_path,
        track_name=args.track,
        headless=args.headless,
        render_interval=args.render_interval
    )
    trainer.target_laps = args.laps

    # 5. Run training
    winner = trainer.run(generations=args.generations)

    # 6. Report results
    if winner:
        print(f"Best fitness: {winner.fitness:.2f}")
        print("Model tersimpan di: models/")
```

---

## Output Files

Training akan menghasilkan file di `models/`:

| File                 | Deskripsi                              |
| -------------------- | -------------------------------------- |
| `winner_genome.pkl`  | Genome yang mencapai target laps       |
| `winner_network.pkl` | Neural network dari winner             |
| `best_genome.pkl`    | Genome terbaik (jika tidak ada winner) |
| `best_network.pkl`   | Network dari best genome               |

Dan checkpoints di `neat_checkpoints/`:

| File                | Deskripsi                    |
| ------------------- | ---------------------------- |
| `neat-checkpoint-X` | Checkpoint setiap 5 generasi |

---

## Mode Training

### Visual Mode (Default)

```bash
python train.py
```

- Window pygame ditampilkan
- Bisa melihat motor bergerak
- Lebih lambat tapi informatif

### Headless Mode

```bash
python train.py --headless
```

- Tanpa window
- 3-5x lebih cepat
- Untuk production training

### Reduced Render

```bash
python train.py --render-interval 10
```

- Window tetap ada
- Render setiap 10 frame
- Kompromi speed vs visibility

---

## Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    TRAIN.PY FLOW                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  $ python train.py -g 100 --track new --headless            │
│     │                                                        │
│     ├── Parse arguments                                      │
│     │                                                        │
│     ├── Create NEATTrainer                                   │
│     │      ├── config_path = "config.txt"                    │
│     │      ├── track_name = "new"                            │
│     │      ├── headless = True                               │
│     │      └── render_interval = 1                           │
│     │                                                        │
│     └── trainer.run(generations=100)                         │
│            │                                                 │
│            ├── [Generation 1]                                │
│            │      └── Evaluate 150 genomes                   │
│            ├── [Generation 2]                                │
│            │      └── Best survive, mutate                   │
│            ├── ...                                           │
│            └── [Generation 100]                              │
│                   └── Save best to models/                   │
│                                                              │
│  Output:                                                     │
│  - models/winner_genome.pkl                                  │
│  - models/winner_network.pkl                                 │
│  - neat_checkpoints/neat-checkpoint-*                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

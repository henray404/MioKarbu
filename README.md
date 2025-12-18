# Mio Karbu Racing

Game balap motor dengan AI menggunakan **NEAT** (NeuroEvolution of Augmenting Topologies).

> Final Project OOP - Semester 3

---

## Cara Main

### Player Mode

```bash
cd src
python main.py
```

| Key               | Action       |
| ----------------- | ------------ |
| `W`               | Maju / Gas   |
| `S`               | Mundur / Rem |
| `A`               | Belok Kiri   |
| `D`               | Belok Kanan  |
| `ESC`             | Pause        |

---

## Training AI

```bash
cd src
python train.py                     # Default: 50 generasi, map-2
python train.py -g 100              # 100 generasi
python train.py -t new-4            # Track new-4
python train.py --headless          # Training tanpa visual (lebih cepat)
python train.py --checkpoint neat_checkpoints/neat-checkpoint-10  # Resume
```

**Output:** Model tersimpan di `models/winner_{map_name}.pkl`

---

## Struktur Project

```
MioKarbu/
├── src/
│   ├── main.py              # Entry point game
│   ├── train.py             # Script training AI
│   ├── core/
│   │   ├── motor.py         # Motor class (main entity)
│   │   ├── physics.py       # Physics engine (velocity, steering, drift)
│   │   ├── collision.py     # Collision detection dari masking
│   │   ├── checkpoint.py    # Lap counting (sequential checkpoint)
│   │   ├── radar.py         # Sensor AI (5 radar)
│   │   ├── game_manager.py  # Asset loading
│   │   └── display_manager.py # Rendering & camera
│   ├── ai/
│   │   └── trainer.py       # NEAT Trainer class
│   ├── screens/
│   │   ├── main_menu.py     # Menu utama
│   │   └── pick_map.py      # Map selection
│   └── ui/
│       ├── hud.py           # Leaderboard, lap counter, speedometer
│       └── hover_button.py  # Button component
├── config/
│   └── game_config.py       # Konfigurasi terpusat (MAP_SETTINGS)
├── assets/
│   ├── motor/               # Sprite motor (pink, blue, purple, yellow)
│   ├── tracks/              # Track images + masking/
│   ├── ui/                  # Button & background
│   └── audio/               # Sound effects
├── models/                  # Trained AI models (.pkl)
├── neat_checkpoints/        # Training checkpoints
└── config.txt               # NEAT configuration
```

---
## Maps

| Key     | Track File | Masking          |
| ------- | ---------- | ---------------- |
| `map-2` | map-2.png  | ai_masking-5.png |
| `new-4` | new-4.png  | ai_masking-4.png |

---

## Install

```bash
pip install -r requirements.txt
```

**Dependencies:**

- Python 3.10+
- Pygame 2.6+
- neat-python


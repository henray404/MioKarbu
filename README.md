# Tabrak Bahlil

Game balap motor dengan AI menggunakan NEAT (NeuroEvolution of Augmenting Topologies).

## Struktur Project

```
tabrak-bahlil/
├── main.py              # Entry point - Player mode (WASD control)
├── config.txt           # NEAT configuration
├── requirements.txt     # Python dependencies
├── assets/
│   ├── motor/           # Sprite motor
│   └── tracks/          # Track images
├── models/              # Trained AI models
│   └── *.pkl
├── neat_checkpoints/    # Training checkpoints
└── src/
    ├── train.py         # Training script untuk AI
    ├── play_ai.py       # Jalankan AI yang sudah ditraining
    ├── core/
    │   ├── ai_car.py    # AI Car class dengan sensor radar
    │   ├── motor.py     # Motor class untuk player
    │   ├── track.py     # Track loader & collision
    │   └── distance_sensor.py
    └── ai/
        └── trainer.py   # NEAT Trainer class
```

## Cara Main

### Player Mode
```bash
python main.py
```
- `W` - Maju
- `S` - Mundur
- `A` - Belok kiri
- `D` - Belok kanan

### Training AI
```bash
cd src
python train.py                     # Default: 50 generasi
python train.py -g 100              # 100 generasi
python train.py -t mandalika -l 10  # Track mandalika, target 10 lap
```

### Play dengan AI
```bash
cd src
python play_ai.py                           # Model default
python play_ai.py -m winner_15laps_genome.pkl  # Model tertentu
```

## Teknologi

- **Python 3.13+** dengan **Pygame 2.6**
- **NEAT-Python** untuk neural evolution
- **5 Sensor Radar** (input untuk neural network)
- **3 Output**: Belok kiri, Lurus, Belok kanan

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Track yang Tersedia

- `mandalika` - Sirkuit Mandalika
- `japan` - Sirkuit Japan
- `japan-1` - Sirkuit Japan (variant)

## Training Tips

1. Mulai dengan generasi kecil (50) untuk testing
2. Tingkatkan target lap secara bertahap
3. Gunakan checkpoint untuk melanjutkan training:
   ```bash
   python train.py --checkpoint neat_checkpoints/neat-checkpoint-49
   ```


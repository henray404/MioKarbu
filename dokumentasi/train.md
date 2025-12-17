# train.py - Entry Point Training AI

> Lokasi: `src/train.py`

---

## Deskripsi Umum

File train.py adalah entry point untuk training AI menggunakan algoritma NEAT (NeuroEvolution of Augmenting Topologies). File ini menyediakan command line interface untuk mengonfigurasi berbagai parameter training.

---

## Command Line Arguments

```bash
python train.py [options]
```

### Tabel Arguments

| Argument          | Short | Type   | Default   | Deskripsi                       |
| ----------------- | ----- | ------ | --------- | ------------------------------- |
| --generations     | -g    | int    | 50        | Jumlah generasi training        |
| --track           | -t    | string | mandalika | Nama file track (tanpa .png)    |
| --laps            | -l    | int    | 15        | Target lap untuk winner         |
| --headless        | -     | flag   | False     | Training tanpa visualisasi      |
| --render-interval | -r    | int    | 1         | Render setiap N frame           |
| --checkpoint      | -c    | string | None      | Path ke checkpoint untuk resume |

### Penjelasan Detail Arguments

**--generations (-g)**

Jumlah generasi yang akan dijalankan. Satu generasi = satu siklus evaluasi populasi + seleksi + reproduksi. Lebih banyak generasi = AI lebih baik tapi butuh waktu lebih lama.

Panduan:

- 10-30: Quick test, hasil belum optimal
- 50-100: Training standar
- 200+: Training intensif untuk hasil terbaik

**--track (-t)**

Nama track yang digunakan untuk training. File track harus ada di `assets/tracks/{nama}.png`. Track yang berbeda memiliki tingkat kesulitan berbeda.

**--laps (-l)**

Jumlah lap yang harus dicapai untuk dianggap "winner". Jika ada genome yang mencapai target ini, training otomatis berhenti dan model disimpan.

**--headless**

Mode tanpa visualisasi grafis. Training berjalan 3-5x lebih cepat karena tidak perlu render frame. Cocok untuk training production di server.

**--render-interval (-r)**

Render visual setiap N frame. Contoh: `--render-interval 10` berarti render 1x setiap 10 frame. Kompromi antara speed dan visibility.

**--checkpoint (-c)**

Path ke checkpoint file untuk melanjutkan training yang terputus. Checkpoint otomatis disimpan setiap 5 generasi di folder `neat_checkpoints/`.

---

## Contoh Penggunaan

### Training Basic

```bash
# Training default (50 generasi, visual)
python train.py

# 100 generasi dengan track "new"
python train.py -g 100 --track new

# Training dengan target 10 lap
python train.py -g 100 --laps 10
```

### Training Cepat (Headless)

```bash
# Headless mode - 3-5x lebih cepat
python train.py --headless

# Headless dengan 200 generasi
python train.py -g 200 --headless

# Reduced render (visual tapi lebih cepat)
python train.py --render-interval 10
```

### Resume Training

```bash
# Lihat checkpoint yang tersedia
ls neat_checkpoints/
# Output: neat-checkpoint-5  neat-checkpoint-10  neat-checkpoint-15 ...

# Resume dari checkpoint tertentu
python train.py -c neat_checkpoints/neat-checkpoint-50

# Resume dan tambah 50 generasi lagi
python train.py -c neat_checkpoints/neat-checkpoint-50 -g 50
```

### Kombinasi Lengkap

```bash
# Training intensif: 200 generasi, headless, track baru, 20 lap target
python train.py -g 200 --headless --track new --laps 20

# Resume training dengan reduced render
python train.py -c neat_checkpoints/neat-checkpoint-100 --render-interval 5
```

---

## Alur Kerja Program

```
+------------------------------------------------------------------+
|                       TRAIN.PY FLOW                               |
+------------------------------------------------------------------+
|                                                                   |
|  1. PARSE ARGUMENTS                                               |
|     |                                                             |
|     +-- argparse.ArgumentParser()                                 |
|     +-- Validate dan set defaults                                 |
|                                                                   |
|  2. SETUP PATHS                                                   |
|     |                                                             |
|     +-- config_path = "config.txt" (NEAT config)                  |
|     +-- Check file exists                                         |
|                                                                   |
|  3. PRINT INFO                                                    |
|     |                                                             |
|     +-- Track, Generations, Target Laps                           |
|     +-- Mode (headless/visual)                                    |
|     +-- Checkpoint jika resume                                    |
|                                                                   |
|  4. CREATE TRAINER                                                |
|     |                                                             |
|     +-- NEATTrainer(config_path, track_name, headless, ...)       |
|     +-- Set target_laps                                           |
|                                                                   |
|  5. RUN TRAINING                                                  |
|     |                                                             |
|     +-- trainer.run(generations, checkpoint_path)                 |
|     |                                                             |
|     +-- [Untuk setiap generasi]                                   |
|     |   +-- Evaluasi semua genome                                 |
|     |   +-- Hitung fitness                                        |
|     |   +-- Seleksi dan reproduksi                                |
|     |   +-- Save checkpoint (setiap 5 gen)                        |
|     |                                                             |
|     +-- Return winner atau best genome                            |
|                                                                   |
|  6. REPORT RESULTS                                                |
|     |                                                             |
|     +-- Print best fitness                                        |
|     +-- Model location                                            |
|                                                                   |
|  7. HANDLE INTERRUPT (Ctrl+C)                                     |
|     |                                                             |
|     +-- Load latest checkpoint                                    |
|     +-- Save best genome ke interrupted_genome.pkl                |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Fitur Auto-save on Interrupt

Jika training dihentikan dengan Ctrl+C, program akan otomatis menyimpan best genome dari checkpoint terakhir.

```python
except KeyboardInterrupt:
    print("Training dihentikan oleh user")

    # Cari checkpoint terakhir
    checkpoint_dir = "neat_checkpoints"
    checkpoints = [f for f in os.listdir(checkpoint_dir)
                   if f.startswith("neat-checkpoint-")]

    if checkpoints:
        # Sort by generation number
        checkpoints.sort(key=lambda x: int(x.split("-")[-1]))
        latest = os.path.join(checkpoint_dir, checkpoints[-1])

        # Load dan save best genome
        pop = neat.Checkpointer.restore_checkpoint(latest)
        best = pop.best_genome

        if best:
            with open('models/interrupted_genome.pkl', 'wb') as f:
                pickle.dump(best, f)
            print("Best genome saved to: models/interrupted_genome.pkl")
            print(f"Fitness: {best.fitness:.2f}")
```

---

## Output Files

### Folder models/

| File                   | Kondisi                             | Deskripsi                     |
| ---------------------- | ----------------------------------- | ----------------------------- |
| winner_genome.pkl      | Ada genome yang mencapai target lap | Genome pemenang               |
| winner_network.pkl     | Ada winner                          | Neural network dari winner    |
| best_genome.pkl        | Training selesai tanpa winner       | Genome terbaik                |
| best_network.pkl       | Training selesai tanpa winner       | Network dari best             |
| interrupted_genome.pkl | Training di-interrupt (Ctrl+C)      | Best dari checkpoint terakhir |

### Folder neat_checkpoints/

| File               | Deskripsi                     |
| ------------------ | ----------------------------- |
| neat-checkpoint-5  | State populasi di generasi 5  |
| neat-checkpoint-10 | State populasi di generasi 10 |
| ...                | Checkpoint setiap 5 generasi  |

---

## Tips Optimasi Training

### Untuk Training Lebih Cepat

1. Gunakan `--headless` untuk skip rendering
2. Gunakan `--render-interval 10` jika butuh visual sesekali
3. Kurangi `--laps` untuk testing
4. Gunakan hardware dengan CPU yang lebih cepat

### Untuk Hasil Lebih Baik

1. Gunakan lebih banyak `--generations` (200+)
2. Tingkatkan `--laps` untuk AI yang lebih reliable
3. Edit `config.txt` untuk tuning parameter NEAT
4. Pastikan track masking sudah benar

### Troubleshooting

**Training terlalu lambat:**

- Gunakan `--headless`
- Kurangi `pop_size` di config.txt (tapi bisa kurangi kualitas)

**AI tidak improve:**

- Cek masking track sudah benar
- Tingkatkan `--generations`
- Coba tuning parameter di config.txt

**Training terputus:**

- Gunakan `--checkpoint` untuk resume
- Check file interrupted_genome.pkl

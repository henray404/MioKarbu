# Dokumentasi Penggunaan Racing Game dengan AI

Panduan lengkap untuk menjalankan game racing dan training AI.

---

## Daftar Isi

1. [Persyaratan Sistem](#1-persyaratan-sistem)
2. [Struktur Folder](#2-struktur-folder)
3. [Menjalankan Game (Main)](#3-menjalankan-game-main)
4. [Training AI](#4-training-ai)
5. [Konfigurasi Training](#5-konfigurasi-training)
6. [Mengedit Masking](#6-mengedit-masking)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Persyaratan Sistem

### Software yang Dibutuhkan

- Python 3.10 atau lebih baru
- pip (Python package manager)

### Instalasi Dependencies

Buka terminal di folder project dan jalankan:

```bash
pip install pygame neat-python
```

### Cek Instalasi

```bash
python -c "import pygame; import neat; print('OK')"
```

Jika output "OK", instalasi berhasil.

---

## 2. Struktur Folder

```
final_project/
├── assets/                 # Asset game
│   ├── track.png          # Gambar track
│   ├── masking.png        # Masking untuk player
│   ├── ai_masking.png     # Masking untuk AI training
│   └── motor_*.png        # Sprite motor
│
├── config.txt             # Konfigurasi NEAT
│
├── dokumentasi/           # Dokumentasi
│   ├── perubahan.md       # Changelog
│   └── penggunaan.md      # File ini
│
├── models/                # Model AI yang sudah ditraining
│   ├── winner_genome.pkl  # Genome terbaik
│   └── winner_network.pkl # Network siap pakai
│
├── neat_checkpoints/      # Checkpoint training NEAT
│
└── src/                   # Source code
    ├── ai/
    │   └── trainer.py     # Training AI
    ├── core/
    │   └── motor.py       # Class motor
    ├── main.py            # Game utama
    ├── train.py           # Entry point training
    └── play_ai.py         # Main model AI
```

---

## 3. Menjalankan Game (Main)

### Menjalankan Game

```bash
cd src
python main.py
```

### Kontrol Player

| Tombol | Fungsi                   |
| ------ | ------------------------ |
| W      | Gas / Maju               |
| S      | Rem / Mundur             |
| A      | Belok Kiri               |
| D      | Belok Kanan              |
| SPACE  | Drift (tahan saat belok) |
| ESC    | Keluar game              |

### Tampilan Game

- Speedometer di kiri bawah
- Lap counter di kanan atas
- Best lap time ditampilkan setelah selesai lap

---

## 4. Training AI

### Menjalankan Training

```bash
cd src
python train.py --generations 50 --track new
```

### Parameter Training

| Parameter       | Deskripsi                           | Default |
| --------------- | ----------------------------------- | ------- |
| `--generations` | Jumlah generasi training            | 50      |
| `--track`       | Nama track ("new" untuk track baru) | new     |
| `--laps`        | Target lap untuk menang             | 3       |

### Contoh Penggunaan

```bash
# Training 100 generasi
python train.py --generations 100 --track new

# Training dengan target 5 lap
python train.py --generations 50 --track new --laps 5
```

### Menghentikan Training

Tekan Ctrl+C di terminal atau tutup window pygame.

### Hasil Training

Setelah training selesai atau ada AI yang menyelesaikan target lap:

- `models/winner_genome.pkl` - Genome AI terbaik
- `models/winner_network.pkl` - Neural network siap pakai

### Checkpoint Training

Training otomatis menyimpan checkpoint setiap 10 generasi di folder `neat_checkpoints/`.
Jika training terputus, kamu bisa melanjutkan dari checkpoint terakhir.

---

## 5. Konfigurasi Training

### File: `config.txt`

Ini adalah file konfigurasi NEAT. Parameter yang sering diubah:

```ini
[NEAT]
pop_size = 30              # Jumlah motor per generasi
                           # Lebih banyak = eksplorasi lebih luas, tapi lebih lambat
```

### Parameter di `trainer.py`

```python
max_gen_time = 60          # Maks waktu per generasi (detik)
max_time_between_checkpoints = 15 * 60  # 15 detik antara checkpoint
target_laps = 3            # Target lap untuk menang
```

### Tips Konfigurasi

| Situasi        | Rekomendasi                      |
| -------------- | -------------------------------- |
| Track mudah    | pop_size=30, max_gen_time=30     |
| Track sulit    | pop_size=100, max_gen_time=60    |
| Training cepat | pop_size=30, kurangi target_laps |
| Hasil terbaik  | pop_size=100, generations=200+   |

---

## 6. Mengedit Masking

### Apa itu Masking?

Masking adalah gambar overlay yang menentukan zona-zona di track:

- Track (hitam) - Jalan normal
- Slow zone (putih/abu) - Kecepatan berkurang
- Wall (merah) - Bounce/meledak
- Checkpoint 1-4 (hijau, cyan, kuning, magenta)

### File Masking

| File                    | Digunakan Untuk     |
| ----------------------- | ------------------- |
| `assets/masking.png`    | Player di main game |
| `assets/ai_masking.png` | AI saat training    |

### Membuat Masking

1. Buka track di software gambar (Photoshop, GIMP, Paint.NET)
2. Buat layer baru di atas track
3. Gambar zona-zona dengan warna yang sesuai:

| Zona         | Warna (RGB)           |
| ------------ | --------------------- |
| Track        | Hitam (0, 0, 0)       |
| Slow Zone    | Putih (255, 255, 255) |
| Wall         | Merah (255, 0, 0)     |
| Checkpoint 1 | Hijau (0, 255, 0)     |
| Checkpoint 2 | Cyan (0, 255, 255)    |
| Checkpoint 3 | Kuning (255, 255, 0)  |
| Checkpoint 4 | Magenta (255, 0, 255) |

4. Save sebagai `masking.png` atau `ai_masking.png`

### Aturan Checkpoint

- Checkpoint harus dilewati berurutan: 1 -> 2 -> 3 -> 4 -> 1 -> ...
- Taruh checkpoint di posisi strategis mengelilingi track
- Pastikan checkpoint cukup besar (lebar minimal 50 pixel)

### Contoh Layout Checkpoint

```
                    [CP2 - Cyan]
                        |
                        v
[START/FINISH] ---> Track ---> [CP3 - Kuning]
     ^                              |
     |                              v
[CP1 - Hijau] <--- Track <--- [CP4 - Magenta]
```

---

## 7. Troubleshooting

### AI Tidak Bergerak

**Penyebab**: Neural network output selalu sama (stuck)

**Solusi**:

- Restart training
- Tunggu beberapa generasi (evolusi butuh waktu)

### Checkpoint Tidak Terdeteksi

**Penyebab**: Warna di masking tidak sesuai threshold

**Solusi**: Pastikan warna checkpoint benar-benar pure:

- Hijau: RGB(0, 255, 0) - bukan (50, 200, 50)
- Cyan: RGB(0, 255, 255)
- Kuning: RGB(255, 255, 0)
- Magenta: RGB(255, 0, 255)

### Lap Tidak Terhitung

**Penyebab**: AI tidak kembali ke area start atau checkpoint tidak lengkap

**Solusi**:

- Cek apakah semua 4 checkpoint terlewati (lihat output "[CP OK]")
- Pastikan AI melewati area start setelah CP4

### Training Terlalu Lambat

**Penyebab**: Populasi terlalu besar atau waktu generasi terlalu lama

**Solusi**:

- Kurangi `pop_size` di config.txt
- Kurangi `max_gen_time` di trainer.py

### AI Mati Terlalu Cepat

**Penyebab**: Timeout terlalu singkat atau banyak failed lap

**Solusi**:

- Tambah `max_time_between_checkpoints` (default 15 detik)
- Tambah `max_failed_lap_checks` di motor.py (default 5)

### Error "ModuleNotFoundError"

**Penyebab**: Package belum terinstall

**Solusi**:

```bash
pip install pygame neat-python
```

### Error "FileNotFoundError: masking.png"

**Penyebab**: File masking tidak ada

**Solusi**: Buat file masking.png di folder assets

---

## Tips Training

1. **Mulai dengan track sederhana** - Track oval atau kotak lebih mudah untuk AI

2. **Checkpoint yang jelas** - Taruh checkpoint di corner atau titik penting

3. **Jangan terlalu banyak populasi** - 30-50 sudah cukup untuk track sederhana

4. **Biarkan berjalan lama** - AI butuh 50+ generasi untuk mulai optimal

5. **Save model terbaik** - Copy file di folder models/ sebelum training ulang

---

## Contoh Output Training yang Baik

```
Generation 0: Best fitness 2000 (AI masih random, banyak mati)
Generation 5: Best fitness 5000 (AI mulai belajar belok)
Generation 10: Best fitness 10000 (AI bisa keliling track)
Generation 20: Best fitness 20000 (AI mulai complete lap)
Generation 50: Best fitness 50000+ (AI optimal, multiple laps)
```

---

Dokumen ini dibuat pada 14 Desember 2024.

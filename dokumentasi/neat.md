# NEAT Algorithm - Dokumentasi Lengkap

> **N**euro**E**volution of **A**ugmenting **T**opologies

---

## Bagian 1: Penjelasan NEAT

### Apa itu NEAT?

NEAT adalah algoritma yang menggabungkan **Neural Networks** dengan **Genetic Algorithm** (evolusi). Berbeda dengan neural network tradisional yang strukturnya tetap, NEAT memungkinkan struktur network **berevolusi** seiring waktu.

### Komponen Utama NEAT

#### 1. Genome (DNA dari Neural Network)

Genome adalah representasi dari neural network dalam bentuk yang bisa dievolusi:

```
Genome
├── Nodes (Neuron)
│   ├── Input nodes (sensor)
│   ├── Hidden nodes (berkembang seiring evolusi)
│   └── Output nodes (aksi)
│
└── Connections (Sinapsis)
    ├── in_node → out_node
    ├── weight (kekuatan koneksi)
    └── enabled (aktif/tidak)
```

**Contoh Genome:**

```
Nodes: [Input1, Input2, Output1]
Connections:
  - Input1 → Output1, weight=0.5, enabled=True
  - Input2 → Output1, weight=-0.3, enabled=True
```

#### 2. Population (Populasi)

Kumpulan genome yang bersaing dalam satu generasi:

```
Generation 1:
┌─────────────────────────────────────────────┐
│ Genome1  Genome2  Genome3 ... Genome150     │
│ (fit=50) (fit=80) (fit=30)    (fit=120)     │
└─────────────────────────────────────────────┘
                    ↓
            Selection & Reproduction
                    ↓
Generation 2:
┌─────────────────────────────────────────────┐
│ Anak dari genome dengan fitness tinggi      │
└─────────────────────────────────────────────┘
```

#### 3. Species (Spesies)

NEAT mengelompokkan genome yang mirip ke dalam spesies yang sama. Ini melindungi inovasi baru dari kompetisi langsung dengan genome yang sudah optimal.

```
Population
├── Species A (Genome mirip struktur A)
│   ├── Genome1
│   └── Genome4
│
├── Species B (Genome mirip struktur B)
│   ├── Genome2
│   └── Genome5
│
└── Species C (Genome yang berbeda)
    └── Genome3
```

**Manfaat Speciation:**

- Inovasi baru dilindungi
- Diversity terjaga
- Mencegah premature convergence

### Proses Evolusi NEAT

```
      ┌─────────────────────────────────────────┐
      │           GENERASI 0                     │
      │  Random population (150 genome)          │
      └────────────────┬────────────────────────┘
                       │
                       ▼
      ┌────────────────────────────────────────┐
      │         EVALUATION (Fitness)            │
      │  Setiap genome diuji dan diberi skor    │
      └────────────────┬───────────────────────┘
                       │
                       ▼
      ┌────────────────────────────────────────┐
      │          SELECTION                      │
      │  Pilih genome dengan fitness tinggi     │
      └────────────────┬───────────────────────┘
                       │
                       ▼
      ┌────────────────────────────────────────┐
      │         REPRODUCTION                    │
      │  - Crossover (gabung 2 parent)          │
      │  - Mutation (ubah weight/struktur)      │
      └────────────────┬───────────────────────┘
                       │
                       ▼
      ┌────────────────────────────────────────┐
      │           GENERASI N+1                  │
      │  Population baru yang lebih baik        │
      └────────────────────────────────────────┘
                       │
                       ▼
               (Ulangi sampai target tercapai)
```

### Mutasi dalam NEAT

NEAT memiliki beberapa jenis mutasi:

#### Mutasi Weight

Mengubah kekuatan koneksi tanpa mengubah struktur:

```
Sebelum: Input1 → Output1, weight=0.5
Sesudah: Input1 → Output1, weight=0.7
```

#### Mutasi Add Connection

Menambah koneksi baru antara node yang ada:

```
Sebelum:                     Sesudah:
Input1 ──→ Output1          Input1 ──→ Output1
Input2 ──→ Output1          Input2 ──→ Output1
                            Input1 ──→ Input2 (BARU!)
```

#### Mutasi Add Node

Menambah node hidden baru dengan memecah koneksi:

```
Sebelum:                     Sesudah:
Input1 ────────→ Output1    Input1 → Hidden1 → Output1
           (disabled)                  ↑
                             Koneksi lama dimatikan
```

### Crossover (Reproduksi)

Dua parent dengan fitness tinggi digabung:

```
Parent A (fitness=100):          Parent B (fitness=80):
Node: [I1, I2, H1, O1]           Node: [I1, I2, O1]
Conn: [C1, C2, C3, C4]           Conn: [C1, C2, C5]

                    ↓ Crossover

Child:
Node: [I1, I2, H1, O1]  ← Dari parent dengan fitness lebih tinggi
Conn: [C1, C2, C3, C4]  ← Matching genes dari kedua parent
                          Disjoint/excess genes dari parent lebih fit
```

---

## Bagian 2: Penerapan NEAT di Projek Mio Karbu

### Arsitektur Neural Network

```
      INPUT LAYER              HIDDEN LAYER           OUTPUT LAYER
      (5 sensor radar)         (evolved by NEAT)      (2 kontrol)

   [Radar -90°] ─────┐                           ┌──→ [Steering]
                     │                           │    (-1 to +1)
   [Radar -45°] ─────┤         ┌───────┐         │
                     ├────────→│ NEAT  │─────────┤
   [Radar   0°] ─────┤         │ akan  │         │
                     ├────────→│evolve │─────────┤
   [Radar +45°] ─────┤         │hidden │         │
                     │         │ nodes │         │
   [Radar +90°] ─────┘         └───────┘         └──→ [Throttle]
                                                      (0.3 to 1.0)
```

### Input (5 Sensor Radar)

| Index | Deskripsi       | Range | Arti                  |
| ----- | --------------- | ----- | --------------------- |
| 0     | Radar kiri 90°  | 0-10  | 0=dekat wall, 10=jauh |
| 1     | Radar kiri 45°  | 0-10  |                       |
| 2     | Radar depan     | 0-10  |                       |
| 3     | Radar kanan 45° | 0-10  |                       |
| 4     | Radar kanan 90° | 0-10  |                       |

### Output (2 Kontrol)

| Index | Deskripsi | Range      | Arti                       |
| ----- | --------- | ---------- | -------------------------- |
| 0     | Steering  | -1 to +1   | -1=kiri, 0=lurus, +1=kanan |
| 1     | Throttle  | 0.3 to 1.0 | Kecepatan (min 30%)        |

### Proses Training

```python
# Pseudo-code alur training

for generation in range(total_generations):

    # 1. EVAL: Setiap genome diuji
    for genome in population:
        car = create_motor()
        network = create_network(genome)

        while car.alive:
            # Input dari radar
            radar_data = car.get_radar_data()  # [5, 8, 10, 7, 3]

            # Neural network decide
            output = network.activate(radar_data)  # [0.3, 0.8]

            # Apply ke motor
            steering = output[0]  # 0.3
            throttle = output[1]  # 0.8
            car.set_ai_input(steering, throttle)

            # Update
            car.update()

        # 2. FITNESS: Hitung skor
        genome.fitness = calculate_fitness(car)

    # 3. EVOLUSI: NEAT otomatis handle selection, crossover, mutation
    # Genome dengan fitness tinggi punya lebih banyak keturunan
```

### Perhitungan Fitness

Fitness menentukan "seberapa bagus" performa genome:

```python
def calculate_fitness(car):
    fitness = 0

    # Base: Jarak tempuh
    fitness += car.distance_traveled

    # Bonus: Checkpoint (sequential bonus lebih besar)
    fitness += car.checkpoint_count * 200

    # Bonus besar: Complete lap
    fitness += car.lap_count * 2000

    return fitness
```

**Contoh Fitness:**

| Skenario       | distance | checkpoints | laps | Fitness |
| -------------- | -------- | ----------- | ---- | ------- |
| Stuck di awal  | 100      | 0           | 0    | 100     |
| Setengah track | 500      | 2           | 0    | 900     |
| 1 lap complete | 1000     | 4           | 1    | 3800    |
| 3 lap complete | 3000     | 12          | 3    | 11400   |

### File Konfigurasi NEAT

File `config.txt` mengatur parameter evolusi:

```ini
[NEAT]
pop_size = 150              # Jumlah genome per generasi

[DefaultGenome]
num_inputs = 5              # 5 sensor radar
num_outputs = 2             # steering + throttle
activation_default = tanh   # Fungsi aktivasi

# Mutation rates
weight_mutate_rate = 0.75   # Peluang weight berubah
conn_add_prob = 0.5         # Peluang tambah koneksi
node_add_prob = 0.4         # Peluang tambah hidden node

[DefaultSpeciesSet]
compatibility_threshold = 2.0  # Threshold speciation

[DefaultStagnation]
max_stagnation = 15         # Gen tanpa improvement sebelum species mati

[DefaultReproduction]
elitism = 2                 # Genome terbaik langsung lolos
survival_threshold = 0.2    # Top 20% yang boleh reproduce
```

### Alur File dalam Training

```
train.py
    │
    ├── Load config.txt (NEAT parameters)
    │
    ├── Create NEATTrainer
    │   │
    │   ├── trainer.setup()
    │   │   ├── Load track surface
    │   │   └── Load masking surface
    │   │
    │   └── trainer.run(generations=100)
    │       │
    │       └── population.run(eval_genomes, 100)
    │           │
    │           └── eval_genomes() [LOOP per generation]
    │               │
    │               ├── Create 150 Motor
    │               ├── Create 150 Neural Network
    │               │
    │               └── [SIMULATION LOOP]
    │                   ├── Get radar data
    │                   ├── Network decide
    │                   ├── Apply steering/throttle
    │                   ├── Update motor
    │                   └── Calculate fitness
    │
    ├── Save checkpoint setiap 5 generasi
    │   └── neat_checkpoints/neat-checkpoint-X
    │
    └── Save winner
        ├── models/winner_genome.pkl
        └── models/winner_network.pkl
```

### Contoh Evolusi Network

```
=== Generasi 1 ===
Network sangat sederhana:
Input1 ─────────→ Output1
Input2 ─────────→ Output1
Input3 ─────────→ Output1
...

Hasil: AI hanya bisa jalan lurus, fitness rendah

=== Generasi 20 ===
Network mulai kompleks:
Input1 ──→ Hidden1 ──→ Output1
Input2 ──→ Hidden1
Input3 ──→ Hidden2 ──→ Output1
...

Hasil: AI mulai bisa belok, fitness meningkat

=== Generasi 50+ ===
Network optimal:
Input1 ──┬──→ Hidden1 ──┬──→ Output1
Input2 ──┤              │
Input3 ──┼──→ Hidden2 ──┼──→ Output2
Input4 ──┤              │
Input5 ──┴──→ Hidden3 ──┘

Hasil: AI bisa complete lap dengan konsisten
```

---

## Referensi

- Stanley, K. O., & Miikkulainen, R. (2002). "Evolving Neural Networks through Augmenting Topologies"
- Library: [neat-python](https://neat-python.readthedocs.io/)

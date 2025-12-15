# 📁 config.txt

> Path: `config.txt` (root project)

## Deskripsi

File konfigurasi untuk **NEAT algorithm**. Mengontrol semua parameter evolusi neural network.

---

## Struktur File

```
[NEAT]           → Parameter global NEAT
[DefaultGenome]  → Parameter struktur neural network
[DefaultSpeciesSet] → Parameter speciation
[DefaultStagnation] → Parameter stagnation/extinction
[DefaultReproduction] → Parameter reproduksi
```

---

## 🎯 Parameter Tunable

### [NEAT] Section

#### `pop_size`

Jumlah motor (genome) per generasi.

```
pop_size = 150
```

| Nilai   | Efek                    |
| ------- | ----------------------- |
| 30-50   | Cepat, tapi bisa stuck  |
| 100-150 | Balance (recommended)   |
| 200-300 | Eksplorasi luas, lambat |

#### `fitness_threshold`

Target fitness untuk stop training.

```
fitness_threshold = 100000.0
```

Set sangat tinggi jika mau training sampai generasi habis.

#### `no_fitness_termination`

Jangan stop meski fitness threshold tercapai.

```
no_fitness_termination = True
```

---

### [DefaultGenome] Section - Mutation Rates

#### `weight_mutate_rate`

Seberapa sering weight connection berubah.

```
weight_mutate_rate = 0.75
```

| Nilai   | Efek                   |
| ------- | ---------------------- |
| 0.3-0.5 | Stabil, lambat improve |
| 0.7-0.8 | Balance                |
| 0.9-1.0 | Agresif, jumpy fitness |

#### `weight_mutate_power`

Seberapa BESAR perubahan weight.

```
weight_mutate_power = 0.7
```

| Nilai   | Efek                          |
| ------- | ----------------------------- |
| 0.3-0.5 | Perubahan halus (fine-tuning) |
| 0.5-0.7 | Balance                       |
| 0.8-1.0 | Perubahan drastis             |

#### `bias_mutate_rate`

Seberapa sering bias neuron berubah.

```
bias_mutate_rate = 0.7
```

#### `conn_add_prob`

Probabilitas menambah koneksi baru.

```
conn_add_prob = 0.5
```

| Nilai   | Efek             |
| ------- | ---------------- |
| 0.2-0.3 | Network simpel   |
| 0.4-0.5 | Balance          |
| 0.6-0.8 | Network kompleks |

#### `node_add_prob`

Probabilitas menambah neuron hidden.

```
node_add_prob = 0.4
```

⚠️ Terlalu tinggi bisa bikin network bloated dan lambat!

---

### [DefaultSpeciesSet] Section

#### `compatibility_threshold`

Threshold untuk grouping genome ke species.

```
compatibility_threshold = 2.0
```

| Nilai   | Efek                     |
| ------- | ------------------------ |
| 1.0-2.0 | Banyak species, diverse  |
| 2.0-3.0 | Balance                  |
| 3.0-5.0 | Sedikit species, homogen |

---

### [DefaultStagnation] Section

#### `max_stagnation`

Hapus species yang tidak improve setelah N generasi.

```
max_stagnation = 15
```

| Nilai | Efek                         |
| ----- | ---------------------------- |
| 5-10  | Agresif remove stuck species |
| 10-15 | Balance                      |
| 20-30 | Beri waktu lebih lama        |

#### `species_elitism`

Minimal species yang selalu dipertahankan.

```
species_elitism = 2
```

---

### [DefaultReproduction] Section

#### `elitism`

Jumlah genome terbaik yang langsung lolos TANPA mutasi.

```
elitism = 2
```

| Nilai | Efek                  |
| ----- | --------------------- |
| 1     | Lebih exploratif      |
| 2-3   | Balance (recommended) |
| 3-5   | Preserve solusi bagus |

#### `survival_threshold`

Persentase genome yang boleh reproduce.

```
survival_threshold = 0.2
```

| Nilai   | Efek                       |
| ------- | -------------------------- |
| 0.1-0.2 | Seleksi ketat, hanya elite |
| 0.2-0.3 | Balance                    |
| 0.3-0.5 | Lebih banyak reproduce     |

---

## 📐 NEAT Algorithm Overview

### Apa itu NEAT?

**NEAT = NeuroEvolution of Augmenting Topologies**

Algoritma yang mengevolusi struktur DAN weight neural network secara bersamaan.

### Komponen Kunci

#### 1. Genome

Representasi neural network sebagai list genes (nodes + connections).

```
Genome = {
    nodes: [input_1, input_2, ..., output_1, output_2, hidden_1, ...],
    connections: [(from, to, weight, enabled), ...]
}
```

#### 2. Species

Grouping genome yang mirip untuk lindungi inovasi baru.

```
Species 1: [genome_1, genome_5, genome_12]
Species 2: [genome_2, genome_8]
...
```

#### 3. Fitness Sharing

Fitness dibagi dalam species untuk mencegah dominasi.

```
adjusted_fitness = raw_fitness / species_size
```

### Flow Tiap Generasi

```
1. Evaluate fitness semua genome
   └── Jalankan simulasi, hitung score

2. Speciation
   └── Kelompokkan genome ke species

3. Adjust fitness
   └── Bagi fitness dengan ukuran species

4. Reproduction
   ├── Elitism: Copy N terbaik langsung
   ├── Crossover: Gabungkan 2 parent
   └── Mutation:
       ├── Weight mutation
       ├── Bias mutation
       ├── Add connection
       └── Add node

5. Replace old population dengan new generation
```

---

## 🔧 Preset Configurations

### Eksplorasi Agresif

Untuk training awal, cari solusi baru.

```
pop_size = 200
weight_mutate_rate = 0.9
conn_add_prob = 0.6
node_add_prob = 0.4
max_stagnation = 10
```

### Stable Fine-tuning

Sudah punya model bagus, mau improve.

```
pop_size = 100
weight_mutate_rate = 0.5
conn_add_prob = 0.3
node_add_prob = 0.1
elitism = 5
```

### Fast Training

Untuk testing/debugging.

```
pop_size = 50
max_stagnation = 5
survival_threshold = 0.3
```

---

## Neural Network Architecture

```python
num_inputs = 5    # 5 sensor radar
num_hidden = 8    # Hidden nodes awal (NEAT akan evolve)
num_outputs = 2   # Steering (-1/+1), Throttle (-1/+1)
```

**Diagram:**

```
    Inputs (5)              Hidden (evolved)        Outputs (2)
    ┌───────┐                   ┌───┐
    │Radar 0│───────────────────│   │──────────┐
    └───────┘                   └───┘          │   ┌──────────┐
    ┌───────┐                   ┌───┐          ├───│ Steering │
    │Radar 1│───────────────┬───│   │──────────┤   └──────────┘
    └───────┘               │   └───┘          │
    ┌───────┐               │   ┌───┐          │   ┌──────────┐
    │Radar 2│───────────────┼───│   │──────────┴───│ Throttle │
    └───────┘               │   └───┘              └──────────┘
    ┌───────┐               │   ┌───┐
    │Radar 3│───────────────┴───│   │
    └───────┘                   └───┘
    ┌───────┐
    │Radar 4│
    └───────┘

    NEAT akan menambah/menghapus koneksi dan hidden nodes
```

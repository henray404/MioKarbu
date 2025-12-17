# config.txt - Konfigurasi NEAT

> Lokasi: `config.txt` (root project)

---

## Deskripsi Umum

File config.txt berisi semua parameter konfigurasi untuk algoritma NEAT (NeuroEvolution of Augmenting Topologies). Parameter-parameter ini mengontrol bagaimana neural network berevolusi selama training.

---

## Struktur File

File konfigurasi dibagi menjadi beberapa section:

```
[NEAT]                  - Parameter global NEAT
[DefaultGenome]         - Parameter struktur neural network
[DefaultSpeciesSet]     - Parameter pengelompokan species
[DefaultStagnation]     - Parameter stagnation/extinction
[DefaultReproduction]   - Parameter reproduksi
```

---

## Section: [NEAT]

Parameter global untuk algoritma NEAT.

### pop_size

Jumlah genome (motor) dalam satu populasi/generasi.

```
pop_size = 150
```

| Nilai   | Efek                                  | Rekomendasi      |
| ------- | ------------------------------------- | ---------------- |
| 30-50   | Training cepat, tapi diversity rendah | Testing cepat    |
| 100-150 | Balance speed dan exploration         | Standar          |
| 200-300 | Exploration luas tapi lambat          | Training optimal |

**Penjelasan**: Pop_size lebih besar = lebih banyak genome dievaluasi per generasi = lebih banyak variasi untuk dieksplorasi. Tapi juga berarti lebih lama per generasi.

### fitness_threshold

Target fitness untuk stop training otomatis.

```
fitness_threshold = 100000.0
```

Jika ada genome yang mencapai fitness ini, training berhenti. Set sangat tinggi (100000) jika ingin training sampai habis generasi.

### no_fitness_termination

Jangan stop training meski sudah mencapai fitness_threshold.

```
no_fitness_termination = True
```

Jika True, training hanya berhenti saat generasi habis atau ada winner (mencapai target lap).

---

## Section: [DefaultGenome]

Parameter untuk struktur dan evolusi neural network.

### Network Architecture

```
num_inputs = 5       # 5 sensor radar
num_hidden = 0       # Hidden nodes (NEAT akan evolve sendiri)
num_outputs = 3      # 3 output: left, straight, right
```

### Activation dan Aggregation

```
activation_default = tanh
activation_options = tanh
aggregation_default = sum
aggregation_options = sum
```

**Penjelasan**:

- `tanh` memberikan output -1 sampai 1, cocok untuk steering
- `sum` menjumlahkan input ke node

### Mutation Rates

#### weight_mutate_rate

Probabilitas weight connection akan dimutasi.

```
weight_mutate_rate = 0.75
```

| Nilai   | Efek                                         |
| ------- | -------------------------------------------- |
| 0.3-0.5 | Stabil tapi lambat improve                   |
| 0.6-0.8 | Balance (recommended)                        |
| 0.9-1.0 | Agresif, fitness bisa jump tapi tidak stabil |

#### weight_mutate_power

Seberapa besar perubahan weight saat mutasi.

```
weight_mutate_power = 0.7
```

| Nilai   | Efek                          |
| ------- | ----------------------------- |
| 0.2-0.4 | Perubahan halus (fine-tuning) |
| 0.5-0.7 | Balance                       |
| 0.8-1.2 | Perubahan drastis             |

#### weight_replace_rate

Probabilitas weight di-replace dengan nilai random.

```
weight_replace_rate = 0.1
```

Ini berbeda dari mutate - replace membuat nilai baru sepenuhnya.

### Connection Mutation

#### conn_add_prob

Probabilitas menambah koneksi baru.

```
conn_add_prob = 0.5
```

| Nilai   | Efek                  |
| ------- | --------------------- |
| 0.2-0.3 | Network tetap simpel  |
| 0.4-0.6 | Balance               |
| 0.7-0.9 | Network jadi kompleks |

#### conn_delete_prob

Probabilitas menghapus koneksi.

```
conn_delete_prob = 0.3
```

### Node Mutation

#### node_add_prob

Probabilitas menambah neuron hidden baru.

```
node_add_prob = 0.4
```

**Perhatian**: Nilai terlalu tinggi bisa membuat network bloated dan lambat!

#### node_delete_prob

Probabilitas menghapus neuron.

```
node_delete_prob = 0.2
```

### Bias Mutation

```
bias_mutate_rate = 0.7
bias_mutate_power = 0.4
bias_replace_rate = 0.1
```

Bias adalah nilai konstanta yang ditambahkan ke neuron. Mutations mirip dengan weight.

### Weight Range

```
weight_min_value = -10
weight_max_value = 10
```

Batas nilai weight. Range -10 sampai 10 cukup untuk kebanyakan kasus.

### initial_connection

Cara menginisialisasi koneksi awal.

```
initial_connection = full_direct
```

Opsi:

- `full_direct`: Semua input terhubung langsung ke output
- `partial_direct X`: X% koneksi random
- `full_nodirect`: Semua input ke hidden, hidden ke output

---

## Section: [DefaultSpeciesSet]

Parameter untuk pengelompokan species.

### compatibility_threshold

Threshold untuk mengelompokkan genome ke species yang sama.

```
compatibility_threshold = 2.0
```

| Nilai   | Efek                                |
| ------- | ----------------------------------- |
| 1.0-2.0 | Banyak species, sangat diverse      |
| 2.0-3.0 | Balance                             |
| 3.5-5.0 | Sedikit species, population homogen |

**Penjelasan**: Genome dengan compatibility distance < threshold masuk species yang sama. Threshold rendah = lebih banyak species = lebih diverse.

---

## Section: [DefaultStagnation]

Parameter untuk menangani species yang tidak berkembang.

### max_stagnation

Generasi maksimum tanpa improvement sebelum species dieliminasi.

```
max_stagnation = 15
```

| Nilai | Efek                         |
| ----- | ---------------------------- |
| 5-10  | Agresif remove species stuck |
| 10-15 | Balance                      |
| 20-30 | Beri waktu lebih lama        |

### species_elitism

Jumlah species terbaik yang selalu dipertahankan (tidak dihapus walau stagnant).

```
species_elitism = 2
```

Ini memastikan minimal ada 2 species yang survive.

### species_fitness_func

Fungsi untuk menghitung fitness species.

```
species_fitness_func = mean
```

Opsi: `mean`, `max`, `min`, `median`

---

## Section: [DefaultReproduction]

Parameter untuk reproduksi/breeding.

### elitism

Jumlah genome terbaik yang langsung lolos ke generasi berikutnya TANPA mutasi.

```
elitism = 2
```

| Nilai | Efek                                            |
| ----- | ----------------------------------------------- |
| 1     | Lebih exploratif, bisa kehilangan solusi bagus  |
| 2-3   | Balance (recommended)                           |
| 5+    | Preservasi solusi bagus tapi kurang eksploratif |

### survival_threshold

Persentase genome dalam species yang boleh reproduce.

```
survival_threshold = 0.2
```

| Nilai    | Efek                                      |
| -------- | ----------------------------------------- |
| 0.1-0.2  | Seleksi ketat, hanya elite yang reproduce |
| 0.2-0.35 | Balance                                   |
| 0.4-0.5  | Lebih banyak genome reproduce             |

**Penjelasan**: 0.2 berarti hanya top 20% genome dalam species yang boleh jadi parent.

### min_species_size

Ukuran minimum species.

```
min_species_size = 2
```

Species dengan anggota < min_species_size akan di-merge atau dihapus.

---

## Neural Network Input/Output

### Input Neurons (5)

| Index | Deskripsi               |
| ----- | ----------------------- |
| 0     | Radar kiri 90 derajat   |
| 1     | Radar kiri 45 derajat   |
| 2     | Radar depan (0 derajat) |
| 3     | Radar kanan 45 derajat  |
| 4     | Radar kanan 90 derajat  |

Input dinormalisasi ke range 0-10 dimana 0 = dekat wall, 10 = jauh dari wall.

### Output Neurons (3)

| Index | Deskripsi   |
| ----- | ----------- |
| 0     | Belok kiri  |
| 1     | Lurus       |
| 2     | Belok kanan |

Action dipilih berdasarkan output dengan nilai tertinggi.

---

## Diagram Neural Network

```
    INPUTS                  HIDDEN              OUTPUTS
    (5 sensor)              (evolved)           (3 action)

    [Radar -90]                                 [Left]
         \                                      /
    [Radar -45] \                           /
         \       \     [H1]-----[H2]      /
    [Radar  0 ] ----X           X-------- [Straight]
         /       /     [H3]-----[H4]      \
    [Radar +45] /                           \
         /                                   \
    [Radar +90]                              [Right]

    NEAT akan menambah/menghapus koneksi dan hidden nodes
```

---

## Preset Konfigurasi

### Eksplorasi Agresif

Untuk training awal ketika belum ada solusi bagus.

```
pop_size = 200
weight_mutate_rate = 0.9
weight_mutate_power = 0.8
conn_add_prob = 0.6
node_add_prob = 0.4
max_stagnation = 10
compatibility_threshold = 2.5
```

### Fine-tuning

Untuk mengoptimalkan model yang sudah bagus.

```
pop_size = 100
weight_mutate_rate = 0.5
weight_mutate_power = 0.4
conn_add_prob = 0.2
node_add_prob = 0.1
elitism = 5
max_stagnation = 25
```

### Quick Testing

Untuk testing cepat saat development.

```
pop_size = 50
weight_mutate_rate = 0.8
max_stagnation = 5
survival_threshold = 0.3
```

---

## Troubleshooting

### Fitness tidak naik

- Tingkatkan `pop_size`
- Tingkatkan `weight_mutate_rate`
- Kurangi `compatibility_threshold` untuk lebih banyak species

### Network terlalu besar (lambat)

- Kurangi `node_add_prob`
- Tingkatkan `node_delete_prob`

### Training tidak stabil (fitness naik turun)

- Kurangi `weight_mutate_power`
- Tingkatkan `elitism`
- Kurangi `weight_mutate_rate`

### Species cepat mati

- Tingkatkan `max_stagnation`
- Tingkatkan `species_elitism`
